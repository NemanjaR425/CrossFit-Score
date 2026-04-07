import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# 1. Page Setup (Optimized for mobile phones)
st.set_page_config(page_title="Judge Score Entry", layout="centered")

st.title("🏆 Event Score Entry")
st.write("Judges: Enter athlete results below.")

# 2. Connect to your Google Sheet
# Make sure your 'Secrets' in Streamlit Cloud has the correct URL!
conn = st.connection("gsheets", type=GSheetsConnection)

# 3. The Entry Form
with st.form("score_form", clear_on_submit=True):
    # Athlete Number (1-100)
    athlete_id = st.number_input("Athlete Number", min_value=1, max_value=100, step=1)
    
    # Workout Selection
    workout = st.selectbox("Select WOD", ["WOD 1", "WOD 2", "WOD 3"])
    
    # Score Entry (Change 'label' to match your workout type)
    score = st.number_input("Result (Total Reps or Total Seconds)", min_value=0, step=1)
    
    # Simple Password to prevent random people from entering scores
    password = st.text_input("Staff Password", type="password")

    submit_button = st.form_submit_button("SUBMIT SCORE")

if submit_button:
    if password == "HN2026": # Change this to whatever password you want
        try:
            # Prepare the new row
            new_row = pd.DataFrame([{
                "Athlete_ID": athlete_id,
                "Workout": workout,
                "Score": score,
                "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])
            
            # Read existing data and add the new row
            existing_data = conn.read()
            updated_df = pd.concat([existing_data, new_row], ignore_index=True)
            
            # Save back to Google Sheets
           conn.update(data=updated_df)
            
            st.success(f"Score for Athlete #{athlete_id} saved!")
            st.balloons()
            
        except Exception as e:
            st.error(f"Error: {e}")
            st.info("Check if your Google Sheet is shared as 'Editor' with 'Anyone with the link'.")
    else:
        st.error("Incorrect Password")
