from abc import ABC, abstractmethod

class BaseExtractor(ABC):
    def __init__(self, url: str):
        self.url = url
        self.data = {}

    @abstractmethod
    def resolve_url(self) -> str:
        pass

    @abstractmethod
    def extract(self) -> dict:
        pass
