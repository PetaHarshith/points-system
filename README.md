### README: Points System API

#### Overview

The **Points System API** is a RESTful web application designed to track and manage points for users across different payers. The application allows adding points, spending points according to specific rules, and retrieving the current balance of points for each payer. Built with Flask, Python, and MongoDB, this API is lightweight, scalable, and easy to extend.

---

#### Features

1. **Add Points**: Add points for a specific payer at a given timestamp.
2. **Spend Points**: Spend points using a "first-in, first-out" policy while ensuring no payer's balance goes negative.
3. **Get Balances**: Retrieve the current point balance grouped by payer.

---

#### Technology Stack

- **Flask**: Framework for building the RESTful API.
- **Python**: Handles business logic and validation.
- **MongoDB**: Stores transactions in a dynamic, JSON-like format for flexibility.
- **pymongo**: Integrates MongoDB with Python for data operations.

---

#### Installation

1. **Clone the Repository**:

    ```bash
    git clone <repository-url>
    cd <repository-folder>
    ```

2. **Set Up a Virtual Environment**:

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install Dependencies**:

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the Application**:

    ```bash
    python app.py
    ```

The application will be available at `http://127.0.0.1:8000/`.

---

#### API Endpoints

1. **Root Endpoint**:

    - URL: `/`
    - Method: `GET`
    - Description: Verifies the API is running.
    - Response:

        ```json
        {"message": "Welcome to the Points System API! Ready to track your points"}
        ```

2. **Add Points**:

    - URL: `/add`
    - Method: `POST`
    - Payload:

        ```json
        {
          "payer": "DANNON",
          "points": 5000,
          "timestamp": "2020-11-02T14:00:00Z"
        }
        ```

    - Response:
        - Success: `Transaction added successfully.`
        - Error: Validation error messages with status `400`.
3. **Spend Points**:

    - URL: `/spend`
    - Method: `POST`
    - Payload:

        ```json
        {"points": 5000}
        ```

    - Response:

        ```json
        [
          {"payer": "DANNON", "points": -100},
          {"payer": "UNILEVER", "points": -200}
        ]
        ```

4. **Get Balances**:

    - URL: `/balance`
    - Method: `GET`
    - Response:

        ```json
        {
          "DANNON": 1000,
          "UNILEVER": 0,
          "MILLER COORS": 5300
        }
        ```

---
### Database Inspection
To inspect the database and verify stored transactions, you can use **MongoDB Compass**:

1. **Download and Install MongoDB Compass**:
   - [Download MongoDB Compass](https://www.mongodb.com/try/download/compass).

2. **Connect to MongoDB**:
   - Open MongoDB Compass and connect to the local database using the connection string:  
     ```
     mongodb://localhost:27017/
     ```

3. **Navigate to the Database**:
   - Select the `points_system` database and the `transactions` collection to view, update, or delete data manually.

4. **Verify Data**:
   - Check that transactions are added correctly when you test the `/add` endpoint.
   - Confirm that points are deducted as expected when testing the `/spend` endpoint.

Using MongoDB Compass makes it easier to debug and understand how the API interacts with the database.
---

#### Running Tests

1. **Test `/add` Endpoint**:

    - File: `test_add_endpoint.py`
    - Run:

        ```bash
        python test_add_endpoint.py
        ```

    - Tests adding valid and invalid transactions.
2. **Test `/spend` Endpoint**:

    - File: `test_spend_endpoint.py`
    - Run:

        ```bash
        python test_spend_endpoint.py
        ```

    - Tests various spending scenarios, including edge cases.

---

#### Example Workflow

#### **Add Transactions**

Simulate the `add_sample_transactions()` function by sending the sample transactions:

```bash
curl -X POST http://localhost:8000/add \
-H "Content-Type: application/json" \
-d '{"payer": "DANNON", "points": 300, "timestamp": "2022-10-31T10:00:00Z"}'

curl -X POST http://localhost:8000/add \
-H "Content-Type: application/json" \
-d '{"payer": "UNILEVER", "points": 200, "timestamp": "2022-10-31T11:00:00Z"}'

curl -X POST http://localhost:8000/add \
-H "Content-Type: application/json" \
-d '{"payer": "MILLER COORS", "points": 10000, "timestamp": "2022-11-01T14:00:00Z"}'

curl -X POST http://localhost:8000/add \
-H "Content-Type: application/json" \
-d '{"payer": "DANNON", "points": 1000, "timestamp": "2022-11-02T14:00:00Z"}'
```

---

#### **Test Spending Points**

Run curl commands for various scenarios to test the `/spend` endpoint:

Make sure the database is empty.

1. **Spend 5000 Points**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 5000}'
    ```

2. **Spend More Points Than Available (20000 Points)**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 20000}'
    ```

3. **Spend a Small Valid Amount (100 Points)**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 100}'
    ```

4. **Spend All Available Points (10500 Points)**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 10500}'
    ```

5. **Spend Zero Points**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 0}'
    ```

6. **Spend Negative Points (Invalid Input)**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": -100}'
    ```

7. **Spend 6300 Points**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 6300}'
    ```

8. **Spend With Missing `Points` Field**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{}'
    ```

9. **Spend 100 Points**:

    ```bash
    curl -X POST http://localhost:8000/spend \
    -H "Content-Type: application/json" \
    -d '{"points": 100}'
    ```

#### **Check Balances**

After each test, use this command to verify the current balances:

```bash
curl -X GET http://localhost:8000/balance
```

------------------------------------------------------------------------

#### Dependencies

The project requires the following Python libraries:

- Flask==2.1.3
- pymongo==4.4.1

Install them using `pip install -r requirements.txt`.

---
