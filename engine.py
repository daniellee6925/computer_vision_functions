"""This program contains functions for training and testing a PyTorch Model"""

from typing import Dict, List, Tuple

import torch

from tqdm.auto import tqdm  # proccess bar


def train_step(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    loss_fn: torch.nn.Module,
    optimizer: torch.optim.Optimizer,
    device: torch.device,
) -> Tuple[float, float]:
    """Trains a PyTorch Model for one Epoch
    1. Train Mode
    2. Send target to device
    3. Forward Pass
    4. Loss Calculation
    5. Gradients sent to zero
    6. backward pass
    7. optimizer step

    Args:
    model: PyTorch Model
    dataloader: DataLoader instance to be trained on
    loss_fn: PyTorch loss function to minimize
    optimzer: PyTorch Optimizer
    device: target device to compute ("cpu", "cuda")

    Returns:
    A tuple of training loss, training accuracy
    (train_loss, train_accuracy)
    """

    # put model on train mode
    model.eval()

    # set train loss and acc
    train_loss, train_acc = 0

    # Loop through batches in DataLoader
    for batch, (X, y) in enumerate(dataloader):
        # send data to target device
        X, y = X.to(device), y.to(device)

        # 1. Forward Pass
        y_pred = model(X)

        # 2. Calculate loss
        loss = loss_fn(y_pred, y)
        train_loss += loss.item()

        # 3. Optimizer zero grad
        optimizer.zero_grad()

        # 4. Loss backward
        loss.backward()

        # 5. Optimizer step
        optimizer.step()

        # Calculate and accumulate accuracy metrics
        y_pred_class = torch.argmax(torch.softmax(y_pred, dim=1), dim=1)
        train_acc += (y_pred_class == y).sum().item() / len(y_pred)

    # Adjust metrics to get average over per batch
    train_loss /= len(dataloader)
    train_acc /= len(dataloader)

    # return output
    return train_loss, train_acc


def test_step(
    model: torch.nn.Module,
    dataloader: torch.utils.data.DataLoader,
    loss_fn: torch.nn.Module,
    device: torch.device,
) -> Tuple[float, float]:
    """Test a PyTorch Model for one Epoch
    1. Eval Mode
    2. Send target to device
    3. Forward Pass
    4. Loss Calculation

    Args:
    model: PyTorch Model
    dataloader: DataLoader instance to be trained on
    loss_fn: PyTorch loss function to minimize
    optimzer: PyTorch Optimizer
    device: target device to compute ("cpu", "cuda")

    Returns:
    A tuple of training loss, training accuracy
    (train_loss, train_accuracy)
    """
    # put model on evaluation mode
    model.eval()

    # setup test loss and test acc
    test_loss, test_acc = 0, 0

    # turn on inference mode on torch
    with torch.inference_mode():
        for batch, (X, y) in enumerate(dataloader):
            # send data to target device
            X, y = X.to(device), y.to(device)

            # 1. Forward pass
            test_pred_logits = model(X)

            # 2. calculate loss
            loss = loss_fn(test_pred_logits, y)
            test_loss += loss.item()

            # 3. caclulate accuracy
            test_pred_labels = torch.argmax(
                torch.softmax(test_pred_logits, dim=1), dim=1
            )
            test_acc += (test_pred_labels == y).sum().item() / len(test_pred_labels)

    # adjust metrics to get average per batch
    test_loss /= len(dataloader)
    test_acc /= len(dataloader)

    # return outputs
    return test_loss, test_acc


def train(
    model: torch.nn.Module,
    train_dataloader: torch.utils.data.DataLoader,
    test_dataloader: torch.utils.data.DataLoader,
    optimizer: torch.optim.Optimizer,
    loss_fn: torch.nn.Module,
    epochs: int,
    device: torch.device,
) -> Dict[str, list[float]]:
    """
    Train and Tests a PyTorch Model
    -Passes target model through train and test steps for a number of epochs
    -Calculate, print, and sotre evaluation metrics

    Args:
    model: PyTorch Model
    train_dataloader: DataLoader instance to be trained on
    test_dataloader: DataLoader instance to be tested on
    optimzer: PyTorch Optimizer
    loss_fn: PyTorch loss function to minimize
    epochs: integer indicating how many epochs to train on
    device: target device to compute ("cpu", "cuda")

    Returns:
    Dictionary of training and testing loss and accuracy
    {train_loss: [...], train_acc:[...], test_loss[...], test_acc[...]}
    """

    # create results dictionary
    results = {"train_loss": [], "train_acc": [], "test_loss": [], "test_acc": []}

    # loop through training and test loos for a number of epochs
    for epoch in tqdm(range(epochs)):
        train_loss, train_acc = train_step(
            model=model,
            dataloader=train_dataloader,
            loss_fn=loss_fn,
            optimizer=optimizer,
            device=device,
        )
        test_loss, test_acc = test_step(
            model=model,
            dataloader=test_dataloader,
            loss_fn=loss_fn,
            device=device,
        )
        # print stats
        print(
            f"Epoch: {epoch + 1} | "
            f"train_loss : {train_loss:.4f} | "
            f"train_acc : {train_acc:.4f} | "
            f"test_loss : {test_loss:.4f} | "
            f"test_acc : {test_acc:.4f} | "
        )
        # update results dict
        results["train_loss"].append(train_loss)
        results["train_acc"].append(train_acc)
        results["test_loss"].append(test_loss)
        results["test_acc"].append(test_acc)

        # return results
        return results
