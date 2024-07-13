import datetime

from aiogram import types
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager, ShowMode, StartMode
from aiogram_dialog.api.entities import MediaAttachment

from service.managers.meet_manager import RideSystem
from service.managers.user_data_manager import UserData
from service.translator.common.translate_dataclasses import TranslationBase
from states.states import OrderStates, DriverSearchSG, MainSG
import bootstrap

bot = bootstrap.MyBot().getInstance()

async def current_request_getter(dialog_manager: DialogManager, **kwargs):

    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return {}
    request = ride.request
    map_photo = MediaAttachment(type=ContentType.PHOTO, url=request.map_url)
    status_dict = ride.calculate_status_dict()
    return {'request': request, 'map_photo': map_photo, **status_dict}


async def matched_request_getter(dialog_manager: DialogManager, **kwargs):
    user = UserData(dialog_manager)
    requests = RideSystem().matched_drivers.get(user.user_id, set())
    requests = list(requests)
    request_user_id = None
    if not requests:
        return {'empty': True}
    for request in requests:
        potential_request_user_id = request
        print(RideSystem().driver_skipped.get(user.user_id), flush=True)
        if potential_request_user_id in RideSystem().driver_skipped.get(user.user_id, set()):
            continue
        else:
            request_user_id = potential_request_user_id
            break
    if not request_user_id:
        return {'empty': True}
    request = RideSystem().request_manager.requests.get(request_user_id)
    map_photo = MediaAttachment(type=ContentType.PHOTO, url=request.map_url)
    dialog_manager.current_context().dialog_data['current_request_user_id'] = request_user_id
    return {'request': request, 'map_photo': map_photo, 'empty': False}


async def skip_request(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    request_user_id = dialog_manager.current_context().dialog_data.get('current_request_user_id')
    if not RideSystem().driver_skipped.get(user.user_id):
        RideSystem().driver_skipped[user.user_id] = set()
    RideSystem().driver_skipped[user.user_id].add(request_user_id)
    dialog_manager.show_mode = ShowMode.EDIT


async def accept_request(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    request_user_id = dialog_manager.current_context().dialog_data.get('current_request_user_id')
    await RideSystem().assign_ride(request_user_id, user.user_id)


async def input_location(message: types.Message, _, dialog_manager: DialogManager):
    if message.location.live_period != 0x7FFFFFFF:
        return
    user = await UserData(dialog_manager).get_data()
    await RideSystem().add_driver(user_data=user, location_message=message)
    await dialog_manager.next()


async def send_on_point(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return
    ride.trip.status = 'WAIT_PASSENGER'
    await ride.trip.update()
    user_bg_manager = await ride.request.user.create_bg_manager()
    await user_bg_manager.start(state=OrderStates.ride)


async def start_ride(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return
    ride.trip.status = ride.trip.Status.RIDE
    await ride.trip.update()
    user_bg_manager = await ride.request.user.create_bg_manager()
    await user_bg_manager.start(state=OrderStates.ride)


async def end_ride(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return
    ride.trip.status = ride.trip.Status.COMPLETED
    ride.trip.end_time = datetime.datetime.now().date().isoformat()
    await ride.trip.update()
    await RideSystem().clear(user_id=user.user_id, clear_driver=False)
    await RideSystem().clear(user_id=ride.request.user.user_id)
    user_bg_manager = await ride.request.user.create_bg_manager()
    await user_bg_manager.start(state=OrderStates.complete, data={'trip_id': ride.trip.id, 'driver_id': user.user_id})
    await dialog_manager.next()


async def cancel_ride(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    ride = RideSystem().ride_manager.users_map.get(user.user_id)
    if not ride:
        return
    ride.trip.status = 'CANCEL'
    await ride.trip.update()
    user_bg_manager = await ride.request.user.create_bg_manager()
    await RideSystem().clear(user_id=user.user_id, clear_driver=False)
    await RideSystem().clear(user_id=ride.request.user.user_id, clear_request=False)
    text = await user.get_translations(TranslationBase.TripCancelled.slag(mode='CLEAR'))
    await callback.message.answer(text)
    text = await ride.request.user.get_translations(TranslationBase.TripCancelled.slag(mode='CLEAR'))
    ride.driver.active = True
    await bot.send_message(ride.request.user.user_id, text)
    await user_bg_manager.start(state=OrderStates.in_search, mode=StartMode.RESET_STACK)
    await dialog_manager.start(state=DriverSearchSG.in_search, mode=StartMode.RESET_STACK)


async def cancel_search(callback: types.CallbackQuery, _, dialog_manager: DialogManager):
    user = UserData(dialog_manager)
    await RideSystem().clear(user_id=user.user_id)
    await dialog_manager.start(state=MainSG.show, mode=StartMode.RESET_STACK)
