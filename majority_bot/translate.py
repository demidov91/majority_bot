import os
import gettext as native_gettext
from contextvars import ContextVar
from json import JSONEncoder
from typing import Optional

from speaklater import make_lazy_gettext, _LazyString

BASE_DIR = os.path.dirname(__file__)
DEFAULT_LANGUAGE = 'be'
AVAILABLE_LANGUAGES = ['ru', 'be']

_active_language = ContextVar('active_language', default=DEFAULT_LANGUAGE)
_translations = {}


def set_active(language: Optional[str]):
    if language is None or language not in AVAILABLE_LANGUAGES:
        return

    _active_language.set(language)


def get_active():
    return _active_language.get()


def get_translation(language_code: str):
    if language_code not in _translations:
        _translations[language_code] = native_gettext.translation(
            'messages', localedir=os.path.join(BASE_DIR, 'locale'), languages=[language_code]
        )

    return _translations[language_code]


def gettext(text):
    return get_translation(get_active()).gettext(text)


gettext_lazy = make_lazy_gettext(lambda: gettext)


class LazyAwareJsonEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, _LazyString):
            return str(o)

        return super().encode(o)