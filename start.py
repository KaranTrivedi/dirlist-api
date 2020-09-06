import uvicorn
import configparser
import logging
import json

# import logging.config
# from logging.config import fileConfig

# import elastic_calls

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')

# log_config = uvicorn.config.LOGGING_CONFIG
# del log_config["handlers"]["access"]
# del log_config["handlers"]["default"]

# log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
# log_config["formatters"]["default"]["fmt"] = "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(funcName)s - %(message)s"

# log_config["handlers"]["access"] = {
#     "formatter" : "access",
#     "class" : 'logging.FileHandler',
#     "filename" : "logs/access.log"
# }

# log_config["handlers"]["default"] = {
#     "formatter" : "default",
#     "class" : 'logging.FileHandler',
#     "filename" : "logs/test.log"
# }

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0",
                port=8000, reload=True) 
                # log_config=log_config, log_level="debug")
