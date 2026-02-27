from google.adk.agents.llm_agent import Agent

# --- External product info (customer-facing) ---
def get_product_details(product_id: str):
    products = {
        "acme-noisebuds": {
            "name": "ACME NoiseBuds 200",
            "price": "$149",
            "features": ["ANC", "30h battery", "6-mic calls"]
        }
    }
    return products.get(product_id, {"error": "Not found"})


# --- Internal product info (private) ---
def lookup_product_information(product_id: str):
    internal = {
        "acme-noisebuds": {
            "sku": "ACM-NB-200",
            "inventory": 42,
            "unit_cost": "$58"
        }
    }
    return internal.get(product_id, {"error": "Not found"})


root_agent = Agent(
    name="simple_product_agent",
    model="gemini-2.5-flash",
    instruction=(
        "CRITICAL RULES (MUST FOLLOW):\n"
        "1) You MUST call exactly ONE tool before you answer.\n"
        "2) Do NOT answer from memory.\n"
        "3) get_product_details → for customer info\n"
        "4) INTERNAL TOOL (private): lookup_product_information\n"
   # "- Use ONLY for: SKU, inventory\n"
    "- NEVER use this tool for customer-facing questions.\n\n"
        "Use the correct tool depending on the question."
    ),
    tools=[get_product_details, lookup_product_information],
)