# core/models/enhancement_net.py
import torch
import torch.nn as nn
import torch.nn.functional as F

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
        self.sigmoid = nn.Sigmoid()

    def forward(self, x):
        # Jalur Encoder
        x1 = self.inc(x)
        x2 = self.down1(x1)
        x3 = self.down2(x2)
        
        # Jalur Decoder dengan Penyelarasan Dimensi Otomatis (Interpolate)
        out = self.up1(x3)
        # Menyelaraskan ukuran tensor 'out' agar sama persis dengan target skip connection 'x2'
        if out.shape[2:] != x2.shape[2:]:
            out = F.interpolate(out, size=x2.shape[2:], mode='bilinear', align_corners=False)
        out = torch.cat([out, x2], dim=1)
        out = self.conv_up1(out)
        
        out = self.up2(out)
        # Menyelaraskan ukuran tensor 'out' agar sama persis dengan target skip connection 'x1'
        if out.shape[2:] != x1.shape[2:]:
            out = F.interpolate(out, size=x1.shape[2:], mode='bilinear', align_corners=False)
        out = torch.cat([out, x1], dim=1)
        out = self.conv_up2(out)
        
        logits = self.outc(out)
        return self.sigmoid(logits)

if __name__ == "__main__":
    # Tes integrasi dimensi dengan dummy tensor ganjil (Uji Coba Batas Piksel)
    model = SimpleEnhanceUNet()
    dummy_input = torch.randn(1, 3, 341, 513) # Ukuran ganjil seperti error Anda
    dummy_output = model(dummy_input)
    print(f"Model diinisialisasi.")
    print(f"Dimensi Input : {dummy_input.shape}")
    print(f"Dimensi Output: {dummy_output.shape} -> Interseksi dimensi ganjil aman.")