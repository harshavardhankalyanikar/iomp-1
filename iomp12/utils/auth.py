import hashlib
import streamlit as st
from utils.db import get_supabase

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_student(name, email, password):
    sb = get_supabase()
    try:
        result = sb.table("students").insert({
            "name": name,
            "email": email,
            "password_hash": hash_password(password),
            "enrolled_subjects": []
        }).execute()
        return result.data[0] if result.data else None
    except Exception as e:
        return None

def login_student(email, password):
    sb = get_supabase()
    result = sb.table("students").select("*").eq("email", email).eq(
        "password_hash", hash_password(password)
    ).execute()
    return result.data[0] if result.data else None

def enroll_subject(student_id, subject_name, current_subjects):
    sb = get_supabase()
    if subject_name not in current_subjects:
        updated = current_subjects + [subject_name]
        sb.table("students").update(
            {"enrolled_subjects": updated}
        ).eq("id", student_id).execute()
        return updated
    return current_subjects