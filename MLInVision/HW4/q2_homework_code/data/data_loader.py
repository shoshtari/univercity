
from torch.utils.data import DataLoader

BATCH_SIZE = 128

def get_dataloader(ds, batch_size=BATCH_SIZE, shuffle=True, num_workers=2):
    return DataLoader(
        ds,
        batch_size=batch_size,
        shuffle=shuffle,                         
        num_workers=num_workers,                 
        persistent_workers=num_workers > 0,      
    )
