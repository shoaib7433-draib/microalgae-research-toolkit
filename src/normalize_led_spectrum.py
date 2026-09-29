#!/usr/bin/env python3
"""Normalise raw LED spectrometer counts to relative intensity.

Expected CSV columns:
    wavelength_nm, raw_counts

The workflow matches the thesis reporting method: no dark-spectrum subtraction
or absolute irradiance calibration is applied. The output describes spectral
shape only.
"""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

import matplotlib.pyplot as plt


def read_spectrum(path: Path) -> list[tuple[float, float]]:
    """Read and validate wavelength/count pairs from a CSV file."""
    points: list[tuple[float, float]] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"wavelength_nm", "raw_counts"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                "Input CSV must contain the columns wavelength_nm and raw_counts."
            )

        for row_number, row in enumerate(reader, start=2):
            try:
                wavelength = float(row["wavelength_nm"])
                counts = float(row["raw_counts"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on CSV row {row_number}.") from exc

            if counts < 0:
                raise ValueError(f"raw_counts cannot be negative (row {row_number}).")

            points.append((wavelength, counts))

    if not points:
        raise ValueError("The input CSV does not contain any spectrum rows.")

    return sorted(points, key=lambda item: item[0])


def normalise(points: list[tuple[float, float]]) -> list[tuple[float, float, float]]:
    """Return wavelength, raw counts and normalised relative intensity."""
    maximum = max(counts for _, counts in points)
    if maximum <= 0:
        raise ValueError("At least one raw_counts value must be greater than zero.")

    return [
        (wavelength, counts, (counts / maximum) * 100.0)
        for wavelength, counts in points
    ]


def write_csv(rows: list[tuple[float, float, float]], path: Path) -> None:
    """Write normalised spectrum data."""
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["wavelength_nm", "raw_counts", "relative_intensity_percent"])
        for wavelength, counts, relative in rows:
            writer.writerow([f"{wavelength:.3f}", f"{counts:.3f}", f"{relative:.4f}"])


def write_plot(rows: list[tuple[float, float, float]], path: Path) -> None:
    """Create a clean spectral-shape plot."""
    wavelengths = [row[0] for row in rows]
    relative = [row[2] for row in rows]
    peak_index = max(range(len(rows)), key=lambda index: rows[index][2])
    peak_wavelength = wavelengths[peak_index]

    fig, axis = plt.subplots(figsize=(9, 5.2), constrained_layout=True)
    axis.plot(wavelengths, relative, color="#0b6b64", linewidth=2.2)
    axis.fill_between(wavelengths, relative, color="#55d8c1", alpha=0.18)
    axis.scatter([peak_wavelength], [100], color="#173a5e", zorder=3)
    axis.annotate(
        f"Maximum response: {peak_wavelength:.1f} nm",
        xy=(peak_wavelength, 100),
        xytext=(12, -28),
        textcoords="offset points",
        arrowprops={"arrowstyle": "->", "color": "#173a5e"},
    )
    axis.set_xlabel("Wavelength (nm)")
    axis.set_ylabel("Relative intensity (%)")
    axis.set_title("Normalised LED emission spectrum")
    axis.set_ylim(0, 105)
    axis.grid(alpha=0.22)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Normalise raw LED detector counts to relative intensity."
    )
    parser.add_argument("input_csv", type=Path, help="CSV with wavelength_nm and raw_counts")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/led"),
        help="Directory for the CSV and PNG outputs",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    rows = normalise(read_spectrum(args.input_csv))
    csv_path = args.output_dir / "normalized_spectrum.csv"
    plot_path = args.output_dir / "normalized_spectrum.png"

    write_csv(rows, csv_path)
    write_plot(rows, plot_path)

    print(f"Saved {csv_path}")
    print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()
