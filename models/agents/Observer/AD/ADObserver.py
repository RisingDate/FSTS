"""
    AgentDesignObserver：观察生成的Actors是否合理
"""
import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class AgentDesignObserver(LLMAgent):
    def __init__(self, agent_name='ADAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            你正在进行复杂社会模型系统推演中的需求分析和Agent设计工作。在此之前，我针对用户的需求提出了一个合理的实验方案，并根据需求和此方案生成了实验所需的Agents。
            你的工作是：参考之后提供的'需求'和'实验方案'，判断我生成的Agent的数量和属性是否合理。
            若不合理，请使用最简练的语言给出不合理的原因。
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

    def format_check(self, agent_design_res: dict) -> (bool, str):
        if type(agent_design_res) != dict:
            return False, '结果不是一个json'
        elif set(agent_design_res.keys()) != {'attribute', 'attribute_explain', 'relationship_net'}:
            return False, '内容key值不正确'
        elif (type(agent_design_res['attribute']) != list or type(agent_design_res['attribute_explain']) != list
              or type(agent_design_res['relationship_net']) != list):
            return False, '存在value不为数组'

        agent_num = len(agent_design_res['attribute'])
        if len(agent_design_res['relationship_net']) != agent_num * (agent_num - 1):
            return False, '关系网络中关系数错误'

        return True, '格式正确'
