from src.v3.database import SessionLocal
from src.v3.models import Instrument


def list_instruments():
    db = SessionLocal()

    instruments = db.query(Instrument).all()

    print(f"Total instruments: {len(instruments)}")
    print()

    for instrument in instruments:
        print(f"ID: {instrument.instrument_id}")
        print(f"Name: {instrument.name}")
        print(f"Manufacturer: {instrument.manufacturer}")
        print(f"Model: {instrument.model}")
        print(f"Serial Number: {instrument.serial_number}")
        print(f"Type: {instrument.instrument_type}")
        print(f"Status: {instrument.status}")
        print(f"Created: {instrument.created_at}")
        print("-" * 40)

    db.close()


if __name__ == "__main__":
    list_instruments()