import torch
import torch.nn as nn

from moneymaker_rl.models import FCN, TransformerCLS
from moneymaker_rl.trainer import Trainer
from moneymaker_rl.trainer.data import get_obsact_dataloaders
from moneymaker_rl.trainer.utils import count_parameters


class PolicyWrapper(nn.Module):
    def __init__(self, model):
        super().__init__()
        self.model = model

    def forward(self, x):
        return self.model(x)


def train(dataset_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")
    cut_filecount_to = None

    batch_size = 4096
    # cut_filecount_to = 1000
    train_loader, test_loader, obs_size, action_size = get_obsact_dataloaders(
        dataset_dir, batch_size=batch_size, cut_filecount_to=cut_filecount_to
    )

    trainer_config = {
        # "learning_rate": 5e-4,
        "learning_rate": 8e-4,
        "num_epochs": 100_000,
        "wandb_project": "rl-replay-trainer",
        # "wandb_project": None,
    }
    model_config = {"dropout": 0.3, "use_batch_norm": True}

    print("Initializing model...")
    model = PolicyWrapper(
        FCN(
            obs_size=obs_size,
            action_size=action_size,
            # layer_sizes=[2048, 2048, 2048, 1024, 1024],
            layer_sizes=[2048, 2048],
            # layer_sizes=[2048, 2048, 1024],
            objective="classification",
            config=model_config,
        )
    )

    print(f"Initialized model: {count_parameters(model)}")
    # model = Transformer(
    #     obs_size=obs_size,
    #     action_size=action_size,
    #     config=model_config,
    # )

    model = PolicyWrapper(
        TransformerCLS(
            obs_size=obs_size,
            action_size=action_size,
            objective="classification",
            config=model_config,
        )
    )
    trainer = Trainer(model, train_loader, test_loader, trainer_config, device)

    print("Training model...")
    trainer.train()


if __name__ == "__main__":
    dataset_dir = "dataset/ssl-1v1-8k"
    train(dataset_dir)
    print("Training complete.")
