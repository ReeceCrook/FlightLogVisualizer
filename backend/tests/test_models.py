from datetime import date

import pytest
from pydantic import ValidationError

from flightlog.models import Flight

REQUIRED_FIELDS = [
    "source_row",
    "logged_date",
    "origin_raw",
    "dest_raw",
    "total_minutes",
]

NON_NEGATIVE_FIELDS = [
    "total_minutes",
    "pic_minutes",
    "sic_minutes",
    "night_minutes",
    "ifr_minutes",
    "day_takeoffs",
    "day_landings",
    "night_takeoffs",
    "night_landings",
    "approaches",
]


@pytest.fixture
def valid_flight_data():
    return {
        "source_row": 2,
        "logged_date": date(2026, 11, 4),
        "origin_raw": " kism",
        "dest_raw": "KPBI",
        "total_minutes": 144,
    }


def test_minimal_flight_keeps_required_values_unchanged(valid_flight_data):
    my_processed_flight = Flight.model_validate(valid_flight_data)
    assert my_processed_flight.source_row == 2
    assert my_processed_flight.logged_date == date(2026, 11, 4)
    assert my_processed_flight.origin_raw == " kism"
    assert my_processed_flight.dest_raw == "KPBI"
    assert my_processed_flight.total_minutes == 144


def test_optional_fields_defaults(valid_flight_data):
    my_processed_flight = Flight.model_validate(valid_flight_data)
    # When
    assert my_processed_flight.departure_utc is None

    # Where
    assert my_processed_flight.via_raw == []
    assert my_processed_flight.origin_airport_id is None
    assert my_processed_flight.dest_airport_id is None
    assert my_processed_flight.via_airport_ids == []

    # Aircraft
    assert my_processed_flight.aircraft_type is None
    assert my_processed_flight.tail is None
    assert my_processed_flight.is_simulator is False

    # Durations
    assert my_processed_flight.pic_minutes is None
    assert my_processed_flight.sic_minutes is None
    assert my_processed_flight.night_minutes is None
    assert my_processed_flight.ifr_minutes is None

    # Counts
    assert my_processed_flight.day_takeoffs is None
    assert my_processed_flight.day_landings is None
    assert my_processed_flight.night_takeoffs is None
    assert my_processed_flight.night_landings is None
    assert my_processed_flight.approaches is None

    # People
    assert my_processed_flight.crew == []

    # Source Specific
    assert my_processed_flight.extras == {}


@pytest.mark.parametrize("field_name", NON_NEGATIVE_FIELDS)
def test_negative_values_are_rejected(valid_flight_data, field_name):
    valid_flight_data[field_name] = -1

    with pytest.raises(ValidationError) as exc_info:
        Flight.model_validate(valid_flight_data)

    assert exc_info.value.errors()[0]["loc"] == (field_name,)
    assert exc_info.value.errors()[0]["type"] == "greater_than_equal"


@pytest.mark.parametrize("field_name", NON_NEGATIVE_FIELDS)
def test_zero_values_are_accepted(valid_flight_data, field_name):
    valid_flight_data[field_name] = 0
    my_processed_flight = Flight.model_validate(valid_flight_data)

    assert getattr(my_processed_flight, field_name) == 0


def test_source_row_zero_is_rejected(valid_flight_data):
    valid_flight_data["source_row"] = 0

    with pytest.raises(ValidationError) as exc_info:
        Flight.model_validate(valid_flight_data)

    assert exc_info.value.errors()[0]["loc"] == ("source_row",)
    assert exc_info.value.errors()[0]["type"] == "greater_than_equal"


def test_source_row_one_is_accepted(valid_flight_data):
    valid_flight_data["source_row"] = 1
    my_processed_flight = Flight.model_validate(valid_flight_data)

    assert my_processed_flight.source_row == 1


@pytest.mark.parametrize("field_name", REQUIRED_FIELDS)
def test_missing_required_field_is_rejected(valid_flight_data, field_name):
    valid_flight_data.pop(field_name)

    with pytest.raises(ValidationError) as exc_info:
        Flight.model_validate(valid_flight_data)

    assert exc_info.value.errors()[0]["loc"] == (field_name,)
    assert exc_info.value.errors()[0]["type"] == "missing"
    assert len(exc_info.value.errors()) == 1
