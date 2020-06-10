# Python Native
from zipfile import ZipFile
import glob
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET
# 3rdparty
from osgeo import gdal
import numpy


################################################################################
## Generate Sentinel Angle view bands
################################################################################

def get_tileid(xml):
    """Get tile id from MTD_TL.xml file.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str: .SAFE tile id.
    """
    tile_id = ""
    # Parse the XML file 
    tree = ET.parse(xml)
    root = tree.getroot()

    # Find the angles
    for child in root:
        if child.tag[-12:] == 'General_Info':
            geninfo = child

    for segment in geninfo:
        if segment.tag == 'TILE_ID':
            tile_id = segment.text.strip()

    return(tile_id)


def get_sun_angles(xml):
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
                values = list(zip( zvalues, avalues )) #row of values
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN' ):
                        zen = float(values[cindex][0] )
                        az = float(values[cindex][1] )
                        solar_zenith_values[rindex,cindex] = zen
                        solar_azimuth_values[rindex,cindex] = az
    return (solar_zenith_values, solar_azimuth_values)


def get_sensor_angles(xml):
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
                values = list(zip( zvalues, avalues )) #row of values
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN' ):
                        zen = float( values[cindex][0] )
                        az = float( values[cindex][1] )
                        sensor_zenith_values[bandId, rindex,cindex] = zen
                        sensor_azimuth_values[bandId, rindex,cindex] = az
    return(sensor_zenith_values, sensor_azimuth_values)


def write_intermediary(newRasterfn, rasterOrigin, proj, array):
    """Writes intermediary angle bands (not resampled, as 23x23 5000m spatial resolution).
    Parameters:
       newRasterfn (str): output raster file name.
       rasterOrigin (tuple): gdal geotransform origin tuple (geotrans[0],geotrans[3]).
       proj (str): gdal projection.
       array (array): angle values array.
    """
    cols = array.shape[1]
    rows = array.shape[0]
    originX = rasterOrigin[0]
    originY = rasterOrigin[1]

    driver = gdal.GetDriverByName('GTiff')
    outRaster = driver.Create(newRasterfn, cols, rows, 1, gdal.GDT_Float32)
    outRaster.SetGeoTransform((originX, 5000, 0, originY, 0, -5000))
    outband = outRaster.GetRasterBand(1)
    outband.WriteArray(array)
    outRaster.SetProjection(proj)
    outband.FlushCache()

    return


def generate_anglebands(xml):
    """Generate angle bands.
    Parameters:
       xml (str): path to MTD_TL.xml.
    """
    path = os.path.split(xml)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    #use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04.jp2", recursive=True)][0]

    tmp_ds = gdal.Open(imgref)
    tmp_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    geotrans = tmp_ds.GetGeoTransform()  #get GeoTranform from existed 'data0'
    proj = tmp_ds.GetProjection() #you can get from a exsited tif or import 

    scenename = get_tileid(xml)
    solar_zenith, solar_azimuth = get_sun_angles(xml)
    sensor_zenith, sensor_azimuth = get_sensor_angles(xml)

    rasterOrigin = (geotrans[0],geotrans[3])

    write_intermediary((angFolder + scenename + "solar_zenith"),rasterOrigin, proj, solar_zenith)
    write_intermediary((angFolder + scenename + "solar_azimuth"),rasterOrigin, proj, solar_azimuth)
    for num_band in (range(len(sensor_azimuth))):
        write_intermediary((angFolder + scenename + "sensor_zenith_b" + str(num_band)), rasterOrigin, proj, sensor_zenith[num_band])
        write_intermediary((angFolder + scenename + "sensor_azimuth_b" + str(num_band)), rasterOrigin, proj, sensor_azimuth[num_band])

    del tmp_ds

    return


