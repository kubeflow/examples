import json
import argparse
from pathlib import Path
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
from qiskit.circuit.library import ZZFeatureMap, RealAmplitudes
from qiskit import QuantumCircuit
from qiskit_machine_learning.neural_networks import EstimatorQNN
from qiskit_machine_learning.connectors import TorchConnector

# Define and create QNN
def create_qnn():
    feature_map = ZZFeatureMap(2)
    ansatz = RealAmplitudes(2, reps=1)
    qc = QuantumCircuit(2)
    qc.compose(feature_map, inplace=True)
    qc.compose(ansatz, inplace=True)

    qnn = EstimatorQNN(
        circuit=qc,
        input_params=feature_map.parameters,
        weight_params=ansatz.parameters,
        input_gradients=True,
    )
    return qnn

class Net(nn.Module):
    def __init__(self, qnn):
        super().__init__()
        self.conv1 = nn.Conv2d(1, 2, kernel_size=5)
        self.conv2 = nn.Conv2d(2, 16, kernel_size=5)
        self.dropout = nn.Dropout2d()
        self.fc1 = nn.Linear(256, 64)
        self.fc2 = nn.Linear(64, 2)
        self.qnn = TorchConnector(qnn)
        self.fc3 = nn.Linear(1, 1)

    def forward(self, x):
        x = F.relu(self.conv1(x))
        x = F.max_pool2d(x, 2)
        x = F.relu(self.conv2(x))
        x = F.max_pool2d(x, 2)
        x = self.dropout(x)
        x = x.view(x.shape[0], -1)
        x = F.relu(self.fc1(x))
        x = self.fc2(x)
        x = self.qnn(x)
        x = self.fc3(x)
        return torch.cat((x, 1 - x), -1)


def train_model(args):
    with open(args.data) as data_file:
        data = json.load(data_file)
    data = json.loads(data)
    x_train = torch.tensor(np.resize(data['x_train'],(200,1,1,28,28)), dtype=torch.float32)
    y_train = torch.tensor(np.resize(data['y_train'],(200,1)))
    x_test = torch.tensor(np.resize(data['x_test'],(100,1,1,28,28)), dtype=torch.float32)
    y_test = torch.tensor(np.resize(data['y_test'],(100,1)))
    
    x_train = x_train / 255
    x_test = x_test/ 255
    
    train=[x_train,y_train] 
    test=[x_test,y_test]
    # Define model, optimizer, and loss function
    qnn = create_qnn()
    model = Net(qnn)
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    loss_func = nn.NLLLoss()

    # Set up data loaders (you need to define train_loader and test_loader)

    # Start training
    epochs = 10  # Set number of epochs
    loss_list = []  # Store loss history
    model.train()  # Set model to training mode
    batch_size=1
    
    for epoch in range(epochs):
        total_loss = []
        train_acc = 0
        for i in range(len(train[0])):
            optimizer.zero_grad(set_to_none=True)  # Initialize gradient
            output = model(train[0][i])  # Forward pass

            loss = loss_func(output, train[1][i])  # Calculate loss
            loss.backward()  # Backward pass
            optimizer.step()  # Optimize weights
            total_loss.append(loss.item())  # Store loss
            pred = output.argmax(dim=1, keepdim=True)
            train_acc += pred.eq(train[1][i].view_as(pred)).sum().item()
        loss_list.append(sum(total_loss) / len(total_loss))
    train_acc = train_acc / len(train[0]) /  batch_size * 100
    model.eval()
    with torch.no_grad():
        test_acc = 0
        total_loss = []
        for i in range(len(test[0])):
            output = model(test[0][i])
            if len(output.shape) == 1:
                output = output.reshape(1, *output.shape)
            pred = output.argmax(dim=1, keepdim=True)
            test_acc += pred.eq(test[1][i].view_as(pred)).sum().item()
            loss = loss_func(output, test[1][i])
            total_loss.append(loss.item())

    test_acc = test_acc / len(test[0]) /  batch_size * 100
    average_loss = sum(total_loss) / len(total_loss)

    accuracy = (f"Qnn train accuracy: {train_acc}\nQnn test accuracy:{test_acc}")
    # Save output into file
    with open(args.accuracy, 'w') as accuracy_file:
        accuracy_file.write(str(accuracy))
if __name__ == '__main__':
        # Defining and parsing the command-line arguments
        parser = argparse.ArgumentParser(description='My program description')
        parser.add_argument('--data', type=str)
        parser.add_argument('--accuracy', type=str)
        args = parser.parse_args()

        # Creating the directory where the output file will be created (the directory may or may not exist).
        Path(args.accuracy).parent.mkdir(parents=True, exist_ok=True)

        train_model(args)