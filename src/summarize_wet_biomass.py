#!/usr/bin/env python3
"""Summarise recovered wet pellet mass by microalgal strain.

Expected CSV columns:
    strain, culture_volume_ml, wet_pellet_mass_g

This script intentionally avoids labelling wet pellet mass as dry biomass or
biomass productivity.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib.pyplot as plt


Observation = tuple[str, float, float, float]


def read_observations(path: Path) -> list[Observation]:
    observations: list[Observation] = []

    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"strain", "culture_volume_ml", "wet_pellet_mass_g"}
        if reader.fieldnames is None or not required.issubset(reader.fieldnames):
            raise ValueError(
                "Input CSV must contain strain, culture_volume_ml and wet_pellet_mass_g."
            )

        for row_number, row in enumerate(reader, start=2):
            strain = (row.get("strain") or "").strip()
            if not strain:
                raise ValueError(f"Missing strain name on CSV row {row_number}.")

            try:
                volume_ml = float(row["culture_volume_ml"])
                wet_mass_g = float(row["wet_pellet_mass_g"])
            except (TypeError, ValueError) as exc:
                raise ValueError(f"Invalid numeric value on CSV row {row_number}.") from exc

            if volume_ml <= 0 or wet_mass_g < 0:
                raise ValueError(
                    f"Volume must be positive and wet mass nonnegative (row {row_number})."
                )

            wet_mass_g_per_l = wet_mass_g / (volume_ml / 1000.0)
            observations.append((strain, volume_ml, wet_mass_g, wet_mass_g_per_l))

    if not observations:
        raise ValueError("The input CSV does not contain any observations.")

    return observations


def summarise(observations: list[Observation]) -> list[dict[str, float | int | str]]:
    grouped: dict[str, list[Observation]] = defaultdict(list)
    for observation in observations:
        grouped[observation[0]].append(observation)

    summary: list[dict[str, float | int | str]] = []
    for strain in sorted(grouped):
        rows = grouped[strain]
        wet_masses = [row[2] for row in rows]
        mass_per_litre = [row[3] for row in rows]
        summary.append(
            {
                "strain": strain,
                "n": len(rows),
                "mean_wet_pellet_mass_g": mean(wet_masses),
                "sd_wet_pellet_mass_g": stdev(wet_masses) if len(rows) > 1 else 0.0,
                "mean_wet_pellet_mass_g_per_l": mean(mass_per_litre),
            }
        )
    return summary


def write_csv(summary: list[dict[str, float | int | str]], path: Path) -> None:
    fields = [
        "strain",
        "n",
        "mean_wet_pellet_mass_g",
        "sd_wet_pellet_mass_g",
        "mean_wet_pellet_mass_g_per_l",
    ]
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in summary:
            writer.writerow(
                {
                    "strain": row["strain"],
                    "n": row["n"],
                    "mean_wet_pellet_mass_g": f"{float(row['mean_wet_pellet_mass_g']):.4f}",
                    "sd_wet_pellet_mass_g": f"{float(row['sd_wet_pellet_mass_g']):.4f}",
                    "mean_wet_pellet_mass_g_per_l": (
                        f"{float(row['mean_wet_pellet_mass_g_per_l']):.4f}"
                    ),
                }
            )


def write_plot(summary: list[dict[str, float | int | str]], path: Path) -> None:
    strains = [str(row["strain"]) for row in summary]
    means = [float(row["mean_wet_pellet_mass_g"]) for row in summary]
    errors = [float(row["sd_wet_pellet_mass_g"]) for row in summary]

    fig, axis = plt.subplots(figsize=(8, 5.2), constrained_layout=True)
    bars = axis.bar(
        strains,
        means,
        yerr=errors if any(errors) else None,
        capsize=5,
        color=["#0b6b64", "#55a8a0", "#7ac9a3", "#173a5e"][: len(strains)],
    )
    axis.bar_label(bars, labels=[f"{value:.2f} g" for value in means], padding=4)
    axis.set_ylabel("Mean recovered wet pellet mass (g)")
    axis.set_title("Recovered wet pellet mass by strain")
    axis.grid(axis="y", alpha=0.2)
    axis.set_axisbelow(True)
    upper = max(means) * 1.25 if max(means) > 0 else 1.0
    axis.set_ylim(0, upper)
    fig.savefig(path, dpi=220)
    plt.close(fig)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Summarise recovered wet pellet mass by microalgal strain."
    )
    parser.add_argument("input_csv", type=Path, help="CSV containing wet pellet observations")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("results/biomass"),
        help="Directory for the CSV and PNG outputs",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    summary = summarise(read_observations(args.input_csv))
    csv_path = args.output_dir / "wet_biomass_summary.csv"
    plot_path = args.output_dir / "wet_biomass_comparison.png"

    write_csv(summary, csv_path)
    write_plot(summary, plot_path)

    print(f"Saved {csv_path}")
    print(f"Saved {plot_path}")


if __name__ == "__main__":
    main()
