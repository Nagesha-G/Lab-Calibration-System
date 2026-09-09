from src.v5.database.database import Base, engine

# Import all models so SQLAlchemy knows about them.
from src.v5.database import models


def initialize_database():
    Base.metadata.create_all(bind=engine)
    print("V5 database initialized successfully.")


if __name__ == "__main__":
    initialize_database()