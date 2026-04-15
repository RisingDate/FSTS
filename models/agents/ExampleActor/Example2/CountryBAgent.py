import os
import sys

sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))))
from config import OLLAMA_MODEL_LIST
from models.agents.LLMAgent import LLMAgent

"""
国家BAgent：代表国家B国家行为体，基于新的属性参数设计
具有动态属性变化、Agent间通信和环境信息获取能力
"""

import random
import json
import time


class CountryBAgent(LLMAgent):
    def __init__(self, agent_name='CountryBAgen', llm_model='deepseek-r1:32b-qwen-distill-q8_0'):
        super().__init__(agent_name=agent_name, has_chat_history=False, online_track=False, json_format=True,
                         system_prompt='', llm_model=llm_model)

        # Agent基础属性 - 基于提供的参数
        self.name = "国家B"
        self.identify = "国家（大国）"
        self.age = 103
        self.military_strength = 0.74
        self.economic_resilience = 0.5
        self.tech_level = 0.7
        self.leadership_risk_aversion = 0.3
        self.leadership_communication_willingness = 0.1
        self.leadership_decision_speed = 0.6
        self.domestic_political_pressure = 0.6
        self.hardline_tendency = 0.95
        self.nuclear_deterrence = 0.9
        self.backchannel_quality = 0.15
        self.third_party_mediation = 0.05
        self.intelligence_reliability = 0.55
        self.proximity_factor = 0.9
        self.alliance_influence = 0.6
        self.signal_noise_level = 0.5
        self.crisis_duration = 0.1
        self.ally_intervention_likelihood = 0.2
        self.event_trajectory_prev = 0.0
        self.international_tension_prev = 0.2

        # 动态属性
        self.current_international_tension = self.international_tension_prev
        self.communication_history = []
        self.environmental_data = {}
        self.agent_communications = {}  # 存储与其他Agent的通信记录

        self.system_prompt = '''
            你是国家B国家行为体，代表国家B在国际危机中的立场和决策。
            
            你的核心特征：
            - 强大的军事力量（0.74）但经济韧性较弱（0.5）
            - 中等的技术水平（0.7）和联盟影响力（0.6）
            - 强大的核威慑能力（0.9）
            - 中等的风险规避（0.3）和决策速度（0.6）
            - 极高的强硬倾向（0.95）
            - 较低的沟通意愿（0.1）和后渠道质量（0.15）
            - 中等偏低的情报可靠性（0.55）
            
            你的决策特点：
            - 中等的国内政治压力（0.6）
            - 较高的邻近因子（0.9）
            - 中等的信号噪声水平（0.5）
            - 极低的第三方调解接受度（0.05）
            - 较低的盟友干预可能性（0.2）
            
            作为国家B，你需要：
            1. 维护国家安全和大国地位
            2. 应对西方的威胁和挑战
            3. 维护传统势力范围和影响力
            4. 平衡军事威慑与有限外交
            5. 考虑国内政治稳定和经济压力
            6. 在危机中保持强硬立场和威慑力
            
            请以国家B的视角和利益来回应各种情况。
        '''
        self.is_first = True

    def communicate_with_agent(self, target_agent_name, message, message_type="diplomatic"):
        """
        与其他Agent进行通信
        
        Args:
            target_agent_name: 目标Agent名称
            message: 消息内容
            message_type: 消息类型（diplomatic, military, economic等）
            
        Returns:
            通信回复
        """
        info_prompt = '''
            你要向{target_agent}发送消息：{message}
            消息类型：{message_type}
            
            基于你的属性：
            - 沟通意愿：{communication_willingness}
            - 强硬倾向：{hardline_tendency}
            - 风险规避：{risk_aversion}
            - 决策速度：{decision_speed}
            - 国内政治压力：{domestic_pressure}
            - 后渠道质量：{backchannel_quality}
            
            当前国际紧张程度：{international_tension}
            
            请制定你的通信策略和回复内容。
            
            请以JSON格式回复：
            - "communication_strategy": 通信策略
            - "message_content": 具体消息内容
            - "tone": 语调（强硬/温和/中性/威胁）
            - "demands": 具体要求
            - "concessions": 可能的让步
            - "expected_response": 预期对方回应
            - "escalation_risk": 升级风险评估（0-1）
        '''

        param_dict = {
            'target_agent': target_agent_name,
            'message': message,
            'message_type': message_type,
            'communication_willingness': self.leadership_communication_willingness,
            'hardline_tendency': self.hardline_tendency,
            'risk_aversion': self.leadership_risk_aversion,
            'decision_speed': self.leadership_decision_speed,
            'domestic_pressure': self.domestic_political_pressure,
            'backchannel_quality': self.backchannel_quality,
            'international_tension': self.current_international_tension
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)
        self.is_first = False

        # 记录通信历史
        communication_record = {
            'timestamp': self._get_timestamp(),
            'target_agent': target_agent_name,
            'message_type': message_type,
            'sent_message': message,
            'response': llm_response,
            'international_tension': self.current_international_tension
        }

        if target_agent_name not in self.agent_communications:
            self.agent_communications[target_agent_name] = []
        self.agent_communications[target_agent_name].append(communication_record)

        return llm_response

    def receive_communication(self, sender_agent_name, message, message_type="diplomatic"):
        """
        接收来自其他Agent的通信
        
        Args:
            sender_agent_name: 发送方Agent名称
            message: 消息内容
            message_type: 消息类型
            
        Returns:
            回复内容
        """
        info_prompt = '''
            收到来自{sender_agent}的消息：{message}
            消息类型：{message_type}
            
            基于你的属性分析并回复：
            - 沟通意愿：{communication_willingness}
            - 强硬倾向：{hardline_tendency}
            - 风险规避：{risk_aversion}
            - 情报可靠性：{intelligence_reliability}
            - 信号噪声水平：{signal_noise}
            - 后渠道质量：{backchannel_quality}
            
            当前国际紧张程度：{international_tension}
            历史通信记录：{communication_history}
            
            请分析消息并制定回复。
            
            请以JSON格式回复：
            - "message_analysis": 消息分析
            - "threat_assessment": 威胁评估
            - "response_message": 回复消息
            - "response_tone": 回复语调
            - "policy_adjustment": 政策调整建议
            - "escalation_potential": 升级潜力评估（0-1）
        '''

        # 获取与该Agent的历史通信记录
        history = self.agent_communications.get(sender_agent_name, [])
        history_summary = json.dumps(history[-3:], ensure_ascii=False) if history else "无历史记录"

        param_dict = {
            'sender_agent': sender_agent_name,
            'message': message,
            'message_type': message_type,
            'communication_willingness': self.leadership_communication_willingness,
            'hardline_tendency': self.hardline_tendency,
            'risk_aversion': self.leadership_risk_aversion,
            'intelligence_reliability': self.intelligence_reliability,
            'signal_noise': self.signal_noise_level,
            'backchannel_quality': self.backchannel_quality,
            'international_tension': self.current_international_tension,
            'communication_history': history_summary
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        # 记录接收的通信
        communication_record = {
            'timestamp': self._get_timestamp(),
            'sender_agent': sender_agent_name,
            'message_type': message_type,
            'received_message': message,
            'response': llm_response,
            'international_tension': self.current_international_tension
        }

        if sender_agent_name not in self.agent_communications:
            self.agent_communications[sender_agent_name] = []
        self.agent_communications[sender_agent_name].append(communication_record)

        return llm_response

    def get_environmental_info(self, environment_data):
        """
        获取并分析外部环境信息
        
        Args:
            environment_data: 环境数据字典
            
        Returns:
            环境信息分析结果
        """
        self.environmental_data.update(environment_data)

        info_prompt = '''
            外部环境信息更新：{environment_data}
            
            基于你的能力分析环境变化：
            - 情报可靠性：{intelligence_reliability}
            - 技术水平：{tech_level}
            - 联盟影响力：{alliance_influence}
            - 邻近因子：{proximity_factor}
            - 信号噪声水平：{signal_noise}
            
            当前属性状态：
            - 国际紧张程度：{international_tension}
            - 军事力量：{military_strength}
            - 经济韧性：{economic_resilience}
            
            请分析环境信息对国家B的影响。
            
            请以JSON格式回复：
            - "environmental_assessment": 环境评估
            - "threat_indicators": 威胁指标识别
            - "opportunity_analysis": 机会分析
            - "strategic_implications": 战略影响
            - "recommended_actions": 建议行动
            - "monitoring_priorities": 监控重点
            - "attribute_impact": 对自身属性的影响评估
        '''

        param_dict = {
            'environment_data': json.dumps(environment_data, ensure_ascii=False),
            'intelligence_reliability': self.intelligence_reliability,
            'tech_level': self.tech_level,
            'alliance_influence': self.alliance_influence,
            'proximity_factor': self.proximity_factor,
            'signal_noise': self.signal_noise_level,
            'international_tension': self.current_international_tension,
            'military_strength': self.military_strength,
            'economic_resilience': self.economic_resilience
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
        更新Agent属性（支持外部影响和自主变化）
        
        Args:
            external_influence: 外部影响因子字典
            autonomous_change: 是否进行自主变化
            
        Returns:
            更新后的属性字典
        """
        changes_made = {}

        if autonomous_change:
            # 自主变化：基于内部逻辑和当前状态

            # 1. 国际紧张程度的自然演化
            tension_change = random.uniform(-0.05, 0.05)
            # 强硬倾向高的国家倾向于维持或增加紧张
            if self.hardline_tendency > 0.8:
                tension_change += random.uniform(0, 0.04)

            old_tension = self.current_international_tension
            self.current_international_tension += tension_change
            self.current_international_tension = max(0, min(1, self.current_international_tension))
            changes_made['international_tension'] = self.current_international_tension - old_tension

            # 2. 风险规避根据紧张程度和经济状况调整
            if self.current_international_tension > 0.7:
                risk_change = random.uniform(-0.03, 0.04)  # 高紧张时可能更激进
            elif self.economic_resilience < 0.6:
                risk_change = random.uniform(-0.02, 0.05)  # 经济压力下可能更谨慎
            else:
                risk_change = random.uniform(-0.03, 0.03)

            old_risk = self.leadership_risk_aversion
            self.leadership_risk_aversion += risk_change
            self.leadership_risk_aversion = max(0, min(1, self.leadership_risk_aversion))
            changes_made['risk_aversion'] = self.leadership_risk_aversion - old_risk

            # 3. 沟通意愿根据危机持续时间和后渠道质量调整
            if self.crisis_duration > 0.5 and self.backchannel_quality < 0.3:
                comm_change = random.uniform(0, 0.02)  # 长期危机且后渠道差可能略增沟通意愿
            else:
                comm_change = random.uniform(-0.02, 0.01)

            old_comm = self.leadership_communication_willingness
            self.leadership_communication_willingness += comm_change
            self.leadership_communication_willingness = max(0, min(1, self.leadership_communication_willingness))
            changes_made['communication_willingness'] = self.leadership_communication_willingness - old_comm

            # 4. 国内政治压力的波动
            pressure_change = random.uniform(-0.04, 0.04)
            # 经济韧性低时国内压力增加
            if self.economic_resilience < 0.6:
                pressure_change += random.uniform(0, 0.03)
            # 高紧张程度可能增加或减少国内压力（取决于民族主义情绪）
            if self.current_international_tension > 0.6:
                pressure_change += random.uniform(-0.02, 0.04)

            old_pressure = self.domestic_political_pressure
            self.domestic_political_pressure += pressure_change
            self.domestic_political_pressure = max(0, min(1, self.domestic_political_pressure))
            changes_made['domestic_pressure'] = self.domestic_political_pressure - old_pressure

            # 5. 经济韧性可能因制裁或其他因素变化
            if self.current_international_tension > 0.7:
                economic_change = random.uniform(-0.03, 0.01)  # 高紧张可能影响经济
            else:
                economic_change = random.uniform(-0.01, 0.02)

            old_economic = self.economic_resilience
            self.economic_resilience += economic_change
            self.economic_resilience = max(0, min(1, self.economic_resilience))
            changes_made['economic_resilience'] = self.economic_resilience - old_economic

        if external_influence:
            # 外部影响：根据外部事件调整属性
            for attribute, change in external_influence.items():
                if hasattr(self, attribute):
                    old_value = getattr(self, attribute)
                    new_value = old_value + change
                    new_value = max(0, min(1, new_value))
                    setattr(self, attribute, new_value)
                    changes_made[attribute] = new_value - old_value

        # 记录属性变化
        if changes_made:
            change_record = {
                'timestamp': self._get_timestamp(),
                'changes': changes_made,
                'external_influence': external_influence,
                'autonomous_change': autonomous_change,
                'resulting_tension': self.current_international_tension
            }

            if 'attribute_changes' not in self.environmental_data:
                self.environmental_data['attribute_changes'] = []
            self.environmental_data['attribute_changes'].append(change_record)

        return self.get_agent_attributes()

    def make_strategic_decision(self, situation_context, decision_type="general"):
        """
        制定战略决策
        
        Args:
            situation_context: 情况背景
            decision_type: 决策类型（military, diplomatic, economic等）
            
        Returns:
            战略决策
        """
        info_prompt = '''
            当前情况：{situation_context}
            决策类型：{decision_type}
            
            基于你的能力和特征：
            - 军事力量：{military_strength}
            - 经济韧性：{economic_resilience}
            - 技术水平：{tech_level}
            - 核威慑：{nuclear_deterrence}
            - 联盟影响力：{alliance_influence}
            - 决策速度：{decision_speed}
            - 强硬倾向：{hardline_tendency}
            - 风险规避：{risk_aversion}
            
            当前状态：
            - 国际紧张程度：{international_tension}
            - 国内政治压力：{domestic_pressure}
            - 危机持续时间：{crisis_duration}
            - 后渠道质量：{backchannel_quality}
            
            请制定战略决策。
            
            请以JSON格式回复：
            - "decision_analysis": 决策分析
            - "strategic_options": 战略选项
            - "recommended_action": 推荐行动
            - "resource_allocation": 资源配置
            - "risk_assessment": 风险评估
            - "timeline": 执行时间表
            - "success_probability": 成功概率评估
            - "contingency_plans": 应急计划
        '''

        param_dict = {
            'situation_context': situation_context,
            'decision_type': decision_type,
            'military_strength': self.military_strength,
            'economic_resilience': self.economic_resilience,
            'tech_level': self.tech_level,
            'nuclear_deterrence': self.nuclear_deterrence,
            'alliance_influence': self.alliance_influence,
            'decision_speed': self.leadership_decision_speed,
            'hardline_tendency': self.hardline_tendency,
            'risk_aversion': self.leadership_risk_aversion,
            'international_tension': self.current_international_tension,
            'domestic_pressure': self.domestic_political_pressure,
            'crisis_duration': self.crisis_duration,
            'backchannel_quality': self.backchannel_quality
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def manage_alliance_relations(self, alliance_context):
        """
        管理联盟关系
        
        Args:
            alliance_context: 联盟背景信息
            
        Returns:
            联盟管理策略
        """
        info_prompt = '''
            联盟背景：{alliance_context}
            
            基于你的联盟能力：
            - 联盟影响力：{alliance_influence}
            - 盟友干预可能性：{ally_intervention}
            - 沟通意愿：{communication_willingness}
            - 后渠道质量：{backchannel_quality}
            
            当前状态：
            - 国际紧张程度：{international_tension}
            - 经济韧性：{economic_resilience}
            - 强硬倾向：{hardline_tendency}
            
            请制定联盟管理策略。
            
            请以JSON格式回复：
            - "alliance_strategy": 联盟策略
            - "support_requests": 支持请求
            - "coordination_plans": 协调计划
            - "influence_tactics": 影响策略
            - "risk_sharing": 风险分担
            - "contingency_support": 应急支持计划
        '''

        param_dict = {
            'alliance_context': alliance_context,
            'alliance_influence': self.alliance_influence,
            'ally_intervention': self.ally_intervention_likelihood,
            'communication_willingness': self.leadership_communication_willingness,
            'backchannel_quality': self.backchannel_quality,
            'international_tension': self.current_international_tension,
            'economic_resilience': self.economic_resilience,
            'hardline_tendency': self.hardline_tendency
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
            "military_strength": self.military_strength,
            "economic_resilience": self.economic_resilience,
            "tech_level": self.tech_level,
            "leadership_risk_aversion": self.leadership_risk_aversion,
            "leadership_communication_willingness": self.leadership_communication_willingness,
            "leadership_decision_speed": self.leadership_decision_speed,
            "domestic_political_pressure": self.domestic_political_pressure,
            "hardline_tendency": self.hardline_tendency,
            "nuclear_deterrence": self.nuclear_deterrence,
            "backchannel_quality": self.backchannel_quality,
            "third_party_mediation": self.third_party_mediation,
            "intelligence_reliability": self.intelligence_reliability,
            "proximity_factor": self.proximity_factor,
            "alliance_influence": self.alliance_influence,
            "signal_noise_level": self.signal_noise_level,
            "crisis_duration": self.crisis_duration,
            "ally_intervention_likelihood": self.ally_intervention_likelihood,
            "event_trajectory_prev": self.event_trajectory_prev,
            "international_tension_prev": self.international_tension_prev,
            "current_international_tension": self.current_international_tension,
            "communication_history": self.communication_history,
            "environmental_data": self.environmental_data,
            "agent_communications": self.agent_communications
        }

    def _get_timestamp(self):
        """获取当前时间戳"""
        return time.time()

    def reset_agent(self):
        """重置Agent状态"""
        self.current_international_tension = self.international_tension_prev
        self.communication_history = []
        self.environmental_data = {}
        self.agent_communications = {}
        self.is_first = True

    def get_communication_summary(self, target_agent_name=None):
        """
        获取通信摘要
        
        Args:
            target_agent_name: 特定Agent名称，如果为None则返回所有通信摘要
            
        Returns:
            通信摘要
        """
        if target_agent_name:
            return self.agent_communications.get(target_agent_name, [])
        else:
            return self.agent_communications

    def assess_crisis_escalation(self):
        """
        评估危机升级风险
        
        Returns:
            危机升级评估
        """
        info_prompt = '''
            基于当前状态评估危机升级风险：
            
            当前属性：
            - 国际紧张程度：{international_tension}
            - 强硬倾向：{hardline_tendency}
            - 风险规避：{risk_aversion}
            - 核威慑：{nuclear_deterrence}
            - 国内政治压力：{domestic_pressure}
            - 经济韧性：{economic_resilience}
            - 危机持续时间：{crisis_duration}
            - 盟友干预可能性：{ally_intervention}
            
            通信历史：{communication_summary}
            环境数据：{environmental_data}
            
            请评估危机升级风险。
            
            请以JSON格式回复：
            - "escalation_risk": 升级风险等级（0-1）
            - "risk_factors": 风险因素分析
            - "de_escalation_opportunities": 降级机会
            - "critical_thresholds": 关键阈值
            - "recommended_monitoring": 建议监控指标
            - "preventive_measures": 预防措施
        '''

        param_dict = {
            'international_tension': self.current_international_tension,
            'hardline_tendency': self.hardline_tendency,
            'risk_aversion': self.leadership_risk_aversion,
            'nuclear_deterrence': self.nuclear_deterrence,
            'domestic_pressure': self.domestic_political_pressure,
            'economic_resilience': self.economic_resilience,
            'crisis_duration': self.crisis_duration,
            'ally_intervention': self.ally_intervention_likelihood,
            'communication_summary': json.dumps(self.get_communication_summary(), ensure_ascii=False),
            'environmental_data': json.dumps(self.environmental_data, ensure_ascii=False)
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response

    def handle_economic_pressure(self, economic_situation):
        """
        处理经济压力
        
        Args:
            economic_situation: 经济形势描述
            
        Returns:
            经济应对策略
        """
        info_prompt = '''
            经济形势：{economic_situation}
            
            基于你的经济能力：
            - 经济韧性：{economic_resilience}
            - 联盟影响力：{alliance_influence}
            - 技术水平：{tech_level}
            
            当前压力：
            - 国内政治压力：{domestic_pressure}
            - 国际紧张程度：{international_tension}
            - 强硬倾向：{hardline_tendency}
            
            请制定经济应对策略。
            
            请以JSON格式回复：
            - "economic_strategy": 经济策略
            - "resource_mobilization": 资源动员计划
            - "alliance_support": 联盟支持请求
            - "domestic_measures": 国内措施
            - "risk_mitigation": 风险缓解
            - "long_term_planning": 长期规划
        '''

        param_dict = {
            'economic_situation': economic_situation,
            'economic_resilience': self.economic_resilience,
            'alliance_influence': self.alliance_influence,
            'tech_level': self.tech_level,
            'domestic_pressure': self.domestic_political_pressure,
            'international_tension': self.current_international_tension,
            'hardline_tendency': self.hardline_tendency
        }

        if self.llm_model in OLLAMA_MODEL_LIST['think']:
            llm_response, think = self.get_response(info_prompt, input_param_dict=param_dict,
                                                    is_first_call=self.is_first)
        else:
            llm_response = self.get_response(info_prompt, input_param_dict=param_dict,
                                             is_first_call=self.is_first)

        return llm_response
