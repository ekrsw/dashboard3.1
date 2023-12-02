import datetime as dt
import logging
import os

from app.controller import controller

import settings

formatter = '%(asctime)s %(levelname)s %(message)s'
logging.basicConfig(filename=settings.LOGFILE, level=logging.INFO, format=formatter)

logger = logging.getLogger(__name__)

if __name__ == '__main__':
    logger.info('test')
    controller.df_to_html()

    