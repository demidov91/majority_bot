import os

import logging


logger = logging.getLogger(__name__)


is_live = bool(os.environ.get('IS_LIVE'))


def read_env(var_name: str, mandatory) -> str:
    if var_name not in os.environ:
        if mandatory:
            raise KeyError(var_name)

        logger.warning('%s is not set.', var_name)
        return None

    return os.environ[var_name]


TEST_CONNECTION_STRING = read_env('TEST_CONNECTION_STRING', mandatory=not is_live)
TEST_SECURE_URL = read_env('TEST_SECURE_URL', mandatory=not is_live)
TG_TOKENS = {
    'live': read_env('LIVE_CLIENT_BOT_TOKEN', mandatory=is_live),
    'test': read_env('TEST_CLIENT_BOT_TOKEN', mandatory=not is_live),
}