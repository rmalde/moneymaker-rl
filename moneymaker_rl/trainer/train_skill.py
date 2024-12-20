import torch
import torch.nn as nn

from moneymaker_rl.models import FCN, SkillMask
from moneymaker_rl.trainer import Trainer
from moneymaker_rl.trainer.data import get_skill_dataloaders


def train(dataset_dir):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Using device: {device}")

    batch_size = 1024
    train_loader, test_loader, obs_size, action_size = get_skill_dataloaders(
        dataset_dir, batch_size=batch_size
    )

    trainer_config = {
        "learning_rate": 5e-3,
        "num_epochs": 100_000,
        # "wandb_project": "rl-skill-trainer",
        "wandb_project": None,
    }
    # model_config = {
    #     "d_model": 64,
    #     "num_heads": 4,
    #     "d_ff": 256,
    #     "attn_pdrop": 0.5,
    #     "residual_pdrop": 0.5,
    #     "num_layers": 8,
    # }
    model_config = {"dropout": 0.5, "use_batch_norm": True}

    print("Initializing model...")
    skill_mask = SkillMask()
    model = nn.Sequential(
        skill_mask,
        FCN(
            obs_size=skill_mask.out_dim,
            action_size=action_size,
            layer_sizes=[1024, 1024, 1024, 1024],
            objective="regression",
            config=model_config,
        ),
    )
    # model = PhysicsTransformer(
    #     obs_size=obs_size,
    #     action_size=action_size,
    #     objective="regression",
    #     config=model_config,
    # )

    trainer = Trainer(
        model,
        train_loader,
        test_loader,
        trainer_config,
        device=device,
        objective="regression",
    )

    print("Training model...")
    trainer.train()


if __name__ == "__main__":
    dataset_dir = "dataset/1v1-skill"
    train(dataset_dir)
