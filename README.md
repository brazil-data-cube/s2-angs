# Sentinel-2 Angle Bands

Generate Sentinel-2 Resampled Angle bands (Solar Azimuth, Solar Zenith, Sensor Azimuth, Sensor Zenith).

This script resamples, through bilinear function, the angle bands (Solar Azimuth, Solar Zenith, View Azimuth and View Zenith) provided inside a Sentinel-2 .SAFE MTD_TL.xml, which are originally provided as a 23x23 grid (5000 m resolution) to a 10 m spatial resolution.


## Dependencies

- Numpy
- GDAL

## Usage

Considering S2A_MSIL1C_20190105T132231_N0207_R038_T23LLF_20190105T145859 Sentinel-2 you can run through

### run using .zip
```
python3 sentinel2_angle_bands.py S2A_MSIL1C_20190105T132231_N0207_R038_T23LLF_20190105T145859.zip
```
this will create a ANG_DATA on the current working directory containing the resampled bands.

### run using .SAFE
```
python3 sentinel2_angle_bands.py S2A_MSIL1C_20190105T132231_N0207_R038_T23LLF_20190105T145859.SAFE
```
this will create a ANG_DATA inside the GRANULE folder of the SAFE.

### run using .MTD_TL.xml
```
python3 sentinel2_angle_bands.py S2A_MSIL1C_20190105T132231_N0207_R038_T23LLF_20190105T145859.SAFE/GRANULE/L1C_T23LLF_A018482_20190105T132228/MTD_TL.xml
```
this will create a ANG_DATA inside the GRANULE folder of the SAFE.


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

View_zenith_azimuth_resample

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_zenith_azimuth_resample.png">

View_zenith_resample

<img width="300" height="300" src="https://github.com/marujore/sentinel_angle_bands/blob/master/doc/imgs/View_zenith_resample.png">

