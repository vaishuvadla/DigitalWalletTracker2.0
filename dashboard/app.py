from flask import Flask, render_template, request, redirect, jsonify, url_for
from pymongo import MongoClient
from financial_analysis import (get_savings_suggestions, compare_spending, cash_flow_analysis,
                                detect_outliers, spending_alerts)
import pandas as pd
from datetime import datetime
from bson import ObjectId

app = Flask(__name__, static_folder='static')

# MongoDB connection setup
from urllib.parse import quote_plus

username = quote_plus("vaishu")
password = quote_plus("123@456")
uri = f"mongodb+srv://{username}:{password}@cluster0.lu2ug.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"

try:
    client = MongoClient(uri)
    db = client['UPI_Transactions']
except Exception as e:
    print("Could not connect to MongoDB:", e)


# Collections for Credit and Debit transactions
credit_collection = db['credit_transactions']
debit_collection = db['debit_transactions']

# Helper function to convert ObjectIds to strings
def convert_object_id(data):
    if isinstance(data, list):
        return [convert_object_id(item) for item in data]
    elif isinstance(data, dict):
        return {key: convert_object_id(value) for key, value in data.items()}
    elif isinstance(data, ObjectId):
        return str(data)
    else:
        return data

# Route for the form page
@app.route('/')
def form():
    return render_template('form.html')

# Route for form submission
@app.route('/submit', methods=['POST'])
def submit_transaction():
    try:
        # Get form data
        name = request.form['name']
        transaction_id = request.form['transaction_id']
        date_str = request.form['date']
        time_str = request.form['time']
        amount = float(request.form['amount'])
        payment_type = request.form['payment_type']  # Credit or Debit
        payee_type = request.form['payee_type']
        personal_reference = request.form.get('personal_reference', None)
        transaction_rating = request.form['transaction_rating']

        # Validate required fields
        if not name or not transaction_id or amount <= 0:
            return "Missing required fields or invalid amount", 400

        # Combine date and time
        date = datetime.strptime(f"{date_str} {time_str}", '%Y-%m-%d %H:%M')

        # Prepare the transaction data
        transaction_data = {
            'name': name,
            'transaction_id': transaction_id,
            'date': date,
            'amount': amount,
            'payee_type': payee_type,
            'personal_reference': personal_reference,
            'transaction_rating': transaction_rating
        }

        # Insert transaction into the respective collection based on payment type
        if payment_type == 'Credited':
            credit_collection.insert_one(transaction_data)
        else:
            debit_collection.insert_one(transaction_data)

        return redirect(url_for('dashboard'))

    except Exception as e:
        return str(e), 500

# Route for the dashboard page (renders the HTML)
@app.route('/dashboard')
def dashboard():
    # Just render the HTML template for the dashboard
    return render_template('dashboard.html')

# Route to provide JSON data for the dashboard
@app.route('/dashboard-data')
def dashboard_data():
    credit_transactions = list(credit_collection.find())
    debit_transactions = list(debit_collection.find())

    credit_df = pd.DataFrame(credit_transactions)
    debit_df = pd.DataFrame(debit_transactions)

    # Convert ObjectId to string to avoid serialization issues
    credit_df['_id'] = credit_df['_id'].apply(str)
    debit_df['_id'] = debit_df['_id'].apply(str)

    # Convert 'date' columns to datetime and coerce errors
    credit_df['date'] = pd.to_datetime(credit_df['date'], infer_datetime_format=True, errors='coerce')
    debit_df['date'] = pd.to_datetime(debit_df['date'], infer_datetime_format=True, errors='coerce')

    all_transactions = pd.concat([credit_df, debit_df], ignore_index=True)
    all_transactions['date'] = pd.to_datetime(all_transactions['date'], infer_datetime_format=True, errors='coerce')

    # Perform financial analysis
    savings_suggestions = get_savings_suggestions(all_transactions)
    monthly_comparison = compare_spending(all_transactions)
    inflows, outflows = cash_flow_analysis(all_transactions)
    outliers = detect_outliers(all_transactions)
    alerts = spending_alerts(all_transactions)

    # Convert the DataFrames to JSON-compatible data structures
    credit_chart_data = {
        'dates': credit_df['date'].dt.strftime('%Y-%m-%d').tolist(),
        'amounts': credit_df['amount'].tolist()
    }
    debit_chart_data = {
        'dates': debit_df['date'].dt.strftime('%Y-%m-%d').tolist(),
        'amounts': debit_df['amount'].tolist()
    }

    # Convert the outliers DataFrame to a list of dictionaries
    outliers_list = outliers.to_dict(orient='records')

    # Dashboard data to send to the frontend
    dashboard_data = {
        'monthly_comparison': monthly_comparison,
        'savings_suggestions': savings_suggestions,
        'inflows': inflows,
        'outflows': outflows,
        'outliers': outliers_list,
        'alerts': alerts,
        'credit_chart_data': credit_chart_data,
        'debit_chart_data': debit_chart_data
    }

    # Ensure ObjectId fields are converted to strings before sending JSON
    return jsonify(convert_object_id(dashboard_data))

# Main entry point
if __name__ == '__main__':
    app.run(debug=True)