from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date, datetime, time
import logging
from Model import Base, Person, Presence, TimeRange

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

    def _get_current_time_range(self) -> TimeRange:
        current_time = datetime.now().time()
        ranges = {
            (time(8), time(10)): TimeRange.RANGE_8_10,
            (time(10), time(12)): TimeRange.RANGE_10_12,
            (time(14), time(16)): TimeRange.RANGE_14_16,
            (time(16), time(19)): TimeRange.RANGE_16_19,
        }
        
        for (start, end), time_range in ranges.items():
            if start <= current_time <= end:
                return time_range
        return None

    def store_presence(self, person_name):
        session = self.Session()
        try:
            person = session.query(Person).filter(Person.name == person_name).first()
            if not person:
                return False, "Person not found"

            current_time_range = self._get_current_time_range()
            if not current_time_range:
                return False, "Outside of valid time ranges"

            current_date = datetime.now().date()
            current_time = datetime.now().time()

            # Check if presence already exists for this time range
            existing_presence = session.query(Presence).filter(
                Presence.person_id == person.id,
                Presence.presence_date == current_date,
                Presence.time_range == current_time_range
            ).first()

            if existing_presence:
                return True, "Presence already recorded"

            new_presence = Presence(
                person_id=person.id,
                presence_date=current_date,
                presence_time=current_time,
                time_range=current_time_range
            )
            session.add(new_presence)
            session.commit()
            return True, "Presence recorded successfully"

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
            persons = session.query(Person).all()
            result = []
            for person in persons:
                presences = session.query(Presence).filter(
                    Presence.person_id == person.id,
                    Presence.presence_date == datetime.now().date()
                ).all()
                
                presence_data = {str(p.time_range): True for p in presences}
                
                result.append({
                    "id": person.id,
                    "name": person.name,
                    "image_path": person.image_path,
                    "presences": presence_data
                })
            return result
        finally:
            session.close()