import json
import re
import random
import os
from urllib.parse import quote_plus

from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

from tools import get_places, budget_calculator, get_weather

# =========================
# 🔐 LOAD ENV
# =========================
load_dotenv()

# =========================
# ✅ LLM (SAFE + HYBRID)
# =========================
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found. Add it in .env or Streamlit secrets.")

llm = ChatGroq(
    model="llama3-70b-8192",
    api_key=api_key,
    temperature=0.5
)

# =========================
# ✅ CITY EXTRACTION
# =========================
def extract_city(query):
    query_lower = query.lower()

    patterns = [
        r"trip to ([a-zA-Z ]+)",
        r"to ([a-zA-Z ]+)",
        r"in ([a-zA-Z ]+)",
        r"visit ([a-zA-Z ]+)"
    ]

    for pattern in patterns:
        match = re.search(pattern, query_lower)
        if match:
            return match.group(1).strip().title()

    return "Goa"

# =========================
# ✅ JSON PARSER (ROBUST)
# =========================
def extract_json(text):
    if hasattr(text, "content"):
        text = text.content

    try:
        return json.loads(text)
    except:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except:
                pass
    return {}

# =========================
# ✅ MAP LINKS
# =========================
def generate_map_links(places):
    return [
        f"https://www.google.com/maps/search/{quote_plus(p)}"
        for p in places
    ]

# =========================
# 🔥 ENSURE STRUCTURE
# =========================
def ensure_structure(data, city, places, weather, budget):
    if not isinstance(data, dict):
        data = {}

    place_list = places.get("places", []) if isinstance(places, dict) else []
    names = [p["name"] for p in place_list]

    itinerary = data.get("itinerary", {})

    day1 = itinerary.get("day1", [])
    day2 = itinerary.get("day2", [])

    if not day1:
        day1 = names[:2]

    if not day2:
        day2 = names[2:4]

    day2 = [p for p in day2 if p not in day1]

    if not day2:
        remaining = [p for p in names if p not in day1]
        random.shuffle(remaining)
        day2 = remaining[:2]

    remaining = [p for p in names if p not in day1 and p not in day2]

    while len(day2) < 2 and remaining:
        day2.append(remaining.pop())

    while len(day2) < 2 and len(day1) > 1:
        day2.append(day1.pop())

    day1 = day1[:2]
    day2 = day2[:2]

    data["itinerary"] = {
        "day1": day1,
        "day2": day2
    }

    data["budget"] = budget
    data["weather"] = weather

    data.setdefault("tips", [
        "Start early to cover more places",
        "Carry water and essentials",
        "Check local transport options"
    ])

    return data

# =========================
# 🚀 MAIN AGENT
# =========================
def run_agent(query):
    try:
        city = extract_city(query)

        places = get_places(city)

        # 🔥 FLEXIBLE PARSING (handles list or dict)
        place_list = places if isinstance(places, list) else places.get("places", [])

        place_names = []
        for p in place_list:
            if isinstance(p, dict) and "name" in p:
                place_names.append(p["name"])
            elif isinstance(p, str):
                place_names.append(p)

        # 🔥 FALLBACK (never fail)
        if not place_names:
            place_names = [
                f"Popular places in {city}",
                f"Tourist attractions in {city}",
                f"Local markets in {city}",
                f"Hidden gems in {city}"
            ]

        weather = get_weather(city)
        budget = budget_calculator(5000, 2)

        prompt = f"""
Plan a 2-day trip.

City: {city}
Places: {place_names}

IMPORTANT:
- Do NOT repeat places across days
- Distribute places evenly across days
- Each day should have different places

Return ONLY JSON:
{{
  "itinerary": {{
    "day1": ["place1", "place2"],
    "day2": ["place3", "place4"]
  }},
  "tips": ["tip1", "tip2"]
}}
"""

        response = llm.invoke(prompt)
        data = extract_json(response)

        if not data:
            return {"error": "⚠️ AI failed to generate valid plan. Try again."}

        data = ensure_structure(data, city, places, weather, budget)

        all_places = list(set(
            data["itinerary"]["day1"] + data["itinerary"]["day2"]
        ))

        data["maps"] = generate_map_links(all_places)

        return data

    except Exception as e:
        return {"error": str(e)}
