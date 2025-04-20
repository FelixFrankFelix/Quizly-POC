import streamlit as st
import json
import requests

# API endpoint URL - change this to the appropriate URL where your FastAPI is running
API_URL = "http://localhost:8000"

# Initialize session state
if 'questions' not in st.session_state:
    st.session_state.questions = []
if 'answers' not in st.session_state:
    st.session_state.answers = {}
if 'score' not in st.session_state:
    st.session_state.score = None
if 'show_explanations' not in st.session_state:
    st.session_state.show_explanations = False
if 'submitted' not in st.session_state:
    st.session_state.submitted = False

def generate_questions():
    try:
        # Show loader while generating questions
        with st.spinner("Generating questions..."):
            # Convert difficulty level to numerical value
            difficulty_map = {"Very-Easy": 1, "Easy": 2, "Medium": 3, "Hard": 4, "Legendary": 5}
            difficulty = difficulty_map[difficulty_level]
            
            # Call the API endpoint instead of directly using main.get_quiz
            payload = {
                "context": context,
                "difficulty": difficulty,
                "num_questions": num_questions
            }
            
            response = requests.post(f"{API_URL}/generate-quiz", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                st.session_state.questions = result['questions']
                # Initialize answers with empty strings
                st.session_state.answers = {str(i): "" for i in range(len(st.session_state.questions))}
                st.session_state.score = None
                st.session_state.show_explanations = False
                st.session_state.submitted = False
            else:
                st.error(f"API Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Error generating questions: {str(e)}")

# App layout
st.title("AI Quiz Generator 🤖📚")

# Context input
context = st.text_input(
    "Quiz Context (e.g., Python programming, World War II history)",
    value="General Knowledge",
    key="context"
)

# Input controls for quiz configuration
col1, col2 = st.columns(2)
with col1:
    num_questions = st.number_input(
        "Number of Questions",
        min_value=1,
        max_value=20,
        value=5,
        key="num_questions"
    )
with col2:
    difficulty_level = st.selectbox(
        "Difficulty Level",
        ["Very-Easy", "Easy", "Medium", "Hard", "Legendary"],
        key="difficulty"
    )

st.button("Generate Questions", on_click=generate_questions)

# Display questions or info message
if st.session_state.questions:
    with st.form("quiz_form"):
        for i, question in enumerate(st.session_state.questions):
            st.subheader(f"Question {i+1}")
            st.write(question['question'])
            
            options = question['options']
            answer_key = f"q_{i}"
            selected_option = st.radio(
                "Select your answer:",
                options=[f"{chr(65+j)}) {option}" for j, option in enumerate(options)],
                key=answer_key,
                index=None
            )
            # Store user's answer (or empty string if not selected)
            if selected_option is not None:
                st.session_state.answers[str(i)] = selected_option.split(")")[0].strip()
            else:
                st.session_state.answers[str(i)] = ""

        submitted = st.form_submit_button("Submit Answers")

        if submitted:
            # Calculate score when form is submitted
            score = 0
            for i, question in enumerate(st.session_state.questions):
                user_answer = st.session_state.answers.get(str(i), "")
                if user_answer == question['answer']:
                    score += 1
            st.session_state.score = score
            st.session_state.submitted = True

    # Display results after submission
    if st.session_state.submitted:
        unanswered = sum(1 for i in range(len(st.session_state.questions)) if st.session_state.answers.get(str(i), "") == "")
        if unanswered > 0:
            st.warning(f"You left {unanswered} question(s) unanswered.")
        st.success(f"Your score: {st.session_state.score}/{len(st.session_state.questions)}")
        
        # Show Explanations toggle button
        if st.button("Show Explanations"):
            st.session_state.show_explanations = not st.session_state.show_explanations

        # Display explanations if toggled
        if st.session_state.show_explanations:
            st.subheader("Explanations")
            for i, question in enumerate(st.session_state.questions):
                user_answer = st.session_state.answers.get(str(i), "")
                correct_answer = question['answer']
                is_correct = user_answer == correct_answer
                
                # Display question
                st.write(f"**Question {i+1}:** {question['question']}")
                
                # Display user's answer and correctness
                if user_answer:
                    if is_correct:
                        st.success(f"✅ Your answer: {user_answer} (Correct)")
                    else:
                        st.error(f"❌ Your answer: {user_answer} (Incorrect)")
                else:
                    st.error("❌ No answer provided")
                
                # Display correct answer
                st.write(f"**Correct Answer:** {correct_answer}")
                
                # Display explanation
                st.write(f"**Explanation:** {question['explanation']}")
                
                # Add some spacing
                st.write("---")
else:
    st.info("Click 'Generate Questions' to start the quiz")