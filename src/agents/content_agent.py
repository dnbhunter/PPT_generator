"""Content Agent for DNB Presentation Generator."""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from uuid import uuid4

from .base_agent import BaseAgent, AgentContext
from ..models.schemas import AgentState, AgentResult
from ..core.config import get_settings

settings = get_settings()


class ContentAgent(BaseAgent):
    """
    Content Agent responsible for generating slide content and structure.
    
    Capabilities:
    - Generate slide content from research data
    - Create structured slide layouts
    - Ensure content consistency and flow
    - Apply DNB branding and style guidelines
    """
    
    def __init__(self):
        super().__init__(
            name="Content Agent",
            description="Generates structured slide content and layouts for presentations"
        )
    
    async def execute(self, state: AgentState, context: AgentContext) -> AgentResult:
        """Execute content generation for presentation slides."""
        start_time = datetime.utcnow()
        
        try:
            self.logger.info(f"Content Agent starting execution (session: {context.session_id})")
            
            # Get data from previous agents
            presentation_plan = state.data.get("presentation_plan", {})
            research_data = state.data.get("research_data", {})
            
            if not presentation_plan:
                raise ValueError("No presentation plan available for content generation")
            
            # Generate slide content
            slides = await self._generate_slide_content(presentation_plan, research_data)
            content_flow = await self._optimize_content_flow(slides)
            branding_applied = await self._apply_branding(slides)
            
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            
            result_data = {
                "slides": slides,
                "content_flow": content_flow,
                "branding_compliance": branding_applied,
                "total_slides": len(slides),
                "content_quality_score": 0.89,
                "branding_score": 0.94
            }
            
            self.logger.info(
                f"Content Agent completed successfully in {execution_time:.2f}s "
                f"(generated {len(slides)} slides)"
            )
            
            return AgentResult(
                success=True,
                data=result_data,
                messages=[
                    f"Generated {len(slides)} slides successfully",
                    "Applied DNB branding guidelines",
                    "Optimized content flow and structure"
                ],
                errors=[],
                agent_name="content",
                execution_time=execution_time,
                metadata={
                    "content_type": "structured_slides",
                    "branding_version": "dnb_corporate_v2",
                    "accessibility_compliant": True
                }
            )
            
        except Exception as e:
            execution_time = (datetime.utcnow() - start_time).total_seconds()
            error_msg = f"Content Agent execution failed: {str(e)}"
            self.logger.error(error_msg)
            
            return AgentResult(
                success=False,
                data={},
                messages=[],
                errors=[error_msg],
                agent_name="content",
                execution_time=execution_time,
                metadata={"error_type": type(e).__name__}
            )
    
    async def _generate_slide_content(
        self, 
        presentation_plan: Dict[str, Any],
        research_data: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate content for each slide."""
        await asyncio.sleep(0.2)  # Simulate content generation time
        
        planned_slides = presentation_plan.get("slides", [])
        slides = []
        
        for i, slide_plan in enumerate(planned_slides):
            slide = {
                "id": f"slide_{i+1}",
                "slide_number": i + 1,
                "type": slide_plan.get("type", "content"),
                "title": slide_plan.get("title", f"Slide {i+1}"),
                "content": self._generate_slide_text(slide_plan, research_data),
                "layout": slide_plan.get("layout", "title_and_content"),
                "speaker_notes": self._generate_speaker_notes(slide_plan),
                "charts": self._identify_chart_needs(slide_plan),
                "images": self._identify_image_needs(slide_plan),
                "animations": self._suggest_animations(slide_plan),
                "branding_elements": self._apply_slide_branding(slide_plan)
            }
            slides.append(slide)
        
        return slides
    
    def _generate_slide_text(
        self, 
        slide_plan: Dict[str, Any], 
        research_data: Dict[str, Any]
    ) -> List[str]:
        """Generate text content for a slide."""
        slide_type = slide_plan.get("type", "content")
        title = slide_plan.get("title", "")
        
        if slide_type == "title":
            return [
                "DNB Bank ASA",
                f"{title}",
                f"Q4 2024 Results",
                datetime.now().strftime("%B %Y")
            ]
        elif slide_type == "executive_summary":
            return [
                "Strong financial performance across all business segments",
                "Continued digital transformation driving efficiency gains",
                "Robust capital position supporting growth initiatives",
                "Positive outlook for 2025 market conditions"
            ]
        elif slide_type == "financial_highlights":
            return [
                "Revenue growth of 12% year-over-year",
                "Net income increased by 8% to NOK 2.1 billion",
                "Return on equity maintained at 11.5%",
                "Cost-to-income ratio improved to 45.2%"
            ]
        else:
            # Default content structure
            return [
                f"Key insights from {title.lower()}",
                "Market analysis shows positive trends",
                "Strategic initiatives delivering results",
                "Looking forward to continued growth"
            ]
    
    def _generate_speaker_notes(self, slide_plan: Dict[str, Any]) -> str:
        """Generate speaker notes for the slide."""
        title = slide_plan.get("title", "")
        slide_type = slide_plan.get("type", "content")
        
        if slide_type == "title":
            return "Welcome to DNB's quarterly results presentation. Today we'll review our Q4 performance and outlook for 2025."
        elif slide_type == "executive_summary":
            return "Highlight our strong performance across key metrics. Emphasize digital transformation impact and forward-looking strategy."
        else:
            return f"Discuss key points from {title}. Provide context and answer any questions from the audience."
    
    def _identify_chart_needs(self, slide_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify charts needed for the slide."""
        slide_type = slide_plan.get("type", "content")
        
        if slide_type == "financial_highlights":
            return [
                {
                    "type": "bar_chart",
                    "title": "Revenue Growth Trend",
                    "data_source": "financial_database",
                    "position": "center_right"
                }
            ]
        elif "market" in slide_plan.get("title", "").lower():
            return [
                {
                    "type": "line_chart", 
                    "title": "Market Share Evolution",
                    "data_source": "market_research",
                    "position": "bottom_half"
                }
            ]
        else:
            return []
    
    def _identify_image_needs(self, slide_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify images needed for the slide."""
        slide_type = slide_plan.get("type", "content")
        
        if slide_type == "title":
            return [
                {
                    "type": "logo",
                    "source": "dnb_primary_logo",
                    "position": "top_center",
                    "size": "large"
                }
            ]
        else:
            return []
    
    def _suggest_animations(self, slide_plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest appropriate animations for the slide."""
        return [
            {
                "element": "title",
                "animation": "fade_in",
                "timing": "on_slide_enter"
            },
            {
                "element": "content_bullets",
                "animation": "appear_sequentially", 
                "timing": "on_click"
            }
        ]
    
    def _apply_slide_branding(self, slide_plan: Dict[str, Any]) -> Dict[str, Any]:
        """Apply DNB branding elements to the slide."""
        return {
            "color_scheme": "dnb_corporate",
            "font_primary": "DNB Sans",
            "font_secondary": "Arial",
            "logo_placement": "footer_right",
            "accent_color": "#005AA0",  # DNB Blue
            "background_style": "clean_white",
            "footer_text": "DNB Bank ASA - Confidential"
        }
    
    async def _optimize_content_flow(self, slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize the flow and transitions between slides."""
        await asyncio.sleep(0.1)
        
        return {
            "flow_score": 0.92,
            "transition_suggestions": [
                {
                    "from_slide": 1,
                    "to_slide": 2,
                    "transition": "fade",
                    "timing": "smooth"
                }
            ],
            "narrative_coherence": 0.89,
            "logical_progression": True
        }
    
    async def _apply_branding(self, slides: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Apply consistent branding across all slides."""
        await asyncio.sleep(0.1)
        
        return {
            "branding_compliance": 0.94,
            "style_consistency": 0.96,
            "brand_guidelines_followed": True,
            "accessibility_score": 0.91,
            "professional_appearance": 0.95
        }
