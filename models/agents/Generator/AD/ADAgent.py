"""
    AgentDesignAgent：在需求分析完成后 设计Agent
"""
import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent


class AgentDesignAgent(LLMAgent):
    def __init__(self, agent_name='ADAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)
        self.system_prompt = '''
            你正在进行复杂社会模型系统推演中的需求分析和Agent设计工作。在此之前，需求的分析已经完成，
            - 你的工作有两种：
                第一种是参考之后提供的'需求'和解析完成之后的'实验设计方案'，设计实验需要的Agent。
                第二种是定我设计好的Agent列表以及人工判断后这些Agent设计错误的原因，你需要重新设计他们。
            这两种工作你都需要保证给出的Agent的属性能够覆盖'实验设计方案'中的'影响因素(influence_factor)'。\
            当然，你设计的Agent也不必拘泥于这些变量，你可以参考网络上的资料并结合自身知识来设计Agent。
            最终，你需要给出初始Agent的数量以及每个Agent的初始属性和属性值。
            若设计的Agent数量不小于2，你还要给出任意两个Agent之间的关系。
        '''
        self.is_first = True

    def agent_design(self, req, exp_plan):
        info_prompt = '''
            现在你需要进行第一种工作。
            用户的需求为：
                {req}
            实验设计方案为：
                {exp_plan}
            - 'exp_plan'中包含的内容解释如下:
                'goal': 实验目的。
                'influence_factor': 影响因素，也就是实验的自变量。
                'response_var': 响应变量，也就是实验的因变量。
                'formula': 影响因素和响应变量之间的对应关系。
                'exp_params': 实验参数。
                'var_explain': 对影响因素和响应变量以及公式的中文解释。
            - 当你回复时，必须采取下面的json格式:
                "attribute": Agent的属性
                "attribute_explain": Agent属性的解释
                "relationship_net": Agent之间的关系网络，包含任意两个Agent之间的关系
            - 接下来是对回复内容中每个key的解释：
            - "attribute"的格式为一个json数组，数组中的每个元素都是一个Agent的属性内容(json格式)。下面是数组中每个元素的json格式：
                "name": Agent的名称，请使用中文，例如'小明'、'小黑'、'大卫'或其他具有实际意义的名称等。
                "identify": Agent的身份，请使用中文，例如'银行柜员'、'国家领导人'、'国会成员'等。
                "age": Agent的年龄，是一个整数，例如'35'、'18'等。
                ...
                注意：'name'、'identify'、'age'是每个Agent的固有属性，而'...'代表的是需要由你来设计的属性，格式与前面提到的三个是相同的。
            - "attribute_explain"的格式为一个json数组，该数组长度与"attribute"数组第0号元素的内容数量相同，\
                数组中的每个元素都是对Agent的某个属性的解释。下面是数组中每个元素的json格式：
                "attribute": 属性名称，与"attribute"数组中的元素内容对应。
                "explain": 属性的解释，使用中文回答
            - "relationship_net"的格式为一个json数组，表示的是"attribute"数组中任意两个Agent之间的关系，需要同时包含A->B与B->A之间的关系。\
                该数组长度为n*(n-1)，其中n为"attribute"数组的长度。下面是对该数组中每个元素的描述：
                "source": 关系中的源智能体，为"attribute"数组中某个Agent的名称。
                "target": 关系中的目标智能体，为"attribute"数组中某个Agent的名称。
                "relationship": 源智能体和目标智能体之间的关系描述，例如'合作'，'竞争'，'同盟'，'敌对'，'恋人'，'未知'等等，\
                你需要结合需求的内容来选择合适的词来描述他们之间的关系。
        '''
        param_dict = {
            'req': req,
            'exp_plan': exp_plan,
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
            'attribute': [],
            'attribute_explain': [],
            'relationship_net': []
        }
        try:
            res = {
                "attribute": llm_response['attribute'],
                "attribute_explain": llm_response['attribute_explain'],
                "relationship_net": llm_response['relationship_net'],
            }
        except Exception as e:
            print(e)

        return res

    def agent_regenerate(self, req, exp_plan, agent_list, error_reason):
        info_prompt = '''
            现在你需要进行第二种工作。
            用户的需求为：
                {req}
            实验设计方案为：
                {exp_plan}
            我设计的智能体列表为：
                {agent_list}
            人工判断后认为智能体列表错误的原因为：
                {error_reason}
            - 'exp_plan'中包含的内容解释如下:
                'goal': 实验目的。
                'influence_factor': 影响因素，也就是实验的自变量。
                'response_var': 响应变量，也就是实验的因变量。
                'formula': 影响因素和响应变量之间的对应关系。
                'exp_params': 实验参数。
                'var_explain': 对影响因素和响应变量以及公式的中文解释。
            - 当你回复时，必须采取下面的json格式，请参考用户需求和错误原因在原先智能体列表的基础上进行修改:
                "attribute": Agent的属性
                "attribute_explain": Agent属性的解释
                "relationship_net": Agent之间的关系网络，包含任意两个Agent之间的关系
            - 接下来是对回复内容中每个key的解释：
            - "attribute"的格式为一个json数组，数组中的每个元素都是一个Agent的属性内容(json格式)。下面是数组中每个元素的json格式：
                "name": Agent的名称，请使用中文，例如'小明'、'小黑'、'大卫'或其他具有实际意义的名称等。
                "identify": Agent的身份，请使用中文，例如'银行柜员'、'国家领导人'、'国会成员'等。
                "age": Agent的年龄，是一个整数，例如'35'、'18'等。
                ...
                注意：'name'、'identify'、'age'是每个Agent的固有属性，而'...'代表的是需要由你来设计的属性，格式与前面提到的三个是相同的。
            - "attribute_explain"的格式为一个json数组，该数组长度与"attribute"数组第0号元素的内容数量相同，\
                数组中的每个元素都是对Agent的某个属性的解释。下面是数组中每个元素的json格式：
                "attribute": 属性名称，与"attribute"数组中的元素内容对应。
                "explain": 属性的解释，使用中文回答
            - "relationship_net"的格式为一个json数组，表示的是"attribute"数组中任意两个Agent之间的关系，需要同时包含A->B与B->A之间的关系。\
                该数组长度为n*(n-1)，其中n为"attribute"数组的长度。下面是对该数组中每个元素的描述：
                "source": 关系中的源智能体，为"attribute"数组中某个Agent的名称。
                "target": 关系中的目标智能体，为"attribute"数组中某个Agent的名称。
                "relationship": 源智能体和目标智能体之间的关系描述，例如'合作'，'竞争'，'同盟'，'敌对'，'恋人'，'未知'等等，\
                你需要结合需求的内容来选择合适的词来描述他们之间的关系。
        '''
        param_dict = {
            'req': req,
            'exp_plan': exp_plan,
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
            'attribute': [],
            'attribute_explain': [],
            'relationship_net': []
        }
        try:
            res = {
                "attribute": llm_response['attribute'],
                "attribute_explain": llm_response['attribute_explain'],
                "relationship_net": llm_response['relationship_net'],
            }
        except Exception as e:
            print(e)

        return res
