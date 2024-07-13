import uuid
from datetime import datetime
from typing import Optional

from aiogram.types import Message
from pydantic import field_validator

from service.http2orm.api import APIClientModel


class Language(APIClientModel):
    pass


class Localization(APIClientModel):
    lang_code: str
    welcome_message: str


class Driver(APIClientModel):
    photo: Optional[str] = None
    profile: Optional[int] = None
    car_number: Optional[str] = None
    fullname: Optional[str] = None
    accepted: bool = False
    rate: float = 0.0


class User(APIClientModel):
    class AdditionalFields:
        location_message: Optional[Message] = None
    id: int
    username: Optional[str] = None
    phone_number: Optional[str] = None
    lang: Optional[str] = None
    ban: bool
    registered: bool
    driver: Optional[Driver]


class Trip(APIClientModel):
    class Status:
        WAIT_DRIVER = 'WAIT_DRIVER'
        WAIT_PASSENGER = 'WAIT_PASSENGER'
        RIDE = 'RIDE'
        COMPLETED = 'COMPLETED'
    id: Optional[str] = None
    passenger: Optional[int]
    driver: Optional[int]
    start_location_latitude: float
    start_location_longitude: float
    end_location_latitude: float
    end_location_longitude: float
    current_location_latitude: float
    current_location_longitude: float
    start_time: Optional[datetime.date] = None
    end_time: Optional[datetime.date] = None
    price: Optional[float]
    status: str = Status.WAIT_DRIVER



class Review(APIClientModel):
    id: Optional[str] = None
    driver: int
    trip: str
    text: str
    rating: float
