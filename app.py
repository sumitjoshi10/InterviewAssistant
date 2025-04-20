import streamlit as st
from streamlit_mic_recorder import speech_to_text
from models import AnswerGenerator

state = st.session_state

# Initialize state
if "question" not in state:
    state.question = ""
if "answer" not in state:
    state.answer = ""
if "manual_input" not in state:
    state.manual_input = ""
if "model" not in state:
    state.model = AnswerGenerator()
    
# Callback function when Enter is pressed
def handle_submit():
    state.STT_output = ""
    state.STT = None
    state.question = state.manual_input
    state.manual_input = ""  # Clear the input field

state

# Sidebar button logic
with st.sidebar:
    st.markdown("## Control Panel")
    text = speech_to_text(start_prompt="🟢 Start Recoding",
                          stop_prompt="🔴 Stop Recoding",
                          language='en', 
                          use_container_width=True, 
                          just_once=False, key='STT'
                        )
    
 # If audio text is detected and no manual input, handle it
    if text and not state.get("manual_input"):
        state.question = text

  

    # Manual text input field using a different key
    st.text_input(
        "Enter the question:",
        key="manual_input",
        on_change=handle_submit
    )

    # st.markdown(f"**Status:** {'🟢 Running' if state.running else '🔴 Stopped'}")
    # st.text(state.question)
    # st.button(
    #     "▶️ Start" if not state.running else "⏹️ Stop",
    #     key="toggle_button",
    #     on_click=toggle,
    # )
  

    ## Context Markdown
    st.markdown(
        f"**Context:** WIP"
    )
    
    # Simulated second sidebar using expander
    with st.expander("📂 Document Uploader", expanded=False):
        st.markdown("Need to Upload the Resume and JD here")
        
        ## Get the Job Position Here
        job_position = st.text_input("Job Position")
        
        ## Upload the Resume
        resume_file = st.file_uploader("Upload your Resume (.docx only)", type=["docx"])
        if resume_file:
            resume_document = state.model.resume_loader(resume_file)
        
        ## Upload the Job Description
        jd_file = st.file_uploader("Upload your Job Description (.txt only)", type=["txt"])
        if jd_file:
            jd_document = state.model.jd_loader(jd_file)

    st.markdown("-----")
    st.markdown("Made by Sumit Joshi")
    
    

# Main page content
st.title(f"Interview Assistant for Job position {job_position}")

st.markdown(
        f"**Resume:** {'✅  Uploaded' if resume_file else '❌ Pending'}"
    )
st.markdown(
        f"**Job Description:** {'✅  Uploaded' if jd_file else '❌ Pending'}"
    )
st.markdown(
    f"<p style='font-size:30px; color:White;'> <b>Question: </b><br> {state.question}</p>",
    unsafe_allow_html=True
)
if resume_file:
    st.write(resume_document)
if jd_file:
    st.write(jd_document)


# Conditional markdown sfor answer
if state.question:
    answer = "WIP"
    msg = f"<p style='font-size:30px; color:White;'><b>Answer: </b><br> {answer} </p>"
else:
    msg = ""
st.markdown(msg, unsafe_allow_html=True)
