"""
通信管理器：管理Agent间的通信和环境信息分发
支持多Agent通信、消息路由和环境数据管理
"""

import json
import threading
import time
from typing import Dict, List, Any


class CommunicationManager:
    """
    Agent间通信管理器
    负责管理多个Agent之间的通信、环境信息分发和全局状态管理
    """

    def __init__(self):
        self.agents = {}  # 存储所有注册的Agent
        self.global_environment = {}  # 全局环境数据
        self.communication_log = []  # 通信日志
        self.environment_history = []  # 环境变化历史
        self.lock = threading.Lock()  # 线程锁，确保线程安全

    def register_agent(self, agent_id: str, agent_instance):
        """
        注册Agent到通信管理器
        
        Args:
            agent_id: Agent唯一标识
            agent_instance: Agent实例
        """
        with self.lock:
            self.agents[agent_id] = agent_instance
            print(f"Agent {agent_id} ({agent_instance.name}) 已注册到通信管理器")

    def unregister_agent(self, agent_id: str):
        """
        从通信管理器注销Agent
        
        Args:
            agent_id: Agent唯一标识
        """
        with self.lock:
            if agent_id in self.agents:
                agent_name = self.agents[agent_id].name
                del self.agents[agent_id]
                print(f"Agent {agent_id} ({agent_name}) 已从通信管理器注销")

    def send_message(self, sender_id: str, receiver_id: str, message: str, message_type: str = "diplomatic"):
        """
        发送消息从一个Agent到另一个Agent
        
        Args:
            sender_id: 发送方Agent ID
            receiver_id: 接收方Agent ID
            message: 消息内容
            message_type: 消息类型
            
        Returns:
            接收方的回复
        """
        if sender_id not in self.agents:
            raise ValueError(f"发送方Agent {sender_id} 未注册")
        if receiver_id not in self.agents:
            raise ValueError(f"接收方Agent {receiver_id} 未注册")

        sender_agent = self.agents[sender_id]
        receiver_agent = self.agents[receiver_id]

        # 记录通信日志
        communication_record = {
            'timestamp': time.time(),
            'sender_id': sender_id,
            'sender_name': sender_agent.name,
            'receiver_id': receiver_id,
            'receiver_name': receiver_agent.name,
            'message': message,
            'message_type': message_type
        }

        try:
            # 接收方处理消息并生成回复
            response = receiver_agent.receive_communication(sender_agent.name, message, message_type)

            communication_record['response'] = response
            communication_record['status'] = 'success'

            with self.lock:
                self.communication_log.append(communication_record)

            print(f"消息已从 {sender_agent.name} 发送到 {receiver_agent.name}")
            return response

        except Exception as e:
            communication_record['error'] = str(e)
            communication_record['status'] = 'failed'

            with self.lock:
                self.communication_log.append(communication_record)

            print(f"消息发送失败: {e}")
            raise e

    def broadcast_message(self, sender_id: str, message: str, message_type: str = "broadcast",
                          exclude_agents: List[str] = None):
        """
        广播消息给所有其他Agent
        
        Args:
            sender_id: 发送方Agent ID
            message: 消息内容
            message_type: 消息类型
            exclude_agents: 排除的Agent ID列表
            
        Returns:
            所有接收方的回复字典
        """
        if sender_id not in self.agents:
            raise ValueError(f"发送方Agent {sender_id} 未注册")

        exclude_agents = exclude_agents or []
        exclude_agents.append(sender_id)  # 排除发送方自己

        responses = {}

        for receiver_id in self.agents:
            if receiver_id not in exclude_agents:
                try:
                    response = self.send_message(sender_id, receiver_id, message, message_type)
                    responses[receiver_id] = response
                except Exception as e:
                    responses[receiver_id] = {'error': str(e)}

        return responses

    def update_global_environment(self, environment_data: Dict[str, Any], notify_agents: bool = True):
        """
        更新全局环境数据
        
        Args:
            environment_data: 环境数据字典
            notify_agents: 是否通知所有Agent环境变化
        """
        with self.lock:
            # 记录环境变化历史
            environment_record = {
                'timestamp': time.time(),
                'previous_state': self.global_environment.copy(),
                'new_data': environment_data,
                'notify_agents': notify_agents
            }

            # 更新全局环境
            self.global_environment.update(environment_data)
            environment_record['resulting_state'] = self.global_environment.copy()

            self.environment_history.append(environment_record)

        if notify_agents:
            # 通知所有Agent环境变化
            for agent_id, agent in self.agents.items():
                try:
                    agent.get_environmental_info(environment_data)
                    print(f"环境信息已更新给 {agent.name}")
                except Exception as e:
                    print(f"向 {agent.name} 更新环境信息失败: {e}")

    def trigger_autonomous_changes(self, agent_ids: List[str] = None):
        """
        触发Agent的自主属性变化
        
        Args:
            agent_ids: 要触发变化的Agent ID列表，如果为None则触发所有Agent
        """
        target_agents = agent_ids if agent_ids else list(self.agents.keys())

        change_results = {}

        for agent_id in target_agents:
            if agent_id in self.agents:
                try:
                    agent = self.agents[agent_id]
                    updated_attributes = agent.update_attributes(autonomous_change=True)
                    change_results[agent_id] = {
                        'agent_name': agent.name,
                        'updated_attributes': updated_attributes,
                        'status': 'success'
                    }
                    print(f"{agent.name} 完成自主属性变化")
                except Exception as e:
                    change_results[agent_id] = {
                        'agent_name': self.agents[agent_id].name,
                        'error': str(e),
                        'status': 'failed'
                    }
                    print(f"{self.agents[agent_id].name} 自主属性变化失败: {e}")

        return change_results

    def apply_external_influence(self, influence_data: Dict[str, Dict[str, float]]):
        """
        对指定Agent应用外部影响
        
        Args:
            influence_data: 影响数据，格式为 {agent_id: {attribute: change_value}}
        """
        influence_results = {}

        for agent_id, influences in influence_data.items():
            if agent_id in self.agents:
                try:
                    agent = self.agents[agent_id]
                    updated_attributes = agent.update_attributes(external_influence=influences)
                    influence_results[agent_id] = {
                        'agent_name': agent.name,
                        'applied_influences': influences,
                        'updated_attributes': updated_attributes,
                        'status': 'success'
                    }
                    print(f"外部影响已应用到 {agent.name}")
                except Exception as e:
                    influence_results[agent_id] = {
                        'agent_name': self.agents[agent_id].name,
                        'applied_influences': influences,
                        'error': str(e),
                        'status': 'failed'
                    }
                    print(f"向 {self.agents[agent_id].name} 应用外部影响失败: {e}")

        return influence_results

    def get_agent_status(self, agent_id: str = None):
        """
        获取Agent状态信息
        
        Args:
            agent_id: Agent ID，如果为None则返回所有Agent状态
            
        Returns:
            Agent状态信息
        """
        if agent_id:
            if agent_id in self.agents:
                agent = self.agents[agent_id]
                return {
                    'agent_id': agent_id,
                    'agent_name': agent.name,
                    'attributes': agent.get_agent_attributes(),
                    'communication_summary': agent.get_communication_summary()
                }
            else:
                return {'error': f'Agent {agent_id} 未注册'}
        else:
            status_summary = {}
            for aid, agent in self.agents.items():
                status_summary[aid] = {
                    'agent_name': agent.name,
                    'current_tension': getattr(agent, 'current_international_tension', 'N/A'),
                    'communication_count': len(agent.get_communication_summary())
                }
            return status_summary

    def get_communication_log(self, limit: int = None):
        """
        获取通信日志
        
        Args:
            limit: 返回的日志条数限制
            
        Returns:
            通信日志列表
        """
        with self.lock:
            if limit:
                return self.communication_log[-limit:]
            return self.communication_log.copy()

    def get_environment_history(self, limit: int = None):
        """
        获取环境变化历史
        
        Args:
            limit: 返回的历史记录条数限制
            
        Returns:
            环境变化历史列表
        """
        with self.lock:
            if limit:
                return self.environment_history[-limit:]
            return self.environment_history.copy()

    def simulate_crisis_scenario(self, scenario_config: Dict[str, Any]):
        """
        模拟危机场景
        
        Args:
            scenario_config: 场景配置，包含环境变化、外部影响等
            
        Returns:
            模拟结果
        """
        simulation_results = {
            'start_time': time.time(),
            'scenario_config': scenario_config,
            'steps': []
        }

        steps = scenario_config.get('steps', [])

        for step_idx, step in enumerate(steps):
            step_result = {
                'step_index': step_idx,
                'step_config': step,
                'timestamp': time.time()
            }

            # 环境变化
            if 'environment_update' in step:
                self.update_global_environment(step['environment_update'])
                step_result['environment_updated'] = True

            # 外部影响
            if 'external_influences' in step:
                influence_results = self.apply_external_influence(step['external_influences'])
                step_result['influence_results'] = influence_results

            # 自主变化
            if step.get('trigger_autonomous_changes', False):
                change_results = self.trigger_autonomous_changes()
                step_result['autonomous_changes'] = change_results

            # Agent通信
            if 'communications' in step:
                comm_results = {}
                for comm in step['communications']:
                    try:
                        response = self.send_message(
                            comm['sender'], comm['receiver'],
                            comm['message'], comm.get('type', 'diplomatic')
                        )
                        comm_results[f"{comm['sender']}_to_{comm['receiver']}"] = response
                    except Exception as e:
                        comm_results[f"{comm['sender']}_to_{comm['receiver']}"] = {'error': str(e)}
                step_result['communication_results'] = comm_results

            # 等待时间
            if 'wait_time' in step:
                time.sleep(step['wait_time'])

            simulation_results['steps'].append(step_result)

        simulation_results['end_time'] = time.time()
        simulation_results['duration'] = simulation_results['end_time'] - simulation_results['start_time']

        return simulation_results

    def reset_all_agents(self):
        """重置所有Agent状态"""
        for agent_id, agent in self.agents.items():
            try:
                agent.reset_agent()
                print(f"{agent.name} 状态已重置")
            except Exception as e:
                print(f"重置 {agent.name} 状态失败: {e}")

        # 清空管理器状态
        with self.lock:
            self.communication_log = []
            self.environment_history = []
            self.global_environment = {}

    def export_session_data(self, filename: str = None):
        """
        导出会话数据
        
        Args:
            filename: 导出文件名，如果为None则使用时间戳
            
        Returns:
            导出的数据字典
        """
        if not filename:
            filename = f"communication_session_{int(time.time())}.json"

        session_data = {
            'export_time': time.time(),
            'agents': {aid: agent.get_agent_attributes() for aid, agent in self.agents.items()},
            'global_environment': self.global_environment,
            'communication_log': self.communication_log,
            'environment_history': self.environment_history
        }

        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(session_data, f, ensure_ascii=False, indent=2)
            print(f"会话数据已导出到 {filename}")
        except Exception as e:
            print(f"导出会话数据失败: {e}")

        return session_data
