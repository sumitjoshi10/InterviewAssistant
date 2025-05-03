import logging
import os
from datetime import datetime

LOF_FILE = f"{datetime.now().strftime('%m_%d_%Y_%H_%M_%S')}.log"
log_path = os.path.join(os.getcwd(),"logs")
os.makedirs(log_path,exist_ok=True)

LOF_FILE_PATH = os.path.join(log_path,LOF_FILE)

logging.basicConfig(
    level=logging.INFO,
    filename=LOF_FILE_PATH,
    format="[ %(asctime)s ] %(lineno)d %(name)s - %(levelname)s - %(message)s"
)
