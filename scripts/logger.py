import logging

logger = logging.getLogger('scanner')
log_handler = logging.StreamHandler()
log_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
logger.addHandler(log_handler)
logger.setLevel(logging.INFO)
