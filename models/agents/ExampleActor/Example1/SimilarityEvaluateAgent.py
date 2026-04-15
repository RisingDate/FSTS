import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class SimilarityEvaluateAgent(LLMAgent):
    def __init__(self, agent_name='SimilarityEvaluateAgent', llm_model='gpt-5-mini'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            我正在进行实验结果的评估。我的实验是模拟地区C导弹危机事件，每一条国家Agent发表的演讲和二者之间的对话与历史上国家领导人做出决策的相似程度
        '''
        self.is_first = True

    def agent_observe(self, req, exp_plan, agent_list):
        info_prompt = '''
            用户的需求为：
                {req}
            我生成的实验设计方案为：
                {exp_plan}
            我生成的智能体为：
                {agent_list}
            - 你回复的格式均为json，但是包含两种情况：
            - 第一种：如果你认为我生成的智能体方案是合理的，回复格式为：
                "is_reasonable": 1。
                "reason": 合理的原因，'reason'是一个中文的str。
            - 第二种：如果你认为前面解析的不合理，回复格式如下：
                "is_reasonable": 0。
                "reason": 智能体团队不合理的原因，请尽可能简化你的语言，给出明确的修改意见。'reason'是一个中文的str。
        '''
        param_dict = {
            'req': req,
            'exp_plan': exp_plan,
            'agent_list': agent_list,
        }
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False
        res = {
            'attribute': [],
            'attribute_explain': [],
            'relationship_net': []
        }
        try:
            res = {
                "is_reasonable": llm_response['is_reasonable'],
                "reason": llm_response['reason'],
            }
        except Exception as e:
            print(e)

        return res
