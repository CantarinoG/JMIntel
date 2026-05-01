import sqlite3
import json
from src.models.job import Job
from src.databases.base_repository import BaseJobRepository
from typing import List


class SQLiteJobRepository(BaseJobRepository):
    """
    SQLite implementation of the Job Repository.
    """

    def __init__(self, db_path: str = "jobs.db"):
        self.db_path = db_path
        self._init_db()

    def _init_db(self):
        """
        Create the jobs table if it doesn't exist.
        """
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS jobs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL COLLATE NOCASE,
                    description TEXT NOT NULL,
                    company TEXT NOT NULL COLLATE NOCASE,
                    url TEXT NOT NULL,
                    platform TEXT NOT NULL,
                    date_collected TEXT NOT NULL,
                    job_category TEXT,
                    seniority_level TEXT,
                    employment_type TEXT,
                    contract_duration TEXT,
                    remote_type TEXT,
                    language TEXT,
                    monthly_salary_min_brl REAL,
                    monthly_salary_max_brl REAL,
                    experience_years_min REAL,
                    hard_skills TEXT,
                    UNIQUE(title, company)
                )
            """)

    def save(self, job: Job) -> bool:
        """
        Save a new job in the SQLite database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR IGNORE INTO jobs (
                        title, description, company, url, platform, date_collected,
                        job_category, seniority_level, employment_type,
                        contract_duration, remote_type, language,
                        monthly_salary_min_brl, monthly_salary_max_brl,
                        experience_years_min, hard_skills
                    )
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        job.title,
                        job.description,
                        job.company,
                        job.url,
                        job.platform,
                        job.date_collected,
                        job.job_category,
                        job.seniority_level,
                        job.employment_type,
                        job.contract_duration,
                        job.remote_type,
                        job.language,
                        job.monthly_salary_min_brl,
                        job.monthly_salary_max_brl,
                        job.experience_years_min,
                        json.dumps(job.hard_skills) if job.hard_skills else None,
                    ),
                )
            return True
        except Exception as e:
            return False

    def get_unprocessed(self) -> List[Job]:
        """
        Retrieve unprocessed jobs.
        """
        jobs = []
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute("SELECT * FROM jobs WHERE job_category IS NULL")

                rows = cursor.fetchall()
                for row in rows:
                    job = Job(
                        title=row["title"],
                        description=row["description"],
                        company=row["company"],
                        url=row["url"],
                        platform=row["platform"],
                        date_collected=row["date_collected"],
                        job_category=row["job_category"],
                        seniority_level=row["seniority_level"],
                        employment_type=row["employment_type"],
                        contract_duration=row["contract_duration"],
                        remote_type=row["remote_type"],
                        language=row["language"],
                        monthly_salary_min_brl=row["monthly_salary_min_brl"],
                        monthly_salary_max_brl=row["monthly_salary_max_brl"],
                        experience_years_min=row["experience_years_min"],
                        hard_skills=json.loads(row["hard_skills"]) if row["hard_skills"] else None,
                    )
                    jobs.append(job)
        except Exception as e:
            pass
        return jobs

    def update(self, job: Job) -> bool:
        """
        Update an existing job in the SQLite database.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    UPDATE jobs 
                    SET 
                        url = ?,
                        description = ?,
                        platform = ?,
                        date_collected = ?,
                        job_category = ?,
                        seniority_level = ?,
                        employment_type = ?,
                        contract_duration = ?,
                        remote_type = ?,
                        language = ?,
                        monthly_salary_min_brl = ?,
                        monthly_salary_max_brl = ?,
                        experience_years_min = ?,
                        hard_skills = ?
                    WHERE title = ? AND company = ?
                """,
                    (
                        job.url,
                        job.description,
                        job.platform,
                        job.date_collected,
                        job.job_category,
                        job.seniority_level,
                        job.employment_type,
                        job.contract_duration,
                        job.remote_type,
                        job.language,
                        job.monthly_salary_min_brl,
                        job.monthly_salary_max_brl,
                        job.experience_years_min,
                        json.dumps(job.hard_skills) if job.hard_skills else None,
                        job.title,
                        job.company,
                    ),
                )
            return True
        except Exception as e:
            return False