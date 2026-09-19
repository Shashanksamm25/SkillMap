"""
app.py — SkillMap Pro  (Single-file, Final Year Project Edition)
Run:  python -m streamlit run app.py
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import hashlib, requests, re, time, os, smtplib
from datetime import datetime, timedelta
from urllib.parse import quote_plus
from email.mime.text import MIMEText
from dotenv import load_dotenv
from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    DateTime, Text, Boolean, text
)
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

st.set_page_config(
    page_title="SkillMap Pro",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────────────────────────────────────
# THEME — "Career Control Deck"  (light / dark)
# ─────────────────────────────────────────────────────────────────────────────
def inject_theme(theme="dark"):
    if theme == "light":
        vars_css = """
            --ink: #F5F6F9; --surface: #FFFFFF; --surface-2: #EEF0F4;
            --sidebar-bg: #FFFFFF; --sidebar-bottom: #EDEFF4;
            --hairline: #DFE2E9; --text: #14181F; --text-muted: #5B6472;
            --cyan: #0C7A6E; --blue: #3730A3; --amber: #A15A06;
            --green: #157347; --coral: #C0392B;
            --cyan-glow: rgba(12,122,110,0.06); --blue-glow: rgba(55,48,163,0.05);
            --grid-line: rgba(20,24,31,0.035); --shadow: rgba(15,23,42,0.10);
            --btn-grad-1: #14B8A6; --btn-grad-2: #4338CA; --btn-text: #FFFFFF;
        """
        px.defaults.template = "plotly_white"
    else:
        vars_css = """
            --ink: #0B0F14; --surface: #121820; --surface-2: #182029;
            --sidebar-bg: #121820; --sidebar-bottom: #0B0F14;
            --hairline: #232B35; --text: #E8EDF2; --text-muted: #8B98A5;
            --cyan: #2DD4BF; --blue: #5B8DEF; --amber: #F5A623;
            --green: #34D399; --coral: #FF6B6B;
            --cyan-glow: rgba(45,212,191,0.08); --blue-glow: rgba(91,141,239,0.07);
            --grid-line: rgba(45,212,191,0.05); --shadow: rgba(0,0,0,0.35);
            --btn-grad-1: #2DD4BF; --btn-grad-2: #5B8DEF; --btn-text: #06110F;
        """
        px.defaults.template = "plotly_dark"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600&display=swap');
    :root {{ {vars_css} }}

    html, body, .stApp {{ font-family: 'Inter', -apple-system, sans-serif !important; font-size: 15px; line-height: 1.55; }}

    .stApp {{
        background:
            radial-gradient(circle at 12% -10%, var(--cyan-glow) 0%, transparent 40%),
            radial-gradient(circle at 90% 0%, var(--blue-glow) 0%, transparent 45%),
            radial-gradient(var(--grid-line) 1px, transparent 1.4px),
            var(--ink) !important;
        background-size: auto, auto, 28px 28px, auto;
        color: var(--text);
    }}

    h1, h2, h3 {{ font-family: 'Inter', sans-serif !important; font-weight: 700; letter-spacing: -0.02em; color: var(--text) !important; }}
    p, span, li, label {{ color: var(--text); }}

    section[data-testid="stSidebar"] {{
        background: linear-gradient(180deg, var(--sidebar-bg) 0%, var(--sidebar-bottom) 100%) !important;
        border-right: 1px solid var(--hairline);
        box-shadow: 3px 0 16px var(--shadow);
    }}
    section[data-testid="stSidebar"] * {{ color: var(--text); }}

    .stButton > button, .stFormSubmitButton > button, .stLinkButton a {{
        border-radius: 10px !important; font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important; border: 1px solid var(--hairline) !important;
        transition: all .15s ease !important;
    }}
    .stButton > button[kind="secondary"], .stFormSubmitButton > button[kind="secondary"] {{
        background: var(--surface) !important; color: var(--text) !important;
    }}
    .stButton > button[kind="secondary"]:hover {{ border-color: var(--cyan) !important; color: var(--cyan) !important; }}
    .stButton > button[kind="primary"], .stFormSubmitButton > button[kind="primary"], .stLinkButton a[kind="primary"] {{
        background: linear-gradient(135deg, var(--btn-grad-1), var(--btn-grad-2)) !important;
        color: var(--btn-text) !important; border: none !important; font-weight: 600 !important;
        box-shadow: 0 8px 20px -10px var(--shadow);
    }}
    .stButton > button[kind="primary"]:hover, .stFormSubmitButton > button[kind="primary"]:hover {{
        filter: brightness(1.08); transform: translateY(-1px);
    }}

    .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div {{
        background: var(--surface-2) !important; border: 1px solid var(--hairline) !important;
        border-radius: 8px !important; color: var(--text) !important;
    }}
    .stTextInput input:focus, .stTextArea textarea:focus {{
        border-color: var(--cyan) !important; box-shadow: 0 0 0 1px var(--cyan) !important;
    }}
    ul[data-baseweb="menu"] {{ background: var(--surface-2) !important; border: 1px solid var(--hairline) !important; }}
    li[role="option"] {{ color: var(--text) !important; }}
    li[role="option"]:hover, li[aria-selected="true"] {{ background: var(--cyan-glow) !important; color: var(--cyan) !important; }}

    .stTabs [data-baseweb="tab-list"] {{ gap: 6px; border-bottom: 1px solid var(--hairline); }}
    .stTabs [data-baseweb="tab"] {{ font-family: 'Inter', sans-serif; color: var(--text-muted); font-weight: 600; }}
    .stTabs [aria-selected="true"] {{ color: var(--cyan) !important; }}
    .stTabs [data-baseweb="tab-highlight"] {{ background-color: var(--cyan) !important; }}

    div[data-testid="stVerticalBlockBorderWrapper"] {{
        background: var(--surface) !important; border: 1px solid var(--hairline) !important;
        border-radius: 14px !important; box-shadow: 0 1px 3px var(--shadow);
    }}

    div[data-testid="stExpander"] {{
        background: var(--surface); border: 1px solid var(--hairline);
        border-radius: 12px; overflow: hidden; transition: all .15s ease;
        box-shadow: 0 1px 3px var(--shadow);
    }}
    div[data-testid="stExpander"]:hover {{ border-color: var(--cyan); box-shadow: 0 4px 14px var(--shadow); }}

    div[data-testid="stMetric"] {{
        background: var(--surface); border: 1px solid var(--hairline);
        border-radius: 12px; padding: 12px 16px; box-shadow: 0 1px 3px var(--shadow);
    }}
    div[data-testid="stMetricValue"] {{ font-family: 'JetBrains Mono', monospace !important; color: var(--text) !important; }}
    div[data-testid="stMetricLabel"] {{ color: var(--text-muted) !important; }}

    div[data-testid="stAlert"] {{ border-radius: 10px !important; }}
    div[data-testid="stDataFrame"] {{ border: 1px solid var(--hairline); border-radius: 10px; overflow: hidden; }}

    div[data-testid="stToggle"] label div[aria-checked="true"] {{ background: var(--blue) !important; }}
    div[data-testid="stToggle"] p {{ font-weight: 600 !important; font-size: 13.5px !important; color: var(--text) !important; }}

    .theme-card {{
        background: var(--surface); border: 1.5px solid var(--hairline); border-radius: 12px;
        padding: 4px 14px 2px; margin-bottom: 14px; box-shadow: 0 3px 10px var(--shadow);
    }}
    .theme-card-label {{
        font-size: 11px; font-weight: 700; text-transform: uppercase; letter-spacing: .07em;
        color: var(--text-muted); padding-top: 10px;
    }}

    .brand-row {{ display:flex; align-items:center; gap:10px; margin: 4px 0 16px; }}
    .brand-mark {{
        width:38px; height:38px; border-radius:10px; background: linear-gradient(135deg, var(--btn-grad-1), var(--btn-grad-2));
        display:flex; align-items:center; justify-content:center;
        font-family:'Inter', sans-serif; font-weight:700; color:var(--btn-text); font-size:14px;
    }}
    .brand-name {{ font-family:'Inter', sans-serif; font-weight:600; font-size:15px; color:var(--text); line-height:1.1; }}
    .brand-sub {{ font-size:11px; color:var(--text-muted); }}

    .project-title-band {{
        text-align:center; padding: 2px 0 26px; margin-bottom: 6px;
        border-bottom: 1px solid var(--hairline);
    }}
    .project-title-main {{
        font-family:'Inter', sans-serif; font-weight:800; font-size:32px;
        letter-spacing:-0.02em; color:var(--text); line-height:1.25;
    }}
    .project-title-sub {{
        font-size:12px; font-weight:600; letter-spacing:.1em; text-transform:uppercase;
        color:var(--text-muted); margin-top:8px;
    }}

    .user-badge {{
        display:flex; align-items:center; gap:10px; background: var(--surface); border:1px solid var(--hairline);
        border-radius:12px; padding:10px 12px; margin-bottom: 10px;
    }}
    .user-avatar {{
        width:34px; height:34px; border-radius:50%; background: var(--surface-2); border:1px solid var(--hairline);
        display:flex; align-items:center; justify-content:center;
        font-family:'Inter', sans-serif; font-weight:700; color:var(--cyan); font-size:14px;
    }}
    .user-name {{ font-weight:600; font-size:13.5px; color:var(--text); }}
    .user-role {{ font-size:10.5px; letter-spacing:.06em; color:var(--text-muted); }}
    .user-role.role-admin {{ color: var(--amber); }}

    .kpi-accent {{ height:3px; border-radius:3px; margin:-14px -14px 12px -14px; }}
    .kpi-label {{ font-family:'Inter', sans-serif; font-size:11.5px; text-transform:uppercase; letter-spacing:.06em; color: var(--text-muted); margin-bottom:4px; }}
    .kpi-value {{ font-family:'JetBrains Mono', monospace; font-size:26px; font-weight:600; color:var(--text); }}

    .pipe-wrap {{ margin: 16px 0 20px; }}
    .pipe-track {{ display:flex; align-items:center; }}
    .pipe-dot {{ width:13px; height:13px; border-radius:50%; flex-shrink:0; }}
    .pipe-line {{ flex:1; height:2px; background: var(--hairline); }}
    .pipe-labels {{ display:flex; justify-content:space-between; margin-top:8px; }}
    .pipe-labels > div {{ flex:1; text-align:center; font-family:'Inter', sans-serif; font-size:10.5px; text-transform:uppercase; letter-spacing:.05em; color:var(--text-muted); }}
    .pipe-count {{ display:block; font-family:'JetBrains Mono', monospace; font-size:14px; color:var(--text); margin-top:3px; }}

    .brand-badge {{
        display:inline-block; font-family:'JetBrains Mono', monospace; font-size:11px; letter-spacing:.12em;
        color: var(--cyan); border:1px solid var(--cyan); background: var(--cyan-glow); padding:4px 10px; border-radius:999px;
    }}
    </style>
    """, unsafe_allow_html=True)

