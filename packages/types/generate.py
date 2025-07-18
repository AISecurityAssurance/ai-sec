#!/usr/bin/env python3
"""
Generate TypeScript types from Pydantic models
This will be used once we have the backend models defined
"""

import os
import sys

def generate_typescript_defs():
    """
    Generate TypeScript definitions from Pydantic models
    """
    # Check if the backend models exist
    backend_models_path = "../../apps/backend/core/models.py"
    
    if not os.path.exists(backend_models_path):
        print("Backend models not found. Skipping type generation.")
        return
    
    try:
        from pydantic2ts import generate_typescript_defs as pydantic_generate
        
        pydantic_generate(
            backend_models_path,
            "./src/generated/api-types.ts",
            json2ts_cmd="npx json2ts"
        )
        print("TypeScript types generated successfully!")
    except ImportError:
        print("pydantic2ts not installed. Install it with: pip install pydantic-to-typescript")
        sys.exit(1)
    except Exception as e:
        print(f"Error generating types: {e}")
        sys.exit(1)

if __name__ == "__main__":
    generate_typescript_defs()