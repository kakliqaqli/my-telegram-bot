import asyncio
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Optional, List, Set, Tuple

from apscheduler.job import Job
from apscheduler.triggers.interval import IntervalTrigger
from aiogram.types import Location, Message
from geopy.distance import geodesic

from service.http2orm.models import Trip
from service.managers.user_data_manager import UserData
import bootstrap
from states.states import DriverSearchSG, OrderStates

scheduler = bootstrap.Scheduler().getInstance()
bot = bootstrap.MyBot().getInstance()


@dataclass
class DriverData:
    user: UserData
    current_location: Location
    location_message: Message
    active: bool = True


@dataclass
class RideRequest:
    user: UserData
    start_location: Location
    end_location: Location
    start_address: str
    end_address: str
    distance: float
    map_url: str
    price: float = None

    def __post_init__(self):
        self.distance = float(self.distance)
        self.price = round(self.distance * 5, 2)


@dataclass
class Ride:
    trip: Trip
    driver: DriverData
    request: RideRequest

    def calculate_status_dict(self):
        attributes = [attr for attr in vars(self.trip.Status) if
                      not callable(getattr(self.trip.Status, attr)) and not attr.startswith("__")]
        current_status = self.trip.status
        return {status: True if status == current_status else False for status in attributes}


class RideRequestManager:
    requests: Dict[int, RideRequest] = {}

    async def add_request(self, user_data: UserData, request_data: dict):
        if user_data.user_id in self.requests:
            return
        args_map = ['latitude', 'longitude']
        _location = lambda x: dict(zip(args_map, x))
        request = RideRequest(
            user=user_data,
            start_location=Location(**_location(request_data['from']['coords'])),
            end_location=Location(**_location(request_data['to']['coords'])),
            start_address=request_data['from']['address'],
            end_address=request_data['to']['address'],
            distance=request_data['route']['distance'],
            map_url=request_data['route']['map_url'],
        )
        self.requests[user_data.user_id] = request

    async def remove_request(self, user_id: int) -> Optional[UserData]:
        return self.requests.pop(user_id, None)


class DriverManager:
    def __init__(self):
        self.drivers: Dict[int, DriverData] = {}

    async def add_driver(self, user_data: UserData, location_message: Message):
        if user_data.user_id in self.drivers:
            return
        self.drivers[user_data.user_id] = DriverData(
            user=user_data,
            current_location=location_message.location,
            location_message=location_message
        )

    async def remove_driver(self, driver_id: int) -> Optional[DriverData]:
        driver = self.drivers.pop(driver_id, None)
        try:
            await driver.location_message.delete()
        except:
            pass
        return driver

    async def update_location(self, driver_id: int, message: Message):
        if driver_id in self.drivers:
            self.drivers[driver_id].location_message = message
            self.drivers[driver_id].current_location = message.location

    async def deactivate_driver(self, driver_id: int):
        if driver_id in self.drivers:
            self.drivers[driver_id].active = False


class RideManager:
    def __init__(self):
        self.rides: Dict[str, Ride] = {}
        self.users_map: Dict[int, Ride] = {}

    async def create_ride(self, driver: DriverData, request: RideRequest):
        trip = Trip.empty_instance()
        trip.passenger = request.user.user_id
        trip.driver = driver.user.user_id
        trip.start_location_latitude = request.start_location.latitude
        trip.start_location_longitude = request.start_location.longitude
        trip.end_location_latitude = request.end_location.latitude
        trip.end_location_longitude = request.end_location.longitude
        trip.current_location_latitude = driver.current_location.latitude
        trip.current_location_longitude = driver.current_location.longitude
        trip.price = request.price
        trip.start_time = datetime.now().date()
        print(trip, flush=True)
        trip = await trip.create()
        ride = Ride(trip=trip, driver=driver, request=request)
        self.rides[trip.id] = ride
        self.users_map[request.user.user_id] = ride
        self.users_map[driver.user.user_id] = ride
        driver.active = False
        return trip

    async def remove_ride(self, trip_id: str) -> Optional[Ride]:
        return self.rides.pop(trip_id, None)

    async def get_trip_by_user(self, user_id: int) -> Optional[Ride]:
        for ride in self.rides.values():
            if any((ride.request.user.user_id == user_id,
                    ride.driver.user.user_id == user_id)):
                return ride


