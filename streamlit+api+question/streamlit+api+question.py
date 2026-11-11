import streamlit as st
from langchain_openai.chat_models import ChatOpenAI

st.title("🦜🔗 Quickstart App")

deepseek_api_key = st.sidebar.text_input("DeepSeek API Key", type="password")


def generate_response(input_text):
    model = ChatOpenAI(model="deepseek-chat", temperature=0.7, api_key=deepseek_api_key, base_url="https://api.deepseek.com")
    st.info(model.invoke(input_text).content)


with st.form("my_form"):
    text = st.text_area(
        "Enter text:",
        "What are the three key pieces of advice for learning how to code?"
    )
    submitted = st.form_submit_button("Submit")
    if not deepseek_api_key:
        st.warning("Please enter your DeepSeek API key!", icon="⚠")
    if submitted and deepseek_api_key:
        generate_response(text)