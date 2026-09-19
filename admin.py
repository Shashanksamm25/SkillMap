"""dashboard/admin.py — Admin view: full analytics + user management + scrape logs"""
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import text
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import get_engine
from auth.auth_db import get_all_users, toggle_user_status
from scraper.scraper import run_scraper

@st.cache_data(ttl=120)
def load_jobs():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM job_postings ORDER BY scraped_at DESC", conn)

@st.cache_data(ttl=120)
def load_skills():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            GROUP BY skill_name ORDER BY count DESC LIMIT 15
        """, conn)

@st.cache_data(ttl=120)
def load_logs():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM scrape_logs ORDER BY ran_at DESC LIMIT 20", conn)

def show_admin():
    st.title("SkillMap — Admin Dashboard")
    st.caption(f"Logged in as admin: {st.session_state.user['username']}")

    # ── Run scraper button ────────────────────────────────────────────────────
    col_btn, col_space = st.columns([1, 4])
    with col_btn:
        if st.button("Run Scraper Now", type="primary"):
            with st.spinner("Scraping jobs..."):
                run_scraper()
                st.cache_data.clear()
            st.success("Scrape complete! Dashboard refreshed.")

    st.divider()

    jobs_df  = load_jobs()
    skills_df = load_skills()
    logs_df  = load_logs()

    # ── KPI cards ─────────────────────────────────────────────────────────────
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Total Jobs",      f"{len(jobs_df):,}")
    k2.metric("Unique Companies", f"{jobs_df['company'].nunique():,}")
    k3.metric("Locations",        f"{jobs_df['location'].nunique():,}")
    k4.metric("Skills Tracked",   f"{len(skills_df):,}")

    st.divider()

    # ── Charts ────────────────────────────────────────────────────────────────
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Top Skills in Demand")
        if not skills_df.empty:
            fig = px.bar(skills_df, x="count", y="skill_name", orientation="h",
                         color="count", color_continuous_scale="teal")
            fig.update_layout(showlegend=False, yaxis=dict(autorange="reversed"),
                              height=350, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig, use_container_width=True)

    with c2:
        st.subheader("Jobs by Location")
        loc = jobs_df["location"].value_counts().head(8).reset_index()
        loc.columns = ["location", "count"]
        if not loc.empty:
            fig2 = px.pie(loc, values="count", names="location", hole=0.4,
                          color_discrete_sequence=px.colors.qualitative.Set2)
            fig2.update_layout(height=350, margin=dict(l=0,r=0,t=10,b=0))
            st.plotly_chart(fig2, use_container_width=True)

    # ── Job type distribution ─────────────────────────────────────────────────
    st.subheader("Job Type Distribution")
    jt = jobs_df["job_type"].value_counts().reset_index()
    jt.columns = ["job_type", "count"]
    fig3 = px.bar(jt, x="job_type", y="count",
                  color_discrete_sequence=["#534AB7"])
    fig3.update_layout(height=250, margin=dict(l=0,r=0,t=10,b=0))
    st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    # ── Recent jobs table ─────────────────────────────────────────────────────
    st.subheader("All Job Postings")
    search = st.text_input("Search by title or company")
    display = jobs_df.copy()
    if search:
        display = display[
            display["title"].str.contains(search, case=False, na=False) |
            display["company"].str.contains(search, case=False, na=False)
        ]
    st.dataframe(
        display[["title","company","location","job_type","tags","scraped_at"]].head(100),
        use_container_width=True, hide_index=True
    )

    st.divider()

    # ── User management ───────────────────────────────────────────────────────
    st.subheader("User Management")
    users = get_all_users()
    if users:
        users_df = pd.DataFrame(users)
        st.dataframe(users_df, use_container_width=True, hide_index=True)
        uid = st.number_input("Toggle user active/inactive by ID", min_value=1, step=1)
        if st.button("Toggle Status"):
            toggle_user_status(int(uid))
            st.success(f"User {uid} status toggled.")
            st.rerun()

    st.divider()

    # ── Scrape logs ───────────────────────────────────────────────────────────
    st.subheader("Scrape Logs")
    st.dataframe(logs_df, use_container_width=True, hide_index=True)