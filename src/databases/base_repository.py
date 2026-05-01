from abc import ABC, abstractmethod
from typing import List
from src.models.job import Job

class BaseJobRepository(ABC):
    """
    Abstract base class for job storage.
    Follows the Repository Pattern to decouple the application logic
    from specific database implementations (SQL vs NoSQL vs File).
    """

    @abstractmethod
    def save(self, job: Job) -> bool:
        """
        Save or update a job in the storage.
        """
        pass

    @abstractmethod
    def get_unprocessed(self) -> List[Job]:
        """
        Retrieve all jobs that have not been processed yet.
        """
        pass

    @abstractmethod
    def update(self, job: Job) -> bool:
        """
        Update an existing job in the storage.
        """
        pass