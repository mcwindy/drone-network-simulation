import enum

import numpy as np

from Channel import Channels
from config import config
from util import fading_matrix, random_pos, random_speed


class DroneType(enum.Enum):
    Base = 1
    Edge = 2
    Uav = 3


class Drone:
    _id = -config["base_count"]

    def __init__(self, pos, type):
        self.id = Drone._id
        Drone._id += 1
        self.pos = pos
        self.speed = (0, 0) if config["dimension"] == 2 else (0, 0, 0)
        self.speed = random_speed()
        self.type = type
        self.channel = None
        self.base = None  # if type if Edge, self.base is not None
        self.edge = None  # if type is Uav, self.edge is not None

    def join_channel(self, channel):
        if self.channel:
            self.channel.drones.remove(self)
        channel.drones.append(self)
        self.channel = channel

    def become_edge(self, base):
        self.type = DroneType.Edge
        self.base = base
        edges.append(self)
        if self in uavs:
            uavs.remove(self)

    def become_uav(self, edge):
        self.type = DroneType.Uav
        self.edge = edge
        uavs.append(self)
        if self in edges:
            edges.remove(self)

    def distance(self, other_drone):
        return (
            (self.pos[0] - other_drone.pos[0]) ** 2 + (self.pos[1] - other_drone.pos[1]) ** 2 + 0
            if config["dimension"] == 2
            else (self.pos[2] - other_drone.pos[2]) ** 2
        ) ** 0.5

    def calculate_interference(self):
        interference = 0
        for drone in self.channel.drones:
            if self.id != drone.id:
                dis2 = (drone.edge or drone.base).distance(drone) ** 2
                fading = fading_matrix[self.channel.id, drone.id]
                interference += fading * config["P"] / 10**3.53 / dis2**3.76
        return interference

    def move(self, frame):
        self.pos[0] += self.speed[0] * config["uav_speed"] * np.sin(frame / 18)
        self.pos[1] += self.speed[1] * config["uav_speed"] * np.cos(frame / 18)
        if config["dimension"] == 3:
            self.pos[2] += self.speed[2] * config["uav_speed"] * np.sin(frame / 10)
        # self.pos = tuple(self.pos[i] + self.speed[i] * config["uav_speed"] for i in range(3 if config["dimension"] == 3 else 2))

    def snr_without_interference(self):
        snr = fading_matrix[self.channel.id, self.id] * config["P"] / 10**3.53 / self.distance(self.base) ** 2
        return snr


bases = [Drone(random_pos(), DroneType.Base) for _ in range(config["base_count"])]
edges = []
uavs = [Drone(random_pos(), DroneType.Uav) for _ in range(config["uav_count"])]

if __name__ == "__main__":
    a = Drone(random_pos(), DroneType.Base)
    b = Drone(random_pos(), DroneType.Edge)
    Channels(10)
    print(a.id, b.id)
    a.join_channel(Channels.channels[1])
    print(Channels.channels[1].drones[0].id)
    print(a.channel.drones)
