import os
import sys
import argparse
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.scrapers.linkedin_scraper import LinkedInScraper
from src.databases.sqlite_repository import SQLiteJobRepository
from src.ai_services.gemini_service import GeminiService
from src.ai_services.job_processor import JobProcessor

load_dotenv()

parser = argparse.ArgumentParser()
parser.add_argument("--query", "-q", default="Developer")
parser.add_argument("--pages", "-p", type=int, default=1)
args = parser.parse_args()

username = os.getenv("LINKEDIN_USERNAME")
password = os.getenv("LINKEDIN_PASSWORD")
api_key = os.getenv("LLM_API_KEY")

if not all([username, password, api_key]):
    print("[!] Error: Missing environment variables. Please check your .env file.")
    sys.exit(1)

print("[*] Initializing services...")
scraper = LinkedInScraper()
repo = SQLiteJobRepository()
ai_service = GeminiService()
ai_service.configure(api_key=api_key)
processor = JobProcessor(ai_service)

print(f"[*] Phase 1: Scraping LinkedIn for '{args.query}'...")

count_scraped = 0
for job in scraper.scrape_jobs(
    query=args.query,
    options={
        "username": username,
        "password": password,
        "posted_at_max_age": 86400,
        "remote_only": True,
        "max_pages": args.pages,
    },
):
    if repo.save(job):
        print(f"    [+] Saved: {job.title} @ {job.company}")
        count_scraped += 1

print(f"[V] Scraping complete. Total new jobs potentially found: {count_scraped}")

print("\n[*] Phase 2: Processing pending jobs with AI...")
pending_jobs = repo.get_unprocessed()
print(f"[*] Found {len(pending_jobs)} jobs awaiting classification.")

count_processed = 0
for job in pending_jobs:
    print(f"[*] Extracting details for: {job.title}...")
    if processor.process(job):
        if repo.update(job):
            print(f"    [OK] Classified as: {job.job_category} | {job.seniority_level}")
            count_processed += 1
        else:
            print(f"    [!] Failed to update database record for {job.title}")
    else:
        print(f"    [!] AI service failed to process {job.title}")

print(f"[V] Processed in this session: {count_processed}")
print(f"\n[V] Execution finished!")