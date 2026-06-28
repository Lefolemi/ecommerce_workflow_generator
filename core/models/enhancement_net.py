# core/models/enhancement_net.py
import torch
import torch.nn as nn

class DoubleConv(nn.Module):
    """(Konvolusi -> BatchNorm -> ReLU) x 2"""
    def __init__(self, in_channels, out_channels):
        super().__init__()
        self.double_conv = nn.Sequential(
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True)
        )

    def forward(self, x):
        return self.double_conv(x)

class SimpleEnhanceUNet(nn.Module):
    def __init__(self, in_channels=3, out_channels=3):
        super().__init__()
        # Encoder (Downsampling)
        self.inc = DoubleConv(in_channels, 32)
        self.down1 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(32, 64))
        self.down2 = nn.Sequential(nn.MaxPool2d(2), DoubleConv(64, 128))
        
        # Decoder (Upsampling)
        self.up1 = nn.ConvTranspose2d(128, 64, kernel_size=2, stride=2)
        self.conv_up1 = DoubleConv(128, 64) # 64 dari up + 64 dari skip connection
        
        self.up2 = nn.ConvTranspose2d(64, 32, kernel_size=2, stride=2)
        self.conv_up2 = DoubleConv(64, 32)  # 32 dari up + 32 dari skip connection
        
        # Output Layer
        self.outc = nn.Conv2d(32, out_channels, kernel_size=1)
        self.sigmoid = nn.Sigmoid() # Memastikan nilai piksel berada di rentang [0, 1]

    def forward(self, x):
        # Jalur Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        
        # Jalur Decoder dengan Skip Connection
        out = self.up1(x3)
        out = torch.cat([out, x2], dim=1) # Menggabungkan fitur spasial
        out = self.conv_up1(out)
        
        out = self.up2(out)
        out = torch.cat([out, x1], dim=1) # Menggabungkan fitur spasial
        out = self.conv_up2(out)
        
        logits = self.outc(out)
        return self.sigmoid(logits)

if __name__ == "__main__":
    # Tes integrasi dimensi dengan dummy tensor
    model = SimpleEnhanceUNet()
    dummy_input = torch.randn(4, 3, 400, 600) # Dimensi yang sama dengan batch dataset Anda
    dummy_output = model(dummy_input)
    print(f"Model diinisialisasi.")
    print(f"Dimensi Input : {dummy_input.shape}")
    print(f"Dimensi Output: {dummy_output.shape} -> Konvergensi dimensi sukses.")