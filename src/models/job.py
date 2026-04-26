from dataclasses import dataclass

@dataclass
class Job:
    """
    Data model representing a job posting.
    """

    title: str
    company: str
    url: str
    platform: str
    date_posted: str
    job_category: str
    seniority_level: str
    employment_type: str | None
    contract_duration: str | None
    remote_type: str | None
    language: str
    monthly_salary_min_brl: float | None
    monthly_salary_max_brl: float | None
    experience_years_min: float | None
    hard_skills: list[str]

    