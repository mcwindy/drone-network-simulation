import numpy as np
from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from Channel import Channels
from config import config
from Draw import fig, update_image
from Drone import DroneType, bases, edges, uavs
from util import fading_matrix, update_fading_matrix


def calculate_throughput():
    uav_throughput = [0 for _ in range(config["uav_count"])]
    for uav in [*edges, *uavs]:
        dis2 = (uav.edge if uav.type == DroneType.Uav else uav.base).distance(uav) ** 2
        fading = fading_matrix[uav.channel.id, uav.id]
        snr = fading * config["P"] / 10**3.53 / dis2**3.76
        sinr = snr / (config["noise"] + uav.calculate_interference())
        uav_throughput[uav.id] += config["channel_bandwith"] * np.log2(1 + sinr)
    edge_sub_throughput = [0 for _ in range(config["uav_count"])]
    for uav in uavs:
        edge_sub_throughput[uav.edge.id] += uav_throughput[uav.id]
    throughput = 0
    for edge in edges:
        edge_sub_throughput[edge.id] = min(uav_throughput[edge.id], edge_sub_throughput[edge.id])
        throughput += edge_sub_throughput[edge.id]
    return throughput, edge_sub_throughput


def calculate_match():
    # TODO
    ...

    from random import choice, sample

    all_uavs = [*edges, *uavs]
    _edges = sample(all_uavs, config["edge_count"])
    for edge in _edges:
        edge.become_edge(choice(bases))
        edge.join_channel(choice(channels.channels))

    _uavs = []
    for uav in all_uavs:
        if uav not in _edges:
            uav.become_uav(choice(_edges))
            uav.join_channel(choice(channels.channels))
            _uavs.append(uav)

    # return:
    #  1. edges
    #  2. uav.channel
    #  3. uav.edge
    #  4. edge.base
    return _edges, _uavs


def main_loop():
    def update(frame):
        global edges, uavs, fading_matrix
        update_fading_matrix()

        # uavs[0].calculate_interference()
        edges, uavs = calculate_match()

        # for uav in uavs:
        #     uav.update()
        throughput, edge_sub_throughput = calculate_throughput()
        # print("fading_matrix:", fading_matrix, throughput)
        for uav in [*edges, *uavs]:
            uav.move(frame)

        update_image(bases, edges, uavs, throughput, edge_sub_throughput)

    ani = FuncAnimation(fig, update, frames=range(1000), repeat=False)
    plt.show()


channels = Channels(config["channel_count"])
if __name__ == "__main__":
    while True:
        main_loop()
