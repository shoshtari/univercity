from config import config
from data.data_loader import get_dataloader, MNISTDataset
from models.models import Model

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

logger = logging.getLogger(__name__)
train_dataloader = get_dataloader(MNISTDataset('train'))
val_dataloader = get_dataloader(MNISTDataset('val'))
logger.info("Data loaders are ready.")

model = Model.get_with_device()
err, acc = model.evaluate(dataloader=val_dataloader)
logger.info(f"Initial evaluation - Error: {err}, Accuracy: {acc}")
model.run_train(config.Epochs, train_dataloader, val_data=val_dataloader)
err, acc = model.evaluate(dataloader=val_dataloader)
logger.info(f"Post-training evaluation - Error: {err}, Accuracy: {acc}")