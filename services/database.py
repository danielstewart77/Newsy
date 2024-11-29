import threading
import os
import logging
import psycopg2
from sqlalchemy.orm import sessionmaker, scoped_session, Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base

logging.basicConfig(level=logging.DEBUG)  # Set the logging level to DEBUG
logger = logging.getLogger(__name__)

Base = declarative_base()

class DatabaseService:
    _instance = None
    _lock = threading.Lock()
    _session_factory = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:  # Thread-safe singleton initialization
                if not cls._instance:
                    cls._instance = super().__new__(cls, *args, **kwargs)
                    cls._instance._init_engine()
        return cls._instance

    def _init_engine(self):
        try:
            db_user = os.getenv('DB_USER')
            db_password = os.getenv('DB_PASSWORD')
            db_host = os.getenv('DB_HOST')
            db_port = os.getenv('DB_PORT')
            db_name = os.getenv('DB_NAME')

            connection_string = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            self.engine = create_engine(connection_string)
            Base.metadata.create_all(self.engine)
            self._session_factory = sessionmaker(bind=self.engine)
        except SQLAlchemyError as e:
            logger.error(f"Error initializing the database engine: {e}", exc_info=True)

    def get_session(self) -> Session:
        if not self._session_factory:
            with self._lock:
                if not self._session_factory:
                    self._init_engine()
        return scoped_session(self._session_factory)