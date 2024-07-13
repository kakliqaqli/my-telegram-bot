import os.path

from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Button, Row, WebApp, Start
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Const, Multi, Format

from app.dialogs.custom_widgets import DynamicLocation, StarRating
from app.dialogs.windows.order.methods import request_getter, increase_price, trip_getter, cancel_search, cancel_ride, \
    input_review, complete_getter, send_review
from service.translator.common.translate_dataclasses import TranslationBase
from service.translator.patching.aiogram_dialog.widgets import TranslationFormat
from states.states import OrderStates, MainSG
OrderWin = (
    Window(
        DynamicLocation(OrderStates.ride),
        TranslationFormat(TranslationBase.OrderWebAppPrompt.slag('FORMATTING')),
        WebApp(text=TranslationFormat(TranslationBase.OrderWebAppButton.slag('FORMATTING')),
               url=Const(os.environ.get("TELEGRAM_BOT_WEBAPP_URL")), id='webapp'),
        parse_mode="markdown",
        state=OrderStates.start_search,
    ),
    Window(
        DynamicLocation(OrderStates.ride),
        DynamicMedia("map_photo"),
        TranslationFormat(TranslationBase.OrderSearchingDriver.slag('FORMATTING')),
        Multi(
            TranslationFormat(TranslationBase.DriverSearch_distance.slag('FORMATTING')),
            Format(' {request.distance} км'),
            sep=""
        ),
        Multi(
            TranslationFormat(TranslationBase.DriverSearch_price.slag('FORMATTING')),
            Format(' {request.price} ₽'),
            sep=""
        ),
        Button(TranslationFormat(TranslationBase.OrderIncreasePrice.slag('FORMATTING')), on_click=increase_price, id='increase_price'),
        Button(TranslationFormat(TranslationBase.DriverSearch_cancel_search.slag('FORMATTING')), on_click=cancel_search, id='cancel_search'),
        getter=request_getter,
        parse_mode="markdown",
        state=OrderStates.in_search,
    ),
    Window(
        DynamicLocation(OrderStates.ride, driver_id=Format('{driver.user.user_id}')),
        DynamicMedia("driver_photo", when='driver_photo'),
        Multi(TranslationFormat(TranslationBase.OrderDriverEnRoute.slag('FORMATTING')), when='WAIT_DRIVER'),
        Multi(TranslationFormat(TranslationBase.OrderDriverArrived.slag('FORMATTING')), when='WAIT_PASSENGER'),
        Multi(TranslationFormat(TranslationBase.OrderHaveANiceTrip.slag('FORMATTING')), when='RIDE'),
        Multi(
            TranslationFormat(TranslationBase.OrderDriver.slag('FORMATTING')),
            Format(' {driver_data.fullname}'),
            sep=""
        ),
        Multi(
            TranslationFormat(TranslationBase.OrderCarNumber.slag('FORMATTING')),
            Format(' {driver_data.car_number}'),
            sep=""
        ),
        Button(TranslationFormat(TranslationBase.DriverSearch_cancel_trip.slag('FORMATTING')), on_click=cancel_ride, id='cancel_search'),
        getter=trip_getter,
        parse_mode="markdown",
        state=OrderStates.ride,
    ),
    Window(
        DynamicLocation(OrderStates.ride),
        TranslationFormat(TranslationBase.OrderTripEnded.slag('FORMATTING')),
        Format('*{review_text}*', when='review_text'),
        MessageInput(func=input_review, content_types=[ContentType.TEXT]),
        StarRating(),
        Start(TranslationFormat(TranslationBase.OrderSendReview.slag('FORMATTING')), on_click=send_review, state=MainSG.show, id='send_review', when='can_send'),
        Start(TranslationFormat(TranslationBase.OrderSkipReview.slag('FORMATTING')),state=MainSG.show, id='skip_review'),
        getter=complete_getter,
        parse_mode="markdown",
        state=OrderStates.complete,
    ),
)
