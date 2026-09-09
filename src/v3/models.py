from datetime import datetime

from sqlalchemy import String, Float, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.v3.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    instrument_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    manufacturer: Mapped[str] = mapped_column(String(100), nullable=False)
    model: Mapped[str] = mapped_column(String(100), nullable=False)
    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )
    instrument_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[str] = mapped_column(
        String(20),
        default="active",
        nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    calibration_records: Mapped[list["CalibrationRecord"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan"
    )


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    record_id: Mapped[int] = mapped_column(
        primary_key=True,
        autoincrement=True
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.instrument_id"),
        nullable=False
    )

    measurement_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    estimated_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    reference_value: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    error: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    tolerance: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="calibration_records"
    )