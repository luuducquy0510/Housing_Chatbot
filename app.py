import streamlit as st
import requests
import json


BACKEND_URL = "http://localhost:8000"

st.set_page_config(page_title="Housing Price Advisor Chatbot")

st.title("🏡 Housing Price Advisor")


# Input fields matching UserInput schema
area = st.number_input("Area (m²)", min_value=10.0, step=1.0)
year = st.number_input("Building Year", min_value=1950, step=1)
station_time = st.number_input("Time to Nearest Station (min)", min_value=0.0, step=1.0)

district_name = st.text_input("District Name").strip().lower()
station_name = st.text_input("Nearest Station").strip().lower()

renovation = st.selectbox("Renovation Status", ["Not yet", "Done"])
floorplan = st.text_input("Floor Plan (e.g. 2LDK)").strip().upper()

quoted_price = st.number_input("Landlord's Quoted Price (¥)", min_value=0.0, step=1.0)

# Memory storage
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Submit
if st.button("Submit"):
    payload = {
        "DistrictName": district_name,
        "NearestStation": station_name,
        "MinTimeToNearestStation": station_time,
        "Area": area,
        "BuildingYear": year,
        "Renovation": renovation,
        "FloorPlan": floorplan,
        "TradePrice": quoted_price
    }

    with st.chat_message("assistant"):
        output_box = st.empty()
        streamed_reply = ""

        response = requests.post(f"{BACKEND_URL}/predict", json=payload, stream=True)
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1):
                if chunk:
                    streamed_reply += chunk.decode("utf-8", errors="ignore")
                    output_box.markdown(streamed_reply)

        st.session_state.messages.append({"role": "assistant", "content": streamed_reply})



if prompt := st.chat_input("Ask your follow-up question..."):
    # Show user message
    st.chat_message("user").markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Build full conversation history (excluding current prompt)
    full_prompt = "\n".join(
        [f"{m['role'].capitalize()}: {m['content']}" for m in st.session_state.messages]
    )

    payload = {"query": full_prompt}
    # Show assistant message streaming
    with st.chat_message("assistant"):
        output_box = st.empty()
        streamed_reply = ""

        # Send request with stream=True
        response = requests.post(f"{BACKEND_URL}/conversation", json=payload, stream=True)
        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1):
                if chunk:
                    streamed_reply += chunk.decode("utf-8", errors="ignore")
                    output_box.markdown(streamed_reply)

    st.session_state.messages.append({"role": "assistant", "content": streamed_reply})
