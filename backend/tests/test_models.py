from datetime import date

import pytest
from pydantic import ValidationError

from flightlog.models import Flight


def test_minimal_flight_keeps_required_values_unchanged():

    my_raw_flight = {
        "source_row": 2,
        "logged_date": date(2026, 11, 4),
        "origin_raw": " kism",
        "dest_raw": "KPBI",
        "total_minutes": 144,
    }

    my_processed_flight = Flight.model_validate(my_raw_flight)
    assert my_processed_flight.source_row == 2
    assert my_processed_flight.logged_date == date(2026, 11, 4)
    assert my_processed_flight.origin_raw == " kism"
    assert my_processed_flight.dest_raw == "KPBI"
    assert my_processed_flight.total_minutes == 144


def test_optional_fields_defaults():
    my_raw_flight = {
        "source_row": 2,
        "logged_date": date(2026, 11, 4),
        "origin_raw": " kism",
        "dest_raw": "KPBI",
        "total_minutes": 144,
    }

    my_processed_flight = Flight.model_validate(my_raw_flight)
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


def test_negative_minutes_are_rejected():
    my_raw_flight = {
        "source_row": 2,
        "logged_date": date(2026, 11, 4),
        "origin_raw": " kism",
        "dest_raw": "KPBI",
        "total_minutes": -144,
    }

    with pytest.raises(ValidationError) as exc_info:
        Flight.model_validate(my_raw_flight)

    assert exc_info.value.errors()[0]["loc"] == ("total_minutes",)
    assert exc_info.value.errors()[0]["type"] == "greater_than_equal"
