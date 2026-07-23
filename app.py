import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import plotly.express as px

# Database setup
DB_PATH = 'observations.db'

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY,
        name TEXT,
        sub_school TEXT,
        faculty TEXT,
        grade_level TEXT,
        subject TEXT,
        UNIQUE(name, sub_school, faculty, grade_level, subject)
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS observations (
        obs_id INTEGER PRIMARY KEY,
        teacher_id INTEGER,
        date TEXT,
        observer TEXT,
        academic_progress TEXT,
        what_worked_well TEXT,
        next_steps TEXT,
        FOREIGN KEY(teacher_id) REFERENCES teachers(teacher_id)
    )''')
    
    conn.commit()
    conn.close()

init_db()

st.set_page_config(page_title="TILP Observation System", layout="wide")

# Sidebar
st.sidebar.title("TILP Observation Tool")
st.sidebar.info("Australian International School")

page = st.sidebar.selectbox("Select Page", ["Observer Entry", "Admin Dashboard", "Data Upload"])

def get_teachers_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("SELECT * FROM teachers", conn)
    conn.close()
    return df

def get_observations_df():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query("""
        SELECT o.*, t.name, t.sub_school, t.faculty, t.grade_level, t.subject 
        FROM observations o 
        JOIN teachers t ON o.teacher_id = t.teacher_id
    """, conn)
    conn.close()
    return df

# Observer Entry
if page == "Observer Entry":
    st.title("Teacher Observation Entry")
    
    teachers_df = get_teachers_df()
    
    if len(teachers_df) == 0:
        st.warning("No teachers loaded. Go to Admin → Data Upload first.")
    else:
        sub_schools = ['All'] + sorted(teachers_df['sub_school'].dropna().unique().tolist())
        selected_sub = st.selectbox("Sub School", sub_schools)
        
        filtered = teachers_df
        if selected_sub != 'All':
            filtered = filtered[filtered['sub_school'] == selected_sub]
        
        faculties = ['All'] + sorted(filtered['faculty'].dropna().unique().tolist())
        selected_fac = st.selectbox("Faculty", faculties)
        
        if selected_fac != 'All':
            filtered = filtered[filtered['faculty'] == selected_fac]
        
        grades = ['All'] + sorted(filtered['grade_level'].dropna().unique().tolist())
        selected_grade = st.selectbox("Grade Level", grades)
        
        if selected_grade != 'All':
            filtered = filtered[filtered['grade_level'] == selected_grade]
        
        subjects = ['All'] + sorted(filtered['subject'].dropna().unique().tolist())
        selected_subj = st.selectbox("Subject", subjects)
        
        if selected_subj != 'All':
            filtered = filtered[filtered['subject'] == selected_subj]
        
        teacher_list = sorted(filtered['name'].unique().tolist())
        selected_teacher = st.selectbox("Teacher", teacher_list)
        
        teacher_row = teachers_df[teachers_df['name'] == selected_teacher].iloc[0]
        teacher_id = teacher_row['teacher_id']
        
        st.subheader(f"Observation for {selected_teacher}")
        
        date = st.date_input("Observation Date", datetime.today())
        observer = st.text_input("Your Name (Observer)", "Observer Name")
        
        academic_progress = st.selectbox(
            "Academic Progress (Mandatory)", 
            ["Emerging", "Progressing", "Thriving", "Beyond Thriving"]
        )
        
        what_worked = st.text_area("What worked well")
        next_steps = st.text_area("Next Steps")
        
        if st.button("Submit Observation"):
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("""INSERT INTO observations 
                        (teacher_id, date, observer, academic_progress, what_worked_well, next_steps)
                        VALUES (?, ?, ?, ?, ?, ?)""",
                     (int(teacher_id), str(date), observer, academic_progress, what_worked, next_steps))
            conn.commit()
            conn.close()
            st.success("✅ Observation saved successfully!")

# Admin Dashboard
elif page == "Admin Dashboard":
    st.title("Admin Dashboard")
    obs_df = get_observations_df()
    
    if len(obs_df) > 0:
        st.metric("Total Observations", len(obs_df))
        
        st.subheader("Academic Progress Distribution")
        fig = px.histogram(obs_df, x="academic_progress", color="sub_school")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("All Observations")
        st.dataframe(obs_df)
        
        csv = obs_df.to_csv(index=False)
        st.download_button("Download as CSV", csv, "observations.csv")
    else:
        st.info("No observations yet.")

# Data Upload
elif page == "Data Upload":
    st.title("Upload Teachers")
    
    uploaded_file = st.file_uploader("Upload Teachers Excel file", type=["xlsx"])
    if uploaded_file:
        df = pd.read_excel(uploaded_file)
        conn = sqlite3.connect(DB_PATH)
        df.to_sql('teachers', conn, if_exists='append', index=False)
        conn.close()
        st.success("Teachers uploaded!")
    
    if st.button("Download Template"):
        template = pd.DataFrame(columns=['name', 'sub_school', 'faculty', 'grade_level', 'subject'])
        template.to_excel('template.xlsx', index=False)
        with open('template.xlsx', 'rb') as f:
            st.download_button("Download Template", f, "teachers_template.xlsx")

st.sidebar.caption("Made for Australian International School")
