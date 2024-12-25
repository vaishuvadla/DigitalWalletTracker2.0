from pymongo import MongoClient
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

def get_spending_forecast():
    # MongoDB connection
    client = MongoClient('mongodb+srv://vaishuvadla2000:f3LJEpKo4TDKY9JB@cluster0.3k5sy.mongodb.net/upi_transactions?retryWrites=true&w=majority&appName=Cluster0')
    db = client['upi_transactions']
    credit_collection = db['credit_transactions']
    debit_collection = db['debit_transactions']

    # Fetch data from collections
    credit_data = list(credit_collection.find())
    debit_data = list(debit_collection.find())

    # Convert to DataFrames
    credit_df = pd.DataFrame(credit_data)
    debit_df = pd.DataFrame(debit_data)

    # Combine data
    all_transactions = pd.concat([credit_df, debit_df])
    all_transactions['date'] = pd.to_datetime(all_transactions['date'])
    all_transactions['amount'] = pd.to_numeric(all_transactions['amount'])

    # Group by month and sum amounts
    monthly_spending = all_transactions.groupby(all_transactions['date'].dt.to_period('M')).sum().reset_index()
    monthly_spending['date'] = monthly_spending['date'].dt.to_timestamp()

    # Prepare data for linear regression
    X = np.array(range(len(monthly_spending))).reshape(-1, 1)  # Months as feature
    y = monthly_spending['amount'].values  # Spending amounts

    model = LinearRegression()
    model.fit(X, y)

    # Predict future spending for the next 3 months
    future_months = np.array(range(len(monthly_spending), len(monthly_spending) + 3)).reshape(-1, 1)
    predictions = model.predict(future_months)

    # Prepare the forecasted data
    predicted_dates = pd.date_range(start=monthly_spending['date'].iloc[-1] + pd.DateOffset(months=1), periods=3, freq='M')
    forecast_df = pd.DataFrame({'date': predicted_dates, 'predicted_amount': predictions})

    # Combine actual and forecasted data
    combined_df = pd.concat([monthly_spending[['date', 'amount']], forecast_df], ignore_index=True)

    return combined_df.to_dict(orient='records')
