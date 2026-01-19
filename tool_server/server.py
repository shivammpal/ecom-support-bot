from fastapi import FastAPI, Query
import json

app = FastAPI()

# -------- LOAD PRODUCTS --------
with open("products.json", "r", encoding="utf-8") as f:
    PRODUCTS = json.load(f)

# -------- LOAD POLICIES --------
with open("policies.json", "r", encoding="utf-8") as f:
    POLICIES = json.load(f)

# -------- TEST TOOL --------
@app.get("/tools/ping")
def ping():
    return {"message": "Tool server is working!"}


# -------- SEARCH PRODUCTS --------
@app.get("/tools/search-product")
def search_product(q: str = Query(..., description="Search keyword")):
    q = q.lower()
    results = []

    for p in PRODUCTS:
        if q in p["name"].lower():
            results.append({
                "id": p["id"],
                "name": p["name"],
                "price": p["price"],
                "stock": p["stock"]
            })

    return {"results": results}


# -------- GET PRODUCT DETAILS --------
@app.get("/tools/get-product")
def get_product(product_id: str):
    for p in PRODUCTS:
        if p["id"] == product_id:
            return p

    return {"error": "Product not found"}

# -------- GET POLICY --------
@app.get("/tools/get-policy")
def get_policy(topic: str):
    topic = topic.lower()
    if topic in POLICIES:
        return {"topic": topic, "text": POLICIES[topic]}
    return {"error": "Policy not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3333)
