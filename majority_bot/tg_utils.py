from telegram import Message


def build_message(text, options):
    data = {
        'method': 'sendMessage',
        'text': text,
    }
    if options:
        if len(options) < 3:
            keyboard = [[{'text': x} for x in options]]

        else:
            keyboard = [[{'text': x}] for x in options]

        data['reply_markup'] = {
            'keyboard': keyboard,
            'resize_keyboard': True,
            'one_time_keyboard': True,
        }

    return data


def message_contains(message: Message, *options: str):
    text = message.text.lower()
    return any(x in text for x in options)
