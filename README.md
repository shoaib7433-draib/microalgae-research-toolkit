# Microalgae Research Toolkit

Small, transparent Python utilities supporting photobioreactor and microalgae research workflows.

This repository accompanies Shoaib Akhtar's Medical Engineering research portfolio. It currently includes:

1. **LED spectrum normalisation** — converts raw detector counts to relative intensity from 0 to 100 percent and exports a publication ready plot.
2. **Recovered wet biomass summary** — calculates wet pellet mass per litre, groups observations by strain and exports a clearly labelled comparison plot.

## Important scientific note

Recovered wet pellet mass is not equivalent to dry biomass concentration or biomass productivity. The script preserves this distinction in its labels and output.

## Repository structure

```text
microalgae-research-toolkit/
├── data/
│   ├── README.md
│   └── wet_biomass_example.csv
├── src/
│   ├── normalize_led_spectrum.py
│   └── summarize_wet_biomass.py
├── .gitignore
├── LICENSE
├── README.md
└── requirements.txt
```

## Installation

```bash
python -m venv .venv
```

Activate the environment and install the plotting dependency:

```bash
pip install -r requirements.txt
```

## Normalise an LED spectrum

Prepare a CSV containing the columns `wavelength_nm` and `raw_counts`, then run:

```bash
python src/normalize_led_spectrum.py data/led_spectrum.csv --output-dir results/led
```

The script creates:

- `normalized_spectrum.csv`
- `normalized_spectrum.png`

The implemented method divides every raw detector value by the maximum observed value and multiplies by 100. It does not apply dark spectrum subtraction or absolute irradiance calibration.

## Summarise recovered wet biomass

Prepare a CSV containing `strain`, `culture_volume_ml` and `wet_pellet_mass_g`, then run:

```bash
python src/summarize_wet_biomass.py data/wet_biomass_example.csv --output-dir results/biomass
```

The script creates:

- `wet_biomass_summary.csv`
- `wet_biomass_comparison.png`

## Research context

The original thesis compared *Chlorella vulgaris* TISTR 8580 and *Chlorella sorokiniana* TISTR 8260 cultivated separately in BG 11 medium under comparable laboratory conditions. LED spectral acquisition used an Ocean Optics USB4000 spectrometer at the cultivation plane.

## Author

**Shoaib Akhtar**  
Medical Engineering researcher, Asian Institute of Technology  
[GitHub profile](https://github.com/shoaib7433-draib) · [LinkedIn](https://www.linkedin.com/in/shoaib-akhtar-919a373aa/)

## Licence

MIT License. See `LICENSE`.
