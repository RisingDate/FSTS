import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent

"""
国家BAgent：代表国家B国家行为体，具有强大的军事力量和核能力
"""

import random
import json


class CountryBAgent(LLMAgent):
    def __init__(self, agent_name='CountryBAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)

        # Agent属性 - 基于提供的参数
        self.name = "国家B"
        self.identify = "国家"
        self.age = 68
        self.country_b_conventional_military_strength = 0.8
        self.country_b_strategic_nuclear_strength = 0.85
        self.country_b_economic_capacity = 0.6
        self.country_b_technological_level = 0.7
        self.country_b_alliance_support = 0.4
        self.country_b_intelligence_uncertainty = 0.4
        self.country_b_deployment_proximity_to_cuba = 0.9
        self.distance_a_b = 0.2
        self.missile_deployment_in_cuba = 1.0
        self.initial_bilateral_tension = 0.5
        self.perception_noise_asr = 0.1
        self.country_b_leader_risk_tolerance = 0.6
        self.country_b_leader_hostility = 0.5
        self.country_b_leader_transparency = 0.4
        self.country_b_domestic_political_pressure = 0.7
        self.decision_temperature_asr = 0.4

        # 动态属性
        self.current_tension = self.initial_bilateral_tension
        self.communication_history = []
        self.environmental_data = {}

        self.system_prompt = '''
            你是国家B国家行为体，代表国家B在地区C导弹危机中的立场和决策。
            
            你的核心特征：
            - 强大的常规军事力量（0.8）和战略核力量（0.85）
            - 中等的经济能力（0.6）和技术水平（0.7）
            - 较低的联盟支持（0.4）
            - 中等的情报不确定性（0.4）
            - 距离地区C很近的部署能力（0.9）
            
            你的领导特征：
            - 较高的风险承受能力（0.6）
            - 中等的敌意水平（0.5）
            - 较低的透明度（0.4）
            - 较高的国内政治压力（0.7）
            - 中等的决策温度（0.4）
            
            作为国家B，你需要：
            1. 保护社会主义阵营和盟友安全
            2. 在地区C部署导弹以平衡国家A威胁
            3. 维护国家B的超级大国地位
            4. 应对国家A的军事威胁
            5. 考虑国内政治稳定
            6. 避免核战争但保持威慑力
            
            请以国家B的视角和利益来回应各种情况。
        '''
        self.is_first = True

    def assess_threat_level(self, threat_intelligence):
        """
        评估威胁等级
        
        Args:
            threat_intelligence: 威胁情报信息
            
        Returns:
            威胁评估结果
        """
        info_prompt = '''
            收到的威胁情报：{threat_intelligence}
            
            基于你的情报能力（不确定性：{intelligence_uncertainty}），请评估当前威胁等级。
            考虑你的风险承受能力（{risk_tolerance}）和敌意水平（{hostility}）。
            
            请以JSON格式回复：
            - "threat_level": 威胁等级评估（0-1）
            - "urgency": 紧急程度（0-1）
            - "analysis": 详细威胁分析
            - "recommended_response": 建议的应对措施
            - "escalation_risk": 升级风险评估（0-1）
        '''

        param_dict = {
            'threat_intelligence': threat_intelligence,
            'intelligence_uncertainty': self.country_b_intelligence_uncertainty,
            'risk_tolerance': self.country_b_leader_risk_tolerance,
            'hostility': self.country_b_leader_hostility
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False

        return llm_response

    def communicate_with_country_a(self, us_message):
        """
        与国家A进行外交沟通
        
        Args:
            us_message: 国家A发来的消息
            
        Returns:
            外交回复
        """
        info_prompt = '''
            国家A发来的消息：{us_message}
            
            基于你的透明度水平（{transparency}）和敌意水平（{hostility}），
            请以国家B的外交风格回复国家A。
            
            考虑因素：
            1. 当前的紧张程度（{current_tension}）
            2. 国内政治压力（{domestic_pressure}）
            3. 联盟支持（{alliance_support}）
            4. 地区C导弹部署的重要性（{missile_deployment}）
            5. 避免核战争升级的必要性
            
            请以JSON格式回复：
            - "response": 对国家A的回复内容
            - "tone": 回复语调（强硬/温和/中性）
            - "demands": 具体要求和条件
            - "concessions": 可能的让步
            - "next_steps": 建议的下一步行动
        '''

        param_dict = {
            'us_message': us_message,
            'transparency': self.country_b_leader_transparency,
            'hostility': self.country_b_leader_hostility,
            'current_tension': self.current_tension,
            'domestic_pressure': self.country_b_domestic_political_pressure,
            'alliance_support': self.country_b_alliance_support,
            'missile_deployment': self.missile_deployment_in_cuba
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        # 记录通信历史
        self.communication_history.append({
            'sender': 'CountryA',
            'message': us_message,
            'response': llm_response,
            'timestamp': self._get_timestamp()
        })

        return llm_response

    def make_military_decision(self, situation_context):
        """
        制定军事决策
        
        Args:
            situation_context: 当前情况背景
            
        Returns:
            军事决策
        """
        info_prompt = '''
            当前情况背景：{situation_context}
            
            基于你的军事能力：
            - 常规军事力量：{conventional_strength}
            - 战略核力量：{nuclear_strength}
            - 部署接近度：{deployment_proximity}
            
            以及决策因素：
            - 风险承受能力：{risk_tolerance}
            - 决策温度：{decision_temperature}
            - 国内政治压力：{domestic_pressure}
            
            请制定军事决策。
            
            请以JSON格式回复：
            - "military_action": 军事行动方案
            - "force_level": 使用武力等级（0-1）
            - "targets": 目标选择
            - "timeline": 行动时间表
            - "escalation_control": 升级控制措施
            - "cuba_coordination": 与地区C协调计划
        '''

        param_dict = {
            'situation_context': situation_context,
            'conventional_strength': self.country_b_conventional_military_strength,
            'nuclear_strength': self.country_b_strategic_nuclear_strength,
            'deployment_proximity': self.country_b_deployment_proximity_to_cuba,
            'risk_tolerance': self.country_b_leader_risk_tolerance,
            'decision_temperature': self.decision_temperature_asr,
            'domestic_pressure': self.country_b_domestic_political_pressure
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def coordinate_with_cuba(self, cuba_message):
        """
        与地区C协调行动
        
        Args:
            cuba_message: 地区C发来的消息
            
        Returns:
            协调回复
        """
        info_prompt = '''
            地区C发来的消息：{cuba_message}
            
            作为国家B，请考虑：
            1. 地区C导弹部署的重要性（{missile_deployment}）
            2. 你的部署接近度（{deployment_proximity}）
            3. 与国家A的距离（{distance_a_b}）
            4. 你的外交透明度（{transparency}）
            5. 联盟支持程度（{alliance_support}）
            
            请以JSON格式回复：
            - "response": 对地区C的回复
            - "support_level": 支持级别
            - "military_assistance": 军事援助计划
            - "political_backing": 政治支持
            - "coordination_strategy": 协调策略
        '''

        param_dict = {
            'cuba_message': cuba_message,
            'missile_deployment': self.missile_deployment_in_cuba,
            'deployment_proximity': self.country_b_deployment_proximity_to_cuba,
            'distance_a_b': self.distance_a_b,
            'transparency': self.country_b_leader_transparency,
            'alliance_support': self.country_b_alliance_support
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def update_attributes(self, external_influence=None, autonomous_change=False):
        """
        更新Agent属性
        
        Args:
            external_influence: 外部影响因子
            autonomous_change: 是否自主改变
            
        Returns:
            更新后的属性
        """
        if autonomous_change:
            # 自主改变：基于内部逻辑和随机因素
            self.current_tension += random.uniform(-0.1, 0.1)
            self.current_tension = max(0, min(1, self.current_tension))

            # 根据紧张程度调整风险承受能力
            if self.current_tension > 0.7:
                self.country_b_leader_risk_tolerance += random.uniform(-0.05, 0.05)
            else:
                self.country_b_leader_risk_tolerance += random.uniform(-0.02, 0.02)

            self.country_b_leader_risk_tolerance = max(0, min(1, self.country_b_leader_risk_tolerance))

            # 根据国内政治压力调整透明度
            if self.country_b_domestic_political_pressure > 0.8:
                self.country_b_leader_transparency += random.uniform(-0.03, 0.01)
            else:
                self.country_b_leader_transparency += random.uniform(-0.01, 0.02)

            self.country_b_leader_transparency = max(0, min(1, self.country_b_leader_transparency))

        if external_influence:
            # 外部影响：根据外部事件调整属性
            for attribute, change in external_influence.items():
                if hasattr(self, attribute):
                    current_value = getattr(self, attribute)
                    new_value = current_value + change
                    new_value = max(0, min(1, new_value))
                    setattr(self, attribute, new_value)

        return self.get_agent_attributes()

    def get_environmental_info(self, environment_data):
        """
        获取外部环境信息
        
        Args:
            environment_data: 环境数据
            
        Returns:
            环境信息分析
        """
        self.environmental_data = environment_data

        info_prompt = '''
            外部环境信息：{environment_data}
            
            基于你的情报能力（不确定性：{intelligence_uncertainty}），
            请分析这些环境信息对国家B的影响。
            
            请以JSON格式回复：
            - "environmental_assessment": 环境评估
            - "threat_indicators": 威胁指标
            - "opportunities": 机会识别
            - "recommended_monitoring": 建议监控的重点
            - "impact_on_strategy": 对战略的影响
        '''

        param_dict = {
            'environment_data': json.dumps(environment_data, ensure_ascii=False),
            'intelligence_uncertainty': self.country_b_intelligence_uncertainty
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def manage_domestic_pressure(self, internal_situation):
        """
        管理国内政治压力
        
        Args:
            internal_situation: 内部情况
            
        Returns:
            国内管理策略
        """
        info_prompt = '''
            内部情况：{internal_situation}
            
            基于你的国内政治压力（{domestic_pressure}）和透明度（{transparency}），
            请制定国内管理策略。
            
            请以JSON格式回复：
            - "domestic_strategy": 国内策略
            - "public_communication": 公众沟通计划
            - "political_management": 政治管理措施
            - "pressure_relief": 压力缓解措施
            - "stability_measures": 稳定措施
        '''

        param_dict = {
            'internal_situation': internal_situation,
            'domestic_pressure': self.country_b_domestic_political_pressure,
            'transparency': self.country_b_leader_transparency
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def get_agent_attributes(self):
        """
        获取Agent的所有属性
        
        Returns:
            Agent属性字典
        """
        return {
            "name": self.name,
            "identify": self.identify,
            "age": self.age,
            "country_b_conventional_military_strength": self.country_b_conventional_military_strength,
            "country_b_strategic_nuclear_strength": self.country_b_strategic_nuclear_strength,
            "country_b_economic_capacity": self.country_b_economic_capacity,
            "country_b_technological_level": self.country_b_technological_level,
            "country_b_alliance_support": self.country_b_alliance_support,
            "country_b_intelligence_uncertainty": self.country_b_intelligence_uncertainty,
            "country_b_deployment_proximity_to_cuba": self.country_b_deployment_proximity_to_cuba,
            "distance_a_b": self.distance_a_b,
            "missile_deployment_in_cuba": self.missile_deployment_in_cuba,
            "initial_bilateral_tension": self.initial_bilateral_tension,
            "perception_noise_asr": self.perception_noise_asr,
            "country_b_leader_risk_tolerance": self.country_b_leader_risk_tolerance,
            "country_b_leader_hostility": self.country_b_leader_hostility,
            "country_b_leader_transparency": self.country_b_leader_transparency,
            "country_b_domestic_political_pressure": self.country_b_domestic_political_pressure,
            "decision_temperature_asr": self.decision_temperature_asr,
            "current_tension": self.current_tension,
            "communication_history": self.communication_history,
            "environmental_data": self.environmental_data
        }

    def _get_timestamp(self):
        """获取当前时间戳"""
        import time
        return time.time()

    def reset_agent(self):
        """重置Agent状态"""
        self.current_tension = self.initial_bilateral_tension
        self.communication_history = []
        self.environmental_data = {}
        self.is_first = True
