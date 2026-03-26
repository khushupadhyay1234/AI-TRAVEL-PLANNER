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
# ✅ LLM
# =========================
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("❌ GROQ_API_KEY not found")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=api_key,
    temperature=0.7   # 🔥 slightly higher = more variation
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
# ✅ JSON PARSER
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

    place_list = places if isinstance(places, list) else places.get("places", [])

    names = []
    for p in place_list:
        if isinstance(p, dict) and "name" in p:
            names.append(p["name"])
        elif isinstance(p, str):
            names.append(p)

    # 🔥 fallback if API fails
    if not names:
        names = [
            f"{city} Fort",
            f"{city} Beach",
            f"{city} Market",
            f"{city} Temple"
        ]

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
        f"Explore local culture of {city}",
        "Start early to avoid crowds",
        "Try local food specialties"
    ])

    return data


# =========================
# 🚀 MAIN AGENT
# =========================
def run_agent(query):
    try:
        city = extract_city(query)

        # 🔥 GET PLACES
        places = get_places(city)

        place_list = places if isinstance(places, list) else places.get("places", [])

        place_names = []
        for p in place_list:
            if isinstance(p, dict) and "name" in p:
                place_names.append(p["name"])
            elif isinstance(p, str):
                place_names.append(p)

        # 🔥 fallback (IMPORTANT)
        if not place_names:
            place_names = [
                f"{city} Fort",
                f"{city} Beach",
                f"{city} Market",
                f"{city} Temple"
            ]

        # DEBUG (optional)
        print("CITY:", city)
        print("PLACES:", place_names)

        weather = get_weather(city)
        budget = budget_calculator(5000, 2)

        # 🔥 STRONG PROMPT (fix repetition issue)
        prompt = f"""
You are a travel expert.

Plan a UNIQUE 2-day trip for {city}.

Available places:
{place_names}

Rules:
- Use ONLY places from the list
- Do NOT repeat places
- Make itinerary specific to {city}
- Avoid generic suggestions

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
            return {"error": "⚠️ AI failed. Try again."}

        data = ensure_structure(data, city, places, weather, budget)

        all_places = list(set(
            data["itinerary"]["day1"] + data["itinerary"]["day2"]
        ))

        data["maps"] = generate_map_links(all_places)

        return data

    except Exception as e:
        return {"error": str(e)}
