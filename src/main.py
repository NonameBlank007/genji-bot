import logging
import time

from telegram import Update
from telegram.ext import ApplicationBuilder

from .cfg import TOKEN
from .util.handler import Handlers
from .util.logging import logger

logger = logging.getLogger(__name__)

logger.info("Starting bot timer")
_start_time = time.time()

app = ApplicationBuilder().token(TOKEN).build()

logger.info("Registering handlers...")
Handlers.register(app)

logger.info("Starting Genji...")
logger.info("Genji Running.")
logger.info(f"Genji took {(time.time() - _start_time):.2f}s to startup.")
app.run_polling(allowed_updates=Update.ALL_TYPES, drop_pending_updates=True)
