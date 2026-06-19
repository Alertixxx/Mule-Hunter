import json
from inference_service import app
import os

contract_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "contracts", "ai-service-api.json")

print("Generating OpenAPI Contract...")
schema = app.openapi()

with open(contract_path, "w") as f:
    json.dump(schema, f, indent=2)

print(f"SUCCESS! API Contract saved to: {contract_path}")