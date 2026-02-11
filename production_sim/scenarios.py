import random
from typing import List, Dict, Any

class ScenarioManager:
    def __init__(self):
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
                "name": "API Burst Protection",
                "dev_requirement": ("Fetch weather data for all users on the homepage."),
                "prod_issue": (
                    "💥 BLOCKED: Our IP was banned by WeatherAPI!\n"
                    "❌ Too many requests were sent in a short time (50k requests/min)."
                ),
                "required_fix_concept": "caching",
                "validation_criteria": (
                    "Use caching (dict, Redis, or LRU) to avoid repeated calls."
                ),
                "requirements": [
                    "cache_weather_api",
                    "check_existing_data_before_call",
                    "ttl_or_expiration_handling"
                ],
                "risk_level": "medium"
            }
        ]

    def get_random_scenario(self) -> Dict[str, Any]:
        """Return a random scenario"""
        return self.scenarios[1]
        return random.choice(self.scenarios)

    def get_scenario_by_id(self, scenario_id: str) -> Dict[str, Any]:
        """Return scenario by ID"""
        for s in self.scenarios:
            if s["id"] == scenario_id:
                return s
        raise ValueError(f"Scenario {scenario_id} not found")
