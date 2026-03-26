import streamlit as st
from agent import run_agent

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")

# 🌍 Header
st.title("🌍 AI Travel Planner")
st.write("✨ Powered by AI Agents + LangChain")

query = st.text_input("Enter your travel plan:")

if st.button("Generate Plan"):
    if query:
        # 🚀 Loading animation
        with st.spinner("🧠 AI is planning your trip..."):
            data = run_agent(query)

        if "error" in data:
            st.error(data["error"])

        else:
            # 📅 Itinerary
            st.subheader("📅 Trip Plan")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Day 1")
                for place in data["itinerary"]["day1"]:
                    st.success(f"📍 {place}")

            with col2:
                st.markdown("### Day 2")
                for place in data["itinerary"]["day2"]:
                    st.success(f"📍 {place}")

            # 💰 Budget
            st.subheader("💰 Budget Breakdown")
            b = data["budget"]

            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Per Day", f"₹{b['per_day']}")
            col2.metric("Stay", f"₹{b['stay']}")
            col3.metric("Food", f"₹{b['food']}")
            col4.metric("Travel", f"₹{b['travel']}")

            # 💎 Optional bonus (looks pro)
            st.write(f"💼 Category: {b.get('category', 'Standard')}")

            # 🌦 Weather (FINAL UX FIX)
            st.subheader("🌦 Weather")
            w = data.get("weather", {})

            if isinstance(w, dict) and "description" in w and "temperature" in w:
                st.warning(f"{w['description']} - {w['temperature']}°C")
            else:
                st.warning("Weather unavailable — plan for moderate conditions ☀️")

            # 💡 Tips
            st.subheader("💡 Travel Tips")
            for tip in data["tips"]:
                st.success(tip)

            # 🗺 Map Links (DEDUP FIX)
            st.subheader("🗺 Map Links")

            all_places = list(set(
                data["itinerary"]["day1"] + data["itinerary"]["day2"]
            ))

            for place in all_places:
                map_link = f"https://www.google.com/maps/search/{place.replace(' ', '+')}"
                st.markdown(f"📍 {place} → [Open Map]({map_link})")

    else:
        st.warning("Please enter a travel query!")