from uuid import uuid4

from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
    Model,
    Measurement,
    CalibrationRecord,
    AuditLog,
    User,
)


def unique_value(prefix):
    return f"{prefix}-{uuid4().hex[:12]}"


def test_create_instrument():
    db = SessionLocal()

    instrument = Instrument(
        name="V5 Test Instrument",
        manufacturer="Test Manufacturer",
        model="TEST-500",
        serial_number=unique_value("SERIAL"),
        instrument_type="gas_sensor",
        status="active",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    assert instrument.instrument_id is not None
    assert instrument.status == "active"

    db.delete(instrument)
    db.commit()
    db.close()


def test_instrument_configuration_relationship():
    db = SessionLocal()

    instrument = Instrument(
        name="Configuration Test Instrument",
        manufacturer="Test Manufacturer",
        model="CONFIG-100",
        serial_number=unique_value("SERIAL"),
        instrument_type="gas_sensor",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    configuration = InstrumentConfiguration(
        instrument_id=instrument.instrument_id,
        configuration_name="CO Configuration",
        input_schema='{"sensor_1": "float", "temperature": "float"}',
        target_variable="CO",
        unit="ppm",
        active=True,
    )

    db.add(configuration)
    db.commit()
    db.refresh(configuration)

    assert configuration.configuration_id is not None
    assert configuration.instrument_id == instrument.instrument_id
    assert configuration.instrument.instrument_id == instrument.instrument_id
    assert len(instrument.configurations) == 1

    db.delete(instrument)
    db.commit()
    db.close()


def test_calibration_policy_relationship():
    db = SessionLocal()

    instrument = Instrument(
        name="Policy Test Instrument",
        manufacturer="Test Manufacturer",
        model="POLICY-100",
        serial_number=unique_value("SERIAL"),
        instrument_type="gas_sensor",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    policy = CalibrationPolicy(
        instrument_id=instrument.instrument_id,
        calibration_interval_days=30,
        tolerance=0.5,
        reference_required=True,
        active=True,
    )

    db.add(policy)
    db.commit()
    db.refresh(policy)

    assert policy.policy_id is not None
    assert policy.calibration_interval_days == 30
    assert policy.instrument.instrument_id == instrument.instrument_id
    assert len(instrument.calibration_policies) == 1

    db.delete(instrument)
    db.commit()
    db.close()


def test_model_creation():
    db = SessionLocal()

    model = Model(
        model_name="V5 CO Calibration Model",
        model_version="1.0.0",
        instrument_type="gas_sensor",
        target_variable="CO",
        framework="scikit-learn",
        artifact_path="models/v2/co_calibration_model.joblib",
        artifact_hash=unique_value("HASH"),
        status="registered",
    )

    db.add(model)
    db.commit()
    db.refresh(model)

    assert model.model_id is not None
    assert model.model_version == "1.0.0"
    assert model.status == "registered"

    db.delete(model)
    db.commit()
    db.close()


def test_measurement_relationship():
    db = SessionLocal()

    instrument = Instrument(
        name="Measurement Test Instrument",
        manufacturer="Test Manufacturer",
        model="MEASURE-100",
        serial_number=unique_value("SERIAL"),
        instrument_type="gas_sensor",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    measurement = Measurement(
        instrument_id=instrument.instrument_id,
        measurement_data='{"sensor_1": 1000.0, "temperature": 20.0}',
    )

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    assert measurement.measurement_id is not None
    assert measurement.instrument.instrument_id == instrument.instrument_id
    assert len(instrument.measurements) == 1

    db.delete(instrument)
    db.commit()
    db.close()


def test_calibration_record_relationships():
    db = SessionLocal()

    instrument = Instrument(
        name="Calibration Test Instrument",
        manufacturer="Test Manufacturer",
        model="CAL-100",
        serial_number=unique_value("SERIAL"),
        instrument_type="gas_sensor",
    )

    db.add(instrument)

    model = Model(
        model_name="Test Calibration Model",
        model_version="1.0.0",
        instrument_type="gas_sensor",
        target_variable="CO",
        framework="scikit-learn",
        artifact_path="models/test.joblib",
        artifact_hash=unique_value("HASH"),
        status="approved",
    )

    db.add(model)

    db.commit()

    db.refresh(instrument)
    db.refresh(model)

    measurement = Measurement(
        instrument_id=instrument.instrument_id,
        measurement_data='{"sensor_1": 1000.0}',
    )

    db.add(measurement)
    db.commit()
    db.refresh(measurement)

    record = CalibrationRecord(
        instrument_id=instrument.instrument_id,
        model_id=model.model_id,
        measurement_id=measurement.measurement_id,
        measurement_time=measurement.created_at,
        estimated_value=2.1,
        reference_value=2.0,
        error=0.1,
        absolute_error=0.1,
        tolerance=0.5,
        status="PASS",
    )

    db.add(record)
    db.commit()
    db.refresh(record)

    assert record.record_id is not None
    assert record.instrument.instrument_id == instrument.instrument_id
    assert record.model.model_id == model.model_id
    assert record.measurement.measurement_id == measurement.measurement_id

    assert len(instrument.calibration_records) == 1
    assert len(model.calibration_records) == 1
    assert measurement.calibration_record.record_id == record.record_id

    db.delete(instrument)
    db.delete(model)
    db.commit()
    db.close()


def test_user_and_audit_log_relationship():
    db = SessionLocal()

    username = unique_value("user")
    email = f"{username}@example.com"

    user = User(
        username=username,
        email=email,
        password_hash="test-password-hash",
        role="ADMIN",
        status="active",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    audit = AuditLog(
        user_id=user.user_id,
        action="TEST_ACTION",
        entity_type="Instrument",
        entity_id=1,
        details="V5 database relationship test",
    )

    db.add(audit)
    db.commit()
    db.refresh(audit)

    assert user.user_id is not None
    assert audit.audit_id is not None
    assert audit.user.user_id == user.user_id
    assert len(user.audit_logs) == 1

    db.delete(user)
    db.commit()
    db.close()