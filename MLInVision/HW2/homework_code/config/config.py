import os
from typing import Literal


ResidualBlockType : Literal["A", "B", "C"] = os.environ.get("RESIDUAL_BLOCK_TYPE", "A")
Epochs : int = int(os.environ.get("EPOCHS", "5"))