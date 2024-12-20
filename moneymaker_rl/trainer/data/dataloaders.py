import json
import os
from collections import defaultdict

from sklearn.model_selection import train_test_split
from torch.utils.data import DataLoader

from moneymaker_rl.trainer.data import ObsActDataset, SkillDataset


def get_obsact_dataloaders(
    dataset_dir, batch_size=1024, num_workers=24, cut_filecount_to=None
):
    print("Loading train and test datasets...")
    # initialize data
    filenames = []
    for filename in os.listdir(os.path.join(dataset_dir, "actions")):
        filenames.append(filename.split(".")[0])

    # TEMP
    if cut_filecount_to is not None:
        filenames = filenames[:cut_filecount_to]
    train_filenames, test_filenames = train_test_split(filenames, test_size=0.2)

    train_dataset = ObsActDataset(dataset_dir, train_filenames)
    test_dataset = ObsActDataset(dataset_dir, test_filenames)

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )
    test_loader = DataLoader(
        test_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True,
    )

    print("Train and test datasets loaded.")
    print(f"Train dataset size: {len(train_dataset)}")
    print(f"Test dataset size: {len(test_dataset)}")
    print(f"Action size: {train_dataset.action_size}")
    print(f"Obs size: {train_dataset.obs_size}")

    return train_loader, test_loader, train_dataset.obs_size, train_dataset.action_size


def get_skill_dataloaders(dataset_dir, batch_size=1024):
    print("Loading train and test datasets...")
    # initialize data
    filename_to_rank = {}
    # must have this file for the skill dataset
    with open(os.path.join(dataset_dir, "filename_to_rank.json")) as f:
        filename_to_rank = json.load(f)

    rank_to_filenames = defaultdict(list)
    for filename, rank in filename_to_rank.items():
        rank_to_filenames[rank].append(filename)

    train_filenames = []
    test_filenames = []

    for rank, filenames in rank_to_filenames.items():
        # TEMP
        # filenames = filenames[:10]
        train, test = train_test_split(filenames, test_size=0.2)
        train_filenames.extend(train)
        test_filenames.extend(test)

    train_dataset = SkillDataset(dataset_dir, train_filenames, filename_to_rank)
    test_dataset = SkillDataset(dataset_dir, test_filenames, filename_to_rank)

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)

    print("Train and test datasets loaded.")
    print(f"Train dataset size: {len(train_dataset)}")
    print(f"Test dataset size: {len(test_dataset)}")
    print(f"Action size: {train_dataset.action_size}")
    print(f"Obs size: {train_dataset.obs_size}")

    return train_loader, test_loader, train_dataset.obs_size, train_dataset.action_size
