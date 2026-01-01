"""Airfoil coordinate data conversion tool."""

import argparse
import csv
import logging
from decimal import Decimal
from io import StringIO
from pathlib import Path
from urllib.parse import urlparse

import requests

logger = logging.getLogger(__name__)


def find_separator_by_x_coordinate(data_lines, start_idx):  # noqa: C901
    """Find separator by detecting direction change in x-coordinates.

    Airfoil data can be ordered in two ways:
    1. Leading edge (x≈0) → Trailing edge (x≈1) then Trailing → Leading
    2. Trailing edge (x≈1) → Leading edge (x≈0) then Leading → Trailing

    The separator is where the direction of x-coordinate progression changes.
    """
    x_coords = []
    valid_indices = []
    valid_length = 2
    for i in range(start_idx, len(data_lines)):
        line = data_lines[i].strip()
        if line:
            parts = line.split()
            if len(parts) == valid_length:
                try:
                    x = float(parts[0])
                    x_coords.append(x)
                    valid_indices.append(i)
                except ValueError:
                    continue

    min_coords = 4
    if len(x_coords) < min_coords:  # Need at least a few points to detect pattern
        return None

    # Detect direction changes in x-coordinates
    # Find where x reaches a minimum or maximum and reverses direction
    for i in range(1, len(x_coords) - 1):
        prev_diff = x_coords[i] - x_coords[i - 1]
        next_diff = x_coords[i + 1] - x_coords[i]
        # Check for direction reversal (going from decreasing to increasing or vice versa)
        # Allow small tolerance for numerical noise
        if abs(prev_diff) > 0.01 and abs(next_diff) > 0.01:  # noqa: PLR2004, SIM102
            # Check if we're at leading edge (x ≈ 0) or trailing edge (x ≈ 1)
            if x_coords[i] < 0.01 or x_coords[i] > 0.99:  # noqa: PLR2004, SIM102
                # Check for sign change in direction
                if prev_diff * next_diff < 0:  # Direction reversal
                    logger.info(f"Separator detected at index {i}: x={x_coords[i]:.6f}")
                    return valid_indices[i + 1]
    # Alternative: find the minimum x value (leading edge) as separator
    min_x_idx = x_coords.index(min(x_coords))
    if 0 < min_x_idx < len(x_coords) - 1:  # Not at the start or end
        logger.info(
            f"Separator detected at minimum x: index {min_x_idx}, x={x_coords[min_x_idx]:.6f}"
        )
        return valid_indices[min_x_idx + 1]
    return None


def parse_coordinates(lines, scale):
    """Parse coordinate lines into scaled (x,y) tuples."""
    coordinates = []
    length = 2
    for line in lines:
        if line.strip():
            parts = line.split()
            if len(parts) == length:
                x, y = map(Decimal, parts)  # Convert to Decimal for precise arithmetic
                # Scale using Decimal arithmetic for precision
                scaled_x = x * Decimal(scale)
                scaled_y = y * Decimal(scale)
                # Use float 0.0 instead of Decimal for zero values
                x_val = 0.0 if scaled_x == 0 else float(scaled_x)
                y_val = 0.0 if scaled_y == 0 else float(scaled_y)
                coordinates.append((x_val, y_val))
    return coordinates


def coordinates_to_csv(coordinates, *, include_header=True):
    """Convert coordinates to CSV format."""
    output = StringIO()
    writer = csv.writer(output)
    if include_header:
        writer.writerow(["X", "Y", "Z"])
    for x, y in coordinates:
        writer.writerow([0.0, y, x])
    return output.getvalue()


def convert_airfoil_data_to_csv(data_str: str, scale: int, *, include_header: bool = True):
    """Convert airfoil data to two CSV strings (upper and lower profiles).

    data_str:
    NACA 0012 AIRFOILS
      66.       66.

    0.0000000 0.0000000
    0.0005839 0.0042603
    0.9994161 0.0013419
    1.0000000 0.0012600

    0.0000000 0.0000000
    0.0005839 -.0042603
    0.9994161 -.0013419
    1.0000000 -.0012600
    """
    # Skip header lines and split data into sections
    lines = data_str.strip().split("\n")
    # Skip title and parameter lines (first two lines)
    data_lines = lines[2:]
    # Skip any leading empty lines
    start_idx = 0
    while start_idx < len(data_lines) and not data_lines[start_idx].strip():
        start_idx += 1
    # Find the separator between upper and lower profiles
    # Look for first empty line after data has started
    separator_idx = None
    for i in range(start_idx, len(data_lines)):
        if not data_lines[i].strip():
            separator_idx = i
            break
    # If no blank line separator found, try to find it automatically
    # by detecting where x-coordinates reach maximum (trailing edge) and start decreasing
    if separator_idx is None:
        logger.info("No blank line separator found, attempting automatic detection")
        separator_idx = find_separator_by_x_coordinate(data_lines, start_idx)
        if separator_idx is None:
            logger.warning(
                "Could not automatically detect separator between upper and lower profiles"
            )
            return "", ""
    # Split into upper and lower profiles
    upper_lines = data_lines[start_idx:separator_idx]
    # Find the start of lower profile data (skip empty lines)
    lower_start = separator_idx + 1
    while lower_start < len(data_lines) and not data_lines[lower_start].strip():
        lower_start += 1
    lower_lines = data_lines[lower_start:]
    # Parse coordinates for each profile
    upper_coords = parse_coordinates(upper_lines, scale)
    lower_coords = parse_coordinates(lower_lines, scale)
    # Convert to CSV
    upper_csv = coordinates_to_csv(upper_coords, include_header=include_header)
    lower_csv = coordinates_to_csv(lower_coords, include_header=include_header)
    return upper_csv, lower_csv


def write_data_to_csv(output_file: Path, data_source: str) -> None:
    """Save to csv file."""
    with Path.open(output_file, "w", newline="") as f:
        f.write(data_source)
    line_count = data_source.count("\n")
    logger.info(f"CSV data written to {output_file} with {line_count} lines.")


def get_request(url: str) -> str:
    """Fetch airfoil data from URL and process it."""
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def args():
    """Arg Parser"""
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-u", "--url", default="https://m-selig.ae.illinois.edu/ads/coord/n0012.dat"
    )
    parser.add_argument("-f", "--filename", help="Output filename base.")
    parser.add_argument("-H", "--header", help="Output Header first", default=False)
    parser.add_argument("-e", "--ext", help="Output file extension", default="sldcrv")
    parser.add_argument("-l", "--loglevel", default="DEBUG", choices=logging.getLevelNamesMapping())
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel)
    return args


def write_airfoil_to_csv_files():
    """Parse airfoil data and write upper and lower profiles to separate CSV files."""
    args_ = args()
    # Parse args
    url = args_.url
    url_parsed = urlparse(url)
    # Set file paths
    file_root = Path(url_parsed.path).stem
    if args_.filename is not None:
        file_root = args_.filename
    upper_file = Path(f"{file_root}_upper.{args_.ext}")
    lower_file = Path(f"{file_root}_lower.{args_.ext}")
    # Do processing
    result = get_request(url)
    upper_csv, lower_csv = convert_airfoil_data_to_csv(
        result,
        scale=100,
        include_header=args_.header,
    )
    write_data_to_csv(upper_file, upper_csv)
    write_data_to_csv(lower_file, lower_csv)


if __name__ == "__main__":
    write_airfoil_to_csv_files()
