import os
import warnings
from collections import deque
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import torch
from torch.utils.data import Dataset
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm


warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


class ObsActDataset(Dataset):
    def __init__(
        self, dataset_dir: str, filenames: list[str], max_cache_size: int = 512
    ) -> None:
        """
        Args:
            dataset_dir (str): Path to the dataset, ie 'dataset/ssl-1v1-100'
            filenames (list of str): List of names for the action/obs numpy files
            max_cache_size (int): Maximum number of files to keep in cache at once
        """
        self.dataset_dir = dataset_dir
        self.filenames = filenames
        self.max_cache_size = max_cache_size
        self.data_cache: dict = {}
        self.cache_queue: deque = deque(maxlen=max_cache_size)
        self.file_usage_count: dict = {}
        self.index_map = self._build_index_map()
        self.obs_size = 111
        self.action_size = 90

    # Function to process a single file
    def _build_index_map(self) -> list:
        def process_file(filename: str) -> list:
            actions_path = os.path.join(self.dataset_dir, "actions", f"{filename}.npz")
            obs_path = os.path.join(self.dataset_dir, "obs", f"{filename}.npz")

            actions = np.load(actions_path)["array"]
            obs = np.load(obs_path)["array"]

            self.file_usage_count[filename] = len(obs) - 1
            return [(filename, i) for i in range(len(obs) - 1)]

        index_map = []

        # Parallelize processing with ThreadPoolExecutor
        with ThreadPoolExecutor(max_workers=16) as executor:
            # Submit tasks for each file and gather results
            results = list(
                tqdm(
                    executor.map(process_file, self.filenames),
                    total=len(self.filenames),
                )
            )

        # Flatten the list of results into a single index map
        for result in results:
            index_map.extend(result)

        return index_map

    def _load_file_into_cache(self, filename: str) -> None:
        if filename in self.data_cache:
            return  # Already cached

        # Load the file
        actions_path = os.path.join(self.dataset_dir, "actions", f"{filename}.npz")
        obs_path = os.path.join(self.dataset_dir, "obs", f"{filename}.npz")

        actions = np.load(actions_path)["array"]
        obs = np.load(obs_path)["array"]

        actions_tensor = torch.from_numpy(actions).long()
        obs_tensor = torch.from_numpy(obs).float()

        # Manage cache size
        if len(self.cache_queue) >= self.max_cache_size:
            oldest_filename = self.cache_queue.popleft()
            del self.data_cache[oldest_filename]

        # Cache the new file
        self.data_cache[filename] = (obs_tensor, actions_tensor)
        self.cache_queue.append(filename)

    def __len__(self) -> int:
        return len(self.index_map)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor]:
        filename, i = self.index_map[idx]

        # Load file into cache if it's not already loaded
        if filename not in self.data_cache:
            self._load_file_into_cache(filename)

        obs_tensor, actions_tensor = self.data_cache[filename]

        # Fetch the observation and action
        obs = obs_tensor[i]
        action = actions_tensor[i + 1]

        return obs, action
