from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime
import logging
from Model import Base, Person, Presence

class PresenceManager:
    def __init__(self, db_url):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def get_session(self):
        return self.Session()

    def get_all_persons(self):
        session = self.Session()
        try:
            return session.query(Person).all()
        finally:
            session.close()

    def store_presence(self, person_name):
        session = self.Session()
        try:
            person = session.query(Person).filter_by(name=person_name).first()
            if person:
                now = datetime.now()
                today_start = datetime(now.year, now.month, now.day)
                
                # Check if person already has presence today
                existing_presence = session.query(Presence).filter(
                    Presence.person_id == person.id,
                    Presence.presence_datetime >= today_start
                ).first()
                
                if existing_presence:
                    return False, f"{person.name}"
                
                presence = Presence(
                    person_id=person.id,
                    presence_datetime=now
                )
                session.add(presence)
                session.commit()
                return True, f"{person.name}"
            else:
                return False, "Person not found"
        except Exception as e:
            session.rollback()
            return False, str(e)
        finally:
            session.close()

    def presence_to_dict(self, presence):
        return {
            "id": presence.id,
            "person_id": presence.person_id,
            "presence_datetime": presence.presence_datetime.isoformat()
        }

    def get_todays_presence(self):
        session = self.Session()
        try:
            today_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
            presences = session.query(Presence).filter(Presence.presence_datetime >= today_start).all()
            return [self.presence_to_dict(presence) for presence in presences]
        finally:
            session.close()

    def get_all_persons_with_presence(self):
        session = self.Session()
        try:
            today_start = datetime(datetime.now().year, datetime.now().month, datetime.now().day)
            persons = session.query(Person).all()
            result = []
            for person in persons:
                presence = session.query(Presence).filter(
                    Presence.person_id == person.id,
                    Presence.presence_datetime >= today_start
                ).order_by(Presence.presence_datetime.desc()).first()
                
                if presence:
                    result.append({
                        "id": person.id,
                        "name": person.name,
                        "presence_datetime": presence.presence_datetime.isoformat()
                    })
                else:
                    result.append({
                        "id": person.id,
                        "name": person.name,
                        "presence_datetime": None
                    })
            return result
        finally:
            session.close()