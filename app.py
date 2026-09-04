import os
import re
from datetime import date

import streamlit as st
from dotenv import load_dotenv

from utils.file_storage import load_json, save_json
from services.dictionary_client import DictionaryClient, enhance_word_with_gemini
from models.flashcard import Flashcard
from services.spaced_repetition import SpacedRepetition
from services.quiz_generator import QuizGenerator

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
FLASHCARDS_FILE = "data/flashcards.json"
SCORES_FILE = "data/scores.json"

st.set_page_config(page_title="Vocab Builder & Flashcards", layout="centered")
st.title("📚 Vocabulary Builder & Smart Flashcards")

dictionary_client = DictionaryClient()


def clean_word_input(raw: str) -> str:
    """Strip punctuation/whitespace, keep only letters and hyphens."""
    return re.sub(r"[^a-zA-Z\-\s]", "", raw).strip()


tab1, tab2, tab3 = st.tabs(["🔍 Search & Save", "🗂 Review Flashcards", "📝 Quiz"])

# ---------------------------------------------------------------
# TAB 1: SEARCH & SAVE
# ---------------------------------------------------------------
with tab1:
    st.subheader("Search a word")
    raw_input = st.text_input("Enter a word to look up")

    if st.button("Search"):
        if not raw_input or not raw_input.strip():
            st.error("Please enter a word before searching.")
        else:
            term = clean_word_input(raw_input)
            if not term:
                st.error("That doesn't look like a valid word. Please use letters only.")
            else:
                try:
                    with st.spinner(f"Looking up '{term}'..."):
                        word_obj = dictionary_client.fetch_word_data(term)
                        word_obj = enhance_word_with_gemini(word_obj, GEMINI_API_KEY)
                    st.session_state["current_word"] = word_obj
                except ValueError as e:
                    st.error(str(e))
                    st.session_state.pop("current_word", None)
                except ConnectionError as e:
                    st.error(f"Couldn't reach the dictionary service: {e}")
                    st.session_state.pop("current_word", None)

    if "current_word" in st.session_state:
        word = st.session_state["current_word"]
        st.markdown(f"### {word.term}")
        if word.phonetic:
            st.caption(word.phonetic)

        if word.definitions:
            st.write("**Definitions:**")
            for d in word.definitions:
                st.write(f"- {d}")

        if word.examples:
            st.write("**Examples:**")
            for ex in word.examples:
                st.write(f"- {ex}")

        if word.synonyms:
            st.write("**Synonyms:** " + ", ".join(word.synonyms))
        if word.antonyms:
            st.write("**Antonyms:** " + ", ".join(word.antonyms))

        if word.simple_explanation:
            st.info(f"💡 {word.simple_explanation}")
        if word.ai_example:
            st.write(f"**AI example:** {word.ai_example}")
        if word.memory_trick:
            st.write(f"**Memory trick:** {word.memory_trick}")

        if st.button("💾 Save as flashcard"):
            saved = load_json(FLASHCARDS_FILE, default_val=[])
            existing_terms = [c["word_dict"]["term"] for c in saved]
            if word.term in existing_terms:
                st.warning(f"'{word.term}' is already saved.")
            else:
                new_card = Flashcard(word_dict=word.to_dict())
                saved.append(new_card.to_dict())
                if save_json(FLASHCARDS_FILE, saved):
                    st.success(f"Saved '{word.term}' as a flashcard!")
                else:
                    st.error("Something went wrong saving the flashcard to disk.")

# ---------------------------------------------------------------
# TAB 2: REVIEW FLASHCARDS
# ---------------------------------------------------------------
with tab2:
    st.subheader("Review your flashcards")
    saved_raw = load_json(FLASHCARDS_FILE, default_val=[])
    cards = [Flashcard.from_dict(c) for c in saved_raw]
    due_cards = [c for c in cards if c.is_due()]

    if not cards:
        st.info("You haven't saved any flashcards yet. Go search for a word first!")
    elif not due_cards:
        st.success("No cards are due for review right now. Check back later!")
    else:
        st.session_state.setdefault("review_index", 0)
        st.session_state.setdefault("show_answer", False)

        idx = st.session_state["review_index"] % len(due_cards)
        current_card = due_cards[idx]
        term = current_card.word_dict["term"]

        st.markdown(f"### {term}")
        st.caption(f"{idx + 1} of {len(due_cards)} due")

        if not st.session_state["show_answer"]:
            if st.button("Show answer"):
                st.session_state["show_answer"] = True
        else:
            defs = current_card.word_dict.get("definitions", [])
            if defs:
                st.write(f"**Definition:** {defs[0]}")
            if current_card.word_dict.get("simple_explanation"):
                st.info(current_card.word_dict["simple_explanation"])

            st.write("How well did you know this?")
            cols = st.columns(4)
            labels = ["Again (0)", "Hard (2)", "Good (3)", "Easy (5)"]
            qualities = [0, 2, 3, 5]

            for col, label, quality in zip(cols, labels, qualities):
                if col.button(label):
                    updated = SpacedRepetition.update_card(current_card, quality)
                    for i, c in enumerate(saved_raw):
                        if c["word_dict"]["term"] == term:
                            saved_raw[i] = updated.to_dict()
                            break
                    save_json(FLASHCARDS_FILE, saved_raw)
                    st.session_state["show_answer"] = False
                    st.session_state["review_index"] += 1
                    st.rerun()

# ---------------------------------------------------------------
# TAB 3: QUIZ
# ---------------------------------------------------------------
with tab3:
    st.subheader("Test yourself")
    saved_raw = load_json(FLASHCARDS_FILE, default_val=[])

    if len(saved_raw) < 2:
        st.info("Save at least 2 flashcards before taking a quiz.")
    else:
        if "quiz_questions" not in st.session_state:
            if st.button("Start quiz"):
                generator = QuizGenerator(saved_raw)
                st.session_state["quiz_questions"] = generator.generate_quiz(num_questions=5)
                st.session_state["quiz_answers"] = {}
                st.session_state["quiz_submitted"] = False
                st.rerun()
        else:
            questions = st.session_state["quiz_questions"]

            for i, q in enumerate(questions):
                st.write(f"**{i + 1}. What does '{q['word']}' mean?**")
                answer = st.radio(
                    "Choose one:",
                    q["options"],
                    key=f"quiz_q_{i}",
                    index=None,
                )
                st.session_state["quiz_answers"][i] = answer

            if not st.session_state.get("quiz_submitted") and st.button("Submit quiz"):
                st.session_state["quiz_submitted"] = True
                score = sum(
                    1 for i, q in enumerate(questions)
                    if st.session_state["quiz_answers"].get(i) == q["correct_answer"]
                )
                st.session_state["quiz_score"] = score

                scores = load_json(SCORES_FILE, default_val=[])
                scores.append({
                    "date": str(date.today()),
                    "score": score,
                    "total": len(questions),
                })
                save_json(SCORES_FILE, scores)
                st.rerun()

            if st.session_state.get("quiz_submitted"):
                score = st.session_state["quiz_score"]
                total = len(questions)
                st.success(f"You scored {score}/{total}!")

                if st.button("Try another quiz"):
                    for key in ("quiz_questions", "quiz_answers", "quiz_submitted", "quiz_score"):
                        st.session_state.pop(key, None)
                    st.rerun()