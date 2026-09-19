"""
database/models.py — All DB tables: users, job_postings, job_skills, scrape_logs
"""
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime
from urllib.parse import quote_plus
from dotenv import load_dotenv
import os

load_dotenv()
Base = declarative_base()

# ── Users table (login/auth) ──────────────────────────────────────────────────
class User(Base):
    __tablename__ = "users"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    username   = Column(String(100), unique=True, nullable=False)
    email      = Column(String(200), unique=True, nullable=False)
    password   = Column(String(255), nullable=False)   # hashed
    role       = Column(String(20), default="user")    # "admin" or "user"
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active  = Column(Boolean, default=True)

# ── Job postings ──────────────────────────────────────────────────────────────
class JobPosting(Base):
    __tablename__ = "job_postings"
    id          = Column(Integer, primary_key=True, autoincrement=True)
    title       = Column(String(255), nullable=False)
    company     = Column(String(255), nullable=False)
    location    = Column(String(255))
    job_type    = Column(String(100))
    salary_min  = Column(Float, nullable=True)
    salary_max  = Column(Float, nullable=True)
    description = Column(Text, nullable=True)
    tags        = Column(String(500))
    source      = Column(String(100))
    url         = Column(String(500), unique=True)
    scraped_at  = Column(DateTime, default=datetime.utcnow)

# ── Skills extracted per job ──────────────────────────────────────────────────
class JobSkill(Base):
    __tablename__ = "job_skills"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    job_id     = Column(Integer, nullable=False)
    skill_name = Column(String(100), nullable=False)

# ── Scrape run logs ───────────────────────────────────────────────────────────
class ScrapeLog(Base):
    __tablename__ = "scrape_logs"
    id         = Column(Integer, primary_key=True, autoincrement=True)
    source     = Column(String(100))
    jobs_found = Column(Integer, default=0)
    jobs_saved = Column(Integer, default=0)
    status     = Column(String(50))
    error_msg  = Column(Text, nullable=True)
    ran_at     = Column(DateTime, default=datetime.utcnow)

# ── Engine & Session ──────────────────────────────────────────────────────────
def get_engine():
    password = quote_plus(os.getenv('DB_PASSWORD', ''))
    DB_URL = (
        f"postgresql://{os.getenv('DB_USER')}:{password}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    return create_engine(DB_URL, echo=False)

def get_session():
    engine = get_engine()
    Session = sessionmaker(bind=engine)
    return Session()

def create_all_tables():
    engine = get_engine()
    Base.metadata.create_all(engine)
    print("All tables created successfully!")

if __name__ == "__main__":
    create_all_tables()