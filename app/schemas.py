"""Pydantic schemas for request/response validation and internal state."""

from typing import Annotated

from pydantic import BaseModel, Field


# ============================================================================
# Request Schemas
# ============================================================================

class OnboardingInput(BaseModel):
    """Input schema for a single onboarding Q&A pair."""
    
    user_id: str = Field(
        ...,
        min_length=1,
        description="Unique identifier for the user"
    )
    question: str = Field(
        ...,
        min_length=1,
        description="The onboarding question posed to the user"
    )
    answer: str = Field(
        ...,
        min_length=1,
        description="The user's free-text response to the question"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "user-123",
                    "question": "What are you looking for in your dating life right now?",
                    "answer": "I'm ready to find a serious partner and I'm tired of casual dating."
                }
            ]
        }
    }


# ============================================================================
# Response Schemas
# ============================================================================

class Insight(BaseModel):
    """Natural language summary and key phrases from InsightAgent."""
    
    summary: str = Field(
        ...,
        description="A short, friendly natural-language summary of the user's response"
    )
    keywords: list[str] = Field(
        default_factory=list,
        min_length=2,
        max_length=5,
        description="2-5 key phrases extracted from the response"
    )


class Trait(BaseModel):
    """A single trait score with reasoning from TraitAgent."""
    
    name: str = Field(
        ...,
        description="Snake_case name for the trait (e.g., 'relationship_goal_readiness')"
    )
    score: Annotated[float, Field(ge=-1.0, le=1.0)] = Field(
        ...,
        description="Numeric score from -1 (strongly negative) to 1 (strongly positive)"
    )
    reason: str = Field(
        ...,
        description="One-sentence reasoning explaining the score"
    )


class AnalysisOutput(BaseModel):
    """Final merged output from all agents."""
    
    user_id: str = Field(..., description="The user's identifier (echoed from input)")
    insight: Insight = Field(..., description="Summary and keywords from InsightAgent")
    traits: list[Trait] = Field(
        default_factory=list,
        min_length=2,
        max_length=5,
        description="2-5 trait scores from TraitAgent"
    )


# ============================================================================
# Internal State Schema
# ============================================================================

class GraphState(BaseModel):
    """State object passed through the LangGraph workflow."""
    
    # Input fields
    user_id: str
    question: str
    answer: str
    
    # Agent output fields (populated during graph execution)
    insight: Insight | None = None
    traits: list[Trait] = Field(default_factory=list)
    
    # Error tracking
    errors: list[str] = Field(default_factory=list)

    model_config = {"extra": "forbid"}

