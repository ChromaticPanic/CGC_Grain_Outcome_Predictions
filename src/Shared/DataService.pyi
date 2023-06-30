import sqlalchemy as sq

class DataService:
    dbURL: str
    engine: sq.engine.base.Engine
    conn: sq.engine.base.Connection
    def __init__(
        self,
        db: str = ...,
        addr: str = ...,
        port: int = ...,
        user: str = ...,
        pw: str = ...,
    ) -> None: ...
    def connect(self) -> sq.engine.base.Connection: ...
    def disconnect(self) -> None: ...
    def cleanup(self) -> None: ...
    def execute(self, query) -> object: ...
