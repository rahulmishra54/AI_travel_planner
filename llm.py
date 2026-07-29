from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
import os
import streamlit as st

load_dotenv()


def get_llm():
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=st.secrets.get("GOOGLE_API_KEY") or os.getenv("GOOGLE_API_KEY"),
        temperature=0.7,
    )