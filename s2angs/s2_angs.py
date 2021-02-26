# Python Native
import glob
import os
import shutil
import xml.etree.ElementTree as ET
from zipfile import ZipFile
# 3rdparty
import affine
import numpy
import rasterio
from rasterio.io import MemoryFile
from skimage.transform import resize

################################################################################
## Generate Sentinel Angle view bands
################################################################################

def extract_tileid(mtdmsi):
    """Get tile id from MTD_TL.xml file.
    Parameters:
       xml (str): path to MTD_TL.xml.
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

    return(tile_id)


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
                values = list(zip( zvalues, avalues )) #row of values
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN' ):
                        zen = float(values[cindex][0] )
                        az = float(values[cindex][1] )
                        solar_zenith_values[rindex,cindex] = zen
                        solar_azimuth_values[rindex,cindex] = az
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
                values = list(zip( zvalues, avalues )) #row of values
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN' ):
                        zen = float( values[cindex][0] )
                        az = float( values[cindex][1] )
                        sensor_zenith_values[bandId, rindex,cindex] = zen
                        sensor_azimuth_values[bandId, rindex,cindex] = az
    return(sensor_zenith_values, sensor_azimuth_values)


def write_raster(array, file_name, profile):
    """Writes intermediary angle bands (not resampled, as 23x23 5000m spatial resolution).
    Parameters:
       newRasterfn (str): output raster file name.
       rasterOrigin (tuple): gdal geotransform origin tuple (geotrans[0],geotrans[3]).
       proj (str): gdal projection.
       array (array): angle values array.
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
        nodata=profile['nodata']
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

    #use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04*.jp2", recursive=True)]
    imgref.sort()
    imgref=imgref[0]

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
       ang_matrix (arr): matrix of angle values.
       imgref (str): path to image that will be used as reference.
       filename (str): filename of the resampled angle band.
    """
    src_dataset = rasterio.open(imgref)
    profile = src_dataset.profile

    profile_intermed = profile
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

    resampled_array = resize(array,(11500,11500))
    resampled_array = resampled_array[:ref_shp[1],:ref_shp[2]]

    # write results to file
    resampled_dataset = rasterio.open(
        filename_out,
        'w',
        driver=intermed_dataset.driver,
        height=ref_shp[1],
        width=ref_shp[2],
        count=intermed_dataset.count,
        dtype=str(resampled_array.dtype),
        crs=intermed_dataset.crs,
        transform=profile['transform'],
        nodata=intermed_dataset.nodata
    )
    resampled_dataset.write(resampled_array, 1)
    resampled_dataset.close()

    return


def generate_resampled_anglebands(mtdmsi, mtd):
    """Generates angle bands resampled to 10 meters.
    Parameters:
       xml (str): path to MTD_TL.xml.
    Returns:
       str, str, str, str: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    path = os.path.split(mtd)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    imgref = [f for f in glob.glob(imgFolder + "**/*04*.jp2", recursive=True)]
    imgref.sort()
    imgref=imgref[0]

    scenename = extract_tileid(mtdmsi)
    solar_zenith, solar_azimuth = extract_sun_angles(mtd)
    sensor_zenith, sensor_azimuth = extract_sensor_angles(mtd)

    sensor_zenith_mean = sensor_zenith[0]
    sensor_azimuth_mean = sensor_azimuth[0]
    for num_band in (range(1,len(sensor_azimuth))):
        sensor_zenith_mean += sensor_zenith[num_band]
        sensor_azimuth_mean += sensor_azimuth[num_band]
    sensor_zenith_mean /= len(sensor_zenith)
    sensor_azimuth_mean /= len(sensor_azimuth)

    sz_path = angFolder + scenename + '_SZAr.tif'
    sa_path = angFolder + scenename + '_SAAr.tif'
    vz_path = angFolder + scenename + '_VZAr.tif'
    va_path = angFolder + scenename + '_VAAr.tif'

    resample_anglebands(solar_zenith, imgref, sz_path)
    resample_anglebands(solar_azimuth, imgref, sa_path)
    resample_anglebands(sensor_zenith_mean, imgref, vz_path)
    resample_anglebands(sensor_azimuth_mean, imgref, va_path)

    return sz_path, sa_path, vz_path, va_path


def xmls_from_safe(SAFEfile):
    """Obtain the MTD_TL.xml path of a .SAFE folder.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
    Returns:
       str: path to MTD_TL.xml.
    """
    mtdmsi = [f for f in glob.glob(os.path.join(SAFEfile,"MTD_MSIL*.xml"), recursive=True)][0]
    mtd = os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'MTD_TL.xml'))

    return mtdmsi, mtd


def gen_s2_ang_from_SAFE(SAFEfile):
    """Generate Sentinel 2 angles using .SAFE.
    Parameters:
       SAFEfile (str): path to Sentinel-2 .SAFE folder.
    Returns:
       sz_path, sa_path, vz_path, va_path: path to solar zenith image, path to solar azimuth image, path to view (sensor) zenith image and path to view (sensor) azimuth image, respectively.
    """
    mtdmsi, mtd = xmls_from_safe(SAFEfile)

    ### Generates resampled anglebands (to 10m)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(mtdmsi, mtd)
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
    shutil.unumpyack_archive(zipfile, temp_dir, 'zip')
    SAFEfile = os.path.join(temp_dir, zipfoldername)
    mtdmsi, mtd = xmls_from_safe(SAFEfile)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(mtdmsi, mtd)
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
    if path.endswith('.SAFE'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_SAFE(path) #path to SAFE
    elif path.endswith('.zip'):
        sz_path, sa_path, vz_path, va_path = gen_s2_ang_from_zip(path) #path to .zip

    return sz_path, sa_path, vz_path, va_path
