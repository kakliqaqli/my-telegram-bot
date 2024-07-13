import json
import os
from typing import Type, TypeVar, Generic, Optional, Dict, Any, Tuple, Protocol, runtime_checkable
import aiohttp
from pydantic import BaseModel

T = TypeVar('T', bound='APIClientModel')


@runtime_checkable
class Filterable(Protocol):
    @classmethod
    def filter(cls, **filters): ...

    @classmethod
    def order_by(cls, *ordering): ...


class APIClientModelMeta(type(BaseModel)):
    def __new__(cls, name, bases, dct):
        if bases:
            dct['filter'] = cls.create_filter_method()
            dct['order_by'] = cls.create_order_by_method()
        return super().__new__(cls, name, bases, dct)

    @staticmethod
    def create_filter_method():
        @classmethod
        def filter(cls, **filters):
            return QuerySet(cls).filter(**filters)

        return filter

    @staticmethod
    def create_order_by_method():
        @classmethod
        def order_by(cls, *ordering):
            return QuerySet(cls).order_by(*ordering)

        return order_by


class QuerySet(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.params = {}

    def filter(self, **filters):
        self.params['filter'] = filters
        return self

    def order_by(self, *ordering):
        self.params['order_by'] = list(ordering)
        return self

    async def fetch(self):
        return await self.model.perform_request('GET', params=self.params)


class APIClientModel(BaseModel, Generic[T], metaclass=APIClientModelMeta):

    class Config:
        arbitrary_types_allowed = True
        base_url = f'http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}/api'

    @classmethod
    async def perform_request(cls, method: str, raw=False, data: Optional[Dict] = None,
                              params: Optional[Dict] = None) -> Any:
        url = f'{cls.Config.base_url}/{cls.__name__.lower()}/'
        if params:
            url += '?__system_params__=' + json.dumps(params)

        async with aiohttp.ClientSession() as session:
            async with session.request(method, url, json=data) as response:
                if response.status == 404:
                    return None
                print(response, flush=True)
                response_data = await response.json()
                if raw:
                    return response_data
                print(response_data, flush=True)
                if isinstance(response_data, list):
                    return [cls.parse_obj(item) for item in response_data]
                print(response_data, flush=True)
                return cls.parse_obj(response_data)

    @classmethod
    async def get(cls: Type[T], raw=False, **query_params) -> Optional[T] | Dict:
        if query_params:
            result = await cls.filter(**query_params).fetch()
            return result[0] if result else result
        return await cls.perform_request('GET', raw, params=query_params)

    async def create(self: Type[T], **data) -> T:
        return await self.perform_request('POST', data=data or json.loads(self.model_dump_json()))

    async def update(self, particle=True, **data) -> None:
        method = 'PATCH' if particle else 'PUT'
        await self.perform_request(method, data=data or json.loads(self.model_dump_json()))
    @classmethod
    async def get_or_create(cls: Type[T], defaults: Optional[Dict[str, Any]] = None, **kwargs) -> Tuple[T, bool]:
        instance = await cls.get(**kwargs)
        if instance:
            return instance, False
        create_data = {**kwargs, **(defaults or {})}
        created_instance = await cls.model_construct().create(**create_data)
        return created_instance, True

    @classmethod
    def filter(cls: Type[T], **filters) -> QuerySet[T]:
        ...

    @classmethod
    def order_by(cls: Type[T], *ordering) -> QuerySet[T]:
        ...

    @classmethod
    def empty_instance(cls):
        values = [None or __.default for _, __ in cls.model_fields.items()]
        values = zip(cls.model_fields.keys(), values)
        return cls.model_construct(_fields_set=set(cls.model_fields.keys()), **dict(values))
