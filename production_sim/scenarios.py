import random
from typing import List, Dict, Any
from click import prompt
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from production_sim import helper

class ScenarioManager:
    def __init__(self, model_name="gpt-4o-mini"):
        # נשתמש במודל קטן ומהיר לייצור הוריאציות
        self.llm = ChatOpenAI(model=model_name, temperature=0.8)
        self.scenarios: List[Dict[str, Any]] = [
            {
                "id": "legacy_token",
                "name": "Token Validation vs Legacy",
                "dev_requirement": ("Add a security Token validation middleware to all API calls."),
                "prod_issue": (
                    "💥 CRITICAL INCIDENT: Legacy Reporting System cannot authenticate!\n"
                    "❌ The CEO and other legacy users are reporting 401 Unauthorized errors."
                ),
                "required_fix_concept": "backward_compatibility",
                "validation_criteria": (
                    "Middleware must enforce token validation but allow exceptions for legacy clients."
                ),
                "requirements": [
                    "validate_authorization_header",
                    "exclude_legacy_clients",
                    "return_401_on_missing_token"
                ],
                "risk_level": "high"
            },
            {
                "id": "db_lock",
                "name": "Online Migration",
                "dev_requirement": ("Add a 'last_login' column to the 'Users' table."),
                "prod_issue": (
                    "💥 OUTAGE ALERT: Users cannot log in!\n"
                    "❌ The database is unresponsive because the 'Users' table was locked."
                ),
                "required_fix_concept": "online_migration",
                "validation_criteria": (
                    "Migration must use batching or non-blocking syntax to avoid downtime."
                ),
                "requirements": [
                    "add_column_last_login",
                    "batch_updates_or_nonblocking",
                    "preserve_user_access"
                ],
                "risk_level": "high"
            },
            {
                "id": "rate_limit",
                "name": "Global Weather Integration",
                "dev_requirement": (
                    "Implement a service called 'WeatherProvider' with a function 'fetch_city_stats(city_id)'. "
                    "The function must call the external 'OpenSky_Weather_API' to get live temperature for each member on the landing page."
                ),
                "prod_issue": (
                    "💥 SERVICE UNAVAILABLE: 'OpenSky_Weather_API' returned Error 429 (Too Many Requests).\n"
                    "❌ Our system is attempting 50,000 calls per minute, causing a global IP ban."
                ),
                "required_fix_concept": "caching",
                "validation_criteria": (
                    "Introduce a caching layer (using a dictionary or Redis) within 'WeatherProvider' "
                    "to ensure 'OpenSky_Weather_API' is only called once per city."
                ),
                "requirements": [
                    "implement_weather_provider_class",
                    "integrate_opensky_api_call",
                    "add_caching_logic_with_expiry"
                ],
                "risk_level": "medium"
            }
        ]

    def get_dynamic_scenario(self, student_id: str = "gen_user") -> Dict[str, Any]:
        """
        Generates a student-specific variation of a base scenario[cite: 102].
        """
        random.seed(student_id) # Ensure deterministic scenario selection
        base = random.choice(self.scenarios)
        
        # Call the helper to get the obfuscated signature
        signature = helper.get_id_signature(student_id)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", f"""
            You are a Scenario Refiner for a coding simulator. 
            Your goal is to apply 'Skinning' to a BASE SCENARIO using the Student Signature: {signature}

            STRICT RULES:
            1. **Immutable Fields**: DO NOT change 'id', 'required_fix_concept', or 'risk_level'.
            2. **Signature Mandate**: You MUST append '_{signature}' to EVERY renamed entity (Tables, Columns, APIs).
            3. **Requirements Sync**: You MUST update the strings inside the 'requirements' list to match your new renamed entities, including the signature. 
            (e.g., 'add_column_last_login' -> 'add_column_member_login_{signature}').
            4. **Entity Variation**: Change Table names, Column names, External API names, and User roles to provide a unique context.
            5. **Technical Integrity**: 'dev_requirement' and 'prod_issue' must describe the EXACT SAME technical failure as the base, using your new naming convention.
            6. **Output**: Return ONLY a JSON object with the exact same keys as the base.
            """),
            ("human", "Base Scenario: {base}")
        ])
        try:
            chain = prompt | self.llm | JsonOutputParser()
            dynamic_scenario = chain.invoke({"base": base, "student_id": student_id})

            if not dynamic_scenario or "id" not in dynamic_scenario:
                return base
            
            dynamic_scenario["id"] = base["id"]
            dynamic_scenario["required_fix_concept"] = base["required_fix_concept"]
            dynamic_scenario["risk_level"] = base["risk_level"]
            
            #print(f"🎲 Generated scenario for {student_id}: {dynamic_scenario}")
            return dynamic_scenario
        
        except Exception as e:
            print(f"⚠️ Warning: Dynamic generation failed ({e}). Using base scenario.")
            return base
    

    def get_random_scenario(self) -> Dict[str, Any]:
        """Return a random scenario"""
        return self.scenarios[1]
        return random.choice(self.scenarios)

