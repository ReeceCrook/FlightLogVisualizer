from datetime import date

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field


class StrictModel(BaseModel):
    model_config = ConfigDict(strict=True)


class Flight(StrictModel):
    # Provenance
    source_row: int = Field(ge=1)

    # When
    logged_date: date
    departure_utc: AwareDatetime | None = Field(default=None)

    # Where
    origin_raw: str
    dest_raw: str
    via_raw: list[str] = Field(default_factory=list)

    origin_airport_id: int | None = None
    dest_airport_id: int | None = None
    via_airport_ids: list[int | None] = Field(default_factory=list)

    # Aircraft
    aircraft_type: str | None = None
    tail: str | None = None
    is_simulator: bool = False

    # Durations
    total_minutes: int = Field(ge=0)
    pic_minutes: int | None = Field(default=None, ge=0)
    sic_minutes: int | None = Field(default=None, ge=0)
    night_minutes: int | None = Field(default=None, ge=0)
    ifr_minutes: int | None = Field(default=None, ge=0)

    # Counts
    day_takeoffs: int | None = Field(default=None, ge=0)
    day_landings: int | None = Field(default=None, ge=0)
    night_takeoffs: int | None = Field(default=None, ge=0)
    night_landings: int | None = Field(default=None, ge=0)
    approaches: int | None = Field(default=None, ge=0)

    # People
    crew: list[str] = Field(default_factory=list)

    # Source Specific
    extras: dict[str, str] = Field(default_factory=dict)
