import os
import certifi
import streamlit as st
from streamlit_mic_recorder import speech_to_text
from models import AnswerGenerator

# Set SSL certs (important for some environments like macOS or some cloud servers)
os.environ["SSL_CERT_FILE"] = certifi.where()

# Initialize session state defaults
state = st.session_state
state.setdefault("question", "")
state.setdefault("answer", {})
state.setdefault("manual_input", "")
state.setdefault("model", AnswerGenerator())
state.setdefault("context", "")
state.setdefault("jd_summarized_document", False)
state.setdefault("resume_vector_store", False)
state.setdefault("job_position", "")
state.setdefault("STT_output", "")
state.setdefault("STT", None)

# Helper: Handle submit from manual input
def handle_submit():
    state.question = state.manual_input
    state.manual_input = ""
    state.STT_output = ""
    state.STT = None

# Sidebar: User inputs and document upload
def render_sidebar():
    with st.sidebar:
        st.markdown("## Control Panel")

        # Mic input
        mic_text = speech_to_text(
            start_prompt="🟢 Start Recording",
            stop_prompt="🔴 Stop Recording",
            language='en',
            use_container_width=True,
            just_once=False,
            key="STT"
        )

        if mic_text and not state.manual_input:
            state.question = mic_text

        # Manual text input
        st.text_input("Enter the question:", key="manual_input", on_change=handle_submit)

        # Document Uploader Section
        with st.expander("📂 Document Uploader", expanded=False):
            st.markdown("Upload the Resume and JD here")

            state.job_position = st.text_input("Job Position", value=state.get("job_position", ""))

            resume_file = st.file_uploader("Upload your Resume (.docx only)", type=["docx"])
            if resume_file and not state.resume_vector_store:
                state.resume_vector_store = state.model.resume_vector_store(resume_file=resume_file)
            elif not resume_file:
                state.resume_vector_store = False

            jd_file = st.file_uploader("Upload your Job Description (.txt only)", type=["txt"])
            if jd_file and not state.jd_summarized_document:
                state.jd_summarized_document = state.model.jd_summarizer(jd_file=jd_file)
            elif not jd_file:
                state.jd_summarized_document = False

        st.markdown("-----")
        st.markdown("Made by Sumit Joshi")

# Main content
def render_main():
    st.title(f"Interview Assistant for Job position: {state.job_position or '❓'}")

    col1, col2, col3 = st.columns(3)

    with col2:
        st.markdown(f"**Resume:** {'✅ Vectorized' if state.resume_vector_store else '❌ Pending'}")

    with col3:
        st.markdown(f"**JD:** {'✅ Summarized' if state.jd_summarized_document else '❌ Pending'}")

    if state.resume_vector_store and state.jd_summarized_document and state.question and state.job_position:
        state.answer = state.model.answer_generator(
            job_position=state.job_position,
            question=state.question
        )
        state.context = state.answer.get("context", "No Context")

    with col1:
        st.markdown(f"<p style='font-size:20px; color:White;'> <b>Context: </b>{state.context}</p>", unsafe_allow_html=True)

    st.markdown(f"<p style='font-size:20px; color:White;'><b>Question:</b><br>{state.question}</p>", unsafe_allow_html=True)

    if state.question:
        st.markdown(f"<p style='font-size:30px; color:White;'><b>Answer:</b></p>", unsafe_allow_html=True)
        answer = state.answer.get("answer", "No Answer")
        if state.context == "Coding":
            st.code(answer)
        else:
            st.write(answer)

# Run the app
render_sidebar()
render_main()