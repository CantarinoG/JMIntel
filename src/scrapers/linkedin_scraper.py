import os
from datetime import datetime
from playwright.sync_api import sync_playwright
from src.scrapers.base_scraper import BaseScraper
from typing import Dict, Any, Generator
from src.models.job import Job

class LinkedInScraper(BaseScraper):
    """
    Concrete implementation of BaseScraper for LinkedIn.
    """

    LOGIN_EMAIL_INPUT = "#session_key"
    LOGIN_PASSWORD_INPUT = "#session_password"
    LOGIN_SUBMIT_BUTTON = (
        "#main-content > section.section.min-h-68.flex-nowrap.pt-6.babybear"
        "\\:min-h-0.babybear\\:px-mobile-container-padding.babybear\\:pt-3"
        ".babybear\\:flex-col > div > div > form > div.flex.justify-between"
        ".sign-in-form__footer--full-width > button"
    )
    JOB_LIST_CONTAINER = "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__list > div"
    JOB_LIST = f"{JOB_LIST_CONTAINER} > ul"
    JOB_ITEM = "li.jobs-search-results-list__list-item"
    NEXT_PAGE_BUTTON = "button.jobs-search-pagination__button--next"
    COMPANY_LINK = "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__detail.overflow-x-hidden.jobs-search__job-details > div > div.jobs-search__job-details--container > div > div.job-view-layout.jobs-details > div:nth-child(1) > div > div:nth-child(1) > div > div.relative.job-details-jobs-unified-top-card__container--two-pane > div > div.display-flex.align-items-center > div.display-flex.align-items-center.flex-1 > div > a"
    TITLE_LINK = "#main > div > div.scaffold-layout__list-detail-inner.scaffold-layout__list-detail-inner--grow > div.scaffold-layout__detail.overflow-x-hidden.jobs-search__job-details > div > div.jobs-search__job-details--container > div > div.job-view-layout.jobs-details > div:nth-child(1) > div > div:nth-child(1) > div > div.relative.job-details-jobs-unified-top-card__container--two-pane > div > div.display-flex.justify-space-between.flex-wrap.mt2 > div > h1 > a"
    DESCRIPTION_TEXT = "#job-details > div > p"

    def scrape_jobs(
        self, query: str, options: Dict[str, Any]
    ) -> Generator[Job, None, None]:
        user_data_dir = os.path.abspath("auth/linkedin_profile")
        if not os.path.exists(user_data_dir):
            os.makedirs(user_data_dir)

        with sync_playwright() as p:
            context = p.chromium.launch_persistent_context(
                user_data_dir=user_data_dir,
                headless=False,
                no_viewport=True,
            )

            page = context.pages[0] if context.pages else context.new_page()
            page.goto("https://www.linkedin.com/jobs")

            try:
                if page.locator(self.LOGIN_EMAIL_INPUT).is_visible(timeout=5000):
                    username = options.get("username")
                    password = options.get("password")
                    if username and password:
                        page.fill(self.LOGIN_EMAIL_INPUT, username)
                        page.fill(self.LOGIN_PASSWORD_INPUT, password)
                        page.click(self.LOGIN_SUBMIT_BUTTON)

                        page.wait_for_load_state("networkidle")
            except Exception as e:
                pass

            max_age = options.get("posted_at_max_age", 86400)
            tpr = f"r{max_age}"
            remote_only = options.get("remote_only", True)
            wt = "2" if remote_only else ""
            search_url = f"https://www.linkedin.com/jobs/search/?f_TPR={tpr}&f_WT={wt}&keywords={query}"
            page.goto(search_url)

            page_num = 1
            while True:
                try:
                    page.wait_for_selector(self.JOB_LIST, timeout=10000)
                except Exception as e:
                    break

                container_selector = self.JOB_LIST_CONTAINER
                for _ in range(5):
                    page.evaluate(
                        f"document.querySelector('{container_selector}').scrollBy({{ top: 1000, behavior: 'smooth' }})"
                    )
                    page.wait_for_timeout(500)

                job_listings = page.locator(f"{self.JOB_LIST} > li").all()

                for i, job_item in enumerate(job_listings):
                    try:
                        job_item.scroll_into_view_if_needed()
                        job_item.click()
                        page.wait_for_timeout(1500)

                        title = (
                            page.locator(self.TITLE_LINK)
                            .inner_text(timeout=2000)
                            .strip()
                        )
                        company = (
                            page.locator(self.COMPANY_LINK)
                            .inner_text(timeout=2000)
                            .strip()
                        )
                        description_parts = page.locator(
                            self.DESCRIPTION_TEXT
                        ).all_inner_texts()
                        description = "\n".join(
                            [p.strip() for p in description_parts if p.strip()]
                        )
                        url = page.url

                        yield Job(
                            title=title,
                            description=description,
                            company=company,
                            url=url,
                            platform="LinkedIn",
                            date_collected=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            job_category=None,
                            seniority_level=None,
                            employment_type=None,
                            contract_duration=None,
                            remote_type="Remote" if remote_only else None,
                            language=None,
                            monthly_salary_min_brl=None,
                            monthly_salary_max_brl=None,
                            experience_years_min=None,
                            hard_skills=None
                        )

                    except Exception as e:
                        pass

                max_pages = options.get("max_pages", 1)
                if page_num >= max_pages:
                    break

                next_button = page.locator(self.NEXT_PAGE_BUTTON)
                if next_button.is_visible() and next_button.is_enabled():
                    next_button.click()
                    page_num += 1
                    page.wait_for_timeout(2000)
                else:
                    break

            page.wait_for_timeout(1000)
            context.close()