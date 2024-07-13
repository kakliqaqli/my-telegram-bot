import uuid

from django.core.exceptions import ValidationError
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from markdownfield.models import MarkdownField
from markdownfield.validators import VALIDATOR_STANDARD


class BaseModel(models.Model):
    created_at = models.DateTimeField(verbose_name='Создан в', auto_now_add=True)
    updated_at = models.DateTimeField(verbose_name='Обновлен в', auto_now=True)

    class Meta:
        abstract = True


class Language(BaseModel):
    code = models.CharField(max_length=4, verbose_name='Код языка', primary_key=True)
    name = models.CharField(max_length=100, verbose_name='Название языка')

    class Meta:
        verbose_name = 'Язык'
        verbose_name_plural = 'Языки'

    def __str__(self):
        return self.name


class Translation(models.Model):
    language = models.ForeignKey(Language, on_delete=models.CASCADE)
    key = models.CharField(max_length=255, null=True)
    title = models.TextField(max_length=255, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        unique_together = ('language', 'key')

    def __str__(self):
        return f"{self.key} ({self.language.code})"


class Localizations(BaseModel):
    lang = models.ForeignKey(Language, verbose_name='Язык', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Локализация'
        verbose_name_plural = 'Локализации'
        unique_together = ('lang',)

    def __str__(self):
        return self.lang.code


class Profile(BaseModel):
    id = models.BigIntegerField(primary_key=True)
    username = models.CharField(max_length=255, verbose_name='Юзернейм', blank=True, null=True)
    phone_number = models.CharField(max_length=255, verbose_name='Номер телефона', blank=True, null=True)
    ban = models.BooleanField(verbose_name='Забанен?', default=False)
    registered = models.BooleanField(default=False, verbose_name='Зарегистрирован?')
    lang = models.ForeignKey(Language, verbose_name='Язык', to_field='code', on_delete=models.SET_NULL, blank=True,
                             null=True)

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return f'Пользователь {"@" + (self.username or str(self.id))}'


class Driver(BaseModel):
    profile = models.OneToOneField(Profile, on_delete=models.CASCADE, primary_key=True)
    photo = models.ImageField(verbose_name='Фото', blank=True, null=True)
    car_number = models.CharField(verbose_name='Номер машины', max_length=255, blank=True, null=True)
    fullname = models.CharField(verbose_name='ФИО', max_length=255, blank=True, null=True)
    accepted = models.BooleanField(verbose_name='Принят?', default=False)
    premium = models.BooleanField(verbose_name='Премиум?', default=False)
    premium_expiration = models.DateField(verbose_name='Дата окончания премиума', blank=True, null=True)
    rate = models.FloatField(verbose_name='Рейтинг', default=0.0,
                             validators=[MinValueValidator(0.0), MaxValueValidator(5.0)])

    class Meta:
        verbose_name = 'Водитель'
        verbose_name_plural = 'Водители'
        unique_together = ('profile',)

    def __str__(self):
        return self.profile.__str__()


class Trip(BaseModel):
    class StatusChoices(models.TextChoices):
        WAIT_DRIVER = 'WAIT_DRIVER', 'Ожидает водителя'
        WAIT_PASSENGER = 'WAIT_PASSENGER', 'Ожидает пассажира'
        CANCEL = 'CANCEL', 'Отменен'
        RIDE = 'RIDE', 'Идет поездка'
        COMPLETED = 'COMPLETED', 'Поездка завершена'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    passenger = models.ForeignKey(Profile, verbose_name='Пассажир', on_delete=models.CASCADE, blank=True, null=True)
    driver = models.ForeignKey(Driver, verbose_name='Водитель', on_delete=models.CASCADE, blank=True, null=True)
    start_location_latitude = models.FloatField(verbose_name='Начальная точка широта')
    start_location_longitude = models.FloatField(verbose_name='Начальная точка долгота')
    end_location_latitude = models.FloatField(verbose_name='Конечная точка широта')
    end_location_longitude = models.FloatField(verbose_name='Конечная точка долгота')
    current_location_latitude = models.FloatField(verbose_name='Текущая точка поездки широта')
    current_location_longitude = models.FloatField(verbose_name='Текущая точка поездки долгота')
    start_time = models.DateTimeField(verbose_name='Время начала', blank=True, null=True)
    end_time = models.DateTimeField(verbose_name='Время окончания', blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена', blank=True, null=True)
    status = models.CharField(verbose_name='Статус', max_length=32, choices=StatusChoices.choices,
                              default=StatusChoices.WAIT_DRIVER)

    class Meta:
        verbose_name = 'Поездка'
        verbose_name_plural = 'Поездки'

    def __str__(self):
        return f'Поездка {self.id} - {self.passenger} - №{self.id}'


class Reviews(BaseModel):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    driver = models.ForeignKey(Driver, verbose_name='Водитель', on_delete=models.CASCADE)
    trip = models.ForeignKey(Trip, verbose_name='Поездка', on_delete=models.CASCADE)
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.FloatField(verbose_name='Рейтинг', validators=[MinValueValidator(0), MaxValueValidator(5)])

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        unique_together = ('driver', 'trip')

    def __str__(self):
        return f'Отзыв {self.id} - {self.trip}'

    def save(
            self, force_insert=False, force_update=False, using=None, update_fields=None
    ):
        self.trip.driver.rate = (self.trip.driver.rate or 5 + self.rating) / 2
        self.trip.driver.save()
        super().save()
