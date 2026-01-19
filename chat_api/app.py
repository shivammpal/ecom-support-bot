from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import requests
import json
import google.generativeai as genai

load_dotenv()

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------------- FASTAPI ----------------
app = FastAPI()

class ChatRequest(BaseModel):
    message: str


TOOL_SERVER = "https://ecom-support-bot.onrender.com"

# ---------------- INTENT PROMPT ----------------
INTENT_PROMPT = """
You are an intent classification API for an e-commerce chatbot.

Return ONLY valid JSON. No markdown. No explanation.

Intent must be one of:
product_query
policy_query
general_chat

If product_query, include: keyword
If policy_query, include: topic (one of: return, refund, delivery, warranty, cancellation, exchange, privacy, payment)

JSON format:

{
  "intent": "...",
  "keyword": "...",
  "topic": "..."
}

User message:
"""


@app.post("/chat")
def chat(req: ChatRequest):

    # -------- STEP 1: AI INTENT DETECTION --------
    intent_response = model.generate_content(
        INTENT_PROMPT + req.message,
        generation_config={
            "response_mime_type": "application/json"
        }
    )

    raw = intent_response.text.strip()

    try:
        intent_data = json.loads(raw)
    except Exception:
        return {
            "source": "ai",
            "debug": raw,
            "reply": "Intent detection failed."
        }

    intent = intent_data.get("intent")

    # -------- STEP 2: POLICY TOOL --------
    if intent == "policy_query":
        topic = intent_data.get("topic")

        r = requests.get(
            f"{TOOL_SERVER}/tools/get-policy",
            params={"topic": topic}
        )

        data = r.json()

        if "text" in data:
            return {
                "source": "tool",
                "reply": data["text"]
            }

        return {
            "source": "tool",
            "reply": "Sorry, I couldn't find that policy."
        }

    # -------- STEP 3: PRODUCT TOOL --------
    if intent == "product_query":
        keyword = intent_data.get("keyword", "")

        r = requests.get(
            f"{TOOL_SERVER}/tools/search-product",
            params={"q": keyword}
        )

        results = r.json().get("results", [])

        if not results:
            return {
                "source": "tool",
                "reply": "Sorry, I couldn't find any product matching your query."
            }

        product_id = results[0]["id"]

        d = requests.get(
            f"{TOOL_SERVER}/tools/get-product",
            params={"product_id": product_id}
        )

        p = d.json()

        reply = (
            f"Product: {p['name']}\n"
            f"Price: ₹{p['price']}\n"
            f"Stock: {p['stock']}\n"
            f"Features: {', '.join(p['features'])}"
        )

        return {
            "source": "tool",
            "reply": reply
        }

    # -------- STEP 4: NORMAL AI CHAT --------
    response = model.generate_content(req.message)

    return {
        "source": "ai",
        "reply": response.text
    }
