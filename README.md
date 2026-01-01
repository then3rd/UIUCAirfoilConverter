# Airfoil Data Converter

A Python utility for converting Selig format airfoil coordinate data from online databases into CSV format suitable for CAD software, and tools for visualizing and analyzing the resulting curves.

## Features

- **Download & Convert**: Fetch airfoil data from the UIUC Airfoil Coordinates Database and convert to CSV
- **Dual Profile Output**: Automatically splits airfoil data into separate upper and lower surface files
- **CAD-Ready Format**: Outputs in `.sldcrv` format (or custom formats) for direct import into SolidWorks or other software
- **Precise Scaling**: Uses Decimal arithmetic for accurate coordinate scaling
- **Curve Visualization**: Analyze and visualize 3D curves with self-intersection detection

## Installation

### Prerequisites

- Python 3.7+
- pip package manager

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd airfoil-converter
```

2. Install dependencies:
```bash
make install
```

## Usage

### Basic Airfoil Conversion

Activate venv
```bash
source .venv/bin/activate
```

Download and convert a NACA 0012 airfoil (default):

```bash
python airfoil_converter.py
```

This creates two files:
- `n0012_upper.sldcrv` - Upper surface coordinates
- `n0012_lower.sldcrv` - Lower surface coordinates

### Custom Airfoil from URL

Convert a different airfoil by specifying the URL:

```bash
python airfoil_converter.py -u https://m-selig.ae.illinois.edu/ads/coord/eh1590.dat
```

### Command Line Options

```bash
python airfoil_converter.py [OPTIONS]
```

**Options:**

- `-u, --url URL` - URL to airfoil data file (default: NACA 0012)
- `-f, --filename NAME` - Output filename base (default: extracted from URL)
- `-H, --header` - Include CSV header row (default: False)
- `-e, --ext EXT` - Output file extension (default: sldcrv)
- `-l, --loglevel LEVEL` - Logging level: DEBUG, INFO, WARNING, ERROR (default: DEBUG)

### Examples

#### Example 1: Convert NACA 2412 with custom output name

```bash
python airfoil_converter.py \
  -u https://m-selig.ae.illinois.edu/ads/coord/naca2412.dat \
  -f my_airfoil \
  -e csv
```

Output: `my_airfoil_upper.csv`, `my_airfoil_lower.csv`

#### Example 2: Convert with CSV headers

```bash
python airfoil_converter.py -H True -e csv
```

#### Example 3: Quiet mode (only errors)

```bash
python airfoil_converter.py -l ERROR
```

### Visualizing Curves

Analyze and visualize 3D curves with self-intersection detection:
```bash
python airfol_display.py
```

**Note:** Edit the `file_path` variable in `airfol_display.py` to analyze different files.

## Output Format

The converter outputs coordinates in the following format:

```csv
X,Y,Z
0.0,0.0,0.0
0.0,0.42603,0.05839
0.0,1.3419,99.94161
0.0,1.26,100.0
```

Where:
- **X**: Always 0.0 (for 2D airfoil profiles)
- **Y**: Scaled y-coordinate (height)
- **Z**: Scaled x-coordinate (chord position)
- **Scale**: Coordinates are scaled by 100 (1.0 chord → 100 units)

## Airfoil Data Sources

This tool works with airfoil data from the [UIUC Airfoil Coordinates Database](https://m-selig.ae.illinois.edu/ads/coord_database.html).

Popular airfoils:
- NACA 0012: `https://m-selig.ae.illinois.edu/ads/coord/n0012.dat`
- NACA 2412: `https://m-selig.ae.illinois.edu/ads/coord/naca2412.dat`
- NACA 4412: `https://m-selig.ae.illinois.edu/ads/coord/naca4412.dat`
- Clark Y: `https://m-selig.ae.illinois.edu/ads/coord/clarky.dat`

## Importing into SolidWorks
1. Run the converter to generate `.sldcrv` files
2. In SolidWorks, create a new sketch
3. Go to **Insert → Curve → Curve Through XYZ Points**
4. Browse and select the generated `.sldcrv` file
5. Repeat for both upper and lower surfaces
6. Use the curves to create a loft or surface

## Troubleshooting

### "No separator found between upper and lower profiles"

This warning indicates the input data format is unexpected. Ensure the URL points to a valid airfoil data file in the standard format.

### Import Issues in CAD Software

If coordinates don't import correctly:
- Try adding headers: `-H True`
- Change file extension: `-e csv` or `-e txt`
- Check the scale factor in the code (default: 100)

## License

MIT License - See LICENSE file for details

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Author

Kelie Bailey
