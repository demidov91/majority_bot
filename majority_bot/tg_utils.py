from telegram import Message


def build_message(text, options):
    data = {
        'method': 'sendMessage',
        'text': text,
    }
    if options:
        if len(options) < 3:
            data['reply_markup'] = [[{'text': x} for x in options]]

        else:
            data['reply_markup'] = [[{'text': x}] for x in options]

    return data


def message_contains(message: Message, *options: str):
    text = message.text.lower()
    return any(x in text for x in options)
