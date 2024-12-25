import pandas as pd
from sklearn.cluster import KMeans
import numpy as np

def get_savings_suggestions(transactions):
    # Sample logic to calculate savings suggestions
    suggestions = {}
    grouped = transactions.groupby('payee_type')['amount'].sum()
    for category, amount in grouped.items():
        if amount > 1000:  # Example threshold
            suggestions[category] = amount * 0.1  # Suggest 10% savings
    return suggestions

def compare_spending(transactions):
    # Group by month and sum the 'amount'
    monthly = transactions.groupby(transactions['date'].dt.to_period('M'))['amount'].sum().reset_index()

    # Convert the 'date' (which is now a period) to a string without using strftime
    monthly['date'] = monthly['date'].astype(str)

    return monthly.to_dict(orient='records')


def cash_flow_analysis(transactions):
    inflows = transactions[transactions['amount'] > 0]['amount'].sum()
    outflows = transactions[transactions['amount'] < 0]['amount'].sum()
    return inflows, abs(outflows)

def detect_outliers(transactions):
    # Example outlier detection logic
    q1 = transactions['amount'].quantile(0.25)
    q3 = transactions['amount'].quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    return transactions[(transactions['amount'] < lower_bound) | (transactions['amount'] > upper_bound)]

def spending_alerts(transactions):
    alerts = []
    high_spenders = transactions.groupby('payee_type')['amount'].sum().nlargest(3)
    for category, amount in high_spenders.items():
        alerts.append(f"High spending detected in {category}: {amount}")
    return alerts

def cluster_spending_behavior(transactions, n_clusters=2):
    """
    Perform K-Means clustering to identify spending behavior.
    
    Parameters:
        transactions: DataFrame containing transaction data.
        n_clusters: Number of clusters to form (default is 2).
        
    Returns:
        A DataFrame with spending clusters for each payee_type.
    """
    # Group by 'payee_type' and compute the total amount spent and transaction frequency
    grouped = transactions.groupby('payee_type').agg({
        'amount': 'sum',  # Total spending
        'transaction_id': 'count'  # Frequency of transactions
    }).rename(columns={'transaction_id': 'frequency'}).reset_index()

    # Feature scaling (Optional: KMeans can perform better if data is scaled)
    # grouped['amount_scaled'] = (grouped['amount'] - grouped['amount'].mean()) / grouped['amount'].std()
    # grouped['frequency_scaled'] = (grouped['frequency'] - grouped['frequency'].mean()) / grouped['frequency'].std()

    # Prepare features for clustering
    X = grouped[['amount', 'frequency']].values
    
    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42)
    grouped['cluster'] = kmeans.fit_predict(X)
    
    # Interpret clusters (optional: you can add meaningful names to the clusters)
    # For example: cluster 0 -> Low-frequency high-spenders, cluster 1 -> High-frequency low-spenders
    grouped['cluster_label'] = np.where(grouped['cluster'] == 0, 'Low-frequency high-spenders', 'High-frequency low-spenders')

    return grouped

