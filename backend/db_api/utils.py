import yaml
import os

def load_translations_from_yaml():
    with open('default_local_ru.yaml', 'r', encoding='utf-8') as file:
        translations = yaml.safe_load(file)
    return translations['translate']
