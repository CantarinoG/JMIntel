from abc import ABC, abstractmethod
from typing import Dict, Any, Generator
from src.models.job import Job

class BaseScraper(ABC):
    """
    Abstract base class for all job board scrapers.
    """

    @abstractmethod
    def scrape_jobs(
        self, query: str, options: Dict[str, Any]
    ) -> Generator[Job, None, None]:
        """
        Scrape job listings based on a search query
        """
        pass