from django import forms
from django.contrib import admin
from django.contrib.admin.widgets import FilteredSelectMultiple
from django.db.models import ManyToManyField, ImageField
from django.utils.safestring import mark_safe

from settings import settings
from . import models, utils


class ManyToManyForm(FilteredSelectMultiple):
    def __init__(self) -> None:
        super().__init__(' ', False)


class DragAndDropFileInput(forms.ClearableFileInput):
    template_name = 'admin/drag_and_drop_file_input.html'

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['BASE_URL'] = settings.FORCE_SCRIPT_NAME
        return context


class BaseFullModelAdmin(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        super().__init__(model, admin_site)
        self.list_display = [field.name for field in model._meta.fields if field.name != 'id']
        self.list_filter = [field.name for field in model._meta.fields if
                            field.name != 'id' and field.get_internal_type() in ['CharField', 'BooleanField']]
        self.search_fields = [field.name for field in model._meta.fields if
                              field.get_internal_type() in ['CharField', 'TextField']]

    formfield_overrides = {
        ImageField: {'widget': DragAndDropFileInput},
        ManyToManyField: {'widget': ManyToManyForm},
    }


class PaymentsAdmin(BaseFullModelAdmin):
    def has_add_permission(self, request):
        return False  # Отключаем возможность добавления записей

    def has_change_permission(self, request, obj=None):
        return False  # Отключаем возможность изменения записей

    def has_delete_permission(self, request, obj=None):
        return False  # Отключаем возможность


class TranslationForm(forms.ModelForm):
    class Meta:
        model = models.Translation
        fields = ['key', 'title', 'description']


class TranslationsInline(admin.TabularInline):
    model = models.Translation
    form = TranslationForm
    can_delete = False

    def get_queryset(self, request):
        # Проверяем, есть ли текущий объект
        if hasattr(self, 'parent_instance') and self.parent_instance:
            qs = super().get_queryset(request).filter(language=self.parent_instance)
        else:
            qs = super().get_queryset(request).none()
        return qs

    def get_formset(self, request, obj=None, **kwargs):
        self.parent_instance = obj
        formset = super().get_formset(request, obj, **kwargs)
        translations_from_yaml = utils.load_translations_from_yaml()
        existing_keys = set(self.get_queryset(request).values_list('key', flat=True))

        additional_translations = [
            {'key': key, 'title': '', 'description': data.get('description', '')}
            for key, data in translations_from_yaml.items() if key not in existing_keys
        ]

        # Обернем оригинальный formset, чтобы добавить недостающие переводы
        class WrappedFormSet(formset):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self.initial_forms_count = len(self.initial_forms)
                for i, form in enumerate(self.extra_forms):
                    if i < len(additional_translations):
                        print(additional_translations[i], flush=True)
                        form.initial.update(additional_translations[i])
                    else:
                        break

        return WrappedFormSet

    def get_extra(self, request, obj=None, **kwargs):
        translations_from_yaml = utils.load_translations_from_yaml()
        existing_keys = set(self.get_queryset(request).values_list('key', flat=True))
        additional_translations = [
            {'key': key, 'title': '', 'description': data.get('description', '')}
            for key, data in translations_from_yaml.items() if key not in existing_keys
        ]
        print(additional_translations, flush=True)
        print(len(additional_translations), flush=True)
        return len(additional_translations)


    def has_delete_permission(self, request, obj=None):
        return False  # Запрещаем удаление существующих инлайнов

class ReviewsInline(admin.TabularInline):
    model = models.Reviews
    extra = 0

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.order_by('-created_at')


class DriversAdmin(admin.ModelAdmin):
    inlines = [ReviewsInline]


class LocalizationsAdmin(admin.ModelAdmin):
    inlines = [TranslationsInline]
    list_display = ('code', 'name')


class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'passenger', 'driver', 'start_time', 'end_time', 'price')

    readonly_fields = ('map_widget',)

    def map_widget(self, obj):
        return mark_safe(f'''
            <div id="map" style="width: 100%; height: 400px; border-radius: 2em; overflow: hidden"></div>
            <input type="hidden" id="id_start_location_latitude" value="{obj.start_location_latitude}">
            <input type="hidden" id="id_start_location_longitude" value="{obj.start_location_longitude}">
            <input type="hidden" id="id_end_location_latitude" value="{obj.end_location_latitude}">
            <input type="hidden" id="id_end_location_longitude" value="{obj.end_location_longitude}">
            <input type="hidden" id="id_current_location_latitude" value="{obj.current_location_latitude}">
            <input type="hidden" id="id_current_location_longitude" value="{obj.current_location_longitude}">
            <script src="https://api-maps.yandex.ru/2.1/?lang=ru_RU&apikey=ac5e7c55-acc8-415a-9ab7-906a46cf1a26"></script>
            <script src='{settings.FORCE_SCRIPT_NAME}/{settings.STATIC_URL}admin/js/trip_map.js'></script>
        ''')

    map_widget.short_description = "Маршрут"


admin.site.register(models.Profile, BaseFullModelAdmin)
admin.site.register(models.Driver, DriversAdmin)
admin.site.register(models.Reviews, BaseFullModelAdmin)
admin.site.register(models.Language, LocalizationsAdmin)
admin.site.register(models.Trip, TripAdmin)
