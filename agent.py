import json
import os
import random
from urllib.parse import quote_plus

from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

from tools import get_places, budget_calculator, get_weather

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# LLM
# =========================
api_key = os.getenv("GROQ_API_KEY") or st.secrets.get("GROQ_API_KEY")

if not api_key:
    raise ValueError("Missing GROQ_API_KEY")

llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=api_key,
    temperature=0.7
)

# =========================
# CITY EXTRACTION (SIMPLE)
# =========================
def extract_city(query):
    words = query.lower().split()

    keywords = ["to", "in", "for", "visit"]

    for i, word in enumerate(words):
        if word in keywords and i + 1 < len(words):
            return words[i + 1].title()

    return words[-1].title() if words else ""

# =========================
# JSON PARSER
# =========================
def extract_json(text):
    if hasattr(text, "content"):
        text = text.content

    try:
        return json.loads(text)
    except:
        return {}

# =========================
# MAP LINKS
# =========================
def generate_map_links(places):
    return [
        f"https://www.google.com/maps/search/{quote_plus(p)}"
        for p in places
    ]

# =========================
# MAIN AGENT
# =========================
def run_agent(query):
    try:
        city = extract_city(query)

        if not city:
            return {"error": "Could not detect city."}

        places = get_places(city)

        place_list = places if isinstance(places, list) else places.get("places", [])

        place_names = []
        for p in place_list:
            if isinstance(p, dict) and "name" in p:
                place_names.append(p["name"])
            elif isinstance(p, str):
                place_names.append(p)

        if not place_names:
            return {"error": f"No places found for {city}"}

        weather = get_weather(city)
        budget = budget_calculator(5000, 2)

        prompt = f"""
Plan a 2-day trip for {city}.

Use only these places:
{place_names}

Return JSON:
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
            return {"error": "AI failed to generate response"}

        # fallback structure
        day1 = data.get("itinerary", {}).get("day1", place_names[:2])
        day2 = data.get("itinerary", {}).get("day2", place_names[2:4])

        data["itinerary"] = {
            "day1": day1,
            "day2": day2
        }

        data["budget"] = budget
        data["weather"] = weather

        all_places = list(set(day1 + day2))
        data["maps"] = generate_map_links(all_places)

        return data

    except Exception as e:
        return {"error": str(e)}
