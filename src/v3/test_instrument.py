from src.v3.database import SessionLocal
from src.v3.models import Instrument


def create_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="CO Monitor 01",
        manufacturer="Test Manufacturer",
        model="CO-X100",
        serial_number="CO-2026-001",
        instrument_type="CO Sensor",
        status="active"
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    print("Instrument created successfully.")
    print(f"Instrument ID: {instrument.instrument_id}")
    print(f"Name: {instrument.name}")
    print(f"Serial Number: {instrument.serial_number}")

    db.close()


if __name__ == "__main__":
    create_instrument()