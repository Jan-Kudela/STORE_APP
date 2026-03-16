
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "sqlite:///warehouse.db"

engine = create_engine(DATABASE_URL, echo=False)

Session = sessionmaker(bind=engine)

Base = declarative_base()
