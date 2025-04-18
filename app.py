import streamlit as st
from models import MicrophoneAccess

# Initialize the state
if "running" not in st.session_state:
    st.session_state.running = False
if "question" not in st.session_state:
    st.session_state.question = ""
if "transcript" not in st.session_state:
    st.session_state.transcript = []
if "mic" not in st.session_state:
    st.session_state.mic = MicrophoneAccess()


# Callback function to toggle the state
def toggle():
    st.session_state.running = not st.session_state.running
    if st.session_state.running:
        st.session_state.transcript = []
        st.session_state.question = ""
        st.session_state.mic.start_stream()
    else:
        transcript = st.session_state.mic.stop_stream_and_transcribe()
        st.session_state.transcript.append(transcript)
        st.session_state.question = " ".join(st.session_state.transcript)
    
# Callback function when Enter is pressed
def handle_submit():
    st.session_state.question = st.session_state.user_input
    st.session_state.user_input = ""  # Clear input



# Sidebar button logic
with st.sidebar:
    st.markdown("## Control Panel")
    st.button(
        "▶️ Start" if not st.session_state.running else "⏹️ Stop",
        key="toggle_button",
        on_click=toggle,
    )
    st.markdown(
        f"**Status:** {'🟢 Running' if st.session_state.running else '🔴 Stopped'}"
    )
    ## to take the user Input 
    new_input = st.text_input(
        "Enter the question:", 
        key="user_input",
        on_change=handle_submit,
        disabled=st.session_state.running
    )
    
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
        
        ## Upload the Job Description
        jd_file = st.file_uploader("Upload your Job Description (.txt only)", type=["txt"])

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
    f"<p style='font-size:30px; color:White;'> <b>Question: </b><br> {st.session_state.question}</p>",
    unsafe_allow_html=True
)


# Conditional markdown sfor answer
if st.session_state.question:
    msg = f"<p style='font-size:30px; color:White;'><b>Answer: </b><br> Answer WIP </p>"
else:
    msg = ""
st.markdown(msg, unsafe_allow_html=True)

