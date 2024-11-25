# Third Party
import numpy as np


ACTION_SPACE = 90


class ContinuousAct:
    def __init__(self) -> None:
        self.ACTION_LEN = 8  # public variable

    def parse_actions(self, action: np.ndarray) -> np.ndarray:
        return action
