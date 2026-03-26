import streamlit as st
from agent import run_agent

st.set_page_config(page_title="AI Travel Planner", page_icon="🌍")

st.title("🌍 AI Travel Planner")
st.write("✨ Powered by AI Agents")

query = st.text_input("Enter your travel plan:")

if st.button("Generate Plan"):
    if query:
        with st.spinner("Planning your trip..."):
            data = run_agent(query)

        if "error" in data:
            st.error(data["error"])
        else:
            st.subheader("📅 Trip Plan")

            col1, col2 = st.columns(2)

            with col1:
                st.markdown("### Day 1")
                for p in data["itinerary"]["day1"]:
                    st.success(p)

            with col2:
                st.markdown("### Day 2")
                for p in data["itinerary"]["day2"]:
                    st.success(p)

            st.subheader("💰 Budget")
            b = data["budget"]

            st.write(f"Per Day: ₹{b['per_day']}")
            st.write(f"Stay: ₹{b['stay']}")
            st.write(f"Food: ₹{b['food']}")
            st.write(f"Travel: ₹{b['travel']}")

            st.subheader("💡 Tips")
            for tip in data["tips"]:
                st.write("✔️", tip)

            st.subheader("🗺 Maps")
            for link in data["maps"]:
                st.markdown(f"[Open Map]({link})")

    else:
        st.warning("Enter something")
