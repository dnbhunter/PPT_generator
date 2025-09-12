"""Base agent class for DNB Presentation Generator multi-agent system."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type
from datetime import datetime
import uuid
import logging
from dataclasses import dataclass

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.language_models import BaseChatModel
from langchain_openai import AzureChatOpenAI

from ..core.config import get_settings, get_azure_openai_config
from ..core.exceptions import AgentError
from ..models.schemas import AgentState, AgentResult


logger = logging.getLogger(__name__)
settings = get_settings()


@dataclass
class AgentContext:
    """Agent execution context."""
    agent_id: str
    session_id: str
    user_id: str
    timestamp: datetime
    metadata: Dict[str, Any]


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system."""
    
    def __init__(
        self,
        name: str,
        description: str,
        llm: Optional[BaseChatModel] = None,
        system_prompt: Optional[str] = None,
    ):
        """Initialize base agent.
        
        Args:
            name: Agent name
            description: Agent description
            llm: Language model instance
            system_prompt: System prompt for the agent
        """
        self.name = name
        self.description = description
        self.agent_id = str(uuid.uuid4())
        self.llm = llm or self._create_default_llm()
        self.system_prompt = system_prompt or self._get_default_system_prompt()
        self.logger = logging.getLogger(f"{__name__}.{self.name}")
        
    def _create_default_llm(self) -> BaseChatModel:
        """Create default Azure OpenAI instance."""
        config = get_azure_openai_config()
        return AzureChatOpenAI(
            azure_endpoint=config["azure_endpoint"],
            api_key=config["api_key"],
            api_version=config["api_version"],
            azure_deployment=config["azure_deployment"],
            model=config["model"],
            temperature=0.3,
            max_tokens=2000,
            request_timeout=60,
        )
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for the agent."""
        return f"""
You are {self.name}, a specialized AI agent for DNB Bank's presentation generation system.

ROLE: {self.description}

RESPONSIBILITIES:
- Process inputs according to your specialization
- Maintain enterprise banking standards
- Ensure compliance with regulatory requirements
- Generate structured, professional outputs
- Handle errors gracefully and provide meaningful feedback

CONSTRAINTS:
- Always maintain data privacy and security
- Follow DNB brand guidelines
- Ensure accessibility compliance (WCAG 2.1 AA)
- Use professional, banking-appropriate language
- Validate all outputs for accuracy and completeness

QUALITY STANDARDS:
- Outputs must be production-ready
- All data must be accurate and verified
- Content must be appropriate for banking context
- Follow established templates and formats
- Maintain audit trail for all decisions

Respond with structured JSON outputs when possible.
"""
    
    @abstractmethod
    async def execute(
        self,
        state: AgentState,
        context: AgentContext,
    ) -> AgentResult:
        """Execute agent logic.
        
        Args:
            state: Current agent state
            context: Execution context
            
        Returns:
            Agent execution result
        """
        pass
    
    async def invoke(
        self,
        messages: List[BaseMessage],
        context: AgentContext,
    ) -> AIMessage:
        """Invoke the agent's language model.
        
        Args:
            messages: List of messages for the conversation
            context: Execution context
            
        Returns:
            AI response message
        """
        try:
            # Add system message if not present
            if not messages or not isinstance(messages[0], SystemMessage):
                system_message = SystemMessage(content=self.system_prompt)
                messages = [system_message] + messages
            
            # Add context metadata to the conversation
            context_message = HumanMessage(
                content=f"Context: Session ID: {context.session_id}, "
                       f"User ID: {context.user_id}, "
                       f"Timestamp: {context.timestamp.isoformat()}"
            )
            messages.append(context_message)
            
            self.logger.info(f"Invoking {self.name} with {len(messages)} messages")
            
            response = await self.llm.ainvoke(messages)
            
            self.logger.info(f"Agent {self.name} execution completed successfully")
            return response
            
        except Exception as e:
            self.logger.error(f"Agent {self.name} execution failed: {str(e)}")
            raise AgentError(
                f"Agent {self.name} failed to execute",
                error_code="AGENT_EXECUTION_FAILED",
                details={
                    "agent_name": self.name,
                    "agent_id": self.agent_id,
                    "error": str(e),
                    "context": context.__dict__,
                }
            )
    
    def validate_input(self, data: Dict[str, Any]) -> bool:
        """Validate input data.
        
        Args:
            data: Input data to validate
            
        Returns:
            True if valid, raises exception if invalid
        """
        if not isinstance(data, dict):
            raise AgentError(
                f"Invalid input type for agent {self.name}",
                error_code="INVALID_INPUT_TYPE",
                details={"expected": "dict", "received": type(data).__name__}
            )
        return True
    
    def validate_output(self, result: AgentResult) -> bool:
        """Validate output result.
        
        Args:
            result: Output result to validate
            
        Returns:
            True if valid, raises exception if invalid
        """
        if not isinstance(result, AgentResult):
            raise AgentError(
                f"Invalid output type from agent {self.name}",
                error_code="INVALID_OUTPUT_TYPE",
                details={"expected": "AgentResult", "received": type(result).__name__}
            )
        return True
    
    async def handle_error(
        self,
        error: Exception,
        context: AgentContext,
        retry_count: int = 0,
    ) -> Optional[AgentResult]:
        """Handle agent execution errors.
        
        Args:
            error: The exception that occurred
            context: Execution context
            retry_count: Number of retries attempted
            
        Returns:
            Recovery result or None if unrecoverable
        """
        self.logger.error(
            f"Agent {self.name} error (attempt {retry_count + 1}): {str(error)}"
        )
        
        # Implement basic retry logic
        max_retries = 3
        if retry_count < max_retries:
            self.logger.info(f"Retrying agent {self.name} (attempt {retry_count + 2})")
            return None  # Signal for retry
        
        # Create error result
        return AgentResult(
            success=False,
            data={},
            messages=[f"Agent {self.name} failed after {max_retries} attempts"],
            errors=[str(error)],
            agent_name=self.name,
            execution_time=0.0,
            metadata={
                "error_type": type(error).__name__,
                "retry_count": retry_count,
                "context": context.__dict__,
            }
        )
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get agent performance metrics.
        
        Returns:
            Dictionary of metrics
        """
        return {
            "agent_name": self.name,
            "agent_id": self.agent_id,
            "description": self.description,
            "model_info": {
                "model_name": getattr(self.llm, "model_name", "unknown"),
                "temperature": getattr(self.llm, "temperature", "unknown"),
                "max_tokens": getattr(self.llm, "max_tokens", "unknown"),
            }
        }
    
    def __str__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', id='{self.agent_id}')"
    
    def __repr__(self) -> str:
        """Detailed representation of the agent."""
        return (
            f"{self.__class__.__name__}("
            f"name='{self.name}', "
            f"id='{self.agent_id}', "
            f"description='{self.description}'"
            f")"
        )
