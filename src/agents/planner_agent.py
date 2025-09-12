"""Planner agent for DNB Presentation Generator."""

import json
from typing import Any, Dict, List
from datetime import datetime

from ..agents.base_agent import BaseAgent, AgentContext
from ..models.schemas import AgentState, AgentResult
from ..core.constants import PresentationTemplate, SlideType
from ..core.exceptions import AgentError


class PlannerAgent(BaseAgent):
    """
    Planner agent responsible for analyzing requirements and creating presentation plans.
    
    This agent:
    1. Analyzes source documents and user requirements
    2. Determines appropriate presentation structure
    3. Creates slide outlines and content hierarchy
    4. Selects optimal templates and themes
    5. Defines success criteria and compliance requirements
    """
    
    def __init__(self):
        """Initialize planner agent."""
        super().__init__(
            name="Planner",
            description="Analyzes requirements and creates comprehensive presentation plans",
            system_prompt=self._get_planner_system_prompt()
        )
    
    def _get_planner_system_prompt(self) -> str:
        """Get specialized system prompt for planner agent."""
        return """
You are the Planner Agent for DNB Bank's presentation generation system.

ROLE: Strategic planning and requirement analysis for presentation generation

RESPONSIBILITIES:
1. Analyze source documents and extract key themes
2. Understand user requirements and presentation objectives
3. Create structured presentation outlines with slide hierarchy
4. Select appropriate templates based on content and audience
5. Define success criteria and quality benchmarks
6. Ensure compliance with banking regulations and brand guidelines

ANALYSIS FRAMEWORK:
- Content Analysis: Extract main topics, supporting data, key messages
- Audience Analysis: Determine appropriate tone, complexity, and format
- Structure Planning: Logical flow, narrative arc, supporting evidence
- Template Selection: Match content type to optimal presentation template
- Compliance Planning: Identify PII, regulatory considerations, approval requirements

OUTPUT FORMAT:
Provide structured JSON response with:
{
    "presentation_outline": {
        "title": "Presentation title",
        "objective": "Main presentation objective",
        "target_audience": "Intended audience description",
        "key_messages": ["List of key messages"],
        "slide_structure": [
            {
                "slide_number": 1,
                "type": "title|content|chart|conclusion",
                "title": "Slide title",
                "content_outline": "Brief content description",
                "estimated_content_length": "words count estimate"
            }
        ]
    },
    "template_recommendation": {
        "primary_template": "corporate|executive|research|financial",
        "rationale": "Why this template was selected",
        "customizations": ["List of template customizations needed"]
    },
    "compliance_requirements": {
        "pii_handling": "required|optional|none",
        "regulatory_flags": ["List of regulatory considerations"],
        "approval_level": "manager|director|executive",
        "content_restrictions": ["List of content restrictions"]
    },
    "success_criteria": {
        "clarity_score": "Expected clarity rating (1-10)",
        "engagement_metrics": "Expected audience engagement",
        "compliance_level": "Required compliance level",
        "accessibility_requirements": ["WCAG compliance requirements"]
    },
    "execution_plan": {
        "estimated_slides": "Number of slides",
        "chart_requirements": ["List of charts needed"],
        "image_requirements": ["List of images needed"],
        "research_needs": ["Additional research required"]
    }
}

QUALITY STANDARDS:
- Plans must be actionable and specific
- All recommendations must be justified
- Compliance requirements must be comprehensive
- Success criteria must be measurable
- Structure must follow logical narrative flow

Always prioritize banking industry standards and regulatory compliance.
"""
    
    async def execute(
        self,
        state: AgentState,
        context: AgentContext,
    ) -> AgentResult:
        """
        Execute planner agent logic.
        
        Args:
            state: Current agent state containing source document and requirements
            context: Execution context
            
        Returns:
            Planning result with presentation outline and recommendations
        """
        start_time = datetime.utcnow()
        
        try:
            self.logger.info("Starting presentation planning analysis")
            
            # Extract input data
            source_document = state.data.get("source_document")
            user_requirements = state.data.get("user_requirements", {})
            
            # Validate inputs
            self._validate_planning_inputs(source_document, user_requirements)
            
            # Create planning prompt
            planning_prompt = self._create_planning_prompt(source_document, user_requirements)
            
            # Execute planning analysis
            planning_result = await self._execute_planning_analysis(planning_prompt, context)
            
            # Validate and structure result
            structured_plan = self._structure_planning_result(planning_result)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            self.logger.info(
                f"Planning analysis completed successfully in {execution_time:.2f}s"
            )
            
            return AgentResult(
                success=True,
                data=structured_plan,
                messages=[
                    "Presentation plan created successfully",
                    f"Recommended template: {structured_plan['template_recommendation']['primary_template']}",
                    f"Estimated slides: {structured_plan['execution_plan']['estimated_slides']}",
                ],
                errors=[],
                agent_name=self.name,
                execution_time=execution_time,
                metadata={
                    "template": structured_plan['template_recommendation']['primary_template'],
                    "slide_count": structured_plan['execution_plan']['estimated_slides'],
                    "compliance_level": structured_plan['compliance_requirements']['approval_level'],
                }
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Planning analysis failed: {str(e)}"
            
            self.logger.error(error_msg)
            
            return AgentResult(
                success=False,
                data={},
                messages=[],
                errors=[error_msg],
                agent_name=self.name,
                execution_time=execution_time,
                metadata={"error_type": type(e).__name__}
            )
    
    def _validate_planning_inputs(
        self,
        source_document: Any,
        user_requirements: Dict[str, Any]
    ) -> None:
        """Validate planning inputs."""
        if not source_document and not user_requirements.get("manual_content"):
            raise AgentError(
                "Either source document or manual content is required for planning",
                error_code="INSUFFICIENT_INPUT_DATA"
            )
        
        # Additional validation logic
        if user_requirements.get("max_slides", 0) > 25:
            raise AgentError(
                "Maximum slides per presentation is 25",
                error_code="INVALID_SLIDE_COUNT"
            )
    
    def _create_planning_prompt(
        self,
        source_document: Any,
        user_requirements: Dict[str, Any]
    ) -> str:
        """Create planning analysis prompt."""
        prompt_parts = [
            "PRESENTATION PLANNING REQUEST",
            "=" * 50,
            "",
        ]
        
        # Add source document information
        if source_document:
            prompt_parts.extend([
                "SOURCE DOCUMENT:",
                f"- Type: {source_document.get('metadata', {}).get('document_type', 'unknown')}",
                f"- Size: {source_document.get('metadata', {}).get('file_size', 'unknown')} bytes",
                f"- Language: {source_document.get('metadata', {}).get('language', 'unknown')}",
                "",
                "DOCUMENT CONTENT:",
                source_document.get('content', '')[:2000] + ("..." if len(source_document.get('content', '')) > 2000 else ""),
                "",
            ])
        
        # Add user requirements
        if user_requirements:
            prompt_parts.extend([
                "USER REQUIREMENTS:",
                f"- Target audience: {user_requirements.get('target_audience', 'Not specified')}",
                f"- Presentation purpose: {user_requirements.get('purpose', 'Not specified')}",
                f"- Preferred template: {user_requirements.get('template', 'Auto-select')}",
                f"- Maximum slides: {user_requirements.get('max_slides', 'Auto-determine')}",
                f"- Include charts: {user_requirements.get('include_charts', True)}",
                f"- Include images: {user_requirements.get('include_images', True)}",
                f"- Compliance level: {user_requirements.get('compliance_level', 'Standard')}",
                "",
            ])
        
        prompt_parts.extend([
            "INSTRUCTIONS:",
            "1. Analyze the content and requirements thoroughly",
            "2. Create a comprehensive presentation plan",
            "3. Recommend the most appropriate template",
            "4. Identify compliance and regulatory considerations",
            "5. Define clear success criteria",
            "6. Provide structured JSON output as specified",
            "",
            "Please analyze this information and create a detailed presentation plan."
        ])
        
        return "\n".join(prompt_parts)
    
    async def _execute_planning_analysis(
        self,
        prompt: str,
        context: AgentContext
    ) -> str:
        """Execute planning analysis using LLM."""
        from langchain_core.messages import HumanMessage
        
        messages = [HumanMessage(content=prompt)]
        response = await self.invoke(messages, context)
        
        return response.content
    
    def _structure_planning_result(self, planning_result: str) -> Dict[str, Any]:
        """Structure and validate planning result."""
        try:
            # Try to parse JSON response
            if "```json" in planning_result:
                json_start = planning_result.find("```json") + 7
                json_end = planning_result.find("```", json_start)
                json_content = planning_result[json_start:json_end].strip()
            else:
                json_content = planning_result.strip()
            
            parsed_result = json.loads(json_content)
            
            # Validate required fields
            required_fields = [
                "presentation_outline",
                "template_recommendation",
                "compliance_requirements",
                "success_criteria",
                "execution_plan"
            ]
            
            for field in required_fields:
                if field not in parsed_result:
                    raise AgentError(f"Missing required field: {field}")
            
            # Add default values and validation
            parsed_result = self._add_default_values(parsed_result)
            
            return parsed_result
            
        except json.JSONDecodeError as e:
            self.logger.warning(f"Failed to parse JSON response: {str(e)}")
            
            # Create fallback structured result
            return self._create_fallback_plan(planning_result)
    
    def _add_default_values(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """Add default values and perform validation."""
        # Ensure slide structure has required fields
        for slide in plan["presentation_outline"].get("slide_structure", []):
            if "type" not in slide:
                slide["type"] = "content"
            if "estimated_content_length" not in slide:
                slide["estimated_content_length"] = "50-100 words"
        
        # Ensure template recommendation has fallback
        if not plan["template_recommendation"].get("primary_template"):
            plan["template_recommendation"]["primary_template"] = "corporate"
        
        # Ensure compliance requirements have defaults
        compliance = plan["compliance_requirements"]
        compliance.setdefault("pii_handling", "required")
        compliance.setdefault("approval_level", "manager")
        compliance.setdefault("regulatory_flags", [])
        compliance.setdefault("content_restrictions", [])
        
        # Ensure execution plan has estimates
        execution = plan["execution_plan"]
        execution.setdefault("estimated_slides", len(plan["presentation_outline"].get("slide_structure", [])))
        execution.setdefault("chart_requirements", [])
        execution.setdefault("image_requirements", [])
        execution.setdefault("research_needs", [])
        
        return plan
    
    def _create_fallback_plan(self, raw_result: str) -> Dict[str, Any]:
        """Create fallback plan when JSON parsing fails."""
        self.logger.warning("Creating fallback plan due to parsing failure")
        
        # Extract basic information from raw text
        estimated_slides = 10  # Default
        template = "corporate"  # Default
        
        # Try to extract slide count from text
        import re
        slide_match = re.search(r'(\d+)\s*slides?', raw_result.lower())
        if slide_match:
            estimated_slides = min(int(slide_match.group(1)), 25)
        
        # Try to extract template preference
        for template_type in ["executive", "research", "financial", "corporate"]:
            if template_type in raw_result.lower():
                template = template_type
                break
        
        return {
            "presentation_outline": {
                "title": "Generated Presentation",
                "objective": "Present key information from source document",
                "target_audience": "Business stakeholders",
                "key_messages": ["Key insights from source material"],
                "slide_structure": [
                    {
                        "slide_number": i + 1,
                        "type": "title" if i == 0 else "content",
                        "title": f"Slide {i + 1}",
                        "content_outline": "Content to be generated",
                        "estimated_content_length": "50-100 words"
                    }
                    for i in range(estimated_slides)
                ]
            },
            "template_recommendation": {
                "primary_template": template,
                "rationale": "Selected based on content analysis",
                "customizations": []
            },
            "compliance_requirements": {
                "pii_handling": "required",
                "regulatory_flags": [],
                "approval_level": "manager",
                "content_restrictions": []
            },
            "success_criteria": {
                "clarity_score": "8",
                "engagement_metrics": "High audience engagement expected",
                "compliance_level": "Standard banking compliance",
                "accessibility_requirements": ["WCAG 2.1 AA compliance"]
            },
            "execution_plan": {
                "estimated_slides": estimated_slides,
                "chart_requirements": [],
                "image_requirements": [],
                "research_needs": []
            }
        }
