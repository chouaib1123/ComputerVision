from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from Model import Base, Person

def initialize_database(db_url="sqlite:///presence.db"):
    # Initialize the database
    engine = create_engine(db_url)
    Base.metadata.create_all(engine)
    
    # Create session
    Session = sessionmaker(bind=engine)
    session = Session()

    # Reference images with names
    reference_images = {
        #"Chouaib Mounssif": r".\Images\cho.jpeg",
        "Fatiha Agdoud": r".\Images\Fat.jpg",
        "Mouhcine Ouaaziz": r".\Images\mo.jpeg",
        "Abdellah Fazza": r".\Images\faz.jpg"
    }

    try:
        # Insert persons with image paths into database
        for name, image_path in reference_images.items():
            person = Person(name=name, image_path=image_path)
            session.add(person)
        
        session.commit()
        print("Database initialized with persons and their image paths!")
        
    except Exception as e:
        session.rollback()
        print(f"Error during initialization: {str(e)}")
    finally:
        session.close()

if __name__ == "__main__":
    initialize_database()