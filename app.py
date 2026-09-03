import streamlit as st
from utils.file_storage import load_json, save_json

st.set_page_config(page_title="Vocab Builder & Flashcards", layout="centered")
st.title("📚 Vocabulary Builder & Smart Flashcards")

tab1, tab2, tab3 = st.tabs(["🔍 Search & Save", "🗂 Review Flashcards", "📝 Quiz"])

with tab1:
    st.write("Search features coming soon.")
with tab2:
    st.write("Flashcard review coming soon.")
with tab3:
    st.write("Quiz engine coming soon.")
    