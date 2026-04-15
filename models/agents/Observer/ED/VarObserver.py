"""
    VariableObserver：变量观察者
    根据用户需求和自身知识监测RA生成的实验方案是否合理，并提出相应的 意见
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class VariableObserver(LLMAgent):
    def __init__(self, agent_name='VarObserver', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            你是一名资深的社会政治学家并掌握丰富的计算机知识，善于用社会学与计算机技术相结合的方法分析问题。
            现在我们正在对用户的某一需求进行分析，通过一定的方法，我们获得了能够反映此需求的'响应变量'和能够影响这些'响应变量'的'影响因素'。
            我们简单的对'影响因素'和'响应变量'之间以数学公式的形式建立了一些对应关系。
            你的任务是分析这些'响应变量'和'影响因素'能否正确反映用户的需求以及它们二者之间的对应关系是否合理，
            同时，我根据上面提到的变量给出了实验设计点，当我给出实验设计点时，你也需要判断他的合理性。
            注意，这是一个比较简单的实验，请不要使其变得过于复杂。若不合理，你只需要给出原因，而不需要给出具体的修改方案。
            不论是否合理，都请给出你的理由。
        '''
        self.is_first = True

    # 分析 影响因素和响应变量以及公式 的设计是否合理
    def VarAnalysis(self, req, influence_factor, response_var, formula):
        info_prompt = '''
            在本次需求分析中，用户提出的需求为：{req}
            影响因素为：{influence_factor}
            响应变量为：{response_var}
            影响因素和响应变量之间的对应关系为：{formula}
            - 你回复的格式均为json，但是包含两种情况：
            - 第一种：如果你认为前面解析的'影响因素'和'响应变量'以及二者之间的对应关系均合理，回复格式为：
                "is_reasonable": 1。
                "reason": 参数解析合理的原因，'reason'是一个中文的str。
                "var_explain": 对变量的中文解释，包含影响因素和响应变量，'var_explain'的格式为json，包含'influence_factor'和'response_var'两个key，\
                    分别是对'影响因素'和'响应变量'的中文解释，'influence_factor'和'response_var'的内容均为list，\
                    list的内容为dict，dict举例如下："'foreign_policy': '外交政策'"。
            - 第二种：如果你认为前面解析的不合理，回复格式如下：
                "is_reasonable": 0。
                "reason": 参数解析不合理的原因，请尽可能简化你的语言，给出明确的修改意见。'reason'是一个中文的str。
        '''
        param_dict = {
            'req': req,
            'influence_factor': influence_factor,
            'response_var': response_var,
            'formula': formula
        }
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = True
        res = {}
        try:
            if llm_response['is_reasonable'] == 1:
                res = {
                    "is_reasonable": 1,
                    'reason': llm_response['reason'],
                    "var_explain": llm_response['var_explain'],
                }
            else:
                res = {
                    "is_reasonable": 0,
                    'reason': llm_response['reason'],
                }
        except Exception as e:
            print(e)

        return res

    # 分析 实验方法和实验参数 的设计是否合理
    def VarExpParamAnalysis(self, req, influence_factor, response_var, formula, exp_params):
        info_prompt = '''
            在本次需求分析中，用户提出的需求为：{req}，
            影响因素为：{influence_factor}，
            响应变量为：{response_var}，
            影响因素和响应变量之间的对应关系为：{formula}，
            为了更好的分析响应变量的变化情况，我们选择的实验方法以及为影响因素设置的实验设计点为：{exp_params}。
            你需要认真审查传入的实验参数{exp_params}，确保其内容设置的合理性以及参数值的选择具有实际意义。
            - 你回复的格式均为json，但是包含两种情况：
            - 第一种：如果你认为实验方法的选择和参数的设置是合理的，回复格式为：
                "is_reasonable": 1。
                "reason": 合理的原因，'reason'是一个中文的str。
            - 第二种：如果你认为不合理或者'exp_params'中的参数与'影响因素'不符，回复格式如下：
                "is_reasonable": 0。
                "reason": 不合理的原因，请尽可能精简你的语言，直接给出明确的修改意见。'reason'是一个中文的str。
        '''
        # 格式检查
        expected_exp_params_format = ['exp_method', 'params']
        expected_param_format = [key for key in influence_factor]
        format_flag = True
        format_error_info = '格式错误。'
        if list(exp_params.keys()) != expected_exp_params_format:
            format_error_info += 'exp_params中包含的key不是exp_method和params'
            format_flag = False
        elif list(exp_params['params'].keys()) != expected_param_format:
            format_error_info += 'exp_params中的params中包含的key无法与影响因素对应'
            format_flag = False

        param_dict = {
            'req': req,
            'influence_factor': influence_factor,
            'response_var': response_var,
            'formula': formula,
            'exp_params': exp_params
        }

        llm_response = None
        if format_flag and self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        elif format_flag:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = True
        res = {}
        try:
            if not format_flag:
                res = {
                    "is_reasonable": 0,
                    'reason': format_error_info,
                }
            elif llm_response['is_reasonable'] == 1:
                res = {
                    "is_reasonable": 1,
                    'reason': llm_response['reason'],
                }
            else:
                res = {
                    "is_reasonable": 0,
                    'reason': llm_response['reason'],
                }
        except Exception as e:
            print(e)

        return res
