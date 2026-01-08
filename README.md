# Ember Date Onboarding Analysis Service

A Python service that analyzes dating app onboarding responses using **LangGraph** with parallel LLM agents.

## Overview

This service takes a single onboarding Q&A pair and runs two LLM agents in parallel:

1. **InsightAgent** - Produces a friendly summary and 2-3 key phrases
2. **TraitAgent** - Scores 2-3 personality/dating traits on a -1 to 1 scale with reasoning

Both results are merged into a single structured JSON output validated with Pydantic.

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                    FastAPI / CLI                     │
├─────────────────────────────────────────────────────┤
│                   LangGraph Graph                    │
│  ┌─────────────┐              ┌─────────────────┐   │
│  │ InsightAgent│   parallel   │   TraitAgent    │   │
│  │  (gpt-4o-   │◄────────────►│  (gpt-4o-mini)  │   │
│  │   mini)     │              │                 │   │
│  └──────┬──────┘              └────────┬────────┘   │
│         │          merge               │            │
│         └──────────────┬───────────────┘            │
│                        ▼                            │
│              AnalysisOutput (Pydantic)              │
└─────────────────────────────────────────────────────┘
```

## Installation

```bash
# Create virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Environment Variables

**Option 1: Using `.env` file (recommended)**

Copy the example environment file and add your API key:

```bash
cp example.env .env
```

Then edit `.env` and replace `your-api-key-here` with your actual OpenAI API key:

```
OPENAI_API_KEY=sk-your-actual-api-key
```

**Option 2: Export directly**

```bash
export OPENAI_API_KEY="your-api-key-here"
```

> **Note:** The `.env` file is automatically loaded by the application using `python-dotenv`. Never commit your `.env` file to version control.

## Running the Service

### Option 1: HTTP Server (FastAPI)

Start the server:

```bash
uvicorn app.main:app --reload --port 8000
```

Make a request:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user-123",
    "question": "What are you looking for in your dating life right now?",
    "answer": "I'\''m ready to find a serious partner and I'\''m tired of casual dating."
  }'
```

### Option 2: CLI Mode

Run with a JSON file:

```bash
python cli.py sample_input.json
```

Or pipe JSON via stdin:

```bash
echo '{"user_id": "user-123", "question": "What are you looking for?", "answer": "A serious relationship"}' | python cli.py
```

## API Reference

### POST /analyze

Analyze an onboarding Q&A response.

**Request Body:**

```json
{
  "user_id": "user-123",
  "question": "What are you looking for in your dating life right now?",
  "answer": "I'm ready to find a serious partner and I'm tired of casual dating."
}
```

**Response:**

```json
{
  "user_id": "user-123",
  "insight": {
    "summary": "Seeking a committed, long-term relationship and is done with casual dating.",
    "keywords": ["serious partner", "long-term", "no casual dating"]
  },
  "traits": [
    {
      "name": "relationship_goal_readiness",
      "score": 0.9,
      "reason": "Explicitly states they are ready for a serious, long-term partner."
    },
    {
      "name": "openness_to_commitment",
      "score": 0.85,
      "reason": "Clear rejection of casual dating signals strong commitment orientation."
    }
  ]
}
```

### GET /health

Health check endpoint. Returns `{"status": "healthy"}`.

## Project Structure

```
ember_date_backend_assessment/
├── README.md
├── requirements.txt
├── example.env              # Template for environment variables
├── sample_input.json
├── cli.py                   # CLI entrypoint
└── app/
    ├── __init__.py
    ├── main.py              # FastAPI app factory
    ├── config.py            # Settings management (pydantic-settings)
    ├── schemas.py           # Pydantic models for I/O and state
    ├── api/
    │   ├── __init__.py
    │   └── routes.py        # API endpoint definitions
    └── services/
        ├── __init__.py
        ├── agents.py        # InsightAgent and TraitAgent
        └── analysis.py      # LangGraph workflow
```

## Design Decisions

1. **Parallel Execution**: Both agents run simultaneously via LangGraph's parallel edges, reducing latency.

2. **Typed State**: The graph uses a Pydantic `GraphState` model for type safety and validation.

3. **JSON Mode**: OpenAI's `response_format={"type": "json_object"}` ensures reliable structured output.

4. **Separation of Concerns**: Models, agents, graph wiring, and HTTP handling are in separate modules.

5. **Dual Entrypoints**: Supports both HTTP API (FastAPI) and CLI for flexibility.

## Error Handling

- Input validation via Pydantic with clear error messages
- Agent errors are captured in the graph state and surfaced appropriately
- HTTP 422 for validation errors, 500 for agent/processing errors

