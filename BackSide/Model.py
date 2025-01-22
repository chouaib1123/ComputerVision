from sqlalchemy import create_engine, Column, Integer, String, Date, UniqueConstraint, ForeignKey, DateTime, Time
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime
from typing import List
import logging
from enum import Enum
from sqlalchemy import Enum as SQLEnum

Base = declarative_base()

class Person(Base):
    __tablename__ = 'persons'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, unique=True)
    image_path = Column(String(255), nullable=False)
    
    presences = relationship('Presence', back_populates='person')
    
    def __repr__(self):
        return f"<Person(name='{self.name}')>"

def add_person(session, name: str, image_path: str) -> Person:
    person = Person(name=name, image_path=image_path)
    session.add(person)
    session.commit()
    return person

def get_all_persons(session) -> List[Person]:
    return session.query(Person).all()

class TimeRange(str, Enum):
    RANGE_8_10 = "8:00-10:00"
    RANGE_10_12 = "10:00-12:00"
    RANGE_14_16 = "14:00-16:00"
    RANGE_16_19 = "16:00-19:00"

class Presence(Base):
    __tablename__ = 'presences'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    presence_date = Column(Date, nullable=False)
    presence_time = Column(Time, nullable=False)
    time_range = Column(SQLEnum(TimeRange), nullable=False)
    
    person = relationship('Person', back_populates='presences')
    
    __table_args__ = (
        UniqueConstraint('person_id', 'presence_date', 'time_range', name='unique_presence_per_range'),
    )
    
    def __repr__(self):
        return f"<Presence(person_id='{self.person_id}', date='{self.presence_date}', time='{self.presence_time}', range='{self.time_range}')>"