PIPE_STAGES = [
    ("saved", "Saved", "#8B98A5"), ("applied", "Applied", "#F5A623"),
    ("interviewing", "Interviewing", "#5B8DEF"), ("offer", "Offer", "#34D399"),
    ("rejected", "Rejected", "#FF6B6B"),
]

def render_pipeline_strip(counts=None):
    dots = ""
    for i, (key, label, color) in enumerate(PIPE_STAGES):
        dots += f'<div class="pipe-dot" style="background:{color}; box-shadow:0 0 10px {color}88;"></div>'
        if i < len(PIPE_STAGES) - 1:
            dots += '<div class="pipe-line"></div>'
    labels = ""
    for key, label, color in PIPE_STAGES:
        count_html = f'<span class="pipe-count">{counts.get(key, 0)}</span>' if counts is not None else ""
        labels += f"<div>{label}{count_html}</div>"
    st.markdown(f'<div class="pipe-wrap"><div class="pipe-track">{dots}</div><div class="pipe-labels">{labels}</div></div>', unsafe_allow_html=True)

def kpi_card(col, label, value, accent, icon=""):
    with col:
        with st.container(border=True):
            st.markdown(f'<div class="kpi-accent" style="background:{accent};"></div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-label">{icon} {label}</div>', unsafe_allow_html=True)
            st.markdown(f'<div class="kpi-value">{value}</div>', unsafe_allow_html=True)

def render_hero_art(size=180):
    st.markdown(f"""
        <div style="display:flex; justify-content:center;">
        <svg width="{size}" height="{size}" viewBox="0 0 180 180" fill="none" xmlns="http://www.w3.org/2000/svg">
          <circle cx="90" cy="90" r="80" stroke="var(--hairline)" stroke-width="1.5"/>
          <circle cx="90" cy="90" r="55" stroke="var(--hairline)" stroke-width="1.5"/>
          <circle cx="90" cy="90" r="30" stroke="var(--hairline)" stroke-width="1.5"/>
          <line x1="90" y1="10" x2="90" y2="170" stroke="var(--hairline)" stroke-width="1"/>
          <line x1="10" y1="90" x2="170" y2="90" stroke="var(--hairline)" stroke-width="1"/>
          <circle cx="90" cy="90" r="6" fill="var(--cyan)"/>
          <circle cx="130" cy="60" r="4.5" fill="var(--amber)"/>
          <circle cx="55" cy="120" r="4.5" fill="var(--blue)"/>
          <circle cx="140" cy="130" r="4" fill="var(--green)"/>
          <circle cx="45" cy="55" r="4" fill="var(--coral)"/>
        </svg>
        </div>
    """, unsafe_allow_html=True)

