import streamlit as st
import hashlib
from utils.db import get_supabase

if "student" not in st.session_state or st.session_state.student is None:
    st.warning("Please login from the main page.")
    st.stop()

student = st.session_state.student
sb = get_supabase()

st.title("⚙️ Settings")
st.subheader("Profile Information")
st.text_input("Name",  value=student["name"],  disabled=True)
st.text_input("Email", value=student["email"], disabled=True)

enrolled = student.get("enrolled_subjects", [])
st.subheader("Enrolled Subjects")
for s in enrolled:
    st.markdown(f"✅ **{s}**")

st.subheader("Change Password")
with st.form("change_password"):
    new_pass = st.text_input("New Password", type="password")
    confirm  = st.text_input("Confirm Password", type="password")
    if st.form_submit_button("Update Password", type="primary"):
        if new_pass != confirm:
            st.error("Passwords don't match!")
        elif len(new_pass) < 6:
            st.error("Password too short!")
        else:
            sb.table("students").update({
                "password_hash": hashlib.sha256(new_pass.encode()).hexdigest()
            }).eq("id", student["id"]).execute()
            st.success("✅ Password updated!")