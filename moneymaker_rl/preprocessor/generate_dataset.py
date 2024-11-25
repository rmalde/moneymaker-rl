import argparse
import os
from concurrent.futures import ProcessPoolExecutor
from typing import Optional, Tuple

import numpy as np
from tqdm.rich import tqdm

from moneymaker_rl.data import zip_dataset
from moneymaker_rl.preprocessor.data import (
    download_replays,
    replay_to_rlgym_frames,
    rlgym_frames_to_action_obs,
)


def make_dirs(dataset_dir: str) -> Tuple[str, str, str, str]:
    def _make_if_not_exists(dir_path: str) -> str:
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)
        return dir_path

    dataset_dir = _make_if_not_exists(dataset_dir)
    replay_dir = _make_if_not_exists(os.path.join(dataset_dir, "replays"))
    actions_dir = _make_if_not_exists(os.path.join(dataset_dir, "actions"))
    obs_dir = _make_if_not_exists(os.path.join(dataset_dir, "obs"))
    return dataset_dir, replay_dir, actions_dir, obs_dir


def process_replay(
    replay_id: str,
    replay_idx: int,
    replay_dir: str,
    actions_dir: str,
    obs_dir: str
) -> Optional[str]:
    replay_path = os.path.join(replay_dir, f"{replay_id}.replay")
    try:
        frames = replay_to_rlgym_frames(replay_path)
    except Exception as e:
        print(f"Error processing {replay_id}: {e}")
        print("Skipping...")
        return None

    actions, obs = rlgym_frames_to_action_obs(frames)
    agent_ids = list(frames[0].state.cars.keys())

    data = []
    for j in range(len(agent_ids)):
        action_path = os.path.join(actions_dir, f"{replay_idx:07}_{j}.npz")
        obs_path = os.path.join(obs_dir, f"{replay_idx:07}_{j}.npz")
        np.savez_compressed(action_path, array=actions[j])
        np.savez_compressed(obs_path, array=obs[j])
        data.append((replay_id, j, action_path, obs_path))

    return replay_id


def gen_dataset(
    dataset_dir: str,
    count: int = 2,
    use_downloaded_replays: bool = False,
    verbose: bool = False,
) -> None:
    dataset_dir, replay_dir, actions_dir, obs_dir = make_dirs(dataset_dir)

    if use_downloaded_replays:
        ids = [f.split(".")[0] for f in os.listdir(replay_dir) if f.endswith(".replay")]
    else:
        ids = download_replays(replay_dir=replay_dir, count=count, verbose=verbose)

    print("Processing replays...")

    with ProcessPoolExecutor(max_workers=4) as executor:
        futures = [
            executor.submit(
                process_replay, replay_id, replay_idx, replay_dir, actions_dir, obs_dir
            )
            for replay_idx, replay_id in enumerate(ids)
        ]
        with tqdm(total=len(futures), desc="Processing replays") as pbar:
            for future in futures:
                result = future.result()
                pbar.update(1)

    print("Zipping dataset...")
    zip_dataset(dataset_dir)

    print("Done!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate dataset")
    # choose one or the other
    parser.add_argument(
        "--count", type=int, default=4, help="Number of replays to process"
    )
    parser.add_argument(
        "--use-downloaded-replays",
        action="store_true",
        default=False,
        help="Use already downloaded replays",
    )
    args = parser.parse_args()

    DATASET_NAME = "ssl-1v1-40-pyr"
    gen_dataset(
        os.path.join("dataset", DATASET_NAME),
        count=args.count,
        use_downloaded_replays=args.use_downloaded_replays,
        verbose=True,
    )
