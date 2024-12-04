import requests

# Base URL for the API
url = "http://127.0.0.1:8000/add"

# Define test cases for the "/add" endpoint
test_cases = [
    {
        "payload": {
            "payer": "DANNON",
            "points": 5000,
            "timestamp": "2020-11-02T14:00:00Z",
        },
        "description": "Valid request - Adding points for DANNON",
    },
    {
        "payload": {
            "payer": "DANNON",
            "points": -500,
            "timestamp": "2020-11-02T14:00:00Z",
        },
        "description": "Invalid request - Negative points are not allowed",
    },
    {
        "payload": {"payer": "DANNON", "points": 5000},
        "description": "Invalid request - Missing timestamp field",
    },
    {
        "payload": {
            "payer": 123,
            "points": 5000,
            "timestamp": "2020-11-02T14:00:00Z",
        },
        "description": "Invalid request - Payer field must be a non-empty string",
    },
    {
        "payload": {
            "payer": "UNILEVER",
            "points": 3000,
            "timestamp": "2022-01-01T10:00:00Z",
        },
        "description": "Valid request - Adding points for UNILEVER",
    },
    {
        "payload": {},
        "description": "Invalid request - Empty request body",
    },
    {
        "payload": {
            "payer": "MILLER COORS",
            "points": "5000",
            "timestamp": "2022-01-01T10:00:00Z",
        },
        "description": "Invalid request - Points must be an integer",
    },
]

# Testing each case
for case in test_cases:
    print(f"Testing: {case['description']}")
    response = requests.post(url, json=case["payload"])
    print(f"Status Code: {response.status_code}")

    if response.headers.get("Content-Type") == "application/json":
        print(f"Response: {response.json()}\n")
    else:
        print(f"Response: {response.text.strip()}\n")
