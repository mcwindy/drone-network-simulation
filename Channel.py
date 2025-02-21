class Channel:
    _id = 0
    drones = []

    def __init__(self, id):
        self.id = Channel._id
        Channel._id += 1
        self.drones = []
        self.bandwidth = 0

    def __str__(self):
        return f"Channel {self.id}"


class Channels:
    channels = []

    def __init__(self, total_channels):
        Channels.channels = [Channel(i) for i in range(total_channels)]
