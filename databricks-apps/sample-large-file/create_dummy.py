#create a big.json file that larget than 10 mb
import json

data = [{"id": i, "text": "dummy text"} for i in range(500000)] # 18mb
with open("big.json", "w") as f:
    json.dump(data, f)
