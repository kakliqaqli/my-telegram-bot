import asyncio
import os
from abc import ABC, abstractmethod, ABCMeta
from typing import TypeVar, Type, Generic

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler

T = TypeVar('T', bound='SingletonBase')


class SingletonMeta(ABCMeta):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(SingletonMeta, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class SingletonBase(ABC, Generic[T], metaclass=SingletonMeta):
    _instance: T = None

    @classmethod
    def getInstance(cls: Type[T]) -> T:
        if cls._instance is None:
            cls._instance = cls._create_instance()
        return cls._instance

    @classmethod
    @abstractmethod
    def _create_instance(cls) -> T:
        pass


class MyBot(SingletonBase[Bot]):
    @classmethod
    def _create_instance(cls) -> Bot:
        return Bot(token=os.environ.get('TELEGRAM_BOT_TOKEN'), parse_mode="markdown")


class Scheduler(SingletonBase[AsyncIOScheduler]):
    @classmethod
    def _create_instance(cls) -> AsyncIOScheduler:
        return AsyncIOScheduler()


class MyDispatcher(SingletonBase[Dispatcher]):
    @classmethod
    def _create_instance(cls) -> Dispatcher:
        return Dispatcher(storage=MemoryStorage())
