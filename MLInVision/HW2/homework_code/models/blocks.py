import torch
import torch.nn as nn


class ResidualBlockA(nn.Module):
    def __init__(self, input_channels: int, out_channels: int, has_skip_conv: bool):
        super(ResidualBlockA, self).__init__()

        self.seqs = nn.Sequential(
         nn.Conv2d(input_channels, out_channels, kernel_size=3, padding=1),
         nn.BatchNorm2d(out_channels),
         nn.ReLU(),
         nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
         nn.BatchNorm2d(out_channels),
        )
        self.relu = nn.ReLU()
        if has_skip_conv:
            self.conv_skip = nn.Conv2d(input_channels, out_channels, kernel_size=1)

    def forward(self, x):
        out = self.seqs(x)
        if hasattr(self, 'conv_skip'):
            out += self.conv_skip(x)
        else:
            out += x
        out = self.relu(out)
        return out

class ResidualBlockB(nn.Module):
    def __init__(self, input_channels: int, out_channels: int):
        super(ResidualBlockB, self).__init__()
        if out_channels % 4 != 0:
            raise ValueError("out_channels must be divisible by 4 for ResidualBlockB.")
        width = out_channels // 4

        self.path1 = nn.Sequential(
            nn.AvgPool2d(kernel_size=3, stride=1, padding=1),
            nn.Conv2d(input_channels, width, 1)
        )
        self.path2 = nn.Sequential(
            nn.Conv2d(input_channels, width, 1)
        )
        self.path3 = nn.Sequential(
            nn.Conv2d(input_channels, 64, 1),   
            nn.Conv2d(64, width, 3, padding=1)
        )
        self.path4 = nn.Sequential(
            nn.Conv2d(input_channels, 64, 1),   
            nn.Conv2d(64, 96, 3, padding=1),
            nn.Conv2d(96, width, 3, padding=1)
        )

    def forward(self, x):
        out1 = self.path1(x)
        out2 = self.path2(x)
        out3 = self.path3(x)
        out4 = self.path4(x)
        out = torch.cat([out1, out2, out3, out4], dim=1)
        return out

class ResidualBlockC(nn.Module):
    def __init__(self, input_channels, out_channels, g: int = 4, b: int = None):
        super(ResidualBlockC, self).__init__()
        if b is None:
            b = out_channels
        
        
        self.conv1 = nn.Conv2d(input_channels, b, kernel_size=1, groups=g, bias=False)
        
        self.conv2 = nn.Conv2d(b, b, kernel_size=3, stride=1, 
                               padding=1, groups=g, bias=False)
        
        self.conv3 = nn.Conv2d(b, out_channels, kernel_size=1, bias=False)

        self.conv_skip = nn.Conv2d(input_channels, out_channels, 1)

    def forward(self, x):
        out = self.conv1(x)
        out = self.conv2(out)
        out = self.conv3(out)

        out += self.conv_skip(x) 
        return out
