import random

class ScenarioManager:
    def __init__(self):
        self.scenarios = [
            {
                "id": "legacy_token",
                "name": "Token Validation vs Legacy",
                "dev_requirement": "Task: Add a security Token validation middleware to all API calls. If an 'Authorization' header is missing, return 401 Unauthorized.",
                "prod_issue": "CRITICAL INCIDENT: The Legacy Reporting System has crashed! It sends requests without headers. The CEO cannot view reports.",
                "required_fix_concept": "backward_compatibility",
                "validation_criteria": "The code must include an exclusion logic or a bypass (e.g., checking for a specific User-Agent or IP) that allows legacy requests to pass without a token."
            },
            {
                "id": "db_lock",
                "name": "Migration Lock",
                "dev_requirement": "Task: Write a script to add a 'last_login' column to the 'Users' table.",
                "prod_issue": "OUTAGE ALERT: The database is unresponsive! Your script locked the entire 'Users' table (10M rows). No one can log in.",
                "required_fix_concept": "online_migration",
                "validation_criteria": "The solution should avoid a full table lock. This can be done by using batching (updating in chunks) or database-specific non-blocking syntax (like 'ALGORITHM=INPLACE' or 'CONCURRENTLY')."
            },
            {
                "id": "rate_limit",
                "name": "Third Party Burst",
                "dev_requirement": "Task: Implement a function that fetches weather data from 'WeatherAPI' for every user on the homepage.",
                "prod_issue": "BLOCKED: 'WeatherAPI' has blocked our IP! We sent 50k requests in 1 minute.",
                "required_fix_concept": "caching",
                "validation_criteria": "The code must implement a caching mechanism (e.g., a dictionary, Redis, or lru_cache) that checks for existing data before making the external API call."
            }
        ]

    def get_random_scenario(self) -> dict:
        """Selects a random scenario for the student"""
        return self.scenarios[1]
        # return random.choice(self.scenarios)