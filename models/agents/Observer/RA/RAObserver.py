import json
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class RequirementAnalysisObserver(LLMAgent):
    def __init__(self, agent_name='RAObserver', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name,
                         has_chat_history=False,
                         online_track=False,
                         json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            我有一个分析用户需求的Agent，你的任务是分析判断这个Agent解析的结果是否正确。
            同时，你还需要复杂查看用户需求是否符合最低的实验要求，你需要仔细思考用户的需求，通过你已有的知识判断是否包含符合实验要求。
            例如对于一个历史事件的复现，你可以联网搜索该事件的相关内容
        '''
        self.is_first = True

    # 判断用户需求是否包含 研究目标、核心变量 和 作用对象 三个要素
    def requirement_observe(self, req):
        info_prompt = '''
            你需要判断我给出的用户需求 {req} 是否包含 '研究目标'， '核心变量'和'作用对象'三个要素。
            - 你回复的格式均为json，但是包含两种情况：
            - 当用户需求包含这三个要素时，你的回复格式如下：
                "flag": 1
                "goal": 从用户需求中解析到的研究目标
                "variable": 从用户需求中解析到的核心变量
                "object": 从用户需求中解析得到的作用对象
            - 当用户需求不包含这三个要素时，你的回复格式如下：
                "flag": 0
                "reason": 不符合要求的原因
        '''
        param_dict = {
            'req': req,
        }
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False

        print("llm_response", llm_response)
        res = {}
        try:
            if llm_response["flag"] == 1:
                res = {
                    "flag": 1,
                    "goal": llm_response['goal'],
                    "variable": llm_response['variable'],
                    "object": llm_response['object'],
                }
            else:
                res = {
                    "flag": 0,
                    "reason": llm_response['reason'],
                }
        except Exception as e:
            print('exception', e)
        return res

    def requirement_format_judge(self, analysis_res: json) -> bool:
        target_keys = ['goal', 'influence_factor', 'response_var', 'formula', 'exp_params']
        goal_keys = ['category', 'explain']
        exp_params_keys = ['exp_method', 'params']
        print(target_keys)
        if list(analysis_res.keys()) != target_keys or list(analysis_res['goal'].keys()) != goal_keys \
                or list(analysis_res['exp_params'].keys()) != exp_params_keys \
                or type(analysis_res['exp_params']['params']) is not dict:
            print("JSON格式错误")
            return False
        elif len(analysis_res['response_var']) != len(analysis_res['formula']):
            print("响应变量与公式数量不符")
            return False
        return True
