import os

import dotenv
import torch
import wandb


dotenv.load_dotenv()


class WandbLogger:
    def __init__(self, project: str):
        self.wandb_enabled = project is not None
        if not self.wandb_enabled:
            return

        wandb_key = os.getenv("WANDB_API_KEY")
        wandb_user = os.getenv("WANDB_USER")
        wandb.login(key=wandb_key)
        wandb.init(project=project, entity=wandb_user)

    def watch(self, model: torch.nn.Module) -> None:
        if not self.wandb_enabled:
            return
        wandb.watch(model)

    def log(self, data: dict) -> None:
        if not self.wandb_enabled:
            return
        wandb.log(data)
