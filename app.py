import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Configuration for Mobile
st.set_page_config(
    page_title="HN CrossFit Live",
    page_icon="🏋️",
    layout="centered"
)

# Custom CSS to make buttons bigger for judges' thumbs
st.markdown("""
    <style>
    div.stButton > button:first-child {
        height: 3em;
        width: 100%;
        background-color: #00ff00;
        color: black;
        font-weight: bold;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. Title and Header
st.title("🏆 Judge Score Entry")
st.subheader("Herceg Novi Local Event")

# 3. Establish Connection to Google Sheets (using your Secrets)
conn = st.connection("gsheets", type=GSheetsConnection)

# 4. The Entry Form
with st.form("score_entry_form", clear_on_submit=True):
    st.write("---")
    
    # Athlete Selection
    athlete_id = st.number_input("Athlete Number (1-100)", min_value=1, max_value=100, step=1)
    
    # Workout Selection (You can change these names)
    workout = st.selectbox("Select Workout", [
        "WOD 1: Strength", 
        "WOD 2: Endurance", 
        "WOD 3: Final"
    ])
    
    # Score Entry
    score = st.number_input("Result (Total Reps or Total Seconds)", min_value=0, step=1, help="Enter reps or convert time to total seconds")
    
    st.write("---")
    
    # Security Password
    password = st.text_input("Enter Staff Password", type="password")
    
    submit_button = st.form_submit_button("SAVE SCORE TO LEADERBOARD")

# 5. Logic to Save Data
if submit_button:
    if password == "HN2026":  # You can change this password
        try:
            # Create a dataframe for the new entry
            new_entry = pd.DataFrame([{
                "Athlete_ID": int(athlete_id),
                "Workout": workout,
                "Score": int(score),
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # Read existing scores first
            existing_data = conn.read()
            
            # Combine old data with the new score
            updated_df = pd.concat([existing_data, new_entry], ignore_index=True)
            
            # Write back to Google Sheets
            conn.update(data=updated_df)
            
            st.success(f"Successfully saved score for Athlete #{athlete_id}!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Something went wrong: {e}")
            st.info("Check if your Google Sheet headers match: Athlete_ID, Workout, Score, Timestamp")
    else:
        st.error("Incorrect Password! Access Denied.")

# 6. Admin View (Optional: Shows the last 5 scores submitted)
st.write("---")
if st.checkbox("Show Recent Submissions"):
    try:
        data = conn.read()
        st.dataframe(data.tail(5))
    except:
        st.write("No data found yet.")
