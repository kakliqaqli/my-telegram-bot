import logging
import os

import requests
from django.core.files.base import ContentFile
from rest_framework import serializers

from . import models



class TranslationSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Translation
        fields = ['key', 'title']
class LanguageSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Language
        fields = ['code', 'translations']

    translations = serializers.SerializerMethodField()

    def get_translations(self, obj):
        translations = models.Translation.objects.filter(language=obj)
        return {translation.key: translation.title for translation in translations}

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        return {representation['code']: representation['translations']}


class DriverSerializer(serializers.ModelSerializer):
    profile = serializers.PrimaryKeyRelatedField(queryset=models.Profile.objects.all())

    class Meta:
        model = models.Driver
        fields = ['profile', 'fullname', 'photo', 'car_number', 'accepted', 'premium', 'premium_expiration', 'rate']

    def to_internal_value(self, data):
        photo_url = data.get('photo')
        if isinstance(photo_url, str) and photo_url.startswith('http'):
            try:
                response = requests.get(photo_url)
                response.raise_for_status()
                file_name = photo_url.split('/')[-1]
                data['photo'] = ContentFile(response.content, name=file_name)
            except requests.RequestException as e:
                raise serializers.ValidationError({'photo': f'Error downloading image from {photo_url}: {str(e)}'})
        return super().to_internal_value(data)

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.photo:
            ret['photo'] = f'http://{os.environ.get("BACKEND_HOST")}:{os.environ.get("BACKEND_PORT")}{instance.photo.url}'
        return ret


class UserModelSerializer(serializers.ModelSerializer):
    driver = DriverSerializer(read_only=True)

    class Meta:
        model = models.Profile
        fields = ['id', 'username', 'phone_number', 'ban', 'registered', 'driver']

    def create(self, validated_data):
        return models.Profile.objects.create(**validated_data)

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            if value is not None:
                setattr(instance, attr, value)
        instance.save()
        return instance


class TripSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Trip
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Reviews
        fields = '__all__'

