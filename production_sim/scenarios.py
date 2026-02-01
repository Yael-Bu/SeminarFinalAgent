import random

class ScenarioManager:
    def __init__(self):
        self.scenarios = [
            {
                "id": "legacy_token",
                "name": "Token Validation vs Legacy",
                "dev_requirement": "Task: Add a security Token validation middleware to all API calls. If an 'Authorization' header is missing, return 401 Unauthorized.",
                "prod_issue": "CRITICAL INCIDENT: The Legacy Reporting System has crashed! It sends requests without headers, and now it's getting 401 errors. The CEO cannot view reports.",
                "required_fix_concept": "backward_compatibility" # The LLM will look for an exclusion/bypass logic
            },
            {
                "id": "db_lock",
                "name": "Migration Lock",
                "dev_requirement": "Task: Write a script to add a 'last_login' column to the 'Users' table.",
                "prod_issue": "OUTAGE ALERT: The database is unresponsive! Your script locked the entire 'Users' table (10M rows) for writing. No one can log in.",
                "required_fix_concept": "online_migration" # The LLM will look for batching or non-locking syntax
            },
            {
                "id": "rate_limit",
                "name": "Third Party Burst",
                "dev_requirement": "Task: Implement a function that fetches weather data from 'WeatherAPI' for every user on the homepage.",
                "prod_issue": "BLOCKED: 'WeatherAPI' has blocked our IP! We sent 50k requests in 1 minute. We need to reduce calls immediately.",
                "required_fix_concept": "caching" # The LLM will look for Redis/Cache logic
            }
        ]

    def get_random_scenario(self) -> dict:
        """Selects a random scenario for the student"""
        return random.choice(self.scenarios)