"""
通信管理器：管理Agent间的通信和外部环境信息获取
"""

import json
import time
from typing import Dict, List, Any, Optional


class CommunicationManager:
    def __init__(self):
        self.message_history = []
        self.environmental_data = {}
        self.agent_registry = {}

    def register_agent(self, agent_name: str, agent_instance):
        """
        注册Agent到通信管理器
        
        Args:
            agent_name: Agent名称
            agent_instance: Agent实例
        """
        self.agent_registry[agent_name] = agent_instance
        print(f"Agent {agent_name} 已注册到通信管理器")

    def send_message(self, sender: str, receiver: str, message: str, message_type: str = "diplomatic") -> Dict[
        str, Any]:
        """
        发送消息给指定Agent
        
        Args:
            sender: 发送方Agent名称
            receiver: 接收方Agent名称
            message: 消息内容
            message_type: 消息类型（diplomatic, military, intelligence等）
            
        Returns:
            通信结果
        """
        if receiver not in self.agent_registry:
            return {
                "success": False,
                "error": f"Agent {receiver} 未注册",
                "timestamp": time.time()
            }

        # 记录消息历史
        message_record = {
            "sender": sender,
            "receiver": receiver,
            "message": message,
            "message_type": message_type,
            "timestamp": time.time()
        }
        self.message_history.append(message_record)

        # 根据接收方类型调用相应的通信方法
        receiver_agent = self.agent_registry[receiver]

        try:
            if receiver == "CountryAAgent":
                response = receiver_agent.communicate_with_country_b(message)
            elif receiver == "CountryBAgent":
                response = receiver_agent.communicate_with_country_a(message)
            else:
                # 通用通信方法
                response = self._generic_communication(receiver_agent, message)

            # 记录响应
            message_record["response"] = response
            message_record["success"] = True

            return {
                "success": True,
                "response": response,
                "timestamp": time.time(),
                "message_id": len(self.message_history) - 1
            }

        except Exception as e:
            message_record["success"] = False
            message_record["error"] = str(e)

            return {
                "success": False,
                "error": str(e),
                "timestamp": time.time()
            }

    def broadcast_message(self, sender: str, message: str, message_type: str = "broadcast") -> Dict[str, Any]:
        """
        广播消息给所有注册的Agent
        
        Args:
            sender: 发送方Agent名称
            message: 消息内容
            message_type: 消息类型
            
        Returns:
            广播结果
        """
        results = {}

        for agent_name in self.agent_registry.keys():
            if agent_name != sender:
                result = self.send_message(sender, agent_name, message, message_type)
                results[agent_name] = result

        return {
            "success": True,
            "results": results,
            "timestamp": time.time()
        }

    def update_environmental_data(self, data: Dict[str, Any], source: str = "external"):
        """
        更新环境数据
        
        Args:
            data: 环境数据
            source: 数据来源
        """
        self.environmental_data.update(data)
        self.environmental_data["last_update"] = time.time()
        self.environmental_data["source"] = source

        # 通知所有Agent环境数据更新
        self._notify_environmental_update()

    def _notify_environmental_update(self):
        """
        通知所有Agent环境数据更新
        """
        for agent_name, agent_instance in self.agent_registry.items():
            try:
                if hasattr(agent_instance, 'get_environmental_info'):
                    agent_instance.get_environmental_info(self.environmental_data)
            except Exception as e:
                print(f"通知Agent {agent_name} 环境更新时出错: {e}")

    def get_environmental_data(self, agent_name: str) -> Dict[str, Any]:
        """
        获取环境数据给指定Agent
        
        Args:
            agent_name: Agent名称
            
        Returns:
            环境数据
        """
        if agent_name in self.agent_registry:
            agent_instance = self.agent_registry[agent_name]
            if hasattr(agent_instance, 'get_environmental_info'):
                return agent_instance.get_environmental_info(self.environmental_data)

        return self.environmental_data

    def coordinate_agents(self, coordinator: str, target_agents: List[str], coordination_message: str) -> Dict[
        str, Any]:
        """
        协调多个Agent的行动
        
        Args:
            coordinator: 协调者Agent名称
            target_agents: 目标Agent列表
            coordination_message: 协调消息
            
        Returns:
            协调结果
        """
        results = {}

        for agent_name in target_agents:
            if agent_name in self.agent_registry:
                result = self.send_message(coordinator, agent_name, coordination_message, "coordination")
                results[agent_name] = result
            else:
                results[agent_name] = {
                    "success": False,
                    "error": f"Agent {agent_name} 未注册"
                }

        return {
            "success": True,
            "coordination_results": results,
            "timestamp": time.time()
        }

    def simulate_crisis_escalation(self, escalation_factor: float = 0.1):
        """
        模拟危机升级
        
        Args:
            escalation_factor: 升级因子
        """
        # 更新环境数据，增加紧张程度
        crisis_data = {
            "crisis_level": min(1.0, self.environmental_data.get("crisis_level", 0.5) + escalation_factor),
            "escalation_event": True,
            "escalation_timestamp": time.time()
        }

        self.update_environmental_data(crisis_data, "crisis_simulation")

        # 通知所有Agent危机升级
        for agent_name, agent_instance in self.agent_registry.items():
            try:
                if hasattr(agent_instance, 'update_attributes'):
                    # 根据危机级别调整Agent属性
                    external_influence = {
                        "current_tension": escalation_factor,
                        "country_b_leader_risk_tolerance": escalation_factor * 0.5 if "CountryB" in agent_name else -escalation_factor * 0.3,
                        "country_a_leader_risk_tolerance": escalation_factor * 0.3 if "CountryA" in agent_name else -escalation_factor * 0.5
                    }
                    agent_instance.update_attributes(external_influence=external_influence)
            except Exception as e:
                print(f"更新Agent {agent_name} 属性时出错: {e}")

    def get_communication_history(self, agent_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取通信历史
        
        Args:
            agent_name: 指定Agent名称，None表示获取所有历史
            
        Returns:
            通信历史列表
        """
        if agent_name:
            return [msg for msg in self.message_history
                    if msg.get("sender") == agent_name or msg.get("receiver") == agent_name]
        return self.message_history

    def analyze_communication_patterns(self) -> Dict[str, Any]:
        """
        分析通信模式
        
        Returns:
            通信模式分析结果
        """
        if not self.message_history:
            return {"message": "暂无通信历史"}

        # 统计通信频率
        sender_counts = {}
        receiver_counts = {}
        message_types = {}

        for msg in self.message_history:
            sender = msg.get("sender", "unknown")
            receiver = msg.get("receiver", "unknown")
            msg_type = msg.get("message_type", "unknown")

            sender_counts[sender] = sender_counts.get(sender, 0) + 1
            receiver_counts[receiver] = receiver_counts.get(receiver, 0) + 1
            message_types[msg_type] = message_types.get(msg_type, 0) + 1

        return {
            "total_messages": len(self.message_history),
            "sender_frequency": sender_counts,
            "receiver_frequency": receiver_counts,
            "message_type_distribution": message_types,
            "analysis_timestamp": time.time()
        }

    def _generic_communication(self, agent_instance, message: str):
        """
        通用通信方法
        
        Args:
            agent_instance: Agent实例
            message: 消息内容
            
        Returns:
            响应结果
        """
        # 尝试调用Agent的通用通信方法
        if hasattr(agent_instance, 'receive_message'):
            return agent_instance.receive_message(message)
        elif hasattr(agent_instance, 'communicate'):
            return agent_instance.communicate(message)
        else:
            return {
                "response": f"Agent {agent_instance.agent_name} 收到消息: {message}",
                "status": "acknowledged"
            }

    def reset_communication_manager(self):
        """
        重置通信管理器
        """
        self.message_history = []
        self.environmental_data = {}
        print("通信管理器已重置")

    def export_communication_data(self, filepath: str):
        """
        导出通信数据到文件
        
        Args:
            filepath: 文件路径
        """
        data = {
            "message_history": self.message_history,
            "environmental_data": self.environmental_data,
            "agent_registry": list(self.agent_registry.keys()),
            "export_timestamp": time.time()
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"通信数据已导出到: {filepath}")
