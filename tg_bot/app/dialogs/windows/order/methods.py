from aiogram import types
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.entities import MediaAttachment

import bootstrap
from service.http2orm.models import Review
from service.managers.meet_manager import RideSystem
from service.managers.user_data_manager import UserData
from service.translator.common.translate_dataclasses import TranslationBase
from states.states import DriverSearchSG, OrderStates, MainSG

bot = bootstrap.MyBot().getInstance()


async def request_getter(dialog_manager: DialogManager, **kwargs):
    user = await UserData(dialog_manager).get_data()

    request = RideSystem().request_manager.requests.get(user.user_id)
    map_photo = MediaAttachment(type=ContentType.PHOTO, url=request.map_url)
    return {'request': request, 'map_photo': map_photo}


async def complete_getter(dialog_manager: DialogManager, **kwargs):
    start_data = dialog_manager.current_context().start_data
    if start_data:
        dialog_manager.current_context().dialog_data.update(**start_data)
    data = dialog_manager.current_context().dialog_data
    return {**data, 'can_send': all((data.get('review_text'), data.get('review_rating')))}


async def trip_getter(dialog_manager: DialogManager, **kwargs):
    user = UserData(dialog_manager)
    ride = await RideSystem().ride_manager.get_trip_by_user(user.user_id)
    driver_photo_url = ride.driver.user.data.driver.photo
    print(driver_photo_url, flush=True)
    if driver_photo_url:
        driver_photo = MediaAttachment(type=ContentType.PHOTO, url=driver_photo_url, use_pipe=True)
    else:
        driver_photo = None
    status_dict = ride.calculate_status_dict()
    return {'driver': ride.driver,
            'driver_photo': driver_photo,
            'driver_data': ride.driver.user.data.driver,
            **status_dict}


async def input_review(message: types.Message, _, dialog_manager: DialogManager):
    dialog_manager.current_context().dialog_data.update({'review_text': message.text})


async def send_review(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    data = dialog_manager.current_context().dialog_data
    await Review(trip=data.get('trip_id'),
                 driver=data.get('driver_id'),
                 text=data.get('review_text'),
                 rating=float(data.get('review_rating'))).create()


async def increase_price(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    request = RideSystem().request_manager.requests.get(user.user_id)
    request.price += 100
    dialog_manager.show_mode = ShowMode.EDIT


async def cancel_ride(callback: types.CallbackQuery, _, dialog_manager: DialogManager):

    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return
    ride.trip.status = 'CANCEL'
    await ride.trip.update()
    user_bg_manager = await ride.driver.user.create_bg_manager()
    await RideSystem().clear(user_id=user.user_id, clear_request=False)
    await RideSystem().clear(user_id=ride.driver.user.user_id, clear_driver=False)
    text = await user.get_translations(TranslationBase.TripCancelled.slag('CLEAR'))
    await callback.message.answer(text)
    text = await ride.driver.user.get_translations(TranslationBase.TripCancelled.slag('CLEAR'))
    ride.driver.active = True
    await bot.send_message(ride.driver.user.user_id, text)
    await user_bg_manager.start(state=DriverSearchSG.in_search, mode=StartMode.RESET_STACK)
    await dialog_manager.start(state=OrderStates.in_search, mode=StartMode.RESET_STACK)


async def cancel_search(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    await RideSystem().clear(user_id=user.user_id)
    await dialog_manager.start(state=MainSG.show, mode=StartMode.RESET_STACK)
