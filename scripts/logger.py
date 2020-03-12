import logging


def make_logger(name):
    _logger = logging.getLogger(name)
    log_handler = logging.StreamHandler()
    log_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    _logger.addHandler(log_handler)
    _logger.setLevel(logging.INFO)
    return _logger


logger = make_logger('scanner')
