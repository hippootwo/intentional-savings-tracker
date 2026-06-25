import firebase_admin
from firebase_admin import firestore
import json

firebase_admin.initialize_app(options={'projectId': 'intentional-tracker-tito'})

db = firestore.client()

print("=== LAST 2 TRANSACTIONS ===")
try:
    docs = db.collection('transactions').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(2).stream()
    found = False
    for doc in docs:
        found = True
        print(f"ID: {doc.id}")
        print(json.dumps(doc.to_dict(), indent=2, default=str))
        print("-" * 20)
    
    if not found:
        print("No transactions found.")
except Exception as e:
    print(f"Error fetching transactions: {e}")
