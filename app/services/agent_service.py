from typing import Dict, Optional
from app.models.agent import Agent
import logging

class AgentService:
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self.logger = logging.getLogger(__name__)
    
    def create_agent(self, goal: str) -> Agent:
        """새로운 에이전트 생성"""
        agent_name = f"agent_{len(self.agents) + 1}"
        agent = Agent(name=agent_name)
        self.agents[agent_name] = agent
        
        self.logger.info(f"Created new agent: {agent_name} with goal: {goal}")
        return agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """에이전트 조회"""
        return self.agents.get(agent_id)
    
    def list_agents(self) -> Dict[str, dict]:
        """모든 에이전트 목록 반환"""
        return {
            agent_id: agent.get_status()
            for agent_id, agent in self.agents.items()
        }
    
    def delete_agent(self, agent_id: str) -> bool:
        """에이전트 삭제"""
        if agent_id in self.agents:
            del self.agents[agent_id]
            self.logger.info(f"Deleted agent: {agent_id}")
            return True
        return False

# 싱글톤 인스턴스
_agent_service = None

def get_agent_service() -> AgentService:
    """Agent 서비스 인스턴스 반환"""
    global _agent_service
    if _agent_service is None:
        _agent_service = AgentService()
    return _agent_service 