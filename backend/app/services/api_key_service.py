from typing import Optional, Dict


API_KEYS = {
    "free_key_123": {
        "name": "Free Demo Client",
        "plan": "free",
        "capacity": 5,
        "refill_rate": 1
    },
    "pro_key_456": {
        "name": "Pro Demo Client",
        "plan": "pro",
        "capacity": 20,
        "refill_rate": 5
    }
}


def get_api_key_details(api_key: str) -> Optional[Dict]:
    return API_KEYS.get(api_key)