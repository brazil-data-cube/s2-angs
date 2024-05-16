#
# This file is part of Brazil Data Cube Sentinel-2 Angle Bands.
# Copyright (C) 2022 INPE.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/gpl-3.0.html>.
#

# Python Native
import glob
import logging
import logging.config
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from zipfile import ZipFile

# 3rdparty
import affine
import numpy
import rasterio
from rasterio.io import MemoryFile
from skimage.transform import resize

from .s2_sensor_angs.s2_sensor_angs import s2_sensor_angs


################################################################################
## Generate Sentinel Angle view bands
################################################################################

def logging_configs():
    """Logging Configurations."""
    # create logger
    global logger
    logger = logging.getLogger(__name__) # or pass an explicit name here, e.g. "mylogger"
    logger.setLevel(logging.INFO)

    # create console handler and set level to debug
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    # create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # add formatter to ch
    ch.setFormatter(formatter)

    # add ch to logger
    logger.addHandler(ch)


def extract_tileid(mtdmsi):
    """Get tile id from MTD_MSI.xml file.
    Parameters:
       mtdmsi (str): path to MTD_MSI.xml.
    Returns:
       str: .SAFE tile id.
    """
    tile_id = ""
    # Parse the XML file
    tree = ET.parse(mtdmsi)
    root = tree.getroot()

    # Find the angles
    for child in root:
        if child.tag[-12:] == 'General_Info':
            geninfo = child

    i=-1
    j=-1
    for segment in geninfo:
        i=i+1
        if segment.tag == 'Product_Info':
            for seg in geninfo[i]:
                j=j+1
                if seg.tag == 'PRODUCT_URI':
                    tile_id = geninfo[i][j].text.strip()

    return(tile_id.replace(".SAFE",""))


def extract_sun_angles(xml):
    """Extract Sentinel-2 solar angle bands values from MTD_TL.xml.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str, str: sz_path, sa_path: path to solar zenith image, path to solar azimuth image, respectively.
    """
    solar_zenith_values = numpy.empty((23,23,)) * numpy.nan #initiates matrix
    solar_azimuth_values = numpy.empty((23,23,)) * numpy.nan

    # Parse the XML file
    tree = ET.parse(xml)
    root = tree.getroot()

    # Find the angles
    for child in root:
        if child.tag[-14:] == 'Geometric_Info':
            geoinfo = child

    for segment in geoinfo:
        if segment.tag == 'Tile_Angles':
            angles = segment

    for angle in angles:
        if angle.tag == 'Sun_Angles_Grid':
            for bset in angle:
                if bset.tag == 'Zenith':
                    zenith = bset
                if bset.tag == 'Azimuth':
                    azimuth = bset
            for field in zenith:
                if field.tag == 'Values_List':
                    zvallist = field
            for field in azimuth:
                if field.tag == 'Values_List':
                    avallist = field
            for rindex in range(len(zvallist)):
                zvalrow = zvallist[rindex]
                avalrow = avallist[rindex]
                zvalues = zvalrow.text.split(' ')
                avalues = avalrow.text.split(' ')
                values = list(zip(zvalues, avalues)) #row of values
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN'):
                        zen = float(values[cindex][0])
                        az = float(values[cindex][1])
                        solar_zenith_values[rindex,cindex] = zen
                        solar_azimuth_values[rindex,cindex] = az
    solar_zenith_values = resize(solar_zenith_values,(22,22))
    solar_azimuth_values = resize(solar_azimuth_values,(22,22))
    return (solar_zenith_values, solar_azimuth_values)


