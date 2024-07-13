import hashlib
import msgpack
from functools import wraps
from django.core.cache import cache
from django.db.models.signals import post_save, post_delete
from django_redis import get_redis_connection


class CacheProxy:
    """
    Класс CacheProxy предоставляет декоратор для кэширования результатов функций,
    с возможностью инвалидации кэша при изменении зависимых моделей Django и тегов.
    Это обеспечивает улучшенное управление кэшем с использованием динамического TTL,
    тегирования и сигналов моделей.

    Attributes:
        atter_connection (str): Атрибут, используемый для отметки моделей, к которым уже подключены сигналы.
    """

    atter_connection = '_memoize_signals_connected'

    @classmethod
    def memoize(cls, timeout=300, args_sensitivity=False, depend_models=None, use_dynamic_ttl=False, tags=None):
        """
        Декоратор для кэширования результатов функций с опциональным автоматическим управлением TTL,
        зависимостями от моделей и тегированием кэшированных данных.

        Args:
            timeout (int): Основное время жизни кэша в секундах.
            args_sensitivity (bool): Если True, ключ кэша будет зависеть от аргументов функции.
            depend_models (list): Список моделей Django, изменения в которых должны инвалидировать кэш.
            use_dynamic_ttl (bool): Если True, TTL будет автоматически адаптироваться на основе частоты обращений к данным.
            tags (list): Список тегов, которые будут присвоены кэшированным данным для групповой инвалидации.
        """
        dynamic_ttl_func = cls.dynamic_ttl(timeout, 3600, 100) if use_dynamic_ttl else lambda x: timeout

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                key_suffix = cls.args_to_hash(*args, **kwargs) if args_sensitivity else ""
                key = f"{func.__name__}-{key_suffix}"
                cached_data = cache.get(key)
                if cached_data is None:
                    result = func(*args, **kwargs)
                    ttl = dynamic_ttl_func(key)
                    cache.set(key, result, ttl)
                    cls.store_keys_in_redis(key, depend_models, ttl)
                    if tags:
                        cls.tag_cache(key, tags, ttl)
                    return result
                return cached_data

            return wrapper

        return decorator

    @classmethod
    def store_keys_in_redis(cls, key, depend_models, timeout):
        """
        Сохраняет ключи кэша в Redis и устанавливает их TTL атомарно с использованием Lua скриптов.

        Args:
            key (str): Ключ кэша.
            depend_models (list): Список моделей, от изменений которых зависит данный ключ.
            timeout (int): Время жизни ключа.
        """
        redis_conn = get_redis_connection("default")
        lua_script = """
        local model_key = KEYS[1]
        local key = ARGV[1]
        local timeout = tonumber(ARGV[2])
        redis.call('SADD', model_key, key)
        redis.call('EXPIRE', model_key, timeout)
        """
        if depend_models:
            for model in depend_models:
                model_key = f"cache_keys:{model._meta.label_lower}"
                redis_conn.eval(lua_script, 1, model_key, key, timeout)
                if not getattr(model, cls.atter_connection, False):
                    cls._connect_signals(model)
                    setattr(model, cls.atter_connection, True)

    @classmethod
    def dynamic_ttl(cls, initial_ttl=300, max_ttl=3600, increment=100):
        """
        Возвращает функцию для динамического вычисления TTL на основе частоты обращений к кэшу.

        Args:
            initial_ttl (int): Начальное значение TTL.
            max_ttl (int): Максимальное значение TTL.
            increment (int): Шаг увеличения TTL.

        Returns:
            function: Функция для вычисления TTL.
        """

        def calculate_ttl(key):
            access_count = cache.get(f"{key}_count", 0) + 1
            cache.set(f"{key}_count", access_count)
            new_ttl = min(initial_ttl + increment * access_count, max_ttl)
            return new_ttl

        return calculate_ttl

    @classmethod
    def tag_cache(cls, key, tags, timeout):
        """
        Связывает ключи кэша с тегами и устанавливает их TTL через Lua скрипт для возможности групповой инвалидации.

        Args:
            key (str): Ключ кэша.
            tags (list): Теги, ассоциированные с данным ключом.
            timeout (int): Время жизни ключа.
        """
        redis_conn = get_redis_connection("default")
        lua_script = """
        local tag_key = KEYS[1]
        local key = ARGV[1]
        local timeout = tonumber(ARGV[2])
        redis.call('SADD', tag_key, key)
        redis.call('EXPIRE', tag_key, timeout)
        """
        for tag in tags:
            tag_key = f"tag:{tag}"
            redis_conn.eval(lua_script, 1, tag_key, key, timeout)

    @classmethod
    def clear_cache(cls, sender, **kwargs):
        """
        Очищает кэш при изменении или удалении записей модели, используя сигналы Django.

        Args:
            sender (class): Класс модели, в которой произошли изменения.
        """
        model_key = f"cache_keys:{sender._meta.label_lower}"
        redis_conn = get_redis_connection("default")
        keys_to_clear = redis_conn.smembers(model_key)
        for key in keys_to_clear:
            cache.delete(key.decode('utf-8'))
        redis_conn.delete(model_key)

    @classmethod
    def _connect_signals(cls, model):
        """
        Подключает сигналы модели для автоматической очистки кэша при изменениях в модели.

        Args:
            model (class): Класс модели Django.
        """
        post_save.connect(cls.clear_cache, sender=model, weak=False)
        post_delete.connect(cls.clear_cache, sender=model, weak=False)

    @staticmethod
    def args_to_hash(*args, **kwargs):
        """
        Генерирует хеш из аргументов функции для создания уникального ключа кэша.

        Args:
            args (tuple): Аргументы функции.
            kwargs (dict): Именованные аргументы функции.

        Returns:
            str: Хеш аргументов функции.
        """
        args_data = msgpack.packb((args, sorted(kwargs.items())), use_bin_type=True)
        return hashlib.md5(args_data).hexdigest()
