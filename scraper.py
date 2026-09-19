import requests, sys, os, time
from datetime import datetime
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from database.models import JobPosting, JobSkill, ScrapeLog, get_session

API_URL = "https://www.arbeitnow.com/api/job-board-api"

KNOWN_SKILLS = [
    "python","java","javascript","typescript","react","angular","vue","node",
    "django","flask","fastapi","sql","postgresql","mysql","mongodb","redis",
    "aws","azure","gcp","docker","kubernetes","git","linux","machine learning",
    "deep learning","tensorflow","pytorch","pandas","numpy","rest api",
    "graphql","microservices","agile","html","css","c++","go","rust","kotlin",
    "swift","r","scala","spark","hadoop","tableau","power bi","excel","nlp"
]

def extract_skills_local(text: str) -> list:
    import re
    text_lower = text.lower()
    found = []
    for skill in KNOWN_SKILLS:
        if re.search(r'\b' + re.escape(skill) + r'\b', text_lower):
            found.append(skill)
    return found

def fetch_jobs(pages: int = 3) -> list:
    all_jobs = []
    for page in range(1, pages + 1):
        try:
            resp = requests.get(f"{API_URL}?page={page}", timeout=15)
            resp.raise_for_status()
            data = resp.json()
            jobs = data.get("data", [])
            all_jobs.extend(jobs)
            print(f"  Page {page}: fetched {len(jobs)} jobs")
            time.sleep(1)
        except Exception as e:
            print(f"  [ERROR] Page {page}: {e}")
    return all_jobs

def save_jobs(jobs: list, session) -> int:
    saved = 0
    for job in jobs:
        url = job.get("url", "")
        if not url:
            continue
        exists = session.query(JobPosting).filter_by(url=url).first()
        if exists:
            continue
        tags = ", ".join(job.get("tags", []))
        new_job = JobPosting(
            title       = job.get("title", "N/A"),
            company     = job.get("company_name", "N/A"),
            location    = job.get("location", "Remote"),
            job_type    = job.get("job_types", [""])[0] if job.get("job_types") else "Full-time",
            description = job.get("description", ""),
            tags        = tags,
            source      = "arbeitnow",
            url         = url,
            scraped_at  = datetime.utcnow(),
        )
        session.add(new_job)
        session.flush()
        combined = f"{new_job.title} {tags} {new_job.description[:300]}"
        for skill in extract_skills_local(combined):
            session.add(JobSkill(job_id=new_job.id, skill_name=skill))
        saved += 1
    session.commit()
    return saved

def run_scraper():
    print(f"\n{'='*50}")
    print(f"  SkillMap Scraper — {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*50}")
    session = get_session()
    log = ScrapeLog(source="arbeitnow")
    try:
        jobs = fetch_jobs(pages=3)
        saved = save_jobs(jobs, session)
        log.jobs_found = len(jobs)
        log.jobs_saved = saved
        log.status = "success"
        print(f"\n  Done! {saved} new jobs saved to database.")
    except Exception as e:
        log.status = "failed"
        log.error_msg = str(e)
        session.rollback()
        print(f"  [FAILED] {e}")
    finally:
        session.add(log)
        session.commit()
        session.close()

if __name__ == "__main__":
    run_scraper()