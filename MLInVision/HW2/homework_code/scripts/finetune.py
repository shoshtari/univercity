"""
Load a saved model and only train its final layers.
"""

from data.data_loader import get_dataloader, FashionMNISTDataset
from models.models import Model
import torch

SAVED_PATH = "./models/saved_models/model_weights.pth"

model = Model()
model.load_state_dict(torch.load(SAVED_PATH))
model = model.to(model.device)

# model.freeze()

train_dataloader = get_dataloader(FashionMNISTDataset("train"))
val_dataloader = get_dataloader(FashionMNISTDataset("val"))
test_dataloader = get_dataloader(FashionMNISTDataset("test"))


print("Initial", model.evaluate(test_dataloader))

model.run_train(10, train_dataloader, val_dataloader)

print("After fine-tuning", model.evaluate(test_dataloader))
