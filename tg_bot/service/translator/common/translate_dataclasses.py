import typing
from dataclasses import dataclass, field, fields
from typing import Literal, Dict

from service.translator.common import types

FORMATING_MODE = Literal['CLEAR', 'FORMATTING']


class PathProxy:
    def __init__(self, path='', mode: FORMATING_MODE = 'CLEAR'):
        self._path = path
        self.mode = mode

    def __getattr__(self, item):
        new_path = f"{self._path}.{item}" if self._path else item
        return PathProxy(new_path, self.mode)

    def __str__(self, mode: FORMATING_MODE = None):
        match mode or self.mode:
            case 'CLEAR':
                return f"{self._path}"
            case 'FORMATTING':
                return f'@{self._path}@'

    def __repr__(self):
        return self.__str__()

    def slag(self, mode: FORMATING_MODE):
        return self.__str__(mode)

class TranslationMeta(type):
    proxy = PathProxy()

    def __call__(cls, *args, **kwargs):
        obj = super().__call__(*args, **kwargs)
        for f in fields(obj):
            if getattr(obj, f.name) is None:
                obj.__setattr__(f.name, f.name)
        return obj

    def __getattr__(cls, name):

        if name in cls.__annotations__.keys():
            return PathProxy(name, cls.proxy.mode)
        raise AttributeError(f"'{cls.__name__}' object has no attribute '{name}'")


@dataclass
class TranslationBase(metaclass=TranslationMeta):
    MainWindow_order_button: typing.Union[str, PathProxy]
    MainWindow_reg_driver_button: typing.Union[str, PathProxy]
    MainWindow_search_orders_button: typing.Union[str, PathProxy]
    MainWindow_profile_button: typing.Union[str, PathProxy]
    main_subscription_button: typing.Union[str, PathProxy]
    OrderWebAppButton: typing.Union[str, PathProxy]
    DriverProfile_photo: typing.Union[str, PathProxy]
    DriverProfile_fullname: typing.Union[str, PathProxy]
    DriverProfile_car_number: typing.Union[str, PathProxy]
    DriverProfile_input_value: typing.Union[str, PathProxy]
    DriverProfile_back: typing.Union[str, PathProxy]
    DriverReg_send_photo: typing.Union[str, PathProxy]
    DriverReg_enter_fullname: typing.Union[str, PathProxy]
    DriverReg_enter_car_number: typing.Union[str, PathProxy]
    DriverSearch_send_location: typing.Union[str, PathProxy]
    DriverSearch_searching_passenger: typing.Union[str, PathProxy]
    DriverSearch_take_order: typing.Union[str, PathProxy]
    DriverSearch_next_order: typing.Union[str, PathProxy]
    DriverSearch_cancel_search: typing.Union[str, PathProxy]
    DriverSearch_go_to_passenger: typing.Union[str, PathProxy]
    DriverSearch_start_ride: typing.Union[str, PathProxy]
    DriverSearch_end_ride: typing.Union[str, PathProxy]
    DriverSearch_arrived: typing.Union[str, PathProxy]
    DriverSearch_start_trip: typing.Union[str, PathProxy]
    DriverSearch_finish_trip: typing.Union[str, PathProxy]
    DriverSearch_cancel_trip: typing.Union[str, PathProxy]
    DriverSearch_trip_complete: typing.Union[str, PathProxy]
    DriverSearch_take_another_trip: typing.Union[str, PathProxy]
    DriverSearch_finish: typing.Union[str, PathProxy]
    DriverSearch_price: typing.Union[str, PathProxy]
    DriverSearch_distance: typing.Union[str, PathProxy]
    DriverSearch_route: typing.Union[str, PathProxy]
    MainGreeting: typing.Union[str, PathProxy]
    MainQuestion: typing.Union[str, PathProxy]
    OrderWebAppPrompt: typing.Union[str, PathProxy]
    OrderSearchingDriver: typing.Union[str, PathProxy]
    OrderIncreasePrice: typing.Union[str, PathProxy]
    OrderCancelSearch: typing.Union[str, PathProxy]
    OrderDriverEnRoute: typing.Union[str, PathProxy]
    OrderDriverArrived: typing.Union[str, PathProxy]
    OrderHaveANiceTrip: typing.Union[str, PathProxy]
    OrderDriver: typing.Union[str, PathProxy]
    OrderCarNumber: typing.Union[str, PathProxy]
    OrderCancelRide: typing.Union[str, PathProxy]
    OrderTripEnded: typing.Union[str, PathProxy]
    OrderSendReview: typing.Union[str, PathProxy]
    OrderSkipReview: typing.Union[str, PathProxy]
    OrderDistance: typing.Union[str, PathProxy]
    OrderPrice: typing.Union[str, PathProxy]
    PayChooseSubscription: typing.Union[str, PathProxy]
    PayInstructions: typing.Union[str, PathProxy]
    PayConfirmation: typing.Union[str, PathProxy]
    UserRegEnterPhone: typing.Union[str, PathProxy]
    UserRegShareContact: typing.Union[str, PathProxy]
    TripCancelled: typing.Union[str, PathProxy]

    NotificationAcceptDriver: typing.Union[str, PathProxy]
    SuccessRegisteredDriver: typing.Union[str, PathProxy]

    @classmethod
    def set_mode(cls, mode: FORMATING_MODE):
        cls.proxy.mode = mode
        return cls

    def __getattr__(self, name, mode: FORMATING_MODE = 'CLEAR'):
        if name not in self.__annotations__.keys():
            return str(PathProxy(name, mode))
        return super().__getattribute__(name)


@dataclass
class Translations:
    data: Dict[str, TranslationBase] = field(default_factory=dict)
