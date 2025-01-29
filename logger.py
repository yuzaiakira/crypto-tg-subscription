import logging


logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='log.txt',
    filemode='a',
)
logger = logging.getLogger("yuzaiakira_tg_subscription")
logging.getLogger('httpx').setLevel(logging.WARNING)
