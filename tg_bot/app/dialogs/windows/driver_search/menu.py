import os.path

from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, SwitchTo
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Multi, Format

from app.dialogs.windows.driver_search.methods import matched_request_getter, input_location, skip_request, \
    accept_request, current_request_getter, send_on_point, start_ride, end_ride, cancel_search, cancel_ride
from service.translator.common.translate_dataclasses import TranslationBase
from service.translator.patching.aiogram_dialog.widgets import TranslationFormat
from states.states import DriverSearchSG
ride_request_template = (
    DynamicMedia("map_photo", when='map_photo'),
    Multi(
        TranslationFormat(TranslationBase.DriverSearch_price.slag(mode='FORMATTING')),
        Format(' {request.price} ₽'),
        sep="", when='request'
    ),
    Multi(
        TranslationFormat(TranslationBase.DriverSearch_distance.slag(mode='FORMATTING')),
        Format(' {request.distance} км'),
        sep="", when='request'
    ),
    Multi(
        TranslationFormat(TranslationBase.DriverSearch_route.slag(mode='FORMATTING')),
        Format(' {request.start_address} -> {request.end_address}'),
        sep="", when='request'
    ),
)

DriverSearchWin = (
    Window(
        TranslationFormat(TranslationBase.DriverSearch_send_location.slag(mode='FORMATTING')),
        MessageInput(func=input_location, content_types=[ContentType.LOCATION]),
        parse_mode="markdown",
        state=DriverSearchSG.input_location,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverSearch_searching_passenger.slag(mode='FORMATTING'), when='empty'),
        *ride_request_template,
        Row(Button(TranslationFormat(TranslationBase.DriverSearch_take_order.slag(mode='FORMATTING')), on_click=accept_request, id='take_order', when='request'),
            Button(TranslationFormat(TranslationBase.DriverSearch_next_order.slag(mode='FORMATTING')), on_click=skip_request, id='skip_order', when='request')),
        Button(TranslationFormat(TranslationBase.DriverSearch_cancel_search.slag(mode='FORMATTING')), on_click=cancel_search, id='cancel_search'),
        getter=matched_request_getter,
        parse_mode="markdown",
        state=DriverSearchSG.in_search,
    ),
    Window(
        Multi(TranslationFormat(TranslationBase.DriverSearch_go_to_passenger.slag(mode='FORMATTING')), when='WAIT_DRIVER'),
        Multi(TranslationFormat(TranslationBase.DriverSearch_start_ride.slag(mode='FORMATTING')), when='WAIT_PASSENGER'),
        Multi(TranslationFormat(TranslationBase.DriverSearch_end_ride.slag(mode='FORMATTING')), when='RIDE'),
        Const('\n----------\n'),
        *ride_request_template,
        Button(TranslationFormat(TranslationBase.DriverSearch_arrived.slag(mode='FORMATTING')), on_click=send_on_point, id='send_on_point', when='WAIT_DRIVER'),
        Button(TranslationFormat(TranslationBase.DriverSearch_start_trip.slag(mode='FORMATTING')), on_click=start_ride, id='start_ride', when='WAIT_PASSENGER'),
        Button(TranslationFormat(TranslationBase.DriverSearch_finish_trip.slag(mode='FORMATTING')), on_click=end_ride, id='end_ride', when='RIDE'),
        Button(TranslationFormat(TranslationBase.DriverSearch_cancel_trip.slag(mode='FORMATTING')), on_click=cancel_ride, id='cancel_ride'),
        getter=current_request_getter,
        parse_mode="markdown",
        state=DriverSearchSG.ride,
    ),
    Window(
        TranslationFormat(TranslationBase.DriverSearch_trip_complete.slag(mode='FORMATTING')),
        *ride_request_template,
        SwitchTo(TranslationFormat(TranslationBase.DriverSearch_take_another_trip.slag(mode='FORMATTING')), state=DriverSearchSG.in_search, id='take_order'),
        Button(TranslationFormat(TranslationBase.DriverSearch_finish.slag(mode='FORMATTING')), on_click=cancel_search, id='take_order'),
        getter=current_request_getter,
        parse_mode="markdown",
        state=DriverSearchSG.complete,
    ),
)