def resample_anglebands(ang_matrix, imgref, filename):
    """Resample angle bands.
    Parameters:
       ang_matrix (arr): matrix of angle values.
       imgref (str): path to image that will be used as reference.
       filename (str): filename of the resampled angle band.
    """
    src_ds = gdal.Open(imgref)
    src_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    geotrans = src_ds.GetGeoTransform() #get GeoTranform from existed 'data0'
    proj = src_ds.GetProjection() #you can get from a exsited tif or import 

    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize

    rasterOrigin = (geotrans[0],geotrans[3])

    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName('MEM')
    tmp_ds = mem_drv.Create('', len(ang_matrix[0]), len(ang_matrix), 1, gdal.GDT_Float32)

    # Set the geotransform
    tmp_ds.SetGeoTransform((rasterOrigin[0], 5000, 0, rasterOrigin[1], 0, -5000))
    tmp_ds.SetProjection(proj)
    tmp_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    tmp_ds.GetRasterBand(1).WriteArray(ang_matrix)

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform(geotrans)
    dst_ds.SetProjection(proj)

    resampling = gdal.GRA_Bilinear
    gdal.ReprojectImage( tmp_ds, dst_ds, tmp_ds.GetProjection(), dst_ds.GetProjection(), resampling)

    del src_ds
    del tmp_ds
    del dst_ds

    return


def generate_resampled_anglebands(xml):
    """Generates angle bands resampled to 10 meters.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    path = os.path.split(xml)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    #use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04.jp2", recursive=True)][0]

    scenename = get_tileid(xml)
    solar_zenith, solar_azimuth = get_sun_angles(xml)
    sensor_zenith, sensor_azimuth = get_sensor_angles(xml)

    sensor_zenith_mean = sensor_zenith[0]
    sensor_azimuth_mean = sensor_azimuth[0]
    for num_band in (range(1,len(sensor_azimuth))):
        sensor_zenith_mean += sensor_zenith[num_band]
        sensor_azimuth_mean += sensor_azimuth[num_band]
    sensor_zenith_mean /= len(sensor_azimuth)
    sensor_azimuth_mean /= len(sensor_azimuth)

    sz_path = angFolder + scenename + '_solar_zenith_resampled.tif'
    sa_path = angFolder + scenename + '_solar_azimuth_resampled.tif'
    vz_path = angFolder + scenename + '_sensor_zenith_mean_resampled.tif'
    va_path = angFolder + scenename + '_sensor_azimuth_mean_resampled.tif'

    resample_anglebands(solar_zenith, imgref, sz_path)
    resample_anglebands(solar_azimuth, imgref, sa_path)
    resample_anglebands(sensor_zenith_mean, imgref, vz_path)
    resample_anglebands(sensor_azimuth_mean, imgref, va_path)

    return sz_path, sa_path, vz_path, va_path


def xml_from_safe(SAFEfile):
    """Obtain the MTD_TL.xml path of a .SAFE folder.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
    Returns:
       str: path to MTD_TL.xml.
    """
    return os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'MTD_TL.xml'))


def gen_s2_ang_from_SAFE(SAFEfile):
    """Generate Sentinel 2 angles using .SAFE.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
    Returns:
       sz_path, sa_path, vz_path, va_path: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    xml = xml_from_safe(SAFEfile)
    ### generate 23x23 Product (not resampled)
    # generate_anglebands(os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'MTD_TL.xml')))

    ### Generates resampled anglebands (to 10m)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_xml(xml):
    """Generate Sentinel 2 angles using a MTD_TL.xml of .SAFE.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_zip(zipfile):
    """Generate Sentinel 2 angles using a zipped .SAFE.
    Parameters:
       zipfile (str): path to zipfile.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    with ZipFile(zipfile) as zipObj:
        zipfoldername = zipObj.namelist()[0][:-1]
    work_dir = os.getcwd()
    os.makedirs('s2_ang_tmp', exist_ok=True)
    temp_dir = os.path.join(os.getcwd(), 's2_ang_tmp')
    shutil.unpack_archive(zipfile, temp_dir, 'zip')
    SAFEfile = os.path.join(temp_dir, zipfoldername)
    xml = xml_from_safe(SAFEfile)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    ang_dir = os.path.join(SAFEfile,'GRANULE', os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'ANG_DATA')
    shutil.move(ang_dir, work_dir)
    shutil.rmtree(temp_dir)

    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang(path):
    """Generate Sentinel 2 angle bands.
    Parameters:
       zipfile (str): path to zipfile.
    """
    print('Generating angles from {}'.format(path), flush=True)
    if path.find("_MSIL2A_") is not -1:
        print('ERROR: Input uses L1C product, not L2A. Change your input file.', flush=True)
    elif path.endswith('.SAFE'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_SAFE(path) #path to SAFE
    elif path.endswith('MTD_TL.xml'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_xml(path) #path MTD_TL.xml
    elif path.endswith('.zip'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_zip(path) #path to .zip

    return sz_path, sa_path, vz_path, va_path
