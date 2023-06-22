import sqlalchemy as sq
from _typeshed import Incomplete

class DataService:
    dbURL: Incomplete
    engine: Incomplete
    conn: Incomplete
    def __init__(
        self,
        db: str = ...,
        addr: str = ...,
        port: int = ...,
        user: str = ...,
        pw: str = ...,
    ) -> None: ...
    def connect(self) -> sq.Connection: ...
    def disconnect(self) -> None: ...
    def cleanup(self) -> None: ...
    def execute(self, query) -> object: ...
