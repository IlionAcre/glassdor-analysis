from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class GD_JOB(Base):
    __tablename__ = "gd_jobs"
    id = Column(Integer(), primary_key=True)
    title = Column(String())
    location = Column(String())
    salary = Column(String())
    description = Column(String())
    
    size = Column(String())
    founded = Column(String())
    type = Column(String())
    industry = Column(String())
    sector = Column(String())
    revenue = Column(String())

    rating = Column(Integer())

    link = Column(String())

    def __repr__(self):
        return f"{self.title}\n{self.location}\n{self.salary}"
    
    def add_company(self, size, founded, type, industry, sector, revenue):
        self.size = size
        self.founded = founded
        self.type = type
        self.industry = industry
        self.sector = sector
        self.revenue = revenue

    def add_rating(self, rating):
        self.rating = rating

class GD_JOBS_USA(Base):
    __tablename__ = 'gd_jobs_usa'
    id = Column(Integer(), primary_key=True)
    title = Column(String())
    location = Column(String())
    salary = Column(String())
    description = Column(String())
    
    size = Column(String())
    founded = Column(String())
    type = Column(String())
    industry = Column(String())
    sector = Column(String())
    revenue = Column(String())

    rating = Column(Integer())

    link = Column(String())

    def __repr__(self):
        return f"{self.title}\n{self.location}\n{self.salary}"
    
    def add_company(self, size, founded, type, industry, sector, revenue):
        self.size = size
        self.founded = founded
        self.type = type
        self.industry = industry
        self.sector = sector
        self.revenue = revenue

    def add_rating(self, rating):
        self.rating = rating
