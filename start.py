import uvicorn
import configparser
import logging

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0",
                port=8000, log_level="info", reload=True,
                log_config="conf/logging.ini")