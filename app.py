import streamlit as st
import requests

st.set_page_config(page_title="ADK-Powered Healthcare Chatbot", page_icon="🏥")

st.title("👩‍⚕️ ADK-Powered Healthcare Chatbot")

# ✨ Add start location here
field_1 = st.text_input("age", placeholder="a")
field_2= st.text_input("gender", placeholder="a")
field_3= st.text_input("name")
field_4= st.text_input("contact")
field_5= st.text_input("phone")


if "messages" not in st.session_state:
    st.session_state.messages = []

# Render previous messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if st.button("Execute"):
    if not all([field_1, field_2, field_3, field_4, field_5]):
        st.warning("Please fill in all the details.")
    else:
        payload = {
            "field_1": field_1,
            "field_2": field_2,
            "field_3": str(field_3),
            "field_4": str(field_4),
            "field_5": field_5
        }
    # Show assistant message streaming
    with st.chat_message("assistant"):
        output_box = st.empty()
        streamed_reply = ""
        response = requests.post("http://localhost:8000/healthcare", json=payload, stream=True)

        if response.status_code == 200:
            for chunk in response.iter_content(chunk_size=1):
                    if chunk:
                        streamed_reply += chunk.decode("utf-8", errors="ignore") # Handle decoding errors
                        output_box.markdown(streamed_reply)
    
    st.session_state.messages.append(
        {"role": "assistant", "content": streamed_reply}
    )