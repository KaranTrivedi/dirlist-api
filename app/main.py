from app import create_root_app

# logging.config.fileConfig('conf/logging.ini')
# # log_listener = logging.config.listen(9030)
# # log_listener.start()

# logger = logging.getLogger("root")
# logger.info("test")

app = create_root_app()