def render_project_title():
    """Big, centered project masthead shown at the top of every dashboard page."""
    st.markdown("""
        <div class="project-title-band">
            <div class="project-title-main">Job Market Data Scraper &amp; Analytics Dashboard</div>
            <div class="project-title-sub">SkillMap Pro &middot; Career Control Deck</div>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# ORM MODELS
# ─────────────────────────────────────────────────────────────────────────────
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    id            = Column(Integer, primary_key=True, autoincrement=True)
    username      = Column(String(100), unique=True, nullable=False)
    email         = Column(String(200), unique=True, nullable=False)
    password      = Column(String(255), nullable=False)
    role          = Column(String(20),  default="user")
    created_at    = Column(DateTime,    default=datetime.utcnow)
    is_active     = Column(Boolean,     default=True)
    resume_skills = Column(Text,        nullable=True)
    notify_email  = Column(Boolean,     default=False)
    last_login    = Column(DateTime,    nullable=True)

class JobPosting(Base):
    __tablename__ = "job_postings"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(255), nullable=False)
    company     = Column(String(255), nullable=False)
    location    = Column(String(255))
    job_type    = Column(String(100))
    salary_min  = Column(Float,       nullable=True)
    salary_max  = Column(Float,       nullable=True)
    description = Column(Text,        nullable=True)
    tags        = Column(String(500))
    source      = Column(String(100))
    url         = Column(String(500), unique=True)
    scraped_at  = Column(DateTime,    default=datetime.utcnow)
    status      = Column(String(50),  default="open")

class JobSkill(Base):
    __tablename__ = "job_skills"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    job_id     = Column(Integer, nullable=False)
    skill_name = Column(String(100), nullable=False)

class ScrapeLog(Base):
    __tablename__ = "scrape_logs"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    source     = Column(String(100))
    jobs_found = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    status     = Column(String(50))
    error_msg  = Column(Text, nullable=True)
    ran_at     = Column(DateTime, default=datetime.utcnow)

class UserApplication(Base):
    __tablename__ = "user_applications"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    user_id    = Column(Integer, nullable=False)
    job_id     = Column(Integer, nullable=False)
    status     = Column(String(50), default="saved")
    notes      = Column(Text,    nullable=True)
    applied_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

# ─────────────────────────────────────────────────────────────────────────────
# ENGINE + SESSION
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_resource
def get_engine():
    pw  = quote_plus(os.getenv("DB_PASSWORD", ""))
    url = (
        f"postgresql://{os.getenv('DB_USER')}:{pw}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(url, echo=False, pool_pre_ping=True)

def get_session():
    return sessionmaker(bind=get_engine())()

# ─────────────────────────────────────────────────────────────────────────────
# MIGRATION
# ─────────────────────────────────────────────────────────────────────────────
def migrate_db():
    engine = get_engine()
    Base.metadata.create_all(engine)
    needed = [
        ("job_postings",   "tags",          "VARCHAR(500)"),
        ("job_postings",   "salary_min",     "FLOAT"),
        ("job_postings",   "salary_max",     "FLOAT"),
        ("job_postings",   "source",         "VARCHAR(100)"),
        ("job_postings",   "description",    "TEXT"),
        ("job_postings",   "status",         "VARCHAR(50) DEFAULT 'open'"),
        ("users",          "resume_skills",  "TEXT"),
        ("users",          "notify_email",   "BOOLEAN DEFAULT FALSE"),
        ("users",          "last_login",     "TIMESTAMP"),
    ]
    with engine.begin() as conn:
        for table, col, col_type in needed:
            exists = conn.execute(text(
                "SELECT 1 FROM information_schema.columns "
                "WHERE table_name=:t AND column_name=:c"
            ), {"t": table, "c": col}).fetchone()
            if not exists:
                conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}"))

# ─────────────────────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────────────────────
def hash_pw(p: str) -> str:
    return hashlib.sha256(f"skillmap_salt_2024{p}".encode()).hexdigest()

def seed_admin():
    session = get_session()
    try:
        h = hash_pw("admin123")
        a = session.query(User).filter_by(username="admin").first()
        if a is None:
            session.add(User(username="admin", email="admin@skillmap.com",
                             password=h, role="admin", is_active=True))
        else:
            a.password = h; a.role = "admin"; a.is_active = True
        session.commit()
    except Exception as e:
        session.rollback()
        st.warning(f"seed_admin: {e}")
    finally:
        session.close()

def create_user(username, email, password, role="user"):
    session = get_session()
    try:
        if session.query(User).filter(
            (User.username == username) | (User.email == email)
        ).first():
            return False
        session.add(User(username=username, email=email,
                         password=hash_pw(password), role=role))
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def verify_login(username, password):
    session = get_session()
    try:
        u = session.query(User).filter_by(
            username=username, password=hash_pw(password), is_active=True
        ).first()
        if u:
            u.last_login = datetime.utcnow()
            session.commit()
            return {"id": u.id, "username": u.username,
                    "email": u.email, "role": u.role,
                    "resume_skills": u.resume_skills or "",
                    "notify_email": bool(u.notify_email)}
        return None
    finally:
        session.close()

def get_all_users():
    session = get_session()
    try:
        rows = []
        for u in session.query(User).all():
            app_count = session.execute(text(
                "SELECT COUNT(*) FROM user_applications WHERE user_id=:uid"
            ), {"uid": u.id}).scalar()
            rows.append({
                "ID": u.id, "Username": u.username, "Email": u.email,
                "Role": u.role, "Active": u.is_active,
                "Applications": app_count,
                "Last Login": u.last_login.strftime("%Y-%m-%d %H:%M") if u.last_login else "Never",
                "Created": u.created_at.strftime("%Y-%m-%d"),
            })
        return rows
    finally:
        session.close()

def toggle_user_status(uid):
    session = get_session()
    try:
        u = session.query(User).filter_by(id=uid).first()
        if u:
            u.is_active = not u.is_active
            session.commit()
    finally:
        session.close()

def save_resume_skills(user_id, skills_text):
    session = get_session()
    try:
        u = session.query(User).filter_by(id=user_id).first()
        if u:
            u.resume_skills = skills_text
            session.commit()
    finally:
        session.close()

def set_email_notify(user_id, val: bool):
    session = get_session()
    try:
        u = session.query(User).filter_by(id=user_id).first()
        if u:
            u.notify_email = val
            session.commit()
    finally:
        session.close()

# ─────────────────────────────────────────────────────────────────────────────
# APPLICATION TRACKER
# ─────────────────────────────────────────────────────────────────────────────
APP_STATUSES  = ["saved", "applied", "interviewing", "offer", "rejected"]
STATUS_COLORS = {"saved": "🔖", "applied": "📤", "interviewing": "💬", "offer": "🎉", "rejected": "❌"}

def upsert_application(user_id, job_id, status, notes=""):
    session = get_session()
    try:
        existing = session.query(UserApplication).filter_by(user_id=user_id, job_id=job_id).first()
        if existing:
            existing.status     = status
            existing.notes      = notes
            existing.updated_at = datetime.utcnow()
        else:
            session.add(UserApplication(user_id=user_id, job_id=job_id, status=status, notes=notes))
        session.commit()
        return True
    except Exception:
        session.rollback()
        return False
    finally:
        session.close()

def get_user_application(user_id, job_id):
    session = get_session()
    try:
        row = session.query(UserApplication).filter_by(user_id=user_id, job_id=job_id).first()
        if row:
            return {"status": row.status, "notes": row.notes or "",
                    "applied_at": row.applied_at, "updated_at": row.updated_at}
        return None
    finally:
        session.close()

def get_user_applications(user_id):
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql(text("""
            SELECT ua.id, ua.job_id, ua.status, ua.notes,
                   ua.applied_at, ua.updated_at,
                   jp.title, jp.company, jp.location,
                   jp.job_type, jp.url, jp.source, jp.tags
            FROM user_applications ua
            JOIN job_postings jp ON jp.id = ua.job_id
            WHERE ua.user_id = :uid
            ORDER BY ua.updated_at DESC
        """), conn, params={"uid": user_id})

def delete_application(user_id, job_id):
    session = get_session()
    try:
        row = session.query(UserApplication).filter_by(user_id=user_id, job_id=job_id).first()
        if row:
            session.delete(row)
            session.commit()
    finally:
        session.close()

# ─────────────────────────────────────────────────────────────────────────────
# VACANCY MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def set_job_status(job_id, status):
    session = get_session()
    try:
        j = session.query(JobPosting).filter_by(id=job_id).first()
        if j:
            j.status = status
            session.commit()
    finally:
        session.close()

# ─────────────────────────────────────────────────────────────────────────────
# SKILLS
# ─────────────────────────────────────────────────────────────────────────────
SKILLS = [
    "python","java","javascript","typescript","react","angular","vue","node",
    "django","flask","fastapi","sql","postgresql","mysql","mongodb","redis",
    "aws","azure","gcp","docker","kubernetes","git","linux","machine learning",
    "deep learning","tensorflow","pytorch","pandas","numpy","rest api",
    "graphql","microservices","agile","html","css","c++","go","rust","kotlin",
    "swift","r","scala","spark","hadoop","tableau","power bi","excel","nlp",
    "devops","ci/cd","spring","laravel","ruby","rails","php","data science",
    "computer vision","llm","openai","langchain","airflow","dbt","selenium",
]

def extract_skills(text: str) -> list:
    tl = text.lower()
    return [s for s in SKILLS if re.search(r"\b" + re.escape(s) + r"\b", tl)]

def match_score(user_skills: list, job_text: str) -> int:
    if not user_skills:
        return 0
    jt = job_text.lower()
    matched = sum(1 for s in user_skills if re.search(r"\b" + re.escape(s.strip().lower()) + r"\b", jt))
    return round(100 * matched / len(user_skills))

# ─────────────────────────────────────────────────────────────────────────────
# SCRAPERS
# ─────────────────────────────────────────────────────────────────────────────
def _save_jobs_batch(jobs: list, source: str, session) -> int:
    saved = 0
    for job in jobs:
        url = job.get("url", "")
        if not url:
            continue
        if session.query(JobPosting).filter_by(url=url).first():
            continue
        tags = job.get("tags", "") or ""
        desc = job.get("description", "") or ""
        new_job = JobPosting(
            title       = str(job.get("title",    "N/A"))[:255],
            company     = str(job.get("company",  "N/A"))[:255],
            location    = str(job.get("location", "Remote"))[:255],
            job_type    = str(job.get("job_type", "Full-time"))[:100],
            salary_min  = job.get("salary_min"),
            salary_max  = job.get("salary_max"),
            description = desc,
            tags        = str(tags)[:500],
            source      = source,
            url         = url[:500],
            scraped_at  = datetime.utcnow(),
            status      = "open",
        )
        session.add(new_job)
        session.flush()
        for skill in extract_skills(f"{new_job.title} {tags} {desc[:400]}"):
            session.add(JobSkill(job_id=new_job.id, skill_name=skill))
        saved += 1
    session.commit()
    return saved

def _fetch_arbeitnow(pages=3):
    jobs, errors = [], []
    for page in range(1, pages + 1):
        try:
            r = requests.get(f"https://www.arbeitnow.com/api/job-board-api?page={page}", timeout=15)
            r.raise_for_status()
            for j in r.json().get("data", []):
                tags = ", ".join(j.get("tags", []))
                jt   = (j.get("job_types") or ["Full-time"])[0]
                jobs.append({
                    "title": j.get("title", "N/A"), "company": j.get("company_name", "N/A"),
                    "location": j.get("location", "Remote"), "job_type": jt,
                    "description": j.get("description", ""), "tags": tags, "url": j.get("url", ""),
                })
            time.sleep(0.8)
        except Exception as e:
            errors.append(f"Arbeitnow p{page}: {e}")
    return jobs, errors

def _fetch_remoteok():
    jobs, errors = [], []
    try:
        headers = {"User-Agent": "SkillMap/2.0 (final year project)"}
        r = requests.get("https://remoteok.com/api", headers=headers, timeout=15)
        r.raise_for_status()
        for j in r.json():
            if not isinstance(j, dict) or not j.get("position"):
                continue
            tags = ", ".join(j.get("tags", []))
            jobs.append({
                "title": j.get("position", "N/A"), "company": j.get("company", "N/A"),
                "location": j.get("location") or "Remote", "job_type": "Remote",
                "description": j.get("description", ""), "tags": tags,
                "url": j.get("url", "") or f"https://remoteok.com/remote-jobs/{j.get('id','')}",
                "salary_min": j.get("salary_min"), "salary_max": j.get("salary_max"),
            })
    except Exception as e:
        errors.append(f"RemoteOK: {e}")
    return jobs, errors

def _fetch_adzuna(pages=2):
    jobs, errors = [], []
    app_id  = os.getenv("ADZUNA_APP_ID", "")
    app_key = os.getenv("ADZUNA_APP_KEY", "")
    if not app_id or not app_key:
        errors.append("Adzuna: ADZUNA_APP_ID / ADZUNA_APP_KEY not set in .env — skipped")
        return jobs, errors
    country = os.getenv("ADZUNA_COUNTRY", "gb")
    for page in range(1, pages + 1):
        try:
            r = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}",
                params={"app_id": app_id, "app_key": app_key, "results_per_page": 50},
                timeout=15,
            )
            r.raise_for_status()
            for j in r.json().get("results", []):
                jobs.append({
                    "title": j.get("title", "N/A"),
                    "company": j.get("company", {}).get("display_name", "N/A"),
                    "location": j.get("location", {}).get("display_name", "Remote"),
                    "job_type": j.get("contract_time", "Full-time"),
                    "description": j.get("description", ""),
                    "tags": j.get("category", {}).get("label", ""),
                    "url": j.get("redirect_url", ""),
                    "salary_min": j.get("salary_min"), "salary_max": j.get("salary_max"),
                })
            time.sleep(0.8)
        except Exception as e:
            errors.append(f"Adzuna p{page}: {e}")
    return jobs, errors

def run_scraper():
    session     = get_session()
    total_found = 0
    total_saved = 0
    all_errs    = []
    for src_name, fetch_fn in [("arbeitnow", _fetch_arbeitnow), ("remoteok", _fetch_remoteok), ("adzuna", _fetch_adzuna)]:
        log = ScrapeLog(source=src_name)
        try:
            jobs, errs = fetch_fn()
            all_errs.extend(errs)
            saved = _save_jobs_batch(jobs, src_name, session)
            log.jobs_found = len(jobs)
            log.jobs_saved = saved
            log.status     = "success"
            total_found   += len(jobs)
            total_saved   += saved
        except Exception as e:
            log.status    = "failed"
            log.error_msg = str(e)
            all_errs.append(f"{src_name}: {e}")
        session.add(log)
    session.commit()
    session.close()
    return total_saved, total_found, all_errs

# ─────────────────────────────────────────────────────────────────────────────
# EMAIL
# ─────────────────────────────────────────────────────────────────────────────
def send_new_jobs_email(to_email: str, new_count: int, sample_titles: list):
    host = os.getenv("SMTP_HOST", "")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER", "")
    pwd  = os.getenv("SMTP_PASS", "")
    if not all([host, user, pwd, to_email]):
        return False
    try:
        titles_html = "".join(f"<li>{t}</li>" for t in sample_titles[:5])
        body = f"<h2>SkillMap — {new_count} new jobs scraped!</h2><ul>{titles_html}</ul><p>Login to SkillMap to explore them.</p>"
        msg = MIMEText(body, "html")
        msg["Subject"] = f"SkillMap: {new_count} new jobs available"
        msg["From"]    = user
        msg["To"]      = to_email
        with smtplib.SMTP(host, port) as s:
            s.starttls()
            s.login(user, pwd)
            s.send_message(msg)
        return True
    except Exception:
        return False

# ─────────────────────────────────────────────────────────────────────────────
# DATA LOADERS
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(ttl=120)
def load_jobs():
    with get_engine().connect() as conn:
        return pd.read_sql("SELECT * FROM job_postings ORDER BY scraped_at DESC", conn)

@st.cache_data(ttl=120)
def load_skills_df(limit=20):
    with get_engine().connect() as conn:
        return pd.read_sql(
            f"SELECT skill_name, COUNT(*) AS count FROM job_skills GROUP BY skill_name ORDER BY count DESC LIMIT {limit}", conn
        )

@st.cache_data(ttl=120)
def load_logs():
    with get_engine().connect() as conn:
        return pd.read_sql("SELECT * FROM scrape_logs ORDER BY ran_at DESC LIMIT 30", conn)

# ─────────────────────────────────────────────────────────────────────────────
# SESSION STATE
# ─────────────────────────────────────────────────────────────────────────────
for _k, _v in [("user", None), ("page", None), ("last_visit", None), ("theme", "dark")]:
    if _k not in st.session_state:
        st.session_state[_k] = _v

# ─────────────────────────────────────────────────────────────────────────────
# THEME TOGGLE (always visible, top of sidebar, works pre-login too)
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    with st.container(border=True):
        st.markdown('<div class="theme-card-label">🎨 Appearance</div>', unsafe_allow_html=True)
        bcol1, bcol2 = st.columns(2)
        with bcol1:
            if st.button("☀️ Light", use_container_width=True,
                         type=("primary" if st.session_state.theme == "light" else "secondary"),
                         key="_theme_light_btn"):
                st.session_state.theme = "light"
                st.rerun()
        with bcol2:
            if st.button("🌙 Dark", use_container_width=True,
                         type=("primary" if st.session_state.theme == "dark" else "secondary"),
                         key="_theme_dark_btn"):
                st.session_state.theme = "dark"
                st.rerun()
    st.markdown("<div style='margin-bottom:4px'></div>", unsafe_allow_html=True)

inject_theme(st.session_state.theme)

# ─────────────────────────────────────────────────────────────────────────────
# STARTUP
# ─────────────────────────────────────────────────────────────────────────────
try:
    migrate_db()
    seed_admin()
except Exception as _e:
    st.error(f"❌ Database error: {_e}")
    st.info("Check DB_HOST / DB_PORT / DB_NAME / DB_USER / DB_PASSWORD in .env")
    st.stop()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR NAV
# ─────────────────────────────────────────────────────────────────────────────
def show_sidebar():
    with st.sidebar:
        st.markdown("""
            <div class="brand-row">
                <div class="brand-mark">SM</div>
                <div>
                    <div class="brand-name">SkillMap Pro</div>
                    <div class="brand-sub">Career Control Deck</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        u    = st.session_state.user
        role = u["role"]
        st.markdown(f"""
            <div class="user-badge">
                <div class="user-avatar">{u['username'][:1].upper()}</div>
                <div>
                    <div class="user-name">{u['username']}</div>
                    <div class="user-role {'role-admin' if role == 'admin' else ''}">● {'ADMIN' if role == 'admin' else 'USER'}</div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        if role != "admin":
            apps_df = get_user_applications(u["id"])
            counts  = apps_df["status"].value_counts().to_dict() if not apps_df.empty else {}
            render_pipeline_strip(counts)

        st.divider()

        if role == "admin":
            pages = {
                "📊 Dashboard": "admin_dashboard", "🗂️ Vacancy Manager": "admin_vacancies",
                "👥 User Management": "admin_users", "📋 Scrape Logs": "admin_logs",
            }
        else:
            pages = {
                "🔍 Job Search": "user_search", "📌 My Applications": "user_applications",
                "🧠 Skill Match": "user_skillmatch", "📈 My Analytics": "user_analytics",
                "⚙️  Settings": "user_settings",
            }

        if not st.session_state.page:
            st.session_state.page = list(pages.values())[0]

        for label, pg in pages.items():
            btn_type = "primary" if st.session_state.page == pg else "secondary"
            if st.button(label, use_container_width=True, type=btn_type, key=f"nav_{pg}"):
                st.session_state.page = pg
                st.rerun()

        st.divider()
        if st.button("🚪 Logout", use_container_width=True):
            st.session_state.user = None
            st.session_state.page = None
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN / SIGNUP
# ─────────────────────────────────────────────────────────────────────────────
def show_login():
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    render_project_title()
    _, col, _ = st.columns([1, 1.3, 1])
    with col:
        render_hero_art(150)
        st.markdown("""
            <div style="text-align:center;">
                <span class="brand-badge" style="display:inline-block; margin-top:14px;">SKILLMAP // CONTROL DECK</span>
                <h1 style="font-size:1.9rem; margin:14px 0 4px;">Run your job search like a mission.</h1>
                <p style="color:var(--text-muted); font-size:15px; margin-bottom:0;">
                    Scrape the market, track every application, land the offer.
                </p>
            </div>
        """, unsafe_allow_html=True)

        render_pipeline_strip()

        with st.container(border=True):
            tab_l, tab_s = st.tabs(["Sign In", "Create Account"])

            with tab_l:
                u = st.text_input("Username", key="li_u")
                p = st.text_input("Password", type="password", key="li_p")
                if st.button("Enter Deck  →", type="primary", use_container_width=True):
                    if u and p:
                        user = verify_login(u, p)
                        if user:
                            st.session_state.user       = user
                            st.session_state.last_visit = datetime.utcnow() - timedelta(hours=24)
                            st.rerun()
                        else:
                            st.error("Invalid username or password.")
                    else:
                        st.warning("Please fill both fields.")
                st.caption("Please fill both fields.")
                #st.caption("Default admin → **admin** / **admin123**")

            with tab_s:
                nu = st.text_input("Username",         key="su_u")
                ne = st.text_input("Email",            key="su_e")
                np = st.text_input("Password",         type="password", key="su_p")
                cp = st.text_input("Confirm Password", type="password", key="su_c")
                if st.button("Create Account", type="primary", use_container_width=True):
                    if not all([nu, ne, np, cp]):
                        st.warning("Fill all fields.")
                    elif np != cp:
                        st.error("Passwords do not match.")
                    elif len(np) < 6:
                        st.error("Password must be ≥ 6 characters.")
                    elif create_user(nu, ne, np):
                        st.success("Account created! Please sign in.")
                    else:
                        st.error("Username or email already taken.")

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────
def admin_dashboard_page():
    hc1, hc2 = st.columns([5, 1])
    with hc1: st.title("📊 Admin Dashboard")
    with hc2: render_hero_art(72)

    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("🔄 Run Scraper Now", type="primary", use_container_width=True):
            with st.spinner("Scraping Arbeitnow · RemoteOK · Adzuna …"):
                try:
                    saved, found, errs = run_scraper()
                    st.cache_data.clear()
                    st.success(f"✅ {saved} new jobs saved out of {found} fetched.")
                    for e in errs:
                        st.warning(e)
                except Exception as e:
                    st.error(f"Scraper error: {e}")

    st.divider()
    jobs_df   = load_jobs()
    skills_df = load_skills_df()

    if jobs_df.empty:
        st.warning("No jobs yet — run the scraper.")
        return

    open_c   = int((jobs_df["status"] == "open").sum())   if "status" in jobs_df else len(jobs_df)
    closed_c = int((jobs_df["status"] == "closed").sum()) if "status" in jobs_df else 0
    filled_c = int((jobs_df["status"] == "filled").sum()) if "status" in jobs_df else 0

    k1,k2,k3,k4,k5,k6 = st.columns(6)
    kpi_card(k1, "Total Jobs",     f"{len(jobs_df):,}",                    "#2DD4BF", "🗂️")
    kpi_card(k2, "Open",           f"{open_c:,}",                          "#34D399", "🟢")
    kpi_card(k3, "Closed",         f"{closed_c:,}",                        "#FF6B6B", "🔴")
    kpi_card(k4, "Filled",         f"{filled_c:,}",                        "#F5A623", "🟡")
    kpi_card(k5, "Companies",      f"{jobs_df['company'].nunique():,}",    "#5B8DEF", "🏢")
    kpi_card(k6, "Skills Indexed", f"{len(skills_df):,}",                  "#2DD4BF", "🧠")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Top Skills in Demand")
        fig = px.bar(skills_df, x="count", y="skill_name", orientation="h", color="count", color_continuous_scale="teal")
        fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"), height=440, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Jobs by Location")
        loc = jobs_df["location"].value_counts().head(10).reset_index()
        loc.columns = ["location","count"]
        fig2 = px.pie(loc, values="count", names="location", hole=0.4, color_discrete_sequence=px.colors.qualitative.Set2)
        fig2.update_layout(height=440, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Job Type Distribution")
        jt = jobs_df["job_type"].value_counts().reset_index()
        jt.columns = ["job_type","count"]
        fig3 = px.bar(jt, x="job_type", y="count", color_discrete_sequence=["#534AB7"])
        fig3.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("Jobs by Source")
        src = jobs_df["source"].value_counts().reset_index()
        src.columns = ["source","count"]
        fig4 = px.bar(src, x="source", y="count", color_discrete_sequence=["#0EA5E9"])
        fig4.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig4, use_container_width=True)

    st.subheader("Jobs Scraped Over Time")
    daily = jobs_df.assign(date=pd.to_datetime(jobs_df["scraped_at"]).dt.date).groupby("date").size().reset_index(name="jobs")
    fig5 = px.area(daily, x="date", y="jobs", color_discrete_sequence=["#534AB7"])
    fig5.update_layout(height=240, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig5, use_container_width=True)

    st.divider()
    st.subheader("All Job Postings")
    search = st.text_input("🔍 Search title or company", key="adm_search")
    disp = jobs_df.copy()
    if search:
        disp = disp[disp["title"].str.contains(search, case=False, na=False) | disp["company"].str.contains(search, case=False, na=False)]
    cols_show = [c for c in ["title","company","location","job_type","source","status","tags","scraped_at"] if c in disp.columns]
    st.dataframe(disp[cols_show].head(200), use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — VACANCY MANAGER
# ─────────────────────────────────────────────────────────────────────────────
def admin_vacancies_page():
    st.title("🗂️ Vacancy Manager")
    st.caption("Control which jobs are visible to users by setting their status.")

    jobs_df = load_jobs()
    if jobs_df.empty:
        st.warning("No jobs yet."); return

    STATUS_ICON = {"open": "🟢", "closed": "🔴", "filled": "🟡"}

    c1,c2,c3 = st.columns(3)
    c1.metric("🟢 Open",   int((jobs_df["status"] == "open").sum())   if "status" in jobs_df else len(jobs_df))
    c2.metric("🔴 Closed", int((jobs_df["status"] == "closed").sum()) if "status" in jobs_df else 0)
    c3.metric("🟡 Filled", int((jobs_df["status"] == "filled").sum()) if "status" in jobs_df else 0)

    st.divider()

    col1, col2, col3 = st.columns([3,1,1])
    with col1: search = st.text_input("🔍 Search title / company", key="vm_search")
    with col2: f_src  = st.selectbox("Source", ["All"] + sorted(jobs_df["source"].dropna().unique().tolist()))
    with col3: f_stat = st.selectbox("Status", ["All","open","closed","filled"])

    st.subheader("Bulk Status Update")
    bc1, bc2, bc3 = st.columns([2,1,1])
    with bc1: bulk_search = st.text_input("Filter jobs for bulk update (keyword)", key="bulk_kw")
    with bc2: bulk_status = st.selectbox("Set all matching to", ["open","closed","filled"], key="bulk_st")
    with bc3:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Apply Bulk Update"):
            bulk_df = jobs_df[
                jobs_df["title"].str.contains(bulk_search, case=False, na=False) |
                jobs_df["company"].str.contains(bulk_search, case=False, na=False)
            ] if bulk_search else jobs_df
            session = get_session()
            for jid in bulk_df["id"].tolist():
                j = session.query(JobPosting).filter_by(id=int(jid)).first()
                if j: j.status = bulk_status
            session.commit(); session.close()
            st.cache_data.clear()
            st.success(f"Updated {len(bulk_df)} jobs to '{bulk_status}'.")
            st.rerun()

    st.divider()

    disp = jobs_df.copy()
    if search:  disp = disp[disp["title"].str.contains(search, case=False, na=False) | disp["company"].str.contains(search, case=False, na=False)]
    if f_src  != "All": disp = disp[disp["source"] == f_src]
    if f_stat != "All": disp = disp[disp["status"] == f_stat]

    st.caption(f"{len(disp)} jobs")

    for _, row in disp.head(60).iterrows():
        cur_status = str(row.get("status", "open"))
        icon = STATUS_ICON.get(cur_status, "🟢")
        with st.expander(f"{icon} **{row['title']}** — {row['company']} | {row['location']}"):
            col_a, col_b, col_c = st.columns([3,1,1])
            with col_a:
                st.write(f"**Source:** {row['source']}  |  **Type:** {row['job_type']}")
                st.write(f"**Current Status:** `{cur_status}`  |  **Scraped:** {str(row['scraped_at'])[:10]}")
                if row.get("url"):
                    st.markdown(f"[View Posting ↗]({row['url']})")
            with col_b:
                new_status = st.selectbox("Set Status", ["open","closed","filled"],
                    index=["open","closed","filled"].index(cur_status), key=f"vs_{row['id']}")
            with col_c:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("✅ Update", key=f"vb_{row['id']}"):
                    set_job_status(int(row["id"]), new_status)
                    st.cache_data.clear()
                    st.success("Updated!")
                    st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — USER MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────
def admin_users_page():
    st.title("👥 User Management")
    users = get_all_users()
    if not users:
        st.info("No users yet."); return

    df = pd.DataFrame(users)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.divider()
    col_a, col_b = st.columns([1, 3])
    with col_a:
        uid = st.number_input("User ID to toggle", min_value=1, step=1)
    with col_b:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Toggle Active / Inactive"):
            toggle_user_status(int(uid))
            st.success(f"User {uid} toggled.")
            st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ADMIN — SCRAPE LOGS
# ─────────────────────────────────────────────────────────────────────────────
def admin_logs_page():
    st.title("📋 Scrape Logs")
    logs_df = load_logs()
    if logs_df.empty:
        st.info("No logs yet."); return

    s  = len(logs_df[logs_df["status"] == "success"])
    f  = len(logs_df[logs_df["status"] == "failed"])
    c1,c2,c3 = st.columns(3)
    c1.metric("Total Runs", len(logs_df))
    c2.metric("Successful", s)
    c3.metric("Failed",     f)

    st.divider()

    fig = px.bar(logs_df.sort_values("ran_at"), x="ran_at", y="jobs_saved", color="source", title="Jobs Saved Per Run")
    fig.update_layout(height=260, margin=dict(l=0,r=0,t=30,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(logs_df, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# USER — JOB SEARCH
# ─────────────────────────────────────────────────────────────────────────────
def user_search_page():
    hc1, hc2 = st.columns([5, 1])
    with hc1: st.title("🔍 Job Search")
    with hc2: render_hero_art(72)

    col_btn, _ = st.columns([2, 5])
    with col_btn:
        if st.button("🔄 Refresh Data", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.success("✅ Job data refreshed!")
            st.rerun()

    jobs_df = load_jobs()
    if jobs_df.empty:
        st.info("No jobs yet. Ask admin to run the scraper."); return

    last_visit = st.session_state.get("last_visit")
    if last_visit and "scraped_at" in jobs_df.columns:
        new_cnt = int((pd.to_datetime(jobs_df["scraped_at"]) > last_visit).sum())
        if new_cnt:
            st.success(f"🆕 **{new_cnt} new jobs** added since your last visit!")

    open_df = jobs_df[jobs_df["status"] == "open"].copy() if "status" in jobs_df.columns else jobs_df.copy()

    k1,k2,k3 = st.columns(3)
    kpi_card(k1, "Open Jobs",        f"{len(open_df):,}",                  "#2DD4BF", "🗂️")
    kpi_card(k2, "Companies Hiring", f"{open_df['company'].nunique():,}",  "#5B8DEF", "🏢")
    kpi_card(k3, "Locations",        f"{open_df['location'].nunique():,}", "#F5A623", "📍")

    apps_snapshot = get_user_applications(st.session_state.user["id"])
    snap_counts   = apps_snapshot["status"].value_counts().to_dict() if not apps_snapshot.empty else {}
    render_pipeline_strip(snap_counts)

    st.divider()

    col1,col2,col3,col4 = st.columns([3,1,1,1])
    with col1: keyword  = st.text_input("Search by title, skill, or company", placeholder="e.g. Python, React, Data Analyst")
    with col2: sel_type = st.selectbox("Job Type",  ["All"] + sorted(open_df["job_type"].dropna().unique().tolist()))
    with col3: sel_src  = st.selectbox("Source",    ["All"] + sorted(open_df["source"].dropna().unique().tolist()))
    with col4: sel_loc  = st.selectbox("Location",  ["All"] + sorted(open_df["location"].dropna().unique().tolist()))

    filtered = open_df.copy()
    if keyword:
        kw = keyword.lower()
        filtered = filtered[
            filtered["title"].str.lower().str.contains(kw, na=False) |
            filtered["company"].str.lower().str.contains(kw, na=False) |
            filtered["tags"].str.lower().str.contains(kw, na=False) |
            filtered["description"].str.lower().str.contains(kw, na=False)
        ]
    if sel_type != "All": filtered = filtered[filtered["job_type"] == sel_type]
    if sel_src  != "All": filtered = filtered[filtered["source"]   == sel_src]
    if sel_loc  != "All": filtered = filtered[filtered["location"] == sel_loc]

    user_skills = [s.strip() for s in (st.session_state.user.get("resume_skills") or "").split(",") if s.strip()]
    if user_skills:
        filtered["match_%"] = filtered.apply(
            lambda r: match_score(user_skills, f"{r['title']} {r['tags']} {r['description']}"), axis=1
        )
        filtered = filtered.sort_values("match_%", ascending=False)

    st.caption(f"**{len(filtered)}** jobs found")

    uid = st.session_state.user["id"]
    for _, job in filtered.head(25).iterrows():
        app = get_user_application(uid, int(job["id"]))
        app_badge   = f" {STATUS_COLORS.get(app['status'],'')} `{app['status']}`" if app else ""
        match_badge = (f" 🎯 {int(job['match_%'])}% match" if user_skills and "match_%" in job.index else "")

        with st.expander(f"**{job['title']}** — {job['company']} | 📍 {job['location']}{app_badge}{match_badge}"):
            col_a, col_b = st.columns([3,1])
            with col_a:
                st.write(f"**Type:** {job['job_type']}  |  **Source:** {job['source']}")
                tags_str = str(job["tags"])[:200] if job["tags"] else "N/A"
                st.write(f"**Tags:** {tags_str}")
                if job["description"]:
                    clean = re.sub(r"<[^>]+>", " ", str(job["description"]))
                    st.write(clean[:500] + "…")
            with col_b:
                already_applied = app is not None and app["status"] != "saved"
                if not already_applied:
                    apply_link = f"?apply={int(job['id'])}&uid={uid}"
                    st.link_button("🚀 Apply Now", apply_link, use_container_width=True, type="primary")
                else:
                    st.success(f"{STATUS_COLORS.get(app['status'],'')} Applied — status: `{app['status']}`")

                cur_st   = app["status"] if app else "saved"
                new_st   = st.selectbox("Update status", APP_STATUSES, index=APP_STATUSES.index(cur_st), key=f"trk_{job['id']}")
                notes_in = st.text_area("Notes", value=app["notes"] if app else "", height=70, key=f"note_{job['id']}",
                                        placeholder="Interview date, HR contact…")
                cs, cd = st.columns(2)
                with cs:
                    if st.button("💾 Save", key=f"save_{job['id']}"):
                        upsert_application(uid, int(job["id"]), new_st, notes_in)
                        st.success("Saved!"); st.rerun()
                with cd:
                    if app and st.button("🗑️", key=f"del_{job['id']}"):
                        delete_application(uid, int(job["id"])); st.rerun()
                st.caption(f"Posted: {str(job['scraped_at'])[:10]}")

# ─────────────────────────────────────────────────────────────────────────────
# USER — MY APPLICATIONS
# ─────────────────────────────────────────────────────────────────────────────
def user_applications_page():
    st.title("📌 My Applications")
    uid     = st.session_state.user["id"]
    apps_df = get_user_applications(uid)

    if apps_df.empty:
        st.info("No applications yet — find a job in Job Search and track it!")
        return

    st.subheader("Application Pipeline")
    pipeline = apps_df["status"].value_counts().reindex(APP_STATUSES, fill_value=0).reset_index()
    pipeline.columns = ["stage","count"]

    cols = st.columns(len(APP_STATUSES))
    for i, (_, row) in enumerate(pipeline.iterrows()):
        icon = STATUS_COLORS.get(row["stage"],"")
        cols[i].metric(f"{icon} {row['stage'].capitalize()}", int(row["count"]))

    fig = px.funnel(pipeline, x="count", y="stage", color_discrete_sequence=["#534AB7","#0EA5E9","#10B981","#F59E0B","#EF4444"])
    fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()

    sc1, sc2 = st.columns([3,1])
    with sc1: srch    = st.text_input("🔍 Search my applications")
    with sc2: f_status = st.selectbox("Filter by status", ["All"] + APP_STATUSES)

    disp = apps_df.copy()
    if srch:     disp = disp[disp["title"].str.contains(srch, case=False, na=False) | disp["company"].str.contains(srch, case=False, na=False)]
    if f_status != "All": disp = disp[disp["status"] == f_status]

    st.caption(f"**{len(disp)}** applications")

    for _, row in disp.iterrows():
        icon = STATUS_COLORS.get(row["status"],"")
        with st.expander(f"{icon} **{row['title']}** — {row['company']} | `{row['status']}`"):
            col_a, col_b = st.columns([3,1])
            with col_a:
                st.write(f"**Location:** {row['location']}  |  **Type:** {row['job_type']}  |  **Source:** {row['source']}")
                st.write(f"**Tags:** {str(row['tags'])[:150] if row['tags'] else 'N/A'}")
                if row["notes"]:
                    st.info(f"📝 {row['notes']}")
                st.caption(f"Tracked: {str(row['applied_at'])[:16]}  |  Updated: {str(row['updated_at'])[:16]}")
            with col_b:
                if row["url"]:
                    st.link_button("View Job 🔗", row["url"])
                new_st   = st.selectbox("Update status", APP_STATUSES, index=APP_STATUSES.index(row["status"]), key=f"ast_{row['job_id']}")
                new_note = st.text_area("Notes", value=row["notes"] or "", height=70, key=f"anote_{row['job_id']}")
                cs, cd = st.columns(2)
                with cs:
                    if st.button("💾 Update", key=f"aupd_{row['job_id']}"):
                        upsert_application(uid, int(row["job_id"]), new_st, new_note)
                        st.success("Updated!"); st.rerun()
                with cd:
                    if st.button("🗑️ Remove", key=f"adel_{row['job_id']}"):
                        delete_application(uid, int(row["job_id"])); st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# USER — SKILL MATCH
# ─────────────────────────────────────────────────────────────────────────────
def user_skillmatch_page():
    st.title("🧠 Resume Skill Match")
    st.markdown("Enter your skills and SkillMap will score every open job by how many of your skills appear in its description and tags.")

    current     = st.session_state.user.get("resume_skills") or ""
    skills_input = st.text_area("Your skills (comma-separated)", value=current, height=100,
                                 placeholder="python, react, docker, sql, machine learning, aws")

    uploaded = st.file_uploader("Or upload your resume (.txt) to auto-detect skills", type=["txt"])
    if uploaded:
        txt   = uploaded.read().decode("utf-8", errors="ignore")
        found = extract_skills(txt)
        if found:
            existing = [s.strip() for s in skills_input.split(",") if s.strip()]
            merged   = list(dict.fromkeys(existing + found))
            skills_input = ", ".join(merged)
            st.success(f"Detected {len(found)} skills from resume — added to your list.")

    if st.button("💾 Save My Skills", type="primary"):
        save_resume_skills(st.session_state.user["id"], skills_input)
        st.session_state.user["resume_skills"] = skills_input
        st.success("Skills saved!")

    st.divider()

    user_skills = [s.strip() for s in skills_input.split(",") if s.strip()]
    if not user_skills:
        st.info("Add your skills above to see matched jobs."); return

    jobs_df = load_jobs()
    if jobs_df.empty:
        st.warning("No jobs in database yet."); return

    open_df = jobs_df[jobs_df["status"] == "open"].copy() if "status" in jobs_df.columns else jobs_df.copy()
    open_df["match_%"] = open_df.apply(
        lambda r: match_score(user_skills, f"{r['title']} {r['tags']} {r['description']}"), axis=1
    )
    matched = open_df[open_df["match_%"] > 0].sort_values("match_%", ascending=False)

    st.subheader(f"🎯 {len(matched)} jobs match your skills")

    if matched.empty:
        st.info("No matches. Try adding more skills or ask admin to run the scraper."); return

    bins  = pd.cut(matched["match_%"], bins=[0,25,50,75,100], labels=["1-25%","26-50%","51-75%","76-100%"])
    dist  = bins.value_counts().sort_index().reset_index()
    dist.columns = ["range","count"]
    fig = px.bar(dist, x="range", y="count", color_discrete_sequence=["#10B981"], labels={"range":"Match Range","count":"Jobs"})
    fig.update_layout(height=220, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig, use_container_width=True)

    st.divider()
    uid = st.session_state.user["id"]
    for _, job in matched.head(30).iterrows():
        with st.expander(f"🎯 **{int(job['match_%'])}%** — **{job['title']}** at {job['company']} | 📍 {job['location']}"):
            col_a, col_b = st.columns([3,1])
            with col_a:
                st.write(f"**Type:** {job['job_type']}  |  **Source:** {job['source']}")
                st.write(f"**Tags:** {str(job['tags'])[:200] if job['tags'] else 'N/A'}")
                if job["description"]:
                    clean = re.sub(r"<[^>]+>", " ", str(job["description"]))
                    st.write(clean[:400] + "…")
            with col_b:
                already = get_user_application(uid, int(job["id"]))
                already_applied = already is not None and already["status"] != "saved"
                if not already_applied:
                    apply_link = f"?apply={int(job['id'])}&uid={uid}"
                    st.link_button("🚀 Apply Now", apply_link, use_container_width=True, type="primary")
                else:
                    st.success(f"{STATUS_COLORS.get(already['status'],'')} Applied — status: `{already['status']}`")
                if st.button("📌 Track Job", key=f"sm_track_{job['id']}"):
                    upsert_application(uid, int(job["id"]), "saved", "")
                    st.success("Added to My Applications!")

# ─────────────────────────────────────────────────────────────────────────────
# USER — MY ANALYTICS
# ─────────────────────────────────────────────────────────────────────────────
def user_analytics_page():
    st.title("📈 My Analytics")
    uid     = st.session_state.user["id"]
    apps_df = get_user_applications(uid)

    if apps_df.empty:
        st.info("Start tracking applications to see your analytics."); return

    total  = len(apps_df)
    offers = int((apps_df["status"] == "offer").sum())
    active = int(apps_df["status"].isin(["applied","interviewing"]).sum())
    rate   = round(100 * offers / total) if total else 0

    k1,k2,k3,k4 = st.columns(4)
    k1.metric("Total Tracked",       total)
    k2.metric("Active (Applied/Int.)",active)
    k3.metric("Offers",              offers)
    k4.metric("Offer Rate",          f"{rate}%")

    st.divider()

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Applications by Status")
        sc = apps_df["status"].value_counts().reset_index()
        sc.columns = ["status","count"]
        color_map = {"saved":"#6B7280","applied":"#3B82F6","interviewing":"#F59E0B","offer":"#10B981","rejected":"#EF4444"}
        fig1 = px.pie(sc, values="count", names="status", color="status", color_discrete_map=color_map, hole=0.4)
        fig1.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig1, use_container_width=True)

    with c2:
        st.subheader("Applications Over Time")
        apps_df["date"] = pd.to_datetime(apps_df["applied_at"]).dt.date
        daily = apps_df.groupby("date").size().reset_index(name="count")
        fig2 = px.bar(daily, x="date", y="count", color_discrete_sequence=["#534AB7"])
        fig2.update_layout(height=340, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Top Companies You Applied To")
    top_co = apps_df["company"].value_counts().head(10).reset_index()
    top_co.columns = ["company","count"]
    fig3 = px.bar(top_co, x="count", y="company", orientation="h", color_discrete_sequence=["#0EA5E9"])
    fig3.update_layout(height=300, yaxis=dict(autorange="reversed"), margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.subheader("Application History")
    disp = apps_df[["title","company","status","applied_at","updated_at","notes"]].copy()
    st.dataframe(disp, use_container_width=True, hide_index=True)

# ─────────────────────────────────────────────────────────────────────────────
# USER — SETTINGS
# ─────────────────────────────────────────────────────────────────────────────
def user_settings_page():
    st.title("⚙️ Settings")
    u = st.session_state.user

    st.subheader("Account Info")
    st.write(f"**Username:** {u['username']}")
    st.write(f"**Email:**    {u['email']}")
    st.write(f"**Role:**     {u['role']}")

    st.divider()
    st.subheader("Email Notifications")
    notify = st.toggle("Notify me when new jobs are scraped", value=u.get("notify_email", False))
    if st.button("Save Notification Preference"):
        set_email_notify(u["id"], notify)
        st.session_state.user["notify_email"] = notify
        st.success("Saved!")
    st.caption("Requires SMTP_HOST / SMTP_USER / SMTP_PASS in .env")

    st.divider()
    st.subheader("Change Password")
    old_pw = st.text_input("Current Password", type="password", key="cp_old")
    new_pw = st.text_input("New Password",     type="password", key="cp_new")
    cfm_pw = st.text_input("Confirm New",      type="password", key="cp_cfm")
    if st.button("Update Password"):
        if not verify_login(u["username"], old_pw):
            st.error("Current password incorrect.")
        elif len(new_pw) < 6:
            st.error("New password must be ≥ 6 characters.")
        elif new_pw != cfm_pw:
            st.error("Passwords do not match.")
        else:
            session = get_session()
            try:
                usr = session.query(User).filter_by(id=u["id"]).first()
                usr.password = hash_pw(new_pw)
                session.commit()
                st.success("Password updated!")
            finally:
                session.close()

# ─────────────────────────────────────────────────────────────────────────────
# FAKE "CAREERS PORTAL" APPLY LANDING PAGE (redirect target for Apply Now)
# ─────────────────────────────────────────────────────────────────────────────
def show_apply_landing():
    qp = st.query_params
    try:
        job_id = int(qp.get("apply"))
        uid    = int(qp.get("uid"))
    except (TypeError, ValueError):
        st.error("Invalid application link.")
        return

    session = get_session()
    job = session.query(JobPosting).filter_by(id=job_id).first()
    session.close()

    if not job:
        st.error("This job posting no longer exists.")
        return

    st.markdown(f"""
        <div style="text-align:center; padding: 30px 0 10px 0;">
            <span class="brand-badge">CAREERS PORTAL</span>
            <h2 style="margin:14px 0 2px;">🏢 {job.company}</h2>
        </div>
    """, unsafe_allow_html=True)

    _, col, _ = st.columns([1, 2, 1])
    with col:
        already = get_user_application(uid, job_id)
        if already and already["status"] != "saved":
            st.success("✅ You have already applied to this role.")
            st.info(f"**{job.title}**  \n{job.company} · {job.location}")
            if st.button("⬅ Back to SkillMap", use_container_width=True):
                st.query_params.clear()
                st.rerun()
            return

        with st.container(border=True):
            st.subheader(job.title)
            st.caption(f"{job.company} · {job.location} · {job.job_type}")
            st.divider()

            if job.description:
                clean_desc = re.sub(r"<[^>]+>", " ", str(job.description))
                with st.expander("📄 Job Description", expanded=True):
                    st.write(clean_desc[:1500] + ("…" if len(clean_desc) > 1500 else ""))
                st.divider()

            with st.form("apply_form"):
                name  = st.text_input("Full Name")
                email = st.text_input("Email")
                phone = st.text_input("Phone (optional)")
                cover = st.text_area("Cover Note (optional)", height=100, placeholder="Why are you a good fit for this role?")
                submitted = st.form_submit_button("🚀 Submit Application", type="primary", use_container_width=True)

            if submitted:
                if not name or not email:
                    st.warning("Please fill in your name and email.")
                else:
                    note = f"Applied via careers portal. Name: {name}, Email: {email}, Phone: {phone or 'N/A'}"
                    if cover:
                        note += f"\nCover note: {cover}"
                    upsert_application(uid, job_id, "applied", note)
                    st.success("✅ Application Submitted Successfully!")
                    st.balloons()
                    st.info("This role now appears under **My Applications** in your SkillMap dashboard.")
                    if st.button("⬅ Back to SkillMap", use_container_width=True):
                        st.query_params.clear()
                        st.rerun()

# ─────────────────────────────────────────────────────────────────────────────
# ROUTER
# ─────────────────────────────────────────────────────────────────────────────
if "apply" in st.query_params:
    show_apply_landing()
elif not st.session_state.user:
    show_login()
else:
    show_sidebar()
    render_project_title()
    pg   = st.session_state.get("page") or ""
    role = st.session_state.user["role"]

    if role == "admin":
        if   pg == "admin_vacancies": admin_vacancies_page()
        elif pg == "admin_users":     admin_users_page()
        elif pg == "admin_logs":      admin_logs_page()
        else:                         admin_dashboard_page()
    else:
        if   pg == "user_applications": user_applications_page()
        elif pg == "user_skillmatch":   user_skillmatch_page()
        elif pg == "user_analytics":    user_analytics_page()
        elif pg == "user_settings":     user_settings_page()
        else:                           user_search_page()