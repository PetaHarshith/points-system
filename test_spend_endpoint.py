import requests

BASE_URL = "http://localhost:8000"


def add_sample_transactions():
    """
    Adds sample transactions to the system.
    """
    print("Adding sample transactions...")
    sample_transactions = [
        {"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"},
        {"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"},
        {"payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"},
        {"payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"},
    ]

    for transaction in sample_transactions:
        response = requests.post(f"{BASE_URL}/add", json=transaction)
        if response.status_code != 200:
            print(f"Failed to add transaction: {transaction}")
            print(f"Response: {response.text}")
            return False

    print("Sample transactions added successfully!")
    return True


def test_spend_points():
    """
    Test the /spend endpoint with various scenarios.
    """
    print("\nTesting /spend Endpoint\n")

    # Add sample transactions
    if not add_sample_transactions():
        return

    # Define test cases
    test_cases = [
        {
            "description": "Spend 5000 points",
            "data": {"points": 5000},
            "expected_status": 200,
        },
        {
            "description": "Spend more points than available (20000 points)",
            "data": {"points": 20000},
            "expected_status": 400,
        },
        {
            "description": "Spend a small valid amount (100 points)",
            "data": {"points": 100},
            "expected_status": 200,
        },
        {
            "description": "Spend all available points (10500 points)",
            "data": {"points": 10500},
            "expected_status": 200,
        },
        {
            "description": "Spend zero points",
            "data": {"points": 0},
            "expected_status": 200,
        },
        {
            "description": "Spend negative points (invalid input)",
            "data": {"points": -100},
            "expected_status": 400,
        },
        {
            "description": "Spend 6300 points",
            "data": {"points": 6300},
            "expected_status": 200,
        },
        {
            "description": "Spend with missing 'points' field (invalid input)",
            "data": {},
            "expected_status": 400,
        },
        {
            "description": "Spend 100 points",
            "data": {"points": 100},
            "expected_status": 200,
        },
    ]

    # Run test cases
    for idx, test_case in enumerate(test_cases):
        print(f"\nTest Case {idx + 1}: {test_case['description']}")
        response = requests.post(f"{BASE_URL}/spend", json=test_case["data"])

        # Check response status
        if response.status_code == test_case["expected_status"]:
            print(f"Status: {response.status_code} (Expected)")
        else:
            print(f"Status: {response.status_code} (Unexpected)")
            print(f"Response: {response.text}")
            continue

        # Print response body for successful cases
        if response.status_code == 200:
            print("Response:")
            print(response.text)  # Handle plain text response


if __name__ == "__main__":
    test_spend_points()
