"""
    VariableRegenerateAgent：变量重新生成 Agent
    根据VarObserver提出的 意见 修改剧本中的影响因素、响应变量及其之间的对应关系 和 实验设计点
"""

import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class VariableRegenerateAgent(LLMAgent):
    def __init__(self, agent_name='VRAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            你是一名资深的社会政治学家，善于用社会学的方法分析国家之间的关系。现在我们正在对用户的某一需求进行分析。
            通过一定的方法，我们获得了能够反映此需求的'响应变量'和能够影响这些'响应变量'的'影响因素'。
            我们简单的对'影响因素'和'响应变量'之间以数学公式的形式建立了一些对应关系。
            但是经过人工判断之后，我们认为方案中的这些内容是有问题的。
            你的任务是根据我给出的修改意见，在原有信息的基础上，修改'影响因素'和'响应变量'以及他们之间的对应公式。
            注意：下面是你掌握的计算实验方法内容，请你在选择实验方法时尽可能的参考下面的内容：
                计算实验方法可以分为确定性实验设计和非确定性实验设计，
                确定性实验设计包括：'一次一因子设计'，'NK因子设计'，'网格设计'，'超饱和设计'，'均匀设计'，'正交设计'，'拉丁方设计'，
                '分布因子设计'，'顺序分支设计'，'迭代分布析因设计'，'多步组筛选设计' 和 '托辛筛选设计'；
                非确定性实验设计包括：'Monte Carlo'，'Markov-Chain Monte Carlo' 和 '重采样'三类方法
        '''
        self.is_first = True

    # 重新生成 影响因素和响应变量以及公式
    def VarRegenerate(self, req, influence_factor, response_var, formula, error_reason):
        info_prompt = '''
            在本次需求分析中，用户提出的需求为：{req}
            影响因素为：{influence_factor}
            响应变量为：{response_var}
            影响因素和响应变量之间的对应关系为：{formula}
            人工判断后认为存在的问题是：{error_reason}
            - 你回复的格式为json，具体格式如下：
                "influence_factor": 影响因素，即实验的自变量，能够尽可能全面的反应对实验的影响，'influence_factor'为一个list。\
                    'influence_factor'的内容全部为英文。
                "response_var": 响应变量，即实验的因变量，能够客观的反映实验的结果，'response_var'为一个list，\
                    'response_var'的内容全部为英文。
                "formula": 影响因素和响应变量之间的对应公式，每个响应变量都有一个确定的对应公式，公式以数学公式的形式给出，\
                    'formula'的格式为json，每个元素的key为响应变量的名称，value为影响因素组成的一个公式，'formula'的长度与'response_var'相同\
                    'formula'的内容全部为英文。'formula'中不应该包含未知量，也不应该包含隐形的函数。
                "var_explain": 对变量的中文解释，包含新生成的影响因素和响应变量，'var_explain'的格式为json，包含'influence_factor'和'response_var'两个key，\
                    分别是对'影响因素'和'响应变量'的中文解释，'influence_factor'和'response_var'的内容均为list，\
                    list的内容为dict，dict举例如下："'foreign_policy': '外交政策'"。
                "formula_explain": 对公式的中文解释，说出你对构造每个公式的思考过程，'formula_explain'是一个json，key的形式为'formula1', 'formula2'....
                    'formula_explain'的key数量需要和'formula'的长度相同。
            '''
        param_dict = {
            'req': req,
            'influence_factor': influence_factor,
            'response_var': response_var,
            'formula': formula,
            'error_reason': error_reason
        }

        llm_response = None
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = True
        res = {}
        try:
            res = {
                'influence_factor': llm_response['influence_factor'],
                'response_var': llm_response['response_var'],
                'formula': llm_response['formula'],
                'var_explain': llm_response['var_explain'],
                'formula_explain': llm_response['formula_explain'],
            }
        except Exception as e:
            print(e)

        return res

    # 分析 实验方法和实验参数 的设计是否合理
    def VarExpParamRegenerate(self, req, influence_factor, response_var, formula, exp_params, error_reason):
        info_prompt = '''
            在本次需求分析中，用户提出的需求为：{req}，
            影响因素为：{influence_factor}，
            响应变量为：{response_var}，
            影响因素和响应变量之间的对应关系为：{formula}，
            为了更好的分析响应变量的变化情况，我们选择的实验方法以及生成的实验设计点为：{exp_params}，
            人工判断后认为实验设计点存在的问题为：{error_reason}。
            - 你回复的格式为json，具体回复格式为：
                "exp_params": 这是你重新分析后对实验设置的参数，你需要在给出的实验设计点的基础上参考错误原因进行修改。
                    实验参数的格式为json，与传入的'exp_params'格式完全相同但内容不同，包含'exp_method'和'params'，\
                    'exp_method'是实验方法，具体参考上面提到的计算实验方法，'exp_method'是一个简单的字符串，只包含实验方法的名称。\
                    'params'是根据'exp_method'生成的实验参数，你需要根据实验方法生成多组实验，每组实验是影响因素的不同取值水平组合，请设置合理的实验组数。\
                    'params'是一个json，而不是一个list，'params'中key的数量与影响因素相等，每个元素的key为影响因素的名称，value为影响因素的取值，所有影响因素的取值数量应该相同。\
                    'params'的内容全部为英文，只需要包含取值组合，而不需要包含额外的解释。
        '''
        param_dict = {
            'req': req,
            'influence_factor': influence_factor,
            'response_var': response_var,
            'formula': formula,
            'exp_params': exp_params,
            'error_reason': error_reason
        }

        llm_response = None
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = True
        res = {}
        try:
            res = {
                'exp_params': llm_response['exp_params'],
            }
        except Exception as e:
            print(e)

        return res
