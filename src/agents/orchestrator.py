"""Multi-agent orchestrator using LangGraph for DNB Presentation Generator."""

import asyncio
import time
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypedDict
from uuid import UUID, uuid4
import logging

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .base_agent import BaseAgent, AgentContext
from .planner_agent import PlannerAgent
from .research_agent import ResearchAgent
from .content_agent import ContentAgent
from .architect_agent import ArchitectAgent
from .qa_compliance_agent import QAComplianceAgent
from .export_agent import ExportAgent

from ..models.schemas import (
    AgentState, AgentResult, WorkflowExecution, WorkflowState,
    Presentation, ProcessedDocument
)
from ..core.exceptions import WorkflowError, AgentError
from ..core.constants import AgentType
from ..core.config import get_settings


logger = logging.getLogger(__name__)
settings = get_settings()


class PresentationWorkflowState(TypedDict):
    """State structure for presentation generation workflow."""
    # Core data
    presentation_id: str
    user_id: str
    session_id: str
    
    # Input data
    source_document: Optional[Dict[str, Any]]
    user_requirements: Dict[str, Any]
    
    # Agent outputs
    presentation_plan: Optional[Dict[str, Any]]
    research_data: Optional[Dict[str, Any]]
    slide_content: Optional[List[Dict[str, Any]]]
    architecture_decisions: Optional[Dict[str, Any]]
    compliance_report: Optional[Dict[str, Any]]
    export_results: Optional[Dict[str, Any]]
    
    # Workflow metadata
    current_step: str
    completed_steps: List[str]
    agent_results: List[Dict[str, Any]]
    errors: List[str]
    start_time: float
    metadata: Dict[str, Any]


