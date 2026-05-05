from typing import Literal, Optional

import torch
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
import torch.nn as nn
import os
from data.data_loader import get_dataloader, MNISTDataset
from models.blocks import ResidualBlockA, ResidualBlockB, ResidualBlockC

class Model(nn.Module):
    def __init__(self, residual_type: Literal["A", "B", "C"] = "A"):
        """
        call with get_device or it risk a device mismatch
        """
        super().__init__()

        match residual_type:
            case "A":
                ResidualBlock = lambda i, o, has_skip_conv: ResidualBlockA(i, o, has_skip_conv)
            case "B":
                ResidualBlock = lambda i, o, has_skip_conv: ResidualBlockB(i, o)
            case "C":
                ResidualBlock = lambda i, o, has_skip_conv: ResidualBlockC(i, o)
            case _:
                raise ValueError("Invalid residual block type. Choose from 'A', 'B', or 'C'.")
        
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(True),

            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),

            ResidualBlock(64, 128, has_skip_conv=True),

            ResidualBlock(128, 128, has_skip_conv=True),

            nn.Conv2d(128, 256, kernel_size=3, padding=1),
            nn.BatchNorm2d(256),
            nn.ReLU(True),
            nn.MaxPool2d(kernel_size=2, stride=2),
            ResidualBlock(256, 256, has_skip_conv=True),
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
        )

        self.linear = nn.Sequential(
            nn.Dropout(0.5),
            nn.Linear(256, 10),
        )
        self.softmax = nn.Softmax(dim=1)

        self.criterion = nn.CrossEntropyLoss()
        self.optimizer = optim.SGD(self.parameters(), lr=0.01, momentum=0.9, weight_decay=5e-4)

    def forward(self, x):
        out = self.features(x)
        out = self.linear(out)
        return out
    
    def train_an_epoch(self, dataloader: DataLoader):
        """ Train the model for one epoch """
        self.train()
        running_loss = 0.0
        correct = 0
        total = 0
        
        for images, labels in dataloader:
            images, labels = images.to(self.device), labels.to(self.device)
            
            outputs = self(images)
            loss = self.criterion(outputs, labels)
            
            self.optimizer.zero_grad() 
            loss.backward()       
            self.optimizer.step()  
            
            running_loss += loss.item() * images.size(0)
            _, predicted = outputs.max(1)
            total += labels.size(0)
            correct += predicted.eq(labels).sum().item()
            
        epoch_loss = running_loss / len(dataloader.dataset)
        epoch_acc = 100. * correct / total
        return epoch_loss, epoch_acc

    def run_train(self, epochs_count: int, train_data: DataLoader, val_data: Optional[DataLoader] = None, verbose: bool = True):
        """ Run training for a specified number of epochs """
        results = []
        for i in range(epochs_count):
            train_loss, train_acc =self.train_an_epoch( train_data)

            results.append({
                "train_loss": train_loss,
                "train_acc": train_acc,
            })
            if val_data:
                val_loss, val_acc = self.evaluate(val_data)

                results[-1]["val_loss"] = val_loss
                results[-1]["val_acc"] = val_acc

            if verbose:
                print(f"Epoch [{i+1}/{epochs_count}]")
                print(f"Train Loss: {train_loss:.4f} | Train Acc: {train_acc:.2f}%")
                if val_data:
                    print(f"Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
                print("-" * 30)
        return results

    def evaluate(self, dataloader):
        self.eval()
        running_loss = 0.0
        correct = 0
        total = 0
        
        with torch.no_grad(): 
            for images, labels in dataloader:
                images, labels = images.to(self.device), labels.to(self.device)
                
                outputs = self(images)
                loss = self.criterion(outputs, labels)
                
                running_loss += loss.item() * images.size(0)

                outputs = self.softmax(outputs)
                _, predicted = outputs.max(1)
                total += labels.size(0)
                correct += predicted.eq(labels).sum().item()
                
        val_loss = running_loss / len(dataloader.dataset)
        val_acc = 100. * correct / total
        return val_loss, val_acc
    
    
    @property 
    def device(self):
        """ Get the device on which the model is running """
        if torch.cuda.is_available():
            return "cuda"
        elif torch.backends.mps.is_available():
            return "mps"
        else:
            return "cpu"

    @classmethod
    def get_with_device(cls, residual_type: Literal["A", "B", "C"] = "A"):
        """ initialize model with the appropriate device """
        model = cls(residual_type=residual_type)
        device = model.device
        return model.to(device)

    def freeze(self):
        """ freeze the feature extractor """
        for param in self.features.parameters():
            param.requires_grad = False
        self.optimizer = optim.SGD([p for p in self.parameters() if p.requires_grad], lr=0.01, momentum=0.9, weight_decay=5e-4)