from src.v3.database import engine, Base
from src.v3.models import Instrument


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully.")
    print("Instrument table created.")


if __name__ == "__main__":
    initialize_database()