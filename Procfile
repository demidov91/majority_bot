web: gunicorn -w 3 -b 0.0.0.0:${PORT} majority_bot.api:init --worker-class aiohttp.GunicornUVLoopWebWorker