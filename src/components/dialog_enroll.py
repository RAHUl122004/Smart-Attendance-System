import streamlit as st
import time
from src.database.db import enroll_student_to_subject
from src.database.config import supabase

@st.dialog("Enroll in Subject")
def enroll_dialog():
    student_data = st.session_state.get('student_data')
    if not student_data:
        st.error("Please login first.")
        return

    student_id = student_data['student_id']
    st.write("Enter the Subject Code provided by your teacher:")
    
    subject_code = st.text_input("Subject Code", placeholder="e.g. CS101")

    if st.button("Enroll Now", type='primary', width='stretch'):
        if not subject_code or not subject_code.strip():
            st.warning("Please enter a subject code.")
            return

        code = subject_code.strip()
        try:
            res = supabase.table('subjects').select('subject_id, name, section').eq('subject_code', code).execute()
            if not res.data:
                st.error("Subject code not found! Please verify the code with your teacher.")
                return

            subject = res.data[0]
            check = supabase.table('subject_students').select('*').eq('subject_id', subject['subject_id']).eq('student_id', student_id).execute()
            if check.data:
                st.info(f"You are already enrolled in {subject['name']}!")
                return

            enroll_student_to_subject(student_id, subject['subject_id'])
            st.toast(f"Successfully enrolled in {subject['name']}!")
            st.success(f"Successfully enrolled in {subject['name']} ({subject.get('section', '')})!")
            time.sleep(1)
            st.rerun()
        except Exception as e:
            st.error(f"Error enrolling: {str(e)}")