import os

import logging


logger = logging.getLogger(__name__)


def read_env(var_name: str, mandatory=True) -> str:
    if var_name not in os.environ:
        if mandatory:
            raise KeyError(var_name)

        logger.warning('%s is not set.', var_name)
        return None

    return os.environ[var_name]


TEST_CONNECTION_STRING = read_env('TEST_CONNECTION_STRING', mandatory=False)
TG_TOKENS = {
    'live': read_env('LIVE_CLIENT_BOT_TOKEN', mandatory=False),
    'test': read_env('TEST_CLIENT_BOT_TOKEN', mandatory=False),
}