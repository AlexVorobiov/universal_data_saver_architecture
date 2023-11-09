from abc import ABC, abstractmethod
from typing import Any, List, Union, TypeVar

RawData = Union[str, bytes, list[dict]]
T = TypeVar('T')
ProcessedData = List[T]


class ConnectionOptions(ABC):
    pass


class DataSourceAdapter(ABC):
    @abstractmethod
    def connect(self, options: ConnectionOptions) -> None:
        pass

    @abstractmethod
    def fetch_data(self) -> RawData:
        pass


class DataTransformation(ABC):
    @abstractmethod
    def transform(self, data: RawData) -> ProcessedData:
        pass


class DataSaver(ABC):
    @abstractmethod
    def save(self, data: ProcessedData, target: Any):
        pass


class SynchronizationEngine(ABC):
    @abstractmethod
    def synchronize(self, source_adapter: DataSourceAdapter,
                    transformation: DataTransformation,
                    destination_adapter: DataSaver) -> bool:
        pass
