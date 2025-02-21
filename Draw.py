from matplotlib import pyplot as plt
from matplotlib.animation import FuncAnimation

from config import config

fig = plt.figure(figsize=(12, 6))
ax1 = fig.add_subplot(121, projection=None if config["dimension"] == 2 else "3d")
ax2 = fig.add_subplot(122)

# Store line chart data
lines_data = [[] for _ in range(config["uav_count"] + 1)]


def update_image(bases, edges, uavs, throughput, edge_sub_throughput):
    ax1.clear()
    ax2.clear()

    # ax1
    if config["dimension"] == 2:
        for base in bases:
            ax1.scatter(base.pos[0], base.pos[1], color="red")
        for edge in edges:
            ax1.scatter(edge.pos[0], edge.pos[1], color="blue")
        for uav in uavs:
            ax1.scatter(uav.pos[0], uav.pos[1], color="green")
        ax1.set_title("2D plot")
    else:
        for base in bases:
            ax1.scatter(base.pos[0], base.pos[1], base.pos[2], color="red")
        for edge in edges:
            ax1.scatter(edge.pos[0], edge.pos[1], edge.pos[2], color="blue")
        for uav in uavs:
            ax1.scatter(uav.pos[0], uav.pos[1], uav.pos[2], color="green")
        ax1.set_title("3D plot")

    ax1.set_xlabel("X axis")
    ax1.set_ylabel("Y axis")

    # ax2
    # Line chart data
    for i in range(config["uav_count"]):
        lines_data[i].append(max(edge_sub_throughput[i], 1))
    lines_data[config["uav_count"]].append(max(throughput, 1))
    # Draw line chart
    for i, line in enumerate(lines_data):
        ax2.plot(range(len(line)), line, label=f"Line {i + 1}")

    ax2.set_title("Line")
    ax2.set_xlabel("Loop Count")
    ax2.set_ylabel("Throughput(bps)")
    ax2.set_yscale("log")

    plt.tight_layout()


if __name__ == "__main__":
    # Example
    bases = []
    edges = []
    uavs = []
    throughput = 0
    edge_sub_throughput = [1, 2, 0, 3, 0, 0, 0, 4, 0, 0]

    def update(frame):
        global edge_sub_throughput
        update_image(bases, edges, uavs, throughput, edge_sub_throughput)
        edge_sub_throughput = [x + 1 for x in edge_sub_throughput]  # 更新示例数据

    ani = FuncAnimation(fig, update, frames=range(10), repeat=False)
    plt.show()
