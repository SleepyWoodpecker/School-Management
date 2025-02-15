from sqlalchemy.exc import SQLAlchemyError


class DBAPIError(Exception):
    """base exception class for DB errors"""

    def __init__(
        self,
        message: str = "DB operation failed",
        sql_statement: str = None,
        params: str = None,
        original_error: str = None,
    ):
        self.message = message
        self.sql_statement = sql_statement
        self.params = params
        self.original_error = original_error

        super().__init__(self.message)

    @property
    def log_message(self) -> str:
        return f"{self.__class__.__name__}: {self.message} | SQL: {self.sql_statement} | params: {self.params} | original error :{str(self.original_error)}"


class DBConnectionError(DBAPIError):
    """error connecting to the database"""

    pass


class DBRecordNotFoundError(DBAPIError):
    """the requested record cannot be found in the DB"""

    pass
