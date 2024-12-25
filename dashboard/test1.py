from pymongo import MongoClient

client = MongoClient("mongodb+srv://vaishuvadla2000:f3LJEpKo4TDKY9JB@cluster0.3k5sy.mongodb.net/upi_transactions?retryWrites=true&w=majority&appName=Cluster0")
db = client['upi_transactions']
transactions_collection = db['transactions']

# Check if MongoDB connection works
print(transactions_collection.find_one())
