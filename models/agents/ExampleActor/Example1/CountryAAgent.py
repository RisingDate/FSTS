import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent

"""
国家AAgent：代表国家A国家行为体，具有强大的经济和军事能力
"""

import random
import json


class CountryAAgent(LLMAgent):
    def __init__(self, agent_name='CountryAAgent', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='',
                         llm_model=llm_model)

        # Agent属性 - 基于提供的参数
        self.name = "国家A"
        self.identify = "国家"
        self.age = 46
        self.country_a_conventional_military_strength = 0.6
        self.country_a_strategic_nuclear_strength = 0.9
        self.country_a_economic_capacity = 0.9
        self.country_a_technological_level = 0.9
        self.country_a_alliance_support = 0.8
        self.country_a_intelligence_uncertainty = 0.4
        self.country_a_deployment_proximity_to_cuba = 0.8
        self.distance_a_b = 0.2
        self.missile_deployment_in_cuba = 1.0
        self.initial_bilateral_tension = 0.5
        self.perception_noise_a = 0.1
        self.country_a_leader_risk_tolerance = 0.5
        self.country_a_leader_hostility = 0.3
        self.country_a_leader_transparency = 0.6
        self.country_a_domestic_political_pressure = 0.6
        self.decision_temperature_a = 0.3

        # 动态属性
        self.current_tension = self.initial_bilateral_tension
        self.communication_history = []
        self.environmental_data = {}

        self.system_prompt = '''
            你是国家A国家行为体，代表国家A在地区C导弹危机中的立场和决策。
            
            你的核心特征：
            - 强大的战略核力量（0.9）和经济能力（0.9）
            - 先进的技术水平（0.9）和联盟支持（0.8）
            - 适度的常规军事力量（0.6）
            - 中等的情报不确定性（0.4）
            - 距离地区C较近的部署能力（0.8）
            
            你的领导特征：
            - 适度的风险承受能力（0.5）
            - 较低的敌意水平（0.3）
            - 中等的透明度（0.6）
            - 中等的国内政治压力（0.6）
            - 较低的决策温度（0.3）
            
            作为国家A，你需要：
            1. 保护国家安全和西半球利益
            2. 应对国家B在地区C的导弹部署威胁
            3. 维护与盟友的关系
            4. 平衡军事行动与外交手段
            5. 考虑国内政治和国际舆论
            6. 避免核战争升级
            
            请以国家A的视角和利益来回应各种情况。
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
            'intelligence_uncertainty': self.country_a_intelligence_uncertainty,
            'risk_tolerance': self.country_a_leader_risk_tolerance,
            'hostility': self.country_a_leader_hostility
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False

        return llm_response

    def communicate_with_country_b(self, ussr_message):
        """
        与国家B进行外交沟通
        
        Args:
            ussr_message: 国家B发来的消息
            
        Returns:
            外交回复
        """
        info_prompt = '''
            国家B发来的消息：{ussr_message}
            
            基于你的透明度水平（{transparency}）和敌意水平（{hostility}），
            请以国家A的外交风格回复国家B。
            
            考虑因素：
            1. 当前的紧张程度（{current_tension}）
            2. 国内政治压力（{domestic_pressure}）
            3. 联盟支持（{alliance_support}）
            4. 避免核战争升级的必要性
            
            请以JSON格式回复：
            - "response": 对国家B的回复内容
            - "tone": 回复语调（强硬/温和/中性）
            - "demands": 具体要求和条件
            - "concessions": 可能的让步
            - "next_steps": 建议的下一步行动
        '''

        param_dict = {
            'ussr_message': ussr_message,
            'transparency': self.country_a_leader_transparency,
            'hostility': self.country_a_leader_hostility,
            'current_tension': self.current_tension,
            'domestic_pressure': self.country_a_domestic_political_pressure,
            'alliance_support': self.country_a_alliance_support
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        # 记录通信历史
        self.communication_history.append({
            'sender': 'CountryB',
            'message': ussr_message,
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
            - "alliance_coordination": 联盟协调计划
        '''

        param_dict = {
            'situation_context': situation_context,
            'conventional_strength': self.country_a_conventional_military_strength,
            'nuclear_strength': self.country_a_strategic_nuclear_strength,
            'deployment_proximity': self.country_a_deployment_proximity_to_cuba,
            'risk_tolerance': self.country_a_leader_risk_tolerance,
            'decision_temperature': self.decision_temperature_a,
            'domestic_pressure': self.country_a_domestic_political_pressure
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
                self.country_a_leader_risk_tolerance += random.uniform(-0.05, 0.05)
            else:
                self.country_a_leader_risk_tolerance += random.uniform(-0.02, 0.02)

            self.country_a_leader_risk_tolerance = max(0, min(1, self.country_a_leader_risk_tolerance))

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
            请分析这些环境信息对国家A的影响。
            
            请以JSON格式回复：
            - "environmental_assessment": 环境评估
            - "threat_indicators": 威胁指标
            - "opportunities": 机会识别
            - "recommended_monitoring": 建议监控的重点
            - "impact_on_strategy": 对战略的影响
        '''

        param_dict = {
            'environment_data': json.dumps(environment_data, ensure_ascii=False),
            'intelligence_uncertainty': self.country_a_intelligence_uncertainty
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def negotiate_with_cuba(self, cuba_message):
        """
        与地区C进行谈判
        
        Args:
            cuba_message: 地区C发来的消息
            
        Returns:
            谈判回复
        """
        info_prompt = '''
            地区C发来的消息：{cuba_message}
            
            作为国家A，请考虑：
            1. 地区C导弹部署的威胁（{missile_deployment}）
            2. 你的部署接近度（{deployment_proximity}）
            3. 与国家B的距离（{distance_a_b}）
            4. 你的外交透明度（{transparency}）
            
            请以JSON格式回复：
            - "response": 对地区C的回复
            - "demands": 对地区C的要求
            - "incentives": 提供的激励
            - "threats": 可能的威胁
            - "negotiation_strategy": 谈判策略
        '''

        param_dict = {
            'cuba_message': cuba_message,
            'missile_deployment': self.missile_deployment_in_cuba,
            'deployment_proximity': self.country_a_deployment_proximity_to_cuba,
            'distance_a_b': self.distance_a_b,
            'transparency': self.country_a_leader_transparency
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
            "country_a_conventional_military_strength": self.country_a_conventional_military_strength,
            "country_a_strategic_nuclear_strength": self.country_a_strategic_nuclear_strength,
            "country_a_economic_capacity": self.country_a_economic_capacity,
            "country_a_technological_level": self.country_a_technological_level,
            "country_a_alliance_support": self.country_a_alliance_support,
            "country_a_intelligence_uncertainty": self.country_a_intelligence_uncertainty,
            "country_a_deployment_proximity_to_cuba": self.country_a_deployment_proximity_to_cuba,
            "distance_a_b": self.distance_a_b,
            "missile_deployment_in_cuba": self.missile_deployment_in_cuba,
            "initial_bilateral_tension": self.initial_bilateral_tension,
            "perception_noise_a": self.perception_noise_a,
            "country_a_leader_risk_tolerance": self.country_a_leader_risk_tolerance,
            "country_a_leader_hostility": self.country_a_leader_hostility,
            "country_a_leader_transparency": self.country_a_leader_transparency,
            "country_a_domestic_political_pressure": self.country_a_domestic_political_pressure,
            "decision_temperature_a": self.decision_temperature_a,
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