def extract_sensor_angles(xml):
    """Extract Sentinel-2 view (sensor) angle bands values from MTD_TL.xml.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str, str: path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    numband = 13
    sensor_zenith_values = numpy.empty((numband,23,23)) * numpy.nan #initiates matrix
    sensor_azimuth_values = numpy.empty((numband,23,23)) * numpy.nan

    # Parse the XML file
    tree = ET.parse(xml)
    root = tree.getroot()

    # Find the angles
    for child in root:
        if child.tag[-14:] == 'Geometric_Info':
            geoinfo = child

    for segment in geoinfo:
        if segment.tag == 'Tile_Angles':
            angles = segment

    for angle in angles:
        if angle.tag == 'Viewing_Incidence_Angles_Grids':
            bandId = int(angle.attrib['bandId'])
            for bset in angle:
                if bset.tag == 'Zenith':
                    zenith = bset
                if bset.tag == 'Azimuth':
                    azimuth = bset
            for field in zenith:
                if field.tag == 'Values_List':
                    zvallist = field
            for field in azimuth:
                if field.tag == 'Values_List':
                    avallist = field
            for rindex in range(len(zvallist)):
                zvalrow = zvallist[rindex]
                avalrow = avallist[rindex]
                zvalues = zvalrow.text.split(' ')
                avalues = avalrow.text.split(' ')
                values = list(zip(zvalues, avalues )) #row of values
                for cindex in range(len(values)):
                    if (values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN'):
                        zen = float(values[cindex][0])
                        az = float(values[cindex][1])
                        sensor_zenith_values[bandId, rindex,cindex] = zen
                        sensor_azimuth_values[bandId, rindex,cindex] = az
    # In the next two lines, 7 is adopted as bandId since for our application we opted to not generate the angle bands for each of the spectral bands. Here we adopted bandId 7 due to its use in vegetation applications
    # Also on the next two lines, we are using 22x22 matrices since the angle bands pixels represent 5000 meters. Sentinel-2 images area 109800x109800 meters. The 23x23 5000m matrix is equivalent to 11500x11500m. Based on that we opted to not use the last column and row. More information can be found on STEP ESA forum: https://forum.step.esa.int/t/generate-view-angles-from-metadata-sentinel-2/5598
    sensor_zenith_values = resize(sensor_zenith_values[7],(22,22))
    sensor_azimuth_values = resize(sensor_azimuth_values[7],(22,22))
    return(sensor_zenith_values, sensor_azimuth_values)


def write_raster(array, file_name, profile):
    """Writes intermediary angle bands (not resampled, as 23x23 5000m spatial resolution).
    Parameters:
       array (array): angle values array.
       file_name (str): output raster file name.
       profile (dict): rasterio profile.
    """
    new_dataset = rasterio.open(
        file_name,
        'w',
        driver='GTiff',
        height=profile['height'],
        width=profile['width'],
        count=profile['count'],
        dtype=profile['dtype'],
        crs=profile['crs'],
        transform=profile['transform'],
        nodata=profile['nodata'],
        compress='deflate'
    )
    new_dataset.write(array, 1)
    new_dataset.close()

    return


def generate_anglebands(mtd):
    """Generate angle bands.
    Parameters:
       mtd (str): path to MTD_TL.xml.
    """
    path = os.path.split(mtd)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    # Use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04*.jp2", recursive=True)]
    # Checks for empty list (No file)
    try:
        imgref.sort()
        imgref=imgref[0]
    except IndexError:
        raise IndexError(f"Missing band B04 .jp2 file on {imgFolder}")

    src_dataset = rasterio.open(imgref)

    profile = src_dataset.profile
    profile.update(nodata=-9999)

    scenename = extract_tileid(mtd)
    solar_zenith, solar_azimuth = extract_sun_angles(mtd)
    sensor_zenith, sensor_azimuth = extract_sensor_angles(mtd)

    write_raster(solar_zenith, (angFolder + scenename + "solar_zenith"), profile)
    write_raster(solar_azimuth, (angFolder + scenename + "solar_azimuth"), profile)
    write_raster(sensor_zenith, (angFolder + scenename + "sensor_zenith"), profile)
    write_raster(sensor_azimuth, (angFolder + scenename + "sensor_azimuth"), profile)

    del src_dataset

    return


def resample_anglebands(array, imgref, filename_out, filename_intermed=None):
    """Resample angle bands.
    Parameters:
       array (arr): matrix of angle values.
       imgref (str): path to image that will be used as reference.
       filename_out (str): filename of the resampled angle band.
       filename_intermed (str): filename of the intermediary angle bands (not resampled).
    """
    src_dataset = rasterio.open(imgref)
    profile = src_dataset.profile

    profile_intermed = profile
    if not profile_intermed['nodata']:
        profile_intermed['nodata'] = -9999
    profile_intermed.update(width=array.shape[1], height=array.shape[0])
    intermed_aff = profile['transform']
    intermed_aff = affine.Affine(5000, intermed_aff.b, intermed_aff.c, intermed_aff.d, -5000, intermed_aff.f)

    memfile = MemoryFile()
    intermed_dataset = memfile.open(#rasterio.open(
        driver='GTiff',
        height=profile_intermed['height'],
        width=profile_intermed['width'],
        count=profile_intermed['count'],
        dtype=numpy.float64,
        crs=profile_intermed['crs'],
        transform=intermed_aff,
        nodata=profile_intermed['nodata']
    )

    #TODO if filename_intermed write angle bands not resampled (23x23)
    # intermed_dataset = rasterio.open(
    #     filename_intermed,
    #     'w',
    #     driver='GTiff',
    #     height=profile_intermed['height'],
    #     width=profile_intermed['width'],
    #     count=profile_intermed['count'],
    #     dtype=numpy.float64,
    #     crs=profile_intermed['crs'],
    #     transform=intermed_aff,
    #     nodata=profile_intermed['nodata']
    # )
    # intermed_dataset.write(array, 1)
    # intermed_dataset.close()

    old_res = [intermed_aff.a, intermed_aff.e]
    new_res = (profile['transform'][0], profile['transform'][4])

    # setup the transform to change the resolution
    ref_shp = rasterio.open(imgref).read().shape
    resampled_array = numpy.empty(shape=(ref_shp[1], ref_shp[2]))

    resampled_array = resize(array,(11000,11000))
    resampled_array = resampled_array[:ref_shp[1],:ref_shp[2]]*100
    resampled_array[numpy.isnan(resampled_array)] = profile_intermed['nodata']
    resampled_array = resampled_array.astype(numpy.intc)

    # write results to file
    resampled_dataset = rasterio.open(
        filename_out,
        'w',
        driver=intermed_dataset.driver,
        height=ref_shp[1],
        width=ref_shp[2],
        count=intermed_dataset.count,
        dtype=numpy.intc,#str(resampled_array.dtype),
        crs=intermed_dataset.crs,
        transform=profile['transform'],
        nodata=intermed_dataset.nodata,
        compress='deflate'
    )
    resampled_dataset.write(resampled_array, 1)
    resampled_dataset.close()

    return


def generate_resampled_anglebands(mtdmsi, mtd, imgFolder, angFolder):
    """Generates angle bands resampled to 10 meters.
    Parameters:
       mtdmsi (str): path to MTD_TL.xml.
       mtd (str): path to MTD_TL.xml.
       imgFolder (str): path to IMG_DATA folder.
       angFolder (str): output path to angle bands.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    logging.debug('Generating resampled anglebands')
    os.makedirs(angFolder, exist_ok=True)

    if not imgFolder.endswith('/'):
        imgFolder = imgFolder + '/'

    # Use band 4 as reference due to 10m spatial resolution
    safe_jp2 = [f for f in glob.glob(imgFolder + "**/*B04*.jp2", recursive=True)]
    safe_tif = [f for f in glob.glob(imgFolder + "**/*B04*.tif", recursive=True)]
    folder_tif = [f for f in glob.glob(imgFolder + "**/*band4*.tif", recursive=True)]
    imgref_list = safe_jp2 + safe_tif + folder_tif
    # Checks for empty list (No file)
    try:
        imgref_list.sort()
        imgref = imgref_list[0]
    except IndexError:
        raise IndexError(f"Missing reference band (4, red) file on {imgFolder}")

    scenename = extract_tileid(mtdmsi)

    sz_path = os.path.join(angFolder, scenename + '_SZAr.tif')
    sa_path = os.path.join(angFolder, scenename + '_SAAr.tif')
    vz_path = os.path.join(angFolder, scenename + '_VZAr.tif')
    va_path = os.path.join(angFolder, scenename + '_VAAr.tif')

    solar_zenith, solar_azimuth = extract_sun_angles(mtd)
    va_path, vz_path = s2_sensor_angs(mtd, imgref, va_path, vz_path)

    resample_anglebands(solar_zenith, imgref, sz_path)
    resample_anglebands(solar_azimuth, imgref, sa_path)

    return sz_path, sa_path, vz_path, va_path


