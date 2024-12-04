from collections import defaultdict
from datetime import datetime

from flask import Flask, jsonify, request
from pymongo import MongoClient, UpdateOne

# initializing the flask app
app = Flask(__name__)

# setting up the mongoDB client and database.
mongodb_client = MongoClient("mongodb://localhost:27017/")
database = mongodb_client["points_system"]
transactions = database["transactions"]


# Root endpoint
@app.route("/", methods=["GET"])
def welcome():
    """
    This is the root endpoint. It provides a friendly message about the Points system API.
    Returns a JSON response with a message and a status code of 200.
    This also acts like a test to check if the backend is connected and running correctly.
    """
    return (
        jsonify(
            {"message": "Welcome to the Points System API! Ready to track your points"}
        ),
        200,
    )


# Endpoint for adding points.
@app.route("/add", methods=["POST"])
def add_points():
    """
    Handles the addition of points to a payer's account.

    This method processes a POST request containing the payer's name, points to be added
    and the transaction timestamp. It validates the input and then stores the transaction
    in the database for future reference.
    """
    try:
        # Parse the incoming JSON data from the request body.
        data = request.json

        # Check if the request body is empty or invalid.
        if not data:
            return "Invalid JSON input or empty request body.\n", 400

        if "payer" not in data or "points" not in data or "timestamp" not in data:
            return "Missing required fields: 'payer', 'points', 'timestamp'.\n", 400

        # Extract the individual fields from the JSON payload.
        payer = data.get("payer")
        points = data.get("points")
        timestamp = data.get("timestamp")

        # Validate the 'payer' field
        if not isinstance(payer, str) or not payer.strip():
            return "Invalid 'payer': It must be a non-empty string.\n", 400

        # Validate the 'points' field
        if not isinstance(points, int) or points < 0:
            return "Invalid 'points': must be an integer 0 or greater.\n", 400

        # Validate and parse the 'timestamp' field
        try:
            # Convert the timestamp string to a datetime object
            timestamp = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except ValueError:
            # Error if the timestamp is not valid.
            return (
                "Invalid 'timestamp': must be a valid ISO 8601 date-time string.\n",
                400,
            )

        # Construct the transaction record to insert into the database
        transaction = {"payer": payer.strip(), "points": points, "timestamp": timestamp}

        # Insert the transaction into the MongoDB collection
        transactions.insert_one(transaction)

        return "Transaction added successfully.\n", 200

    except Exception as e:
        return f"Unexpected error: {str(e)}\n", 500  # Handle any unexpected errors


@app.route("/spend", methods=["POST"])
def spend_points():
    """
    Handles the spending of points from a user's account.

    This method processes a POST request to deduct points using the oldest transactions first.
    It ensures no payer's balance goes negative and updates the database accordingly.
    """
    try:
        data = request.json

        # Validate that the request contains the 'points' key and is not empty
        if not data or "points" not in data:
            return "Missing 'points' in request body.\n", 400

        points_to_spend = data["points"]
        if not isinstance(points_to_spend, int) or points_to_spend < 0:
            return "Points to spend must be a non-negative integer.\n", 400

        # Handle the case where points_to_spend is 0
        if points_to_spend == 0:
            return jsonify([]), 200

        # Fetch transactions from the database, sorted by timestamp to prioritize oldest points first
        sorted_transactions = list(transactions.find().sort("timestamp", 1))
        if not sorted_transactions:
            return "No transactions available to spend points.\n", 400

        # calculating the total points available from all transactions
        total_points = sum(transaction["points"] for transaction in sorted_transactions)
        if points_to_spend > total_points:
            return "Not enough points to spend.\n", 400

        # Aggregate points by payer to check current balances
        payer_balances = defaultdict(int)
        for transaction in sorted_transactions:
            payer_balances[transaction["payer"]] += transaction["points"]

        # Check if any payer's balance is negative before processing
        if any(balance < 0 for balance in payer_balances.values()):
            return "Payer balances cannot go negative.\n", 400

        deductions = []
        remaining_points = points_to_spend
        bulk_updates = []

        for transaction in sorted_transactions:
            if remaining_points <= 0:  # Stop if all points have been spent
                break

            payer = transaction["payer"]
            transaction_points = transaction["points"]

            if transaction_points <= 0:
                continue

            # Deduct points from the current transaction, minimizing remaining points
            points_to_deduct = min(transaction_points, remaining_points)
            remaining_points -= points_to_deduct

            deductions.append({"payer": payer, "points": -points_to_deduct})

            # Prepare a bulk update to reduce points in the database
            bulk_updates.append(
                UpdateOne(
                    {"_id": transaction["_id"]},
                    {"$set": {"points": transaction_points - points_to_deduct}},
                )
            )

        # Execute the bulk updates in a single database operation for efficiency
        if bulk_updates:
            transactions.bulk_write(bulk_updates)

        if remaining_points > 0:
            return (
                f"Points to spend exceeded available points. Remaining: {remaining_points}\n",
                500,
            )

        aggregated_deductions = defaultdict(int)
        for deduction in deductions:
            aggregated_deductions[deduction["payer"]] += deduction["points"]

        result = (
            "\n".join(
                [
                    f"{payer}: {points}"
                    for payer, points in aggregated_deductions.items()
                ]
            )
            + "\n"
        )  # Append a newline to the result

        return result, 200

    except pymongo.errors.BulkWriteError as bwe:
        return f"Database write error: {bwe.details}\n", 500
    except Exception as e:
        return f"Unexpected error: {str(e)}\n", 500


@app.route("/balance", methods=["GET"])
def get_balance():
    """
    Retrieves the current point balances for each payer.

    This method processes a GET request to calculate and return the total points available
    per payer, aggregated from all transactions in the database.
    """
    try:
        # MongoDB aggregation pipeline to calculate the total points per payer
        pipeline = [
            {"$match": {"payer": {"$exists": True}, "points": {"$exists": True}}},
            {"$group": {"_id": {"$toUpper": "$payer"}, "points": {"$sum": "$points"}}},
        ]

        # Execute the aggregation pipeline to get balances
        aggregated_result = transactions.aggregate(pipeline)

        balances = {doc["_id"]: doc["points"] for doc in aggregated_result}

        # Return the aggregated balances as a JSON response with HTTP status 200
        return jsonify(balances), 200
    except Exception as e:
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500


if __name__ == "__main__":
    # This ensures that the Flask app runs only when the script is executed directly
    # and not when it is imported as a module in another script.
    app.run(port=8000, debug=True)
    # app.run(): Starts the Flask development server.
    # port=8000: Specifies that the server will listen on port 8000.
    # debug=True: Enables debug mode, allowing for detailed error messages
    # and automatic server reloads when code changes are detected (useful for development).
