# for the ballchasing api: \
# https://github.com/Rolv-Arild/python-ballchasing/blob/master/ballchasing/api.py

import os
import warnings
from typing import Any, Iterator, List, Optional

import ballchasing
from ballchasing.constants import Playlist, Rank, Season
from dotenv import load_dotenv
from tqdm import TqdmExperimentalWarning
from tqdm.rich import tqdm


warnings.filterwarnings("ignore", category=TqdmExperimentalWarning)


load_dotenv()


def get_api() -> ballchasing.Api:
    api_key = os.getenv("BALLCHASING_API_KEY")
    if api_key is None:
        raise ValueError("BALLCHASING_API_KEY environment variable is not set")
    return ballchasing.Api(api_key)


# Initialize API at module level
api = get_api()


def get_replay_dicts(
    count: int = 2,
    min_rank: Optional[Rank] = None,
    max_rank: Optional[Rank] = None,
) -> Iterator[dict[str, Any]]:
    if min_rank is None:
        min_rank = Rank.SUPERSONIC_LEGEND
    if max_rank is None:
        max_rank = Rank.SUPERSONIC_LEGEND

    return api.get_replays(
        # player_name="retals",
        playlist=Playlist.RANKED_DUELS,
        season=Season.SEASON_13_FTP,
        min_rank=min_rank,
        max_rank=max_rank,
        count=count,
    )


def download_replays(
    replay_dir: str,
    count: int = 2,
    min_rank: Optional[Rank] = None,
    max_rank: Optional[Rank] = None,
    verbose: bool = False,
) -> List[str]:
    print(f"Downloading replays between {min_rank} and {max_rank} to {replay_dir}")

    if not os.path.exists(replay_dir):
        os.makedirs(replay_dir)

    ids = []
    with tqdm(total=count) as pbar:
        for replay in get_replay_dicts(
            count=count, min_rank=min_rank, max_rank=max_rank
        ):
            if verbose:
                orange_players = ", ".join(
                    [player["name"] for player in replay["orange"]["players"]]
                )
                blue_players = ", ".join(
                    [player["name"] for player in replay["blue"]["players"]]
                )
                print(f"{orange_players} vs. {blue_players}")

            api.download_replay(replay["id"], replay_dir)
            ids.append(replay["id"])

            pbar.update(1)
    return ids


if __name__ == "__main__":
    ids = download_replays(replay_dir="dataset/replays", count=10, verbose=True)
    print("Downloaded replay ids: ", ids)
