from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GD_JOB(Base):
    __tablename__ = "gd_jobs"
    id = Column(Integer(), primary_key=True)
    title = Column(String())
    location = Column(String())
    salary = Column(String())
    link = Column(String())

    def __repr__(self):
        return f"{self.title}\n{self.location}\n{self.salary}"