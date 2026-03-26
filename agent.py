import json
import re
import os
from urllib.parse import quote_plus

from langchain_groq import ChatGroq
import streamlit as st
from dotenv import load_dotenv

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
# CITY EXTRACTION (SAFE)
# =========================
def extract_city(query):
    words = query.lower().split()
    keywords = ["to", "in", "for", "visit"]

    for i, word in enumerate(words):
        if word in keywords and i + 1 < len(words):
            return words[i + 1].title()

    return words[-1].title() if words else ""

# =========================
# GET PLACES (AI BASED)
# =========================
def get_places(city):
    try:
        prompt = f"""
Give 6 famous tourist places in {city}.
Return ONLY a JSON list.
"""

        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)

        match = re.search(r'\[.*\]', text, re.DOTALL)
        if match:
            return json.loads(match.group())

    except:
        pass

    return []


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
            return {"error": "City not detected"}

        places = get_places(city)

        # 🔥 fallback (ALWAYS WORKS)
        if not places:
            places = [
                f"{city} famous place 1",
                f"{city} famous place 2",
                f"{city} famous place 3",
                f"{city} famous place 4"
            ]

        prompt = f"""
Create a 2-day itinerary for {city}.

Use these places:
{places}

Return JSON only:
{{
 "itinerary": {{
   "day1": ["place1", "place2"],
   "day2": ["place3", "place4"]
 }},
 "tips": ["tip1", "tip2"]
}}
"""

        response = llm.invoke(prompt)
        text = response.content if hasattr(response, "content") else str(response)

        # 🔥 safe parsing
        try:
            data = json.loads(text)
        except:
            match = re.search(r'\{.*\}', text, re.DOTALL)
            if match:
                try:
                    data = json.loads(match.group())
                except:
                    data = {}
            else:
                data = {}

        # 🔥 fallback itinerary (NEVER FAIL)
        day1 = data.get("itinerary", {}).get("day1", places[:2])
        day2 = data.get("itinerary", {}).get("day2", places[2:4])

        return {
            "itinerary": {
                "day1": day1,
                "day2": day2
            },
            "budget": {
                "per_day": 2500,
                "stay": 1000,
                "food": 750,
                "travel": 750,
                "category": "Mid-range"
            },
            "weather": {
                "description": "Moderate",
                "temperature": 25
            },
            "tips": data.get("tips", ["Explore local culture", "Start early"]),
            "maps": generate_map_links(list(set(day1 + day2)))
        }

    except Exception as e:
        return {"error": str(e)}
