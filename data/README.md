# Data format

## LED spectrum CSV

Required columns:

```csv
wavelength_nm,raw_counts
350,0
351,0
```

Use the original detector export where possible. The normalisation script does not perform dark spectrum subtraction or convert counts into absolute irradiance.

## Wet biomass CSV

Required columns:

```csv
strain,culture_volume_ml,wet_pellet_mass_g
Chlorella vulgaris TISTR 8580,400,1.05
Chlorella sorokiniana TISTR 8260,400,0.60
```

The example values are recovered wet pellet masses from the thesis experiment. They must not be reported as dry biomass or biomass productivity.
