import streamlit as st
import importlib.util
import os
from utils.auth import login_student, register_student
from utils.db import get_supabase
from dotenv import load_dotenv


load_dotenv()

# ─── Page Config ───────────────────────────────────────
st.set_page_config(
    page_title="Smart Study Planner",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── Session State Init ────────────────────────────────
if "student" not in st.session_state:
    st.session_state.student = None
if "nav_page" not in st.session_state:
    st.session_state.nav_page = "Dashboard"

# ─── Page Loader Helper ────────────────────────────────
def load_page(filename):
    """Dynamically load a page file from the pages/ directory."""
    path = os.path.join("pages", filename)
    if not os.path.exists(path):
        st.error(f"Page file not found: {path}")
        return
    spec = importlib.util.spec_from_file_location("page_module", path)
    mod  = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

# ─── Auth Page ─────────────────────────────────────────
def show_auth():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');
        * { font-family: 'DM Sans', sans-serif; }

        [data-testid="stSidebar"]       { display: none; }
        [data-testid="collapsedControl"] { display: none; }

        .block-container {
            max-width: 500px !important;
            padding: 3rem 2rem !important;
            margin: 0 auto !important;
        }
        .auth-header {
            background: linear-gradient(135deg, #0f0c29, #302b63, #24243e);
            padding: 2.5rem 2rem; border-radius: 20px; color: white;
            text-align: center; margin-bottom: 2rem;
        }
        .auth-header h1 {
            font-family: 'Syne', sans-serif;
            font-size: 2rem; margin: 0; font-weight: 800;
        }
        .auth-header p { opacity: 0.85; margin: 8px 0 0; font-size: 1rem; }

        .stTabs [data-baseweb="tab-list"] { gap: 8px; }
        .stTabs [data-baseweb="tab"] {
            border-radius: 8px 8px 0 0;
            padding: 8px 24px; font-weight: 600;
        }
        .stTextInput input {
            border-radius: 8px !important;
            padding: 10px 14px !important;
            font-size: 15px !important;
        }
        .stFormSubmitButton button {
            width: 100% !important;
            border-radius: 8px !important;
            padding: 12px !important;
            font-size: 16px !important;
            font-weight: 600 !important;
            margin-top: 8px !important;
        }
    </style>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="auth-header">
        <h1>🎓 Smart Study Planner</h1>
        <p>Master Python & C++ with structured learning</p>
    </div>
    """, unsafe_allow_html=True)

    tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])

    with tab1:
        with st.form("login_form"):
            email    = st.text_input("Email", placeholder="student@example.com")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login", use_container_width=True, type="primary")
            if submitted:
                student = login_student(email, password)
                if student:
                    st.session_state.student = student
                    st.session_state.nav_page = "Dashboard"
                    st.success("Welcome back! 🎉")
                    st.rerun()
                else:
                    st.error("Invalid email or password.")

    with tab2:
        with st.form("register_form"):
            name     = st.text_input("Full Name", placeholder="John Doe")
            email    = st.text_input("Email", placeholder="john@example.com")
            password = st.text_input("Password", type="password")
            confirm  = st.text_input("Confirm Password", type="password")
            submitted = st.form_submit_button("Register", use_container_width=True, type="primary")
            if submitted:
                if password != confirm:
                    st.error("Passwords don't match!")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    student = register_student(name, email, password)
                    if student:
                        st.session_state.student = student
                        st.session_state.nav_page = "Dashboard"
                        st.success("Account created! Welcome 🎉")
                        st.rerun()
                    else:
                        st.error("Email already exists.")

# ─── Main App Shell ────────────────────────────────────
def show_app():
    student = st.session_state.student

    with st.sidebar:
        st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@400;500&display=swap');

            [data-testid="stSidebar"] {
                background: linear-gradient(180deg, #0f0c29, #302b63) !important;
                min-width: 220px !important;
                max-width: 220px !important;
            }
            div[data-testid="stSidebarNav"] { display: none !important; }

            .nav-logo {
                text-align: center;
                padding: 1.5rem 1rem 1rem;
                border-bottom: 1px solid rgba(255,255,255,0.1);
                margin-bottom: 0.5rem;
            }
            .nav-logo h2 {
                font-family: 'Syne', sans-serif;
                color: white; font-size: 1.1rem;
                margin: 6px 0 0; font-weight: 700;
            }
            .nav-logo p {
                color: rgba(255,255,255,0.55);
                font-size: 0.78rem; margin: 3px 0 0;
            }
            .nav-avatar {
                width: 50px; height: 50px;
                background: linear-gradient(135deg, #667eea, #764ba2);
                border-radius: 50%;
                display: flex; align-items: center; justify-content: center;
                font-size: 1.3rem; margin: 0 auto 6px;
                box-shadow: 0 4px 15px rgba(102,126,234,0.5);
                font-family: 'Syne', sans-serif;
                font-weight: 800; color: white;
            }
            .nav-section-label {
                color: rgba(255,255,255,0.3);
                font-size: 10px; font-weight: 700;
                letter-spacing: 1.5px; text-transform: uppercase;
                padding: 10px 16px 4px;
            }
            /* All sidebar buttons */
            section[data-testid="stSidebar"] .stButton button {
                background: transparent !important;
                border: none !important;
                color: rgba(255,255,255,0.7) !important;
                text-align: left !important;
                padding: 9px 14px !important;
                border-radius: 10px !important;
                font-size: 13.5px !important;
                font-weight: 500 !important;
                width: 100% !important;
                transition: all 0.2s !important;
                font-family: 'DM Sans', sans-serif !important;
            }
            section[data-testid="stSidebar"] .stButton button:hover {
                background: rgba(255,255,255,0.08) !important;
                color: white !important;
                transform: translateX(3px) !important;
            }
            .nav-active button {
                background: linear-gradient(135deg, #667eea, #764ba2) !important;
                color: white !important;
                box-shadow: 0 4px 12px rgba(102,126,234,0.35) !important;
            }
            .nav-active button:hover {
                transform: none !important;
            }
            .logout-btn button {
                background: rgba(245,87,108,0.12) !important;
                color: #f5576c !important;
                border: 1px solid rgba(245,87,108,0.25) !important;
                margin-top: 6px !important;
            }
            .logout-btn button:hover {
                background: rgba(245,87,108,0.25) !important;
                transform: none !important;
            }
        </style>
        """, unsafe_allow_html=True)

        # ── Avatar & branding ──────────────────────────
        initials = student['name'][0].upper()
        st.markdown(f"""
        <div class="nav-logo">
            <div class="nav-avatar">{initials}</div>
            <h2>StudyPlanner</h2>
            <p>👋 {student['name']}</p>
        </div>
        """, unsafe_allow_html=True)

        # ── Nav items ──────────────────────────────────
        nav_items = [
            ("Dashboard",   "🏠", "Dashboard"),
            ("My Subjects", "📚", "My Subjects"),
            ("Topics",      "📌", "Topics"),
            ("Videos",      "🎬", "Videos"),
            ("Assignments", "📝", "Assignments"),
            ("Cheatsheets", "📄", "Cheatsheets"),
            ("Study Plan",  "🧠", "Study Plan"),
            ("Settings",    "⚙️",  "Settings"),
        ]

        st.markdown('<div class="nav-section-label">Menu</div>', unsafe_allow_html=True)

        for key, icon, label in nav_items:
            is_active = st.session_state.nav_page == key
            st.markdown(f'<div class="{"nav-active" if is_active else ""}">', unsafe_allow_html=True)
            if st.button(f"{icon}  {label}", key=f"nav_{key}", use_container_width=True):
                st.session_state.nav_page = key
                st.rerun()
            st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="nav-section-label" style="margin-top:0.8rem;">Account</div>',
                    unsafe_allow_html=True)
        st.markdown('<div class="logout-btn">', unsafe_allow_html=True)
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True):
            st.session_state.student = None
            st.session_state.nav_page = "Dashboard"
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

    # ── Route to page files ───────────────────────────
    page = st.session_state.nav_page

    PAGE_MAP = {
        "Dashboard":   "Dashboard.py",
        "My Subjects": "Subjects.py",
        "Topics":      "Topics.py",
        "Videos":      "Videos.py",
        "Assignments": "Assignments.py",
        "Cheatsheets": "Cheatsheets.py",
        "Study Plan":  "Study_Plan.py",
        "Settings":    "Settings.py",
    }

    filename = PAGE_MAP.get(page)
    if filename:
        load_page(filename)
    else:
        st.error(f"Unknown page: {page}")


# ─── Settings Page (inline fallback if no 8_Settings.py) ──
def show_settings_inline():
    sb = get_supabase()
    student = st.session_state.student

    st.title("⚙️ Settings")
    st.subheader("Profile Information")
    st.text_input("Name",  value=student["name"],  disabled=True)
    st.text_input("Email", value=student["email"], disabled=True)

    enrolled = student.get("enrolled_subjects", [])
    st.subheader("Enrolled Subjects")
    if enrolled:
        for s in enrolled:
            st.markdown(f"✅ **{s}**")
    else:
        st.info("Not enrolled in any subject yet.")

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
                import hashlib
                sb.table("students").update({
                    "password_hash": hashlib.sha256(new_pass.encode()).hexdigest()
                }).eq("id", student["id"]).execute()
                st.success("✅ Password updated!")

# ─── Main Entry ────────────────────────────────────────
if st.session_state.student is None:
    show_auth()
else:
    show_app()