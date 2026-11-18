import streamlit as st
from src.database.config import supabase
import bcrypt

def handle_db_error(e):
    err_msg = str(e)
    if "PGRST205" in err_msg or "schema cache" in err_msg:
        st.error("⚠️ **Database tables not found in Supabase!**\nPlease run the provided `schema.sql` script in your Supabase SQL Editor (https://supabase.com/dashboard/project/qjjkkuefxcvhjlrpynyx/sql/new).")
    else:
        st.error(f"Database error: {err_msg}")

def hash_pass(pwd):
    return bcrypt.hashpw(pwd.encode(), bcrypt.gensalt()).decode()

def check_pass(pwd, hashed):
    return bcrypt.checkpw(pwd.encode(), hashed.encode())

def check_teacher_exists(username):
    try:
        response = supabase.table("teachers").select("username").eq("username", username).execute()
        return len(response.data) > 0
    except Exception as e:
        handle_db_error(e)
        return False

def create_teacher(username, password, name):
    try:
        data = {"username": username, "password": hash_pass(password), "name": name}
        response = supabase.table("teachers").insert(data).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        raise e

def teacher_login(username, password):
    try:
        response = supabase.table("teachers").select("*").eq("username", username).execute()
        if response.data:
            teacher = response.data[0]
            if check_pass(password, teacher['password']):
                return teacher
        return None
    except Exception as e:
        handle_db_error(e)
        return None

def get_all_students():
    try:
        response = supabase.table('students').select("*").execute()
        return response.data or []
    except Exception as e:
        handle_db_error(e)
        return []

def create_student(new_name, face_embedding=None, voice_embedding=None):
    try:
        data = {'name': new_name, 'face_embedding': face_embedding, "voice_embedding": voice_embedding}
        response = supabase.table('students').insert(data).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        return None

def create_subject(subject_code, name, section, teacher_id):
    try:
        data = {"subject_code": subject_code, "name": name, "section": section, "teacher_id": teacher_id}
        response = supabase.table("subjects").insert(data).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        raise e

def get_teacher_subjects(teacher_id):
    try:
        response = supabase.table('subjects').select("*, subject_students(count), attendance_logs(timestamp)").eq("teacher_id", teacher_id).execute()
        subjects = response.data or []

        for sub in subjects:
            sub['total_students'] = sub.get("subject_students", [{}])[0].get('count', 0) if sub.get('subject_students') else 0
            attendance = sub.get('attendance_logs', [])
            unique_sessions = len(set(log['timestamp'] for log in attendance))
            sub['total_classes'] = unique_sessions

            sub.pop('subject_students', None)
            sub.pop('subject_student', None)
            sub.pop('attendance_logs', None)

        return subjects
    except Exception as e:
        handle_db_error(e)
        return []

def enroll_student_to_subject(student_id, subject_id):
    try:
        data = {'student_id': student_id, "subject_id": subject_id}
        response = supabase.table('subject_students').insert(data).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        return None

def unenroll_student_to_subject(student_id, subject_id):
    try:
        response = supabase.table('subject_students').delete().eq('student_id', student_id).eq('subject_id', subject_id).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        return None

def get_student_subjects(student_id):
    try:
        response = supabase.table('subject_students').select('*, subjects(*)').eq('student_id', student_id).execute()
        return response.data or []
    except Exception as e:
        handle_db_error(e)
        return []

def get_student_attendance(student_id):
    try:
        response = supabase.table('attendance_logs').select('*, subjects(*)').eq('student_id', student_id).execute()
        return response.data or []
    except Exception as e:
        handle_db_error(e)
        return []

def create_attendance(logs):
    try:
        response = supabase.table('attendance_logs').insert(logs).execute()
        return response.data
    except Exception as e:
        handle_db_error(e)
        raise e

def get_attendance_for_teacher(teacher_id):
    try:
        response = supabase.table('attendance_logs').select("*, subjects!inner(*)").eq('subjects.teacher_id', teacher_id).execute()
        return response.data or []
    except Exception as e:
        handle_db_error(e)
        return []
