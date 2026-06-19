from pymongo import MongoClient

client = MongoClient("mongodb+srv://prisha:Prisha123@cluster0.pjwljsk.mongodb.net/test")
db = client['test']
txs = db.transactions.find().limit(5)
for tx in txs:
    print(f"TX {tx.get('_id')}: risk_score={tx.get('riskScore')}, gnn={tx.get('gnnScore')}, eif={tx.get('unsupervisedScore')}")
