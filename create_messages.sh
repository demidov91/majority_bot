pybabel extract majority_bot -o _tmp_messages.po -k gettext -k gettext_lazy

msgmerge majority_bot/locale/ru/LC_MESSAGES/messages.po _tmp_messages.po -o majority_bot/locale/ru/LC_MESSAGES/messages.po --lang=ru
msgmerge majority_bot/locale/be/LC_MESSAGES/messages.po _tmp_messages.po -o majority_bot/locale/be/LC_MESSAGES/messages.po --lang=be

rm _tmp_messages.po

