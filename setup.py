"""
setup.py — Run this ONCE to set up everything
Creates all tables and the default admin account.
"""
import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.models import create_all_tables
from auth.auth_db import seed_admin

print("Setting up SkillMap...")
create_all_tables()
seed_admin()
print("\nSetup complete!")
print("Run the scraper:  python scraper/scraper.py")
print("Start the app:    python -m streamlit run app.py")