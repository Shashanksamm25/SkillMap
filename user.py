"""dashboard/user.py — Regular user view: search jobs + skill analytics"""
import streamlit as st
import pandas as pd
import plotly.express as px
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import get_engine

@st.cache_data(ttl=180)
def load_jobs():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("SELECT * FROM job_postings ORDER BY scraped_at DESC", conn)

@st.cache_data(ttl=180)
def load_skills():
    engine = get_engine()
    with engine.connect() as conn:
        return pd.read_sql("""
            SELECT skill_name, COUNT(*) as count FROM job_skills
            GROUP BY skill_name ORDER BY count DESC LIMIT 12
        """, conn)

def show_user():
    st.title("SkillMap — Job Market Explorer")
    st.caption(f"Welcome, {st.session_state.user['username']}!")

    jobs_df   = load_jobs()
    skills_df = load_skills()

    # ── KPIs ──────────────────────────────────────────────────────────────────
    k1, k2, k3 = st.columns(3)
    k1.metric("Jobs Available",   f"{len(jobs_df):,}")
    k2.metric("Companies Hiring", f"{jobs_df['company'].nunique():,}")
    k3.metric("Locations",        f"{jobs_df['location'].nunique():,}")

    st.divider()

    # ── Job Search ────────────────────────────────────────────────────────────
    st.subheader("Search Jobs")
    col1, col2 = st.columns([3, 1])
    with col1:
        keyword = st.text_input("Search by job title, skill, or company", placeholder="e.g. Python, React, Data Analyst")
    with col2:
        job_types = ["All"] + sorted(jobs_df["job_type"].dropna().unique().tolist())
        selected_type = st.selectbox("Job Type", job_types)

    filtered = jobs_df.copy()
    if keyword:
        filtered = filtered[
            filtered["title"].str.contains(keyword, case=False, na=False) |
            filtered["company"].str.contains(keyword, case=False, na=False) |
            filtered["tags"].str.contains(keyword, case=False, na=False)
        ]
    if selected_type != "All":
        filtered = filtered[filtered["job_type"] == selected_type]

    st.caption(f"{len(filtered)} jobs found")

    # Show job cards
    for _, job in filtered.head(15).iterrows():
        with st.expander(f"{job['title']} — {job['company']} | {job['location']}"):
            col_a, col_b = st.columns([2,1])
            with col_a:
                st.write(f"**Type:** {job['job_type']}")
                st.write(f"**Tags:** {job['tags'][:150] if job['tags'] else 'N/A'}")
                if job['description']:
                    st.write(job['description'][:400] + "...")
            with col_b:
                if job['url']:
                    st.link_button("Apply Now", job['url'])
                st.caption(f"Scraped: {str(job['scraped_at'])[:10]}")

    st.divider()

    # ── Skill Analytics ───────────────────────────────────────────────────────
    st.subheader("Top Skills in the Market")
    if not skills_df.empty:
        fig = px.bar(skills_df, x="skill_name", y="count",
                     color="count", color_continuous_scale="teal",
                     labels={"skill_name": "Skill", "count": "Job Postings"})
        fig.update_layout(showlegend=False, height=320,
                          margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig, use_container_width=True)

    st.divider()

    # ── Location chart ────────────────────────────────────────────────────────
    st.subheader("Jobs by Location")
    loc = jobs_df["location"].value_counts().head(10).reset_index()
    loc.columns = ["location", "count"]
    if not loc.empty:
        fig2 = px.bar(loc, x="location", y="count",
                      color_discrete_sequence=["#534AB7"])
        fig2.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0))
        st.plotly_chart(fig2, use_container_width=True)