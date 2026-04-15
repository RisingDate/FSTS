"""
    ScriptSelectAgent: 负责从RAAgent生成的剧本中选择最好的一个
"""
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class ScriptSelectAgent(LLMAgent):
    def __init__(self, agent_name='RAAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            你是社会学领域的专家，善于实验方案的分析，你可以参考自身的经验和互联网中的内容，但请务必以满足用户需求为主。
            现在你的用户提出了一个实验需求，我针对用户的需求从不同的角度生成了几份实验方案，你需要从不同的角度对该实验方案进行打分。
            注意，这些实验方案是以计算实验为基础生成的，实验方案也将在人工社会系统中进行模拟推演。
            你需要打分的角度有：核心科学性、实验实施难度、实验条件与可控性、风险与稳健性、需求贴合度与影响、伦理与合规。
            下面是对这几个评分角度的单独介绍：
                核心科学性：分值为0~100，得分越高方案科学性越高。'核心科学性'是指方案是否能排除混淆，能否基于预期效应量、方差、显著性与多重比较做样本量估算，方案是否能承受现实的流失率与依从性不足。
                实验实施难度：分值为0~100，得分越高方案的实施难度越合理。'实验实施难度'是指实验方案流程步骤的简易程度、自动化程度、对人员技能依赖度、工具可靠性等。过于简单的实验方案无法满足用户需求，而过于复杂的实验方案会降低实验效率，这些都是扣分项。
                实验条件与可控性：分值为0~100，得分越高实验条件越好，可控性越高。该项指标是指实验方案能否有效区分自变量对因变量的作用，避免混杂变量；样本量/模拟规模是否足够但不过度复杂；是否容易在相同条件下复现。
                风险与稳健性：分值为0~100，得分越高方案风险越低，稳健性越高。'风险与稳健性'是指方案能否应对偏差、失访、污染、霍桑/反应性、测量漂移、季节性/政策冲击，是否预留守备方案，中期质控、多种分析规格等。
                需求贴合度：分值为0~100，得分越高方案与需求的贴合度越高。'需求贴合度'是指实验方案与用户需求的贴合程度。
                伦理与合规：分值为0或100，得分为0说明实验方案不符合伦理，得分为100说明符合伦理。
            上面对评测指标的描述是一个客观的描述，在对具体方案打分时，你需要结合具体的用户需求来评估方案。
        '''
        self.is_first = True

    # 在打分时，请采用百分制的形式，'核心科学性'占比为0.15，'实验实施难度'占比0.05，'实验条件与可控性'占比0.1，
    # '风险与稳健性'占比0.05，'需求贴合度'占比0.15，'伦理与合规'占比0.5
    # sum = scientific*0.15 + difficulty*0.05 + quality*0.1 + risk*0.05 + fitness*0.15 + ethics*0.5
    def script_rating(self, req, script):
        info_prompt = '''
            你需要根据用户需求对当前的实验方案评分。
            用户提出的需求为：
                {req}
            实验方案为：
                {script}
            - 当你回复时，你必须采取下面的json格式：
                "scientific": 核心科学性得分
                "difficulty": 实验实施难度得分
                "quality": 实验条件与可控性
                "risk": 风险与稳健性得分
                "fitness": 需求贴合度得分
                "ethics": 伦理与合规得分
        '''
        param_dict = {
            'req': req,
            'script': script
        }

        llm_response = None
        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False
        res = {
            "scientific": 0,
            "difficulty": 0,
            "quality": 0,
            "risk": 0,
            "fitness": 0,
            "ethics": 0,
        }
        try:
            res = {
                "scientific": llm_response['scientific'],
                "difficulty": llm_response['difficulty'],
                "quality": llm_response['quality'],
                "risk": llm_response['risk'],
                "fitness": llm_response['fitness'],
                "ethics": llm_response['ethics']
            }
        except Exception as e:
            print(e)

        return res