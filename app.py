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
renovation = st.selectbox("Renovation Status", ["Not yet", "Done"])
renovation_encoded = 0 if renovation == "Done" else 1
quoted_price = st.number_input("Landlord's Quoted Price (¥)", step=1.0)


# Submit
submit_button_placeholder = st.empty()

# Memory storage
if "messages" not in st.session_state:
    st.session_state.messages = []

with submit_button_placeholder.container():
    if st.button("Submit"):
        st.session_state.messages = []
        payload = {
            "Area": area,
            "BuildingYear": year,
            "TimeToNearestStation": station_time,
            "DistrictName": district_name,
            "RenovationEncoded": renovation_encoded,
            "TradePrice": quoted_price
        }

        response = requests.post(f"{BACKEND_URL}/predict", json=payload, stream=True)
        if response.status_code == 200:
            streamed_reply = ""
            for chunk in response.iter_content(chunk_size=1):
                if chunk:
                    streamed_reply += chunk.decode("utf-8", errors="ignore")
                    # output_box.markdown(streamed_reply)

            st.session_state.messages.append({"role": "assistant", "content": streamed_reply})




# Display chat history
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

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