class RideSystem:
    request_manager = RideRequestManager()
    driver_manager = DriverManager()
    ride_manager = RideManager()
    matched_drivers: Dict[int, set[int]] = {}
    matched_users: Dict[int, set[int]] = {}
    driver_skipped: Dict[int, set[int]] = {}
    lock = asyncio.Lock()

    async def add_driver(self, user_data: UserData, location_message: Message):
        print(user_data, location_message, flush=True)
        await self.driver_manager.add_driver(user_data, location_message)
        await self.generate_pairs()

    async def add_request(self, user_data: UserData, request_data: dict):
        await self.request_manager.add_request(user_data, request_data)
        await self.generate_pairs()

    async def assign_ride(self, user_id: int, driver_id: int):
        async with self.lock:
            if user_id in self.ride_manager.users_map:
                return
            request = self.request_manager.requests[user_id]
            driver = self.driver_manager.drivers[driver_id]
            await self.ride_manager.create_ride(request=request, driver=driver)
            user_bg_manager = await request.user.create_bg_manager()
            await user_bg_manager.start(OrderStates.ride)
            driver_bg_manager = await driver.user.create_bg_manager()
            await driver_bg_manager.start(DriverSearchSG.ride)

    async def update_location(self, driver_id: int, message: Message):
        if message.location is None:
            return
        await self.driver_manager.update_location(driver_id, message)
        ride = await self.ride_manager.get_trip_by_user(driver_id)
        if ride:
            ride.trip.current_location_latitude = message.location.latitude
            ride.trip.current_location_longitude = message.location.longitude
            await ride.trip.update()
            user_bg_manager = await ride.request.user.create_bg_manager()
            await user_bg_manager.start(OrderStates.ride)

    async def _find_matches(self) -> List[DriverData]:
        matches = []
        for driver_id, driver in self.driver_manager.drivers.items():
            if not driver.active:
                continue
            for user_id, request in self.request_manager.requests.items():
                if user_id in self.matched_drivers.get(driver_id, set()):
                    continue
                print(driver.current_location, flush=True)
                print(request.start_location, flush=True)
                distance = geodesic(
                    (driver.current_location.latitude, driver.current_location.longitude),
                    (request.start_location.latitude, request.start_location.longitude)
                ).kilometers
                if distance <= 5:
                    matches.append(driver)
                    if driver_id not in self.matched_drivers:
                        self.matched_drivers[driver_id] = set()
                    self.matched_drivers[driver_id].add(user_id)

                    if user_id not in self.matched_users:
                        self.matched_users[user_id] = set()
                    self.matched_users[user_id].add(driver_id)
        return matches

    async def generate_pairs(self):
        async with self.lock:
            try:
                matches = await self._find_matches()
                print(matches, flush=True)
                for driver in matches:
                    bg_manager = await driver.user.create_bg_manager()
                    await bg_manager.start(state=DriverSearchSG.in_search)
            except Exception as e:
                print(e, flush=True)
                return

    async def clear(self, user_id, clear_ride=True, clear_request=True, clear_driver=True):
        self.matched_drivers.pop(user_id, None)
        self.matched_users.pop(user_id, None)
        self.driver_skipped.pop(user_id, None)
        if clear_ride:
            ride = self.ride_manager.users_map.pop(user_id, None)
            if ride:
                await self.ride_manager.remove_ride(ride.trip.id)
        if clear_request:
            await self.request_manager.remove_request(user_id)
        if clear_driver:
            await self.driver_manager.remove_driver(user_id)


# Example usage
async def main():
    tests_request_data = {'from': {'coords': [59.741587, 30.415093],
                                   'address': 'Санкт-Петербург, Пушкин, Детскосельский бульвар, 9'},
                          'to': {'coords': [59.736734339960186, 30.395180280273422],
                                 'address': 'Санкт-Петербург, Пушкин'}, 'user_id': 474081470}

    system = RideSystem()
    await system.add_driver(DriverData(101, Location(50.4501, 30.5234)))
    await system.add_ride_request(UserData(1, Location(50.4547, 30.5238), Location(50.4550, 30.5150), 150.0))
    matches = await system.find_matches()

    # Assign ride to matched pairs
    for driver_id, user_id in matches.items():
        ride = await system.assign_ride(user_id, driver_id)
        print(f"Ride assigned: {ride}")

    print("Matches found:", matches)

# asyncio.run(main())
