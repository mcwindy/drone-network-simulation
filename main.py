from random import choice, sample

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
    all_uavs = [*edges, *uavs]
    _edges, _uavs = [], []

    def random_match():
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

    def greedy_match():
        channel_best_uavs = []
        for channel in channels.channels:
            for uav in all_uavs:
                channel_best_uav, max_snr = None, 0
                for base in bases:
                    uav.become_edge(base)
                    uav.join_channel(channel)
                    snr = uav.snr_without_interference()
                    if snr > max_snr:
                        max_snr = snr
                        channel_best_uav = uav
                        channel_best_base = base
                channel_best_uavs.append((channel, channel_best_uav, channel_best_base, max_snr))
        for uav in all_uavs:
            uav.become_uav(None)
        ll = sorted(channel_best_uavs, key=lambda x: x[3], reverse=True)
        for channel, uav, uav_best_base, max_snr in ll:
            if len(_edges) == config["edge_count"]:
                break
            if uav not in _edges and channel not in [edge.channel for edge in _edges]:
                uav.become_edge(uav_best_base)
                uav.join_channel(channel)
                _edges.append(uav)

        for uav in all_uavs:
            if uav.type == DroneType.Uav:
                min_interference = 1e20
                min_interference_channel = None
                min_interference_edge = None
                for edge in _edges:
                    for channel in channels.channels:
                        uav.join_channel(channel)
                        if uav.calculate_interference() < min_interference:
                            min_interference = uav.calculate_interference()
                            min_interference_channel = channel
                            min_interference_edge = edge
                uav.become_uav(min_interference_edge)
                uav.join_channel(min_interference_channel)
                _uavs.append(uav)

        return _edges, _uavs

    _edges, _uavs = greedy_match()
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
