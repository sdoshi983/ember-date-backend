#!/usr/bin/env python3
"""CLI entrypoint for onboarding analysis."""

import json
import sys

from dotenv import load_dotenv
from pydantic import ValidationError

# Load .env before importing app modules
load_dotenv()

from app.config import get_settings
from app.schemas import OnboardingInput
from app.services.analysis import analyze_response


def main():
    """Run analysis from command line with JSON input."""
    # Validate settings
    try:
        get_settings()
    except Exception as e:
        print(f"Error: Configuration error - {e}", file=sys.stderr)
        sys.exit(1)
    
    # Read JSON from file argument or stdin
    if len(sys.argv) > 1:
        try:
            with open(sys.argv[1], 'r') as f:
                input_json = json.load(f)
        except FileNotFoundError:
            print(f"Error: File not found: {sys.argv[1]}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in file: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        try:
            input_json = json.load(sys.stdin)
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON input: {e}", file=sys.stderr)
            sys.exit(1)
    
    # Validate input
    try:
        input_data = OnboardingInput(**input_json)
    except ValidationError as e:
        print(f"Error: Invalid input: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Run analysis
    try:
        result = analyze_response(input_data)
        print(result.model_dump_json(indent=2))
    except Exception as e:
        print(f"Error: Analysis failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()

