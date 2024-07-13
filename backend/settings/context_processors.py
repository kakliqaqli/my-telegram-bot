from settings import settings


def custom_settings(request):
    return {
        'FORCE_SCRIPT_NAME': settings.FORCE_SCRIPT_NAME,
    }