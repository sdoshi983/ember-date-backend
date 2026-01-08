"""LLM-powered agents for analyzing onboarding responses."""

import json

from openai import OpenAI

from app.config import get_settings
from app.schemas import GraphState, Insight, Trait


def get_openai_client() -> OpenAI:
    """Get OpenAI client using settings."""
    settings = get_settings()
    return OpenAI(api_key=settings.openai_api_key)


# ============================================================================
# InsightAgent
# ============================================================================

INSIGHT_SYSTEM_PROMPT = """You are an InsightAgent for a dating app's onboarding system.

Your job is to analyze a user's response to an onboarding question and produce:
1. A SHORT, FRIENDLY natural-language summary (1-2 sentences max)
2. 2-3 key phrases that capture the essence of their response

Be warm and empathetic. Focus on what the user truly wants.

You MUST respond with valid JSON in this exact format:
{
  "summary": "A brief, friendly summary of what the user is looking for",
  "keywords": ["keyword1", "keyword2", "keyword3"]
}

Only output the JSON, nothing else."""


def run_insight_agent(state: GraphState) -> dict:
    """
    InsightAgent: Produces a summary and keywords from the user's response.
    
    Args:
        state: Current graph state with question and answer
        
    Returns:
        Dict with 'insight' key containing the Insight object
    """
    settings = get_settings()
    client = get_openai_client()
    
    user_message = f"""Onboarding Question: {state.question}

User's Response: {state.answer}

Analyze this response and provide a summary with keywords."""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": INSIGHT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=300,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        insight = Insight(
            summary=parsed.get("summary", ""),
            keywords=parsed.get("keywords", [])[:5]
        )
        
        return {"insight": insight}
        
    except Exception as e:
        return {"errors": state.errors + [f"InsightAgent error: {str(e)}"]}


# ============================================================================
# TraitAgent
# ============================================================================

TRAIT_SYSTEM_PROMPT = """You are a TraitAgent for a dating app's onboarding system.

Your job is to analyze a user's response and score 2-3 personality/dating traits.
Each trait should have:
- A snake_case name (e.g., relationship_goal_readiness, social_energy, openness_to_commitment)
- A numeric score from -1.0 to 1.0 where:
  - -1.0 = strongly negative/low
  - 0.0 = neutral/ambiguous
  - 1.0 = strongly positive/high
- A one-sentence reasoning explaining the score

Consider traits relevant to dating like:
- relationship_goal_readiness: How clear and ready are they for their stated goals?
- openness_to_commitment: How willing are they to commit?
- social_energy: Introvert (-1) to extrovert (1)
- emotional_availability: How emotionally open do they seem?
- self_awareness: How self-aware do they appear about their needs?

Pick 2-3 traits that are MOST RELEVANT to what the user said.

You MUST respond with valid JSON in this exact format:
{
  "traits": [
    {"name": "trait_name", "score": 0.8, "reason": "One sentence explanation"},
    {"name": "another_trait", "score": 0.5, "reason": "One sentence explanation"}
  ]
}

Only output the JSON, nothing else."""


def run_trait_agent(state: GraphState) -> dict:
    """
    TraitAgent: Produces numeric trait scores with reasoning.
    
    Args:
        state: Current graph state with question and answer
        
    Returns:
        Dict with 'traits' key containing list of Trait objects
    """
    settings = get_settings()
    client = get_openai_client()
    
    user_message = f"""Onboarding Question: {state.question}

User's Response: {state.answer}

Analyze this response and score relevant personality/dating traits."""

    try:
        response = client.chat.completions.create(
            model=settings.openai_model,
            messages=[
                {"role": "system", "content": TRAIT_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            temperature=0.7,
            max_tokens=400,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        parsed = json.loads(content)
        
        traits = []
        for t in parsed.get("traits", [])[:5]:
            score = max(-1.0, min(1.0, float(t.get("score", 0))))
            traits.append(Trait(
                name=t.get("name", "unknown_trait"),
                score=score,
                reason=t.get("reason", "")
            ))
        
        return {"traits": traits}
        
    except Exception as e:
        return {"errors": state.errors + [f"TraitAgent error: {str(e)}"]}

