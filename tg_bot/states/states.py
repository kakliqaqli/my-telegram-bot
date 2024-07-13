from aiogram.fsm.state import StatesGroup, State


class MainSG(StatesGroup):
    show = State()


class UserRegSG(StatesGroup):
    input_phone = State()


class DriverRegSG(StatesGroup):
    input_photo = State()
    input_car_number = State()
    input_fullname = State()


class DriverProfileSG(StatesGroup):
    show = State()
    input_photo = State()
    input_car_number = State()
    input_fullname = State()


class DriverSearchSG(StatesGroup):
    input_location = State()
    in_search = State()
    ride = State()
    complete = State()


# ? --------------------------
class CanceledOrder(StatesGroup):
    input_reason = State()


class InputReview(StatesGroup):
    input = State()


class OrderStates(StatesGroup):
    start_search = State()
    in_search = State()
    ride = State()
    complete = State()


class PayStates(StatesGroup):
    choose = State()
    pay = State()


class DriverStates(StatesGroup):
    search = State()
    ride = State()
