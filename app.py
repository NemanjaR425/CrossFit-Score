import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# Set page to mobile-friendly wide mode
st.set_page_config(page_title="Judge Entry", layout="centered")

st.title("⏱️ Score Entry")

# 1. Connect to Google Sheets
# You'll need to set up a 'secrets.toml' file with your sheet URL
conn = st.connection("gsheets", type=GSheetsConnection)

# 2. Setup Form
with st.form("score_form", clear_on_submit=True):
    st.subheader("Enter Athlete Result")
    
    # Athlete Selection (Using ID numbers is faster for judges)
    athlete_id = st.number_input("Athlete Number", min_value=1, max_value=100, step=1)
    athlete_name = st.text_input("Athlete Name (Optional confirmation)")
    
    # Workout Selection
    workout = st.selectbox("Select WOD", ["WOD 1: 21-15-9", "WOD 2: AMRAP 12", "WOD 3: Max Clean"])
    
    # Score Entry
    col1, col2 = st.columns(2)
    with col1:
        minutes = st.number_input("Minutes", min_value=0, max_value=60, step=1)
    with col2:
        seconds = st.number_input("Seconds/Reps", min_value=0, max_value=500, step=1)

    submitted = st.form_submit_button("SUBMIT SCORE")

    if submitted:
        # Create a new row of data
        new_data = pd.DataFrame([{
            "Athlete_ID": athlete_id,
            "Name": athlete_name,
            "Workout": workout,
            "Score_Raw": (minutes * 60) + seconds, # Convert to total seconds/reps for easy math
            "Timestamp": pd.Timestamp.now()
        }])
        
        # Append to Google Sheet
        try:
            # Note: This requires 'Write' permissions set in your secrets
            existing_data = conn.read(worksheet="Scores")
            updated_df = pd.concat([existing_data, new_data], ignore_index=True)
            conn.update(worksheet="Scores", data=updated_df)
            st.success(f"Score for #{athlete_id} saved successfully!")
            st.balloons()
        except Exception as e:
            st.error(f"Error saving score: {e}")
