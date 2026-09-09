import json

import joblib
import pytest
from sklearn.dummy import DummyRegressor

from src.v5.database.database import SessionLocal
from src.v5.database.models import (
    Instrument,
    InstrumentConfiguration,
    CalibrationPolicy,
    Model,
)
from src.v5.services.measurement_service import (
    create_measurement,
)
from src.v5.services.calibration_engine import (
    run_calibration,
)


TEST_MODEL_PATH = "models/v5_test_model.joblib"


def create_test_setup(
    model_status="approved",
):
    db = SessionLocal()

    instrument = Instrument(
        name="Calibration Test Instrument",
        manufacturer="Test Manufacturer",
        model="CE-100",
        serial_number="CAL-ENGINE-TEST-001",
        instrument_type="gas_analyzer",
        status="active",
    )

    db.add(instrument)
    db.commit()
    db.refresh(instrument)

    configuration = InstrumentConfiguration(
        instrument_id=instrument.instrument_id,
        configuration_name="Test CO Configuration",
        input_schema=json.dumps(
            {
                "sensor_1": "sensor_1",
                "sensor_2": "sensor_2",
            }
        ),
        target_variable="CO(GT)",
        unit="mg/m3",
        active=True,
    )

    policy = CalibrationPolicy(
        instrument_id=instrument.instrument_id,
        calibration_interval_days=30,
        tolerance=0.5,
        reference_required=True,
        active=True,
    )

    model = Model(
        model_name="Test Calibration Model",
        model_version="test-1.0.0",
        instrument_type="gas_analyzer",
        target_variable="CO(GT)",
        framework="sklearn",
        artifact_path=TEST_MODEL_PATH,
        artifact_hash="test-hash",
        status=model_status,
    )

    db.add(configuration)
    db.add(policy)
    db.add(model)
    db.commit()

    instrument_id = instrument.instrument_id
    model_id = model.model_id

    db.close()

    return instrument_id, model_id


def delete_test_instrument(instrument_id):
    db = SessionLocal()

    instrument = (
        db.query(Instrument)
        .filter(
            Instrument.instrument_id == instrument_id
        )
        .first()
    )

    if instrument:
        db.delete(instrument)
        db.commit()

    db.close()


def delete_test_models():
    db = SessionLocal()

    db.query(Model).filter(
        Model.model_name == "Test Calibration Model"
    ).delete(
        synchronize_session=False
    )

    db.commit()
    db.close()


def create_test_model():
    model = DummyRegressor(
        strategy="constant",
        constant=5.0,
    )

    model.fit(
        [[1, 2]],
        [5],
    )

    joblib.dump(
        model,
        TEST_MODEL_PATH,
    )


def test_successful_calibration_pass():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        record = run_calibration(
            instrument_id=instrument_id,
            measurement_id=measurement.measurement_id,
            model_id=model_id,
            reference_value=5.2,
        )

        assert record.record_id is not None
        assert record.instrument_id == instrument_id
        assert record.model_id == model_id
        assert (
            record.measurement_id
            == measurement.measurement_id
        )
        assert record.estimated_value == 5.0
        assert record.reference_value == 5.2
        assert record.absolute_error == 0.2
        assert record.status == "PASS"

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_successful_calibration_fail():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        record = run_calibration(
            instrument_id=instrument_id,
            measurement_id=measurement.measurement_id,
            model_id=model_id,
            reference_value=6.0,
        )

        assert record.estimated_value == 5.0
        assert record.reference_value == 6.0
        assert record.absolute_error == 1.0
        assert record.status == "FAIL"

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_invalid_instrument():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="does not exist",
        ):
            run_calibration(
                instrument_id=999999,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_measurement_must_belong_to_instrument():
    create_test_model()

    instrument_id_1, model_id = create_test_setup()

    db = SessionLocal()

    instrument_2 = Instrument(
        name="Second Test Instrument",
        manufacturer="Test Manufacturer",
        model="CE-200",
        serial_number="CAL-ENGINE-TEST-002",
        instrument_type="gas_analyzer",
        status="active",
    )

    db.add(instrument_2)
    db.commit()
    db.refresh(instrument_2)

    instrument_id_2 = instrument_2.instrument_id

    db.close()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id_1,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="does not exist for this instrument",
        ):
            run_calibration(
                instrument_id=instrument_id_2,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id_1)
        delete_test_instrument(instrument_id_2)
        delete_test_models()


def test_unapproved_model_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup(
        model_status="registered"
    )

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="must be approved",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_missing_reference_value_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="greater than 0",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_missing_measurement_input_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
            },
        )

        with pytest.raises(
            ValueError,
            match="missing required input",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_missing_active_configuration_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    db = SessionLocal()

    configurations = (
        db.query(InstrumentConfiguration)
        .filter(
            InstrumentConfiguration.instrument_id
            == instrument_id
        )
        .all()
    )

    for configuration in configurations:
        configuration.active = False

    db.commit()
    db.close()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="No active instrument configuration",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_missing_active_policy_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    db = SessionLocal()

    policies = (
        db.query(CalibrationPolicy)
        .filter(
            CalibrationPolicy.instrument_id
            == instrument_id
        )
        .all()
    )

    for policy in policies:
        policy.active = False

    db.commit()
    db.close()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="No active calibration policy",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()


def test_target_variable_mismatch_rejected():
    create_test_model()

    instrument_id, model_id = create_test_setup()

    db = SessionLocal()

    configuration = (
        db.query(InstrumentConfiguration)
        .filter(
            InstrumentConfiguration.instrument_id
            == instrument_id
        )
        .first()
    )

    configuration.target_variable = "NO2"

    db.commit()
    db.close()

    try:
        measurement = create_measurement(
            instrument_id=instrument_id,
            measurement_data={
                "sensor_1": 1,
                "sensor_2": 2,
            },
        )

        with pytest.raises(
            ValueError,
            match="target does not match",
        ):
            run_calibration(
                instrument_id=instrument_id,
                measurement_id=measurement.measurement_id,
                model_id=model_id,
                reference_value=5.0,
            )

    finally:
        delete_test_instrument(instrument_id)
        delete_test_models()