from typing import Dict, List, Optional, Tuple

import numpy as np


ACTION_SPACE = 90


class InverseLookupAct:
    def __init__(self, bins: Optional[List[Tuple[float, ...]]] = None) -> None:
        self.ACTION_LEN = 1  # public variable

        if bins is None:
            self.bins: List[Tuple[float, ...]] = [(-1.0, 0.0, 1.0)] * 5
        else:
            assert len(bins) == 5, "Need bins for throttle, steer, pitch, yaw and roll"
            # Ensure all elements are float tuples
            self.bins = [tuple(float(x) for x in bin_tuple) for bin_tuple in bins]

        self._lookup_table: np.ndarray = self.make_lookup_table(self.bins)
        self._inverse_lookup_table: Dict[Tuple[float, ...], int] = {
            tuple(action): i for i, action in enumerate(self._lookup_table)
        }
        # print(self._lookup_table)
        # quit()

    @staticmethod
    def make_lookup_table(bins: List[Tuple[float, ...]]) -> np.ndarray:
        actions = []
        # Ground
        for throttle in bins[0]:
            for steer in bins[1]:
                for boost in (0.0, 1.0):
                    for handbrake in (0.0, 1.0):
                        if boost == 1.0 and throttle != 1.0:
                            continue
                        actions.append(
                            [
                                float(throttle or boost),
                                float(steer),
                                0.0,
                                float(steer),
                                0.0,
                                0.0,
                                float(boost),
                                float(handbrake),
                            ]
                        )
        # [ 1 -1  0  0  0  0  1  0]

        # Aerial
        for pitch in bins[2]:
            for yaw in bins[3]:
                for roll in bins[4]:
                    for jump in (0.0, 1.0):
                        for boost in (0.0, 1.0):
                            if (
                                jump == 1.0 and yaw != 0.0
                            ):  # Only need roll for sideflip
                                continue
                            if pitch == roll == jump == 0.0:  # Duplicate with ground
                                continue
                            # Enable handbrake for potential wavedashes
                            handbrake = jump == 1.0 and (
                                pitch != 0.0 or yaw != 0.0 or roll != 0.0
                            )
                            actions.append(
                                [
                                    float(boost),
                                    float(yaw),
                                    float(pitch),
                                    float(yaw),
                                    float(roll),
                                    float(jump),
                                    float(boost),
                                    float(handbrake),
                                ]
                            )
        actions_np = np.array(actions)
        return actions_np

        # [throttle or boost, steer, 0, steer, 0, 0, boost, handbrake]
        # [boost, yaw, pitch, yaw, roll, jump, boost, handbrake]
        # actual:
        # [throttle, steer, pitch, yaw, roll, jump, boost, handbrake]

        # [ 1 -1  0  0  0  0  1  0]
        # (0.0, -1.0, -1.0, -1.0, -1.0, 0.0, 1.0, 0.0)

    def get_possible_actions(self) -> np.ndarray:
        possible_actions = np.zeros((ACTION_SPACE, 8))
        for i, action in enumerate(self._lookup_table):
            possible_actions[i] = action
        return possible_actions

    def round_actions(self, action: np.ndarray) -> np.ndarray:
        # throttle, steer, pitch, yaw, roll
        bins = np.array([-0.25, 0.25])
        action[:5] = np.digitize(action[:5], bins) - 1
        # jump, boost, handbrake
        action[5:] = action[5:] > 0.5

        throttle, steer, pitch, yaw, roll, jump, boost, handbrake = range(8)
        # if we're ground
        if action[pitch] == action[roll] == action[jump] == 0:
            # set yaw to the steer value
            action[yaw] = action[steer]
            # set throttle to 1 if we're boosting
            if action[boost] == 1:
                action[throttle] = 1
        else:  # if we're in the air
            # set throttle to the boost value
            action[throttle] = action[boost]
            # set steer to the yaw value
            action[steer] = action[yaw]
            # enable handbrake for wavedashes
            action[handbrake] = action[jump] == 1 and (
                action[pitch] != 0 or action[yaw] != 0 or action[roll] != 0
            )
            # change yaw jump to roll jump
            if action[jump] == 1 and action[yaw] != 0:
                action[roll] = action[yaw]
                action[yaw] = 0
                action[steer] = 0

        return action

    def parse_actions(self, action: np.ndarray, round: bool = False) -> int:
        if round:
            action = self.round_actions(action)
        return self._inverse_lookup_table[tuple(action)]

    def __repr__(self) -> str:
        return_str = ""
        for i, action in enumerate(self._lookup_table):
            return_str += f"{i}: {action}\n"
        return return_str
