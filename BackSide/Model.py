from sqlalchemy import create_engine, Column, Integer, String, Date, UniqueConstraint, ForeignKey, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import date, datetime
from typing import List
import logging

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

class Presence(Base):
    __tablename__ = 'presences'
    
    id = Column(Integer, primary_key=True)
    person_id = Column(Integer, ForeignKey('persons.id'), nullable=False)
    presence_datetime = Column(DateTime, nullable=False)  # Changed from presence_date
    
    person = relationship('Person', back_populates='presences')
    
    __table_args__ = (UniqueConstraint('person_id', 'presence_datetime', name='unique_presence_datetime'),)
    
    def __repr__(self):
        return f"<Presence(person_id='{self.person_id}', datetime='{self.presence_datetime}')>"
