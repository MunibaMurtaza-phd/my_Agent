import streamlit as st 
from google import genai 
# ----------------------------
# Gemini Client 
# ---------------------------- 
client = genai.Client( api_key=st.secrets["GOOGLE_API_KEY"] )
# Temporary test 


st.write("Key starts with:", st.secrets["GOOGLE_API_KEY"][:10])
# ----------------------------
# Streamlit UI
# ---------------------------- 
st.set_page_config( page_title="AI PDF Assistant", page_icon="🤖", layout="wide" )
