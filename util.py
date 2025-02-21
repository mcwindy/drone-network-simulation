from random import random

import numpy as np

from config import config

fading_matrix = np.zeros((config["channel_count"], config["uav_count"]))  # channel*uav_count


def random_pos() -> list:
    if config["dimension"] == 2:
        return [
            random() * 100,
            random() * 100,
        ]
    else:
        return [
            random() * 100,
            random() * 100,
            random() * 100,
        ]


def random_speed() -> tuple:
    if config["dimension"] == 2:
        return (
            random(),
            random(),
        )
    else:
        return (
            random(),
            random(),
            random(),
        )


def update_fading_matrix():
    global fading_matrix
    scale = 1 / np.sqrt(np.pi / 2)  # Rayleigh fading scale parameter is 1/sqrt(pi/2)
    fading_matrix[:] = np.random.rayleigh(scale=scale, size=(config["channel_count"], config["uav_count"]))
