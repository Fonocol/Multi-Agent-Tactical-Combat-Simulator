import torch
import torch.nn as nn
import torch.nn.functional as F


class DQN(nn.Module):
    def __init__(self, input_dim, output_dim):
        super(DQN, self).__init__()

        self.fc1 = nn.Linear(input_dim, 256)
        self.bn1 = nn.LayerNorm(256)  # Stabilise l'entraînement

        self.fc2 = nn.Linear(256, 256)
        self.bn2 = nn.LayerNorm(256)

        self.fc3 = nn.Linear(256, 128)
        self.out = nn.Linear(128, output_dim)

    def forward(self, x):
        x = F.relu(self.bn1(self.fc1(x)))
        x = F.relu(self.bn2(self.fc2(x)))
        x = F.relu(self.fc3(x))
        return self.out(x)



class CombinedDQN(nn.Module):
    def __init__(self, flat_input_dim, output_dim, minimap_channels=18, minimap_size=64):
        super(CombinedDQN, self).__init__()

        # ------------------------
        # CNN  pour la minimap
        # ------------------------
        self.conv1 = nn.Sequential(
            nn.Conv2d(minimap_channels, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 64 -> 32
        )
        
        self.conv2 = nn.Sequential(
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.BatchNorm2d(64),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 32 -> 16
        )

        self.conv3 = nn.Sequential(
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.BatchNorm2d(128),
            nn.ReLU(),
            nn.MaxPool2d(2)  # 16 -> 8
        )

        # Calcul automatique de la taille de sortie du CNN
        with torch.no_grad():
            dummy_input = torch.zeros(1, minimap_channels, minimap_size, minimap_size)
            dummy_output = self.conv3(self.conv2(self.conv1(dummy_input)))
            self.conv_output_size = dummy_output.view(1, -1).shape[1]

        # ------------------------
        # MLP pour l'état plat
        # ------------------------
        self.flat_fc1 = nn.Linear(flat_input_dim, 256)
        self.flat_fc2 = nn.Linear(256, 256)

        # ------------------------
        # Fusion CNN + MLP
        # ------------------------
        self.fc_combined = nn.Linear(self.conv_output_size + 256, 512)
        self.out = nn.Linear(512, output_dim)

    def forward(self, flat_input, minimap_input):
        # Partie CNN
        x = self.conv1(minimap_input)
        x = self.conv2(x)
        x = self.conv3(x)
        x = x.view(x.size(0), -1)  # Flatten

        # Partie MLP
        f = F.relu(self.flat_fc1(flat_input))
        f = F.relu(self.flat_fc2(f))

        # Fusion
        combined = torch.cat((x, f), dim=1)
        combined = F.relu(self.fc_combined(combined))
        return self.out(combined)
