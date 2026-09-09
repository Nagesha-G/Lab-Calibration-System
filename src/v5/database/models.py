from datetime import datetime

from sqlalchemy import (
    String,
    Float,
    DateTime,
    ForeignKey,
    Boolean,
    Text,
    Integer
)

from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.v5.database.database import Base


class Instrument(Base):
    __tablename__ = "instruments"

    instrument_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    manufacturer: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    model: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    serial_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    instrument_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

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

    configurations: Mapped[list["InstrumentConfiguration"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan"
    )

    calibration_policies: Mapped[list["CalibrationPolicy"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan"
    )

    measurements: Mapped[list["Measurement"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan"
    )

    calibration_records: Mapped[list["CalibrationRecord"]] = relationship(
        back_populates="instrument",
        cascade="all, delete-orphan"
    )


class InstrumentConfiguration(Base):
    __tablename__ = "instrument_configurations"

    configuration_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.instrument_id"),
        nullable=False
    )

    configuration_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    input_schema: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    target_variable: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="configurations"
    )


class CalibrationPolicy(Base):
    __tablename__ = "calibration_policies"

    policy_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.instrument_id"),
        nullable=False
    )

    calibration_interval_days: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    tolerance: Mapped[float] = mapped_column(
        Float,
        nullable=False
    )

    reference_required: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        onupdate=datetime.now,
        nullable=False
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="calibration_policies"
    )


class Model(Base):
    __tablename__ = "models"

    model_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    model_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False
    )

    model_version: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    instrument_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    target_variable: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    framework: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    artifact_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False
    )

    artifact_hash: Mapped[str] = mapped_column(
        String(128),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="registered",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    calibration_records: Mapped[list["CalibrationRecord"]] = relationship(
        back_populates="model"
    )


class Measurement(Base):
    __tablename__ = "measurements"

    measurement_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.instrument_id"),
        nullable=False
    )

    measurement_data: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    instrument: Mapped["Instrument"] = relationship(
        back_populates="measurements"
    )

    calibration_record: Mapped["CalibrationRecord"] = relationship(
        back_populates="measurement",
        uselist=False
    )


class CalibrationRecord(Base):
    __tablename__ = "calibration_records"

    record_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    instrument_id: Mapped[int] = mapped_column(
        ForeignKey("instruments.instrument_id"),
        nullable=False
    )

    model_id: Mapped[int] = mapped_column(
        ForeignKey("models.model_id"),
        nullable=False
    )

    measurement_id: Mapped[int] = mapped_column(
        ForeignKey("measurements.measurement_id"),
        nullable=False,
        unique=True
    )

    measurement_time: Mapped[datetime] = mapped_column(
        DateTime,
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

    absolute_error: Mapped[float] = mapped_column(
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

    model: Mapped["Model"] = relationship(
        back_populates="calibration_records"
    )

    measurement: Mapped["Measurement"] = relationship(
        back_populates="calibration_record"
    )


class AuditLog(Base):
    __tablename__ = "audit_logs"

    audit_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=True
    )

    action: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    entity_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    entity_id: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )

    details: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    user: Mapped["User | None"] = relationship(
        back_populates="audit_logs"
    )


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False
    )

    email: Mapped[str] = mapped_column(
        String(200),
        unique=True,
        nullable=False
    )

    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    role: Mapped[str] = mapped_column(
        String(50),
        nullable=False
    )

    status: Mapped[str] = mapped_column(
        String(30),
        default="active",
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False
    )

    audit_logs: Mapped[list["AuditLog"]] = relationship(
        back_populates="user"
    )