class MultiAgentOrchestrator:
    """
    LangGraph-based multi-agent orchestrator for presentation generation.
    
    Coordinates the execution of specialized agents in a structured workflow:
    1. Planner Agent: Analyzes requirements and creates presentation plan
    2. Research Agent: Validates content and enriches with additional data
    3. Content Agent: Generates slide content and structure
    4. Architect Agent: Makes technical decisions and optimizations
    5. QA/Compliance Agent: Validates quality and compliance
    6. Export Agent: Generates final presentation files
    """
    
    def __init__(self):
        """Initialize the multi-agent orchestrator."""
        self.logger = logging.getLogger(__name__)
        self.checkpointer = MemorySaver()
        self.agents = self._initialize_agents()
        self.workflow = self._create_workflow()
        
        self.logger.info("Multi-agent orchestrator initialized successfully")
    
    def _initialize_agents(self) -> Dict[str, BaseAgent]:
        """Initialize all agents."""
        agents = {
            "planner": PlannerAgent(),
            "research": ResearchAgent(),
            "content": ContentAgent(),
            "architect": ArchitectAgent(),
            "qa_compliance": QAComplianceAgent(),
            "export": ExportAgent(),
        }
        
        self.logger.info(f"Initialized {len(agents)} agents: {list(agents.keys())}")
        return agents
    
    def _create_workflow(self) -> StateGraph:
        """Create the LangGraph workflow."""
        workflow = StateGraph(PresentationWorkflowState)
        
        # Add nodes for each agent
        workflow.add_node("planner", self._execute_planner)
        workflow.add_node("research", self._execute_research)
        workflow.add_node("content", self._execute_content)
        workflow.add_node("architect", self._execute_architect)
        workflow.add_node("qa_compliance", self._execute_qa_compliance)
        workflow.add_node("export", self._execute_export)
        
        # Define the workflow edges
        workflow.set_entry_point("planner")
        workflow.add_edge("planner", "research")
        workflow.add_edge("research", "content")
        workflow.add_edge("content", "architect")
        workflow.add_edge("architect", "qa_compliance")
        workflow.add_edge("qa_compliance", "export")
        workflow.add_edge("export", END)
        
        # Add conditional edges for error handling
        workflow.add_conditional_edges(
            "planner",
            self._should_continue_after_planner,
            {
                "continue": "research",
                "retry": "planner",
                "abort": END
            }
        )
        
        return workflow.compile(checkpointer=self.checkpointer)
    
    async def execute_workflow(
        self,
        presentation_id: UUID,
        user_id: UUID,
        source_document: Optional[ProcessedDocument] = None,
        user_requirements: Optional[Dict[str, Any]] = None,
    ) -> WorkflowExecution:
        """
        Execute the complete presentation generation workflow.
        
        Args:
            presentation_id: ID of the presentation to generate
            user_id: ID of the user requesting generation
            source_document: Source document to process
            user_requirements: User-specified requirements
            
        Returns:
            Workflow execution result
        """
        session_id = str(uuid4())
        start_time = time.time()
        
        # Initialize workflow state
        initial_state: PresentationWorkflowState = {
            "presentation_id": str(presentation_id),
            "user_id": str(user_id),
            "session_id": session_id,
            "source_document": source_document.model_dump() if source_document else None,
            "user_requirements": user_requirements or {},
            "presentation_plan": None,
            "research_data": None,
            "slide_content": None,
            "architecture_decisions": None,
            "compliance_report": None,
            "export_results": None,
            "current_step": "initialized",
            "completed_steps": [],
            "agent_results": [],
            "errors": [],
            "start_time": start_time,
            "metadata": {
                "workflow_version": "1.0",
                "agents_count": len(self.agents),
                "environment": settings.environment,
            }
        }
        
        try:
            self.logger.info(
                f"Starting workflow execution for presentation {presentation_id} "
                f"(session: {session_id})"
            )
            
            # Execute the workflow
            config = {"configurable": {"thread_id": session_id}}
            result = await self.workflow.ainvoke(initial_state, config)
            
            execution_time = time.time() - start_time
            
            # Create workflow execution result
            workflow_execution = WorkflowExecution(
                id=UUID(session_id),
                presentation_id=presentation_id,
                user_id=user_id,
                state=WorkflowState.COMPLETED if not result["errors"] else WorkflowState.ERROR,
                agent_results=[
                    AgentResult(**agent_result) for agent_result in result["agent_results"]
                ],
                total_execution_time=execution_time,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.utcnow(),
            )
            
            self.logger.info(
                f"Workflow execution completed in {execution_time:.2f}s "
                f"(session: {session_id})"
            )
            
            return workflow_execution
            
        except Exception as e:
            execution_time = time.time() - start_time
            self.logger.error(
                f"Workflow execution failed after {execution_time:.2f}s: {str(e)} "
                f"(session: {session_id})"
            )
            
            # Create error workflow execution
            workflow_execution = WorkflowExecution(
                id=UUID(session_id),
                presentation_id=presentation_id,
                user_id=user_id,
                state=WorkflowState.ERROR,
                agent_results=[],
                total_execution_time=execution_time,
                started_at=datetime.fromtimestamp(start_time),
                completed_at=datetime.utcnow(),
            )
            
            raise WorkflowError(
                f"Workflow execution failed: {str(e)}",
                error_code="WORKFLOW_EXECUTION_FAILED",
                details={
                    "session_id": session_id,
                    "presentation_id": str(presentation_id),
                    "execution_time": execution_time,
                    "error": str(e),
                }
            )
    
    async def _execute_planner(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute planner agent."""
        return await self._execute_agent("planner", state)
    
    async def _execute_research(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute research agent."""
        return await self._execute_agent("research", state)
    
    async def _execute_content(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute content agent."""
        return await self._execute_agent("content", state)
    
    async def _execute_architect(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute architect agent."""
        return await self._execute_agent("architect", state)
    
    async def _execute_qa_compliance(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute QA/compliance agent."""
        return await self._execute_agent("qa_compliance", state)
    
    async def _execute_export(self, state: PresentationWorkflowState) -> PresentationWorkflowState:
        """Execute export agent."""
        return await self._execute_agent("export", state)
    
    async def _execute_agent(
        self,
        agent_name: str,
        state: PresentationWorkflowState
    ) -> PresentationWorkflowState:
        """
        Execute a specific agent and update workflow state.
        
        Args:
            agent_name: Name of the agent to execute
            state: Current workflow state
            
        Returns:
            Updated workflow state
        """
        agent = self.agents[agent_name]
        start_time = time.time()
        
        try:
            self.logger.info(f"Executing agent: {agent_name}")
            
            # Create agent context
            context = AgentContext(
                agent_id=agent.agent_id,
                session_id=state["session_id"],
                user_id=state["user_id"],
                timestamp=datetime.utcnow(),
                metadata=state["metadata"]
            )
            
            # Create agent state from workflow state
            agent_state = AgentState(
                workflow_id=UUID(state["session_id"]),
                current_agent=AgentType(agent_name.upper()),
                state=WorkflowState.RUNNING,
                data=state,
                history=state["completed_steps"],
                metadata=state["metadata"]
            )
            
            # Execute agent
            result = await agent.execute(agent_state, context)
            
            execution_time = time.time() - start_time
            
            # Update workflow state with agent result
            state["completed_steps"].append(agent_name)
            state["current_step"] = agent_name
            state["agent_results"].append(result.model_dump())
            
            # Update specific state fields based on agent type
            if agent_name == "planner":
                state["presentation_plan"] = result.data
            elif agent_name == "research":
                state["research_data"] = result.data
            elif agent_name == "content":
                state["slide_content"] = result.data.get("slides", [])
            elif agent_name == "architect":
                state["architecture_decisions"] = result.data
            elif agent_name == "qa_compliance":
                state["compliance_report"] = result.data
            elif agent_name == "export":
                state["export_results"] = result.data
            
            if not result.success:
                state["errors"].extend(result.errors)
            
            self.logger.info(
                f"Agent {agent_name} completed in {execution_time:.2f}s "
                f"(success: {result.success})"
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"Agent {agent_name} failed: {str(e)}"
            
            self.logger.error(f"{error_msg} (execution time: {execution_time:.2f}s)")
            
            state["errors"].append(error_msg)
            
            # Create error result
            error_result = AgentResult(
                success=False,
                data={},
                messages=[],
                errors=[error_msg],
                agent_name=agent_name,
                execution_time=execution_time,
                metadata={"error_type": type(e).__name__}
            )
            
            state["agent_results"].append(error_result.model_dump())
        
        return state
    
    def _should_continue_after_planner(self, state: PresentationWorkflowState) -> str:
        """Determine whether to continue workflow after planner agent."""
        if state["errors"]:
            retry_count = len([s for s in state["completed_steps"] if s == "planner"])
            if retry_count < 3:
                return "retry"
            else:
                return "abort"
        return "continue"
    
    async def get_workflow_status(self, session_id: str) -> Dict[str, Any]:
        """
        Get the current status of a workflow execution.
        
        Args:
            session_id: Workflow session ID
            
        Returns:
            Workflow status information
        """
        try:
            config = {"configurable": {"thread_id": session_id}}
            state = await self.workflow.aget_state(config)
            
            return {
                "session_id": session_id,
                "current_step": state.values.get("current_step", "unknown"),
                "completed_steps": state.values.get("completed_steps", []),
                "total_steps": len(self.agents),
                "errors": state.values.get("errors", []),
                "is_complete": state.is_complete,
                "metadata": state.values.get("metadata", {}),
            }
        except Exception as e:
            self.logger.error(f"Failed to get workflow status: {str(e)}")
            return {
                "session_id": session_id,
                "error": str(e),
                "status": "unknown"
            }
    
    async def cancel_workflow(self, session_id: str) -> bool:
        """
        Cancel a running workflow.
        
        Args:
            session_id: Workflow session ID
            
        Returns:
            True if cancelled successfully
        """
        try:
            # Note: LangGraph doesn't have direct cancellation API
            # This would need to be implemented with a custom cancellation mechanism
            self.logger.warning(f"Workflow cancellation requested for session {session_id}")
            # Implementation would depend on specific cancellation requirements
            return True
        except Exception as e:
            self.logger.error(f"Failed to cancel workflow: {str(e)}")
            return False
    
    def get_agent_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all agents."""
        return {
            name: agent.get_metrics()
            for name, agent in self.agents.items()
        }
    
    def get_workflow_metrics(self) -> Dict[str, Any]:
        """Get workflow performance metrics."""
        return {
            "agents_count": len(self.agents),
            "workflow_steps": len(self.agents),
            "checkpointer_type": type(self.checkpointer).__name__,
            "agents": list(self.agents.keys()),
        }
