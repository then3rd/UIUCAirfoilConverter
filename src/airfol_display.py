"""Aifoil visualizer (work in progress)"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
from scipy.interpolate import splev, splprep
from scipy.spatial import KDTree


def load_curve_points(file_path: Path):
    """Load 3D points from a SLDCRV file."""
    points = []
    with Path.open(file_path) as f:
        lines = f.readlines()
        # Skip the first line (header)
        for line in lines[1:]:
            if line.strip():  # Skip empty lines
                x, y, z = map(float, line.strip().split(","))
                points.append([x, y, z])
    return np.array(points)


def create_spline_curve(points, num_points=1000):
    """Create a spline interpolation of the curve with more points."""
    tck, u = splprep([points[:, 0], points[:, 1], points[:, 2]], s=0)
    u_new = np.linspace(0, 1, num_points)
    x_new, y_new, z_new = splev(u_new, tck)
    return np.column_stack((x_new, y_new, z_new))


def find_self_intersections(curve_points, threshold=0.001):
    """Find self-intersections in the curve."""
    # Create a KDTree for efficient nearest-neighbor search
    tree = KDTree(curve_points)

    intersections = []

    # For each point, find the nearest points
    for i, point in enumerate(curve_points):
        # Find all points within threshold distance
        distances, indices = tree.query(point, k=10, distance_upper_bound=threshold)

        # Filter out adjacent points in the curve
        for j, idx in enumerate(indices):
            if idx < len(curve_points) and distances[j] > 0:  # Valid index and not the same point
                # Check if points are not adjacent in the curve
                if abs(i - idx) > 5:  # Not close in the parameter space
                    # This is likely a self-intersection
                    intersections.append((i, idx, point, curve_points[idx]))

    return intersections


def visualize_curve_and_intersections(curve_points, intersections):
    """Visualize the curve and its self-intersections."""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    # Plot the curve
    ax.plot(curve_points[:, 0], curve_points[:, 1], curve_points[:, 2], "b-", linewidth=1)

    # Plot the intersections
    for i, idx, p1, p2 in intersections:
        ax.plot([p1[0]], [p1[1]], [p1[2]], "ro", markersize=8)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Curve with Self-Intersections")
    plt.show()


def main():
    # Load the points from file
    file_path = "n0012_upper.sldcrv"
    points = load_curve_points(file_path)

    # Create a smooth curve with more points
    curve_points = create_spline_curve(points)

    # Find self-intersections
    intersections = find_self_intersections(curve_points)

    print(f"Found {len(intersections)} potential self-intersections")

    # Visualize the results
    visualize_curve_and_intersections(curve_points, intersections)


if __name__ == "__main__":
    main()
