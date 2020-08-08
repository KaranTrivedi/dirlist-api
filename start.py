import uvicorn
import configparser
import logging
# from logging.config import fileConfig

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')
SECTION = 'start'

logging.config.fileConfig('conf/logging.ini')
logger = logging.getLogger("root")

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0",
                port=8000, log_level="info", reload=True,
                access_log=True, log_config="conf/logging.ini")
