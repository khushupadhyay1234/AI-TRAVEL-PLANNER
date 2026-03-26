import streamlit as st
from agent import run_agent

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍", layout="wide")

# 🌍 HEADER
st.markdown("""
<h1 style='text-align: center;'>🌍 AI Travel Planner</h1>
<p style='text-align: center; color: gray;'>Plan your perfect trip with AI ✨</p>
""", unsafe_allow_html=True)

# INPUT
query = st.text_input("✈️ Enter your travel plan:")

if st.button("🚀 Generate Plan"):
    if query:
        with st.spinner("🧠 Planning your trip..."):
            data = run_agent(query)

        if "error" in data:
            st.error(data["error"])
        else:
            st.success("✅ Trip planned successfully!")

            # 📅 ITINERARY
            st.markdown("## 📅 Trip Plan")

            col1, col2 = st.columns(2)

            # 🎴 CARD STYLE FUNCTION
            def place_card(place):
                st.markdown(f"""
                <div style="
                    background: linear-gradient(135deg, #1f4037, #99f2c8);
                    padding: 15px;
                    border-radius: 12px;
                    margin-bottom: 10px;
                    color: black;
                    font-weight: 600;">
                    📍 {place}
                </div>
                """, unsafe_allow_html=True)

            with col1:
                st.markdown("### Day 1")
                for place in data["itinerary"]["day1"]:
                    place_card(place)

            with col2:
                st.markdown("### Day 2")
                for place in data["itinerary"]["day2"]:
                    place_card(place)

            # 💰 BUDGET CARDS
            st.markdown("## 💰 Budget Breakdown")
            b = data["budget"]

            col1, col2, col3, col4 = st.columns(4)

            col1.metric("Per Day", f"₹{b['per_day']}")
            col2.metric("Stay", f"₹{b['stay']}")
            col3.metric("Food", f"₹{b['food']}")
            col4.metric("Travel", f"₹{b['travel']}")

            # 💡 TIPS
            st.markdown("## 💡 Travel Tips")
            for tip in data["tips"]:
                st.markdown(f"""
                <div style="
                    background:#111;
                    padding:10px;
                    border-radius:8px;
                    margin-bottom:8px;">
                    ✔️ {tip}
                </div>
                """, unsafe_allow_html=True)

            # 🗺 MAP LINKS (FIXED + CLEAN)
            st.markdown("## 🗺 Explore Locations")

            all_places = list(set(
                data["itinerary"]["day1"] + data["itinerary"]["day2"]
            ))

            for place, link in zip(all_places, data["maps"]):
                st.markdown(f"""
                <div style="margin-bottom:8px;">
                📍 <b>{place}</b> → <a href="{link}" target="_blank">Open Map</a>
                </div>
                """, unsafe_allow_html=True)

    else:
        st.warning("⚠️ Please enter a travel query")
