from fastapi import APIRouter, HTTPException

from app.schemas import OnboardingInput, AnalysisOutput
from app.services.analysis import analyze_response


router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    return {"status": "healthy"}


@router.post(
    "/analyze",
    response_model=AnalysisOutput,
    tags=["Analysis"],
    summary="Analyze onboarding response",
    description="Runs two LLM agents in parallel to analyze a Q&A response"
)
async def analyze_onboarding(input_data: OnboardingInput) -> AnalysisOutput:
    """
    Analyze an onboarding Q&A response.
    
    Runs two LLM agents in parallel:
    - **InsightAgent**: produces a summary and keywords
    - **TraitAgent**: produces trait scores with reasoning
    
    Returns the merged analysis result.
    """
    try:
        return analyze_response(input_data)
    except ValueError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

