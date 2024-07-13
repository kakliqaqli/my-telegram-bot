from typing import Optional, Dict, List

from .common import types
from .common.translate_dataclasses import Translations, TranslationBase


class TranslationService:
    translations: Optional[Translations] = Translations(data={})
    base: TranslationBase = TranslationBase
    @classmethod
    def load_translations(self, translations: List[Dict[str, dict]]):
        for translation in translations:
            for key, value in translation.items():
                translate = TranslationBase(**value)
                self.translations.data[key] = translate

    @classmethod
    def translate(cls, slag: str, lang: str = 'ru') -> str:
        if not cls.translations:
            return slag
        print(lang, flush=True)
        translation = cls.translations.data.get(lang, cls.translations.data.get('ru'))
        if not translation:
            translation = TranslationBase()
        translate = translation.__getattr__(slag)
        if not isinstance(translation, str):
            return translate.__str__()
        else:
            return translate



