import sqlite3
import requests
import os


# 📍 GET PLACES
def get_places(city):
    try:
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()

        cursor.execute("SELECT name, type, cost FROM places WHERE city=?", (city,))
        results = cursor.fetchall()
        conn.close()

        if not results:
            return {"error": f"No places found for {city}"}

        places = []
        for name, type_, cost in results:
            places.append({
                "name": name,
                "type": type_,
                "cost": cost
            })

        return {"city": city, "places": places}

    except Exception as e:
        return {"error": str(e)}


# 💰 BUDGET
def budget_calculator(budget, days):
    per_day = max(budget // days, 1000)

    if per_day > 5000:
        category = "Luxury"
    elif per_day > 2000:
        category = "Mid-range"
    else:
        category = "Budget"

    return {
        "per_day": per_day,
        "stay": int(per_day * 0.4),
        "food": int(per_day * 0.3),
        "travel": int(per_day * 0.3),
        "category": category
    }


# 🌦 WEATHER
def get_weather(city):
    try:
        api_key = os.getenv("OPENWEATHER_API_KEY")

        if not api_key:
            return {"error": "Weather API key not set"}

        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

        response = requests.get(url, timeout=5)
        data = response.json()

        if response.status_code != 200 or "main" not in data:
            return {"error": f"Weather not available for {city}"}

        return {
            "city": city,
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"]
        }

    except Exception as e:
        return {"error": str(e)}


# 🗺 MAP LINK
def get_map_link(place):
    return f"https://www.google.com/maps/search/{place.replace(' ', '+')}"