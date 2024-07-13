import asyncio
import re
from typing import Dict

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.common import WhenCondition
from aiogram_dialog.widgets.text import Format
from aiogram_dialog.widgets.text.format import _FormatDataStub
from service.translator.base import TranslationService


class SafeFormatter(str):
    def translate_and_format(self, mapping, lang: str):
        # Ищем слаги в тексте
        slugs = re.findall(r'@(\w+)@', self)
        translated_text = self
        print(mapping)
        # Переводим каждый слаг
        for slug in slugs:
            translated = TranslationService.translate(slug, lang)
            translated_text = translated_text.replace(f'@{slug}@', translated)

        # Форматируем текст с использованием SafeDict
        formated = translated_text.format_map(mapping)
        return self.escape_markdown(formated)

    @staticmethod
    def escape_markdown(text):
        # Экранируем все специальные символы
        escape_chars = r'\_*[]()~`>#+-=|{}.!'
        text = re.sub(f"([{re.escape(escape_chars)}])", r"\\\1", text)

        # Восстанавливаем корректные маркеры
        # Bold и italic маркеры
        text = re.sub(r'\\\*\\\*(.*?)\\\*\\\*', r'**\1**', text)
        text = re.sub(r'\\\*(.*?)\\\*', r'*\1*', text)

        # Подчеркнутый текст
        text = re.sub(r'\\\_\\\_(.*?)\\\_\\\_', r'__\1__', text)
        text = re.sub(r'\\\_(.*?)\\\_', r'_\1_', text)

        # Страйк
        text = re.sub(r'\\\~\\\~(.*?)\\\~\\\~', r'~~\1~~', text)

        # Inline code
        text = re.sub(r'\\\`(.*?)\\\`', r'`\1`', text)

        # Ссылки
        text = re.sub(r'\\\[(.*?)\\\]\\\((.*?)\\\)', r'[\1](\2)', text)

        return text


class TranslationFormat(Format):
    """
    Виджет форматирования текста, который поддерживает как стандартное форматирование, так и перевод слагов.

    Этот виджет расширяет функциональность класса `Format`, интегрируя сервис перевода. Он позволяет
    динамически переводить слаги внутри текста в зависимости от кода языка пользователя, а затем
    выполняет стандартное форматирование строки с использованием предоставленных данных.
    слаги указываются в формате `@slag@`.
    Атрибуты:
        text (str): Шаблон текста, который будет отформатирован и переведен.
        when (WhenCondition, optional): Условие, определяющее, когда этот виджет должен отображаться.
    """

    def __init__(self, text: str, when: WhenCondition = None):
        super().__init__(when=when, text=text)
        self.text = SafeFormatter(text)

    async def _render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        if manager.is_preview():
            return self.text.format_map(_FormatDataStub(data=data))
        lang = manager.middleware_data["event_from_user"].language_code
        return self.text.translate_and_format(_FormatDataStub(data=data), lang)

    async def render_text(
            self, data: Dict, manager: DialogManager,
    ) -> str:
        return await self._render_text(data, manager)

# async def example_usage():
#    data = {'key': 'Виктор'}
#    manager = DialogManager  # Предположим, что у вас есть экземпляр DialogManager
#    translation_format = TranslationFormat("Hello, {key} {2name} and @slug@")
#
#    rendered_text = await translation_format._render_text(data, manager)
#    print(rendered_text)
#
## Запуск примера
# asyncio.run(example_usage())
