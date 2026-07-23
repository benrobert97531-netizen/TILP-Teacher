import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px

st.set_page_config(page_title="TILP Observation System", layout="wide")

# Initialize data in session state (works on Streamlit Cloud)
if 'teachers' not in st.session_state:
    st.session_state.teachers = pd.DataFrame(columns=['name', 'sub_school', 'faculty', 'grade_level', 'subject'])
if 'observations' not in st.session_state:
    st.session_state.observations = pd.DataFrame(columns=['date', 'observer', 'teacher', 'academic_progress', 'what_worked_well', 'next_steps'])

st.sidebar.title("TILP Observation Tool")
st.sidebar.info("Australian International School & Cognita")

page = st.sidebar.selectbox("Select Page", ["Observer Entry", "Admin Dashboard", "Data Upload"])

# Observer Entry Page
if page == "Observer Entry":
    st.title("Teacher Observation Entry")
    
    if len(st.session_state.teachers) == 0:
        st.warning("No teachers loaded yet. Go to 'Data Upload' first.")
    else:
        df = st.session_state.teachers
        sub_schools = ['All'] + sorted(df['sub_school'].dropna().unique().tolist())
        selected_sub = st.selectbox("Sub School", sub_schools)
        
        filtered = df.copy()
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
        
        st.subheader(f"Observation for {selected_teacher}")
        
        date = st.date_input("Observation Date", datetime.today())
        observer = st.text_input("Observer Name", "Your Name")
        
        academic_progress = st.selectbox("Academic Progress (Mandatory)", 
                                       ["Emerging", "Progressing", "Thriving", "Beyond Thriving"])
        
        what_worked = st.text_area("What worked well")
        next_steps = st.text_area("Next Steps")
        
        if st.button("Submit Observation"):
            new_obs = pd.DataFrame([{
                'date': str(date),
                'observer': observer,
                'teacher': selected_teacher,
                'academic_progress': academic_progress,
                'what_worked_well': what_worked,
                'next_steps': next_steps
            }])
            st.session_state.observations = pd.concat([st.session_state.observations, new_obs], ignore_index=True)
            st.success("✅ Observation saved!")

# Admin Dashboard
elif page == "Admin Dashboard":
    st.title("Admin Dashboard")
    obs = st.session_state.observations
    
    if len(obs) > 0:
        st.metric("Total Observations", len(obs))
        
        fig = px.histogram(obs, x="academic_progress", title="Academic Progress Distribution")
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("All Observations")
        st.dataframe(obs)
        
        st.download_button("Download Data as CSV", obs.to_csv(index=False), "observations.csv")
    else:
        st.info("No observations yet.")

# Data Upload
elif page == "Data Upload":
    st.title("Upload Teachers")
    
    uploaded_file = st.file_uploader("Upload Teachers Excel (columns: name, sub_school, faculty, grade_level, subject)", type=["xlsx"])
    if uploaded_file:
        new_data = pd.read_excel(uploaded_file)
        st.session_state.teachers = pd.concat([st.session_state.teachers, new_data], ignore_index=True)
        st.success(f"Added {len(new_data)} teacher records!")
    
    if st.button("Download Template"):
        template = pd.DataFrame(columns=['name', 'sub_school', 'faculty', 'grade_level', 'subject'])
        st.download_button("Download teachers_template.xlsx", template.to_csv(index=False), "teachers_template.csv")

st.caption("TILP Maturity Rubric System")
