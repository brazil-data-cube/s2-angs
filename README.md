# Sentinel-2 Angle Bands

Generate Sentinel-2 Resampled Angle bands (Solar Azimuth, Solar Zenith, View Azimuth, View Zenith).

This script uses Sentinel-2 L1C products as input to generate angle bands (Solar Azimuth, Solar Zenith, View Azimuth and View Zenith). Originally the angles are provided as a 23x23 grid (5000 m resolution) in MTD_TL.xml file (Inside GRANULE folder). This script resample the angles through bilinear function to a 10 m spatial resolution.


## Dependencies

- Numpy
- GDAL

## Installing via Git

```
python3 -m pip install git+https://github.com/marujore/sentinel2_angle_bands
```

or

```
git clone https://github.com/marujore/sentinel2_angle_bands
cd sentinel2_angle_bands
pip install .
```

## Usage

```
import s2_angs

#You can indicate a .zip, a .SAFE or the MTD_TL.xml file
s2_angs.gen_s2_ang('/path/to/my/S2_file/S2B_MSIL1C_20191223T131239_N0208_R138_T23KMR_20191223T135458.zip')
```

## Results
### Intermediary files (matrix 23x23)
Solar_azimuth_23

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/Solar_azimuth_23.png">

Solar_zenith_23

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/Solar_zenith_23.png">

View_azimuth_23

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_azimuth_23.png">

View_zenith_23

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_zenith_23.png">


### Resampled
Solar_azimuth_resampled

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/Solar_azimuth_resampled.png">

Solar_zenith_resample

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/Solar_zenith_resample.png">

View_azimuth_resample

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_zenith_azimuth_resample.png">

View_zenith_resample

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_zenith_resample.png">

## Disclaimer

The script may not work on L2A products, since the MTD_TL.xml file is different from L1C.
