import logging
import datetime
import os

def create_logger(request_name: str):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"log/pt_req_{request_name}_{timestamp}.log"

    if not os.path.exists(os.path.dirname(filename)):
       os.makedirs(os.path.dirname(filename))

    logging.basicConfig(filename=filename, level=logging.INFO)

    return logging.getLogger(__name__)


def logging_request(requst_name: str, raw_data: bytes):
    logger = create_logger(requst_name)
    logger.info("{}".format(raw_data))