def xmls_from_safe(SAFEfile):
    """Obtain the MTD_TL.xml path of a .SAFE folder.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
    Returns:
       str: path to MTD_TL.xml.
    """
    print(SAFEfile)
    mtdmsi = [f for f in glob.glob(os.path.join(SAFEfile, "MTD_MSIL*.xml"), recursive=True)][0]
    mtd = os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile, 'GRANULE/'))[0], 'MTD_TL.xml'))

    return mtdmsi, mtd


def gen_s2_ang_from_SAFE(SAFEfile, output_dir=None):
    """Generate Sentinel 2 angles using .SAFE.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
       output_dir (str) (optional): path to output folder.
    Returns:
       sz_path, sa_path, vz_path, va_path: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    logging.debug('Using .SAFE approach')
    mtdmsi, mtd = xmls_from_safe(SAFEfile)

    path = os.path.split(mtd)[0]
    imgFolder = os.path.join(path, "IMG_DATA")
    angFolder = os.path.join(path, "ANG_DATA")
    if output_dir is not None:
        angFolder = output_dir

    ### Generates resampled anglebands (to 10m)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(mtdmsi, mtd, imgFolder, angFolder)
    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_zip(zipfile, output_dir=None):
    """Generate Sentinel 2 angles using a zipped .SAFE.
    Parameters:
       zipfile (str): path to zipfile.
       output_dir (str) (optional): path to output folder.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    logging.debug('Using .zip approach')

    with ZipFile(zipfile) as zipObj:
        zipfoldername = zipObj.namelist()[0][:-1]
    work_dir = os.getcwd()
    if output_dir is not None:
        work_dir = output_dir
    os.makedirs('s2_ang_tmp', exist_ok=True)
    s2_ang_tmp = os.path.join(os.getcwd(), 's2_ang_tmp')
    temp_SAFE = os.path.join(s2_ang_tmp, zipfoldername)
    shutil.unpack_archive(zipfile, temp_SAFE, 'zip')
    SAFEfile = os.path.join(temp_SAFE, zipfoldername)
    mtdmsi, mtd = xmls_from_safe(SAFEfile)
    path = os.path.split(mtd)[0]
    imgFolder = os.path.join(path, "IMG_DATA")
    angFolder = os.path.join(path, "ANG_DATA")

    ### Generates resampled anglebands (to 10m)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(mtdmsi, mtd, imgFolder, angFolder)
    ang_dir = os.path.join(SAFEfile,'GRANULE', os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'ANG_DATA')

    new_sz_path = os.path.join(work_dir, Path(sz_path).name)
    new_sa_path = os.path.join(work_dir, Path(sa_path).name)
    new_vz_path = os.path.join(work_dir, Path(vz_path).name)
    new_va_path = os.path.join(work_dir, Path(va_path).name)

    shutil.move(sz_path, new_sz_path)
    shutil.move(sa_path, new_sa_path)
    shutil.move(vz_path, new_vz_path)
    shutil.move(va_path, new_va_path)
    shutil.rmtree(temp_SAFE)
    Path(s2_ang_tmp).rmdir()

    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_folder(folder, output_dir=None):
    """Generate Sentinel 2 angles using all files in a single folder.
    Parameters:
       folder (str): path to Sentinel-2 folder.
       output_dir (str) (optional): path to output folder.
    Returns:
       sz_path, sa_path, vz_path, va_path: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    logging.debug('Using Folder approach')

    mtdmsi = [f for f in glob.glob(os.path.join(folder,"MTD_MSIL*.xml"), recursive=True)][0]
    mtd = os.path.join(folder, 'MTD_TL.xml')

    ### Generates resampled anglebands (to 10m)
    ang_folder = os.path.join(folder, 'ANG_DATA')
    if output_dir is not None:
        angFolder = output_dir

    os.makedirs(ang_folder, exist_ok=True)

    if not folder.endswith('/'):
        imgFolder = folder + '/'

    safe_jp2 = [f for f in glob.glob(imgFolder + "**/*B04*.jp2", recursive=True)]
    safe_tif = [f for f in glob.glob(imgFolder + "**/*B04*.tif", recursive=True)]
    folder_tif = [f for f in glob.glob(imgFolder + "**/*band4*.tif", recursive=True)]
    imgref_list = safe_jp2 + safe_tif + folder_tif
    imgref_list.sort()

    imgref = imgref_list[0]

    scenename = extract_tileid(mtdmsi)

    sz_path = os.path.join(ang_folder, scenename + '_SZAr.tif')
    sa_path = os.path.join(ang_folder, scenename + '_SAAr.tif')
    vz_path = os.path.join(ang_folder, scenename + '_VZAr.tif')
    va_path = os.path.join(ang_folder, scenename + '_VAAr.tif')

    solar_zenith, solar_azimuth = extract_sun_angles(mtd)
    view_zenith, view_azimuth = extract_sensor_angles(mtd)

    resample_anglebands(solar_zenith, imgref, sz_path)
    resample_anglebands(solar_azimuth, imgref, sa_path)
    resample_anglebands(view_zenith, imgref, vz_path)
    resample_anglebands(view_azimuth, imgref, va_path)

    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang(path, output_dir=None):
    """Generate Sentinel 2 angle bands.
    Parameters:
       path (str): path to zipfile, .SAFE or folder containing S2 data.
       output_dir (str) (optional): path to output folder.
    Returns:
       sz_path, sa_path, vz_path, va_path: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    logging_configs()
    logger.info(f'Generating angles from {path}')
    if path.endswith('.SAFE'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_SAFE(path, output_dir) #path to SAFE
    elif path.endswith('.zip'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_zip(path, output_dir) #path to .zip
    else:
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_folder(path, output_dir)

    return sz_path, sa_path, vz_path, va_path
