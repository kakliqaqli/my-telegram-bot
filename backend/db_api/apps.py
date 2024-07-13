from django.apps import AppConfig



class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'db_api'
    verbose_name = 'Бот'

    def ready(self) -> None:
        from . import signals
        signals.app_ready()
