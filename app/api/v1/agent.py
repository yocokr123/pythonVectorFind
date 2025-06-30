from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import logging

from app.models.agent import Agent, AgentAction
from app.core.dependencies import get_agent_service

router = APIRouter(prefix="/agent", tags=["agent"])

class AgentRequest(BaseModel):
    goal: str
    context: Optional[str] = ""
    tools: Optional[List[str]] = []

class AgentResponse(BaseModel):
    agent_id: str
    status: str
    plan: Optional[List[str]] = None
    actions: Optional[List[Dict[str, Any]]] = None
    result: Optional[Dict[str, Any]] = None

class AgentActionRequest(BaseModel):
    tool_name: str
    parameters: Dict[str, Any]

@router.post("/create", response_model=AgentResponse)
async def create_agent(request: AgentRequest):
    """새로운 AI Agent 생성"""
    try:
        agent_service = get_agent_service()
        agent = agent_service.create_agent(request.goal)
        
        # 계획 수립
        plan = agent.think(request.goal, request.context or "")
        
        return AgentResponse(
            agent_id=agent.name,
            status=agent.status.value,
            plan=plan
        )
    except Exception as e:
        logging.error(f"Agent creation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/{agent_id}/execute", response_model=AgentResponse)
async def execute_agent_action(agent_id: str, request: AgentActionRequest):
    """에이전트 액션 실행"""
    try:
        agent_service = get_agent_service()
        agent = agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        action = agent.execute_action(request.tool_name, **request.parameters)
        
        return AgentResponse(
            agent_id=agent_id,
            status=agent.status.value,
            actions=[{
                'id': action.id,
                'tool_name': action.tool_name,
                'success': action.success,
                'result': action.result,
                'error': action.error_message
            }]
        )
    except Exception as e:
        logging.error(f"Agent action execution failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}/status")
async def get_agent_status(agent_id: str):
    """에이전트 상태 조회"""
    try:
        agent_service = get_agent_service()
        agent = agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return agent.get_status()
    except Exception as e:
        logging.error(f"Agent status retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{agent_id}/history")
async def get_agent_history(agent_id: str):
    """에이전트 실행 히스토리 조회"""
    try:
        agent_service = get_agent_service()
        agent = agent_service.get_agent(agent_id)
        
        if not agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            'agent_id': agent_id,
            'actions_history': [
                {
                    'id': action.id,
                    'tool_name': action.tool_name,
                    'success': action.success,
                    'timestamp': action.timestamp.isoformat(),
                    'result': action.result
                }
                for action in agent.actions_history
            ],
            'memory': agent.memory
        }
    except Exception as e:
        logging.error(f"Agent history retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 