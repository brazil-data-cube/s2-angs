# Python Native
from zipfile import ZipFile
import glob
import os
import shutil
import sys
import time
import xml.etree.ElementTree as ET

# 3rdparty
from osgeo import gdal, osr, ogr
import numpy


if len(sys.argv) < 2:
    print('ERROR: usage: <path to L1C .SAFE, .zip or MTD_TL.xml >')
    sys.exit()

################################################################################
## Generate Sentinel Angle view bands
################################################################################

def get_tileid(XML_File):
    tile_id = ""
    # Parse the XML file 
    tree = ET.parse(XML_File)
    root = tree.getroot()

    # Find the angles
    for child in root:
        if child.tag[-12:] == 'General_Info':
            geninfo = child

    for segment in geninfo:
        if segment.tag == 'TILE_ID':
            tile_id = segment.text.strip()
    return(tile_id)


def get_sun_angles(XML_File):
    solar_zenith_values = numpy.empty((23,23,)) * numpy.nan #initiates matrix
    solar_azimuth_values = numpy.empty((23,23,)) * numpy.nan

    # Parse the XML file 
    tree = ET.parse(XML_File)
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


def get_sensor_angles(XML_File):
    numband = 13
    sensor_zenith_values = numpy.empty((numband,23,23)) * numpy.nan #initiates matrix
    sensor_azimuth_values = numpy.empty((numband,23,23)) * numpy.nan

    # Parse the XML file 
    tree = ET.parse(XML_File)
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
                # print(values[0])
                for cindex in range(len(values)):
                    if ( values[cindex][0] != 'NaN' and values[cindex][1] != 'NaN' ):
                        zen = float( values[cindex][0] )
                        az = float( values[cindex][1] )
                        sensor_zenith_values[bandId, rindex,cindex] = zen
                        sensor_azimuth_values[bandId, rindex,cindex] = az
    return(sensor_zenith_values,sensor_azimuth_values)


def write_intermediary(newRasterfn,rasterOrigin,proj, array):
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


def generate_anglebands(XMLfile):
    path = os.path.split(XMLfile)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    #use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04.jp2", recursive=True)][0]

    tmp_ds = gdal.Open(imgref)
    tmp_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    geotrans = tmp_ds.GetGeoTransform()  #get GeoTranform from existed 'data0'
    proj = tmp_ds.GetProjection() #you can get from a exsited tif or import 

    scenename = get_tileid(XMLfile)
    solar_zenith, solar_azimuth = get_sun_angles(XMLfile)
    sensor_zenith, sensor_azimuth = get_sensor_angles(XMLfile)

    rasterOrigin = (geotrans[0],geotrans[3])

    write_intermediary((angFolder + scenename + "solar_zenith"),rasterOrigin,proj,solar_zenith)
    write_intermediary((angFolder + scenename + "solar_azimuth"),rasterOrigin,proj,solar_azimuth)
    for num_band in (range(len(sensor_azimuth))):
        write_intermediary((angFolder + scenename + "sensor_zenith_b" + str(num_band)),rasterOrigin,proj,sensor_zenith[num_band])
        write_intermediary((angFolder + scenename + "sensor_azimuth_b" + str(num_band)),rasterOrigin,proj,sensor_azimuth[num_band])

    del tmp_ds


def resample_anglebands(ang_matrix, imgref, filename):
    src_ds = gdal.Open(imgref)
    src_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    geotrans = src_ds.GetGeoTransform()  #get GeoTranform from existed 'data0'
    proj = src_ds.GetProjection() #you can get from a exsited tif or import 

    cols = src_ds.RasterXSize
    rows = src_ds.RasterYSize

    rasterOrigin = (geotrans[0],geotrans[3])

    # Now, we create an in-memory raster
    mem_drv = gdal.GetDriverByName( 'MEM' )
    tmp_ds = mem_drv.Create('', len(ang_matrix[0]), len(ang_matrix), 1, gdal.GDT_Float32)

    # Set the geotransform
    tmp_ds.SetGeoTransform( (rasterOrigin[0], 5000, 0, rasterOrigin[1], 0, -5000) )
    tmp_ds.SetProjection ( proj )
    tmp_ds.GetRasterBand(1).SetNoDataValue(numpy.nan)
    tmp_ds.GetRasterBand(1).WriteArray(ang_matrix)

    driver = gdal.GetDriverByName('GTiff')
    dst_ds = driver.Create(filename, cols, rows, 1, gdal.GDT_Float32)
    dst_ds.SetGeoTransform( geotrans )
    dst_ds.SetProjection( proj )

    resampling = gdal.GRA_Bilinear
    gdal.ReprojectImage( tmp_ds, dst_ds, tmp_ds.GetProjection(), dst_ds.GetProjection(), resampling)

    del src_ds
    del tmp_ds
    del dst_ds


def generate_resampled_anglebands(XMLfile):
    path = os.path.split(XMLfile)[0]
    imgFolder = path + "/IMG_DATA/"
    angFolder = path + "/ANG_DATA/"
    os.makedirs(angFolder, exist_ok=True)

    #use band 4 as reference due to 10m spatial resolution
    imgref = [f for f in glob.glob(imgFolder + "**/*04.jp2", recursive=True)][0]

    scenename = get_tileid(XMLfile)
    solar_zenith, solar_azimuth = get_sun_angles(XMLfile)
    sensor_zenith, sensor_azimuth = get_sensor_angles(XMLfile)

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
    return os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'MTD_TL.xml'))


def gen_s2_ang_from_SAFE(SAFEfile):
    xml = xml_from_safe(SAFEfile)
    ### generate 23x23 Product (not resampled)
    # generate_anglebands(os.path.join(SAFEfile, 'GRANULE', os.path.join(os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'MTD_TL.xml')))

    ### Generates resampled anglebands (to 10m)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_xml(xml):
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    return sz_path, sa_path, vz_path, va_path


def gen_s2_ang_from_zip(zipfile):
    with ZipFile(zipfile) as zipObj:
        zipfoldername = zipObj.namelist()[0][:-1]
    work_dir = os.getcwd()
    os.mkdir('s2_ang_tmp', exist_ok=True)
    temp_dir = os.path.join(os.getcwd(), 's2_ang_tmp')
    shutil.unpack_archive(zipfile, temp_dir, 'zip')
    SAFEfile = os.path.join(temp_dir, zipfoldername)
    xml = xml_from_safe(SAFEfile)
    sz_path, sa_path, vz_path, va_path = generate_resampled_anglebands(xml)
    ang_dir = os.path.join(SAFEfile,'GRANULE', os.listdir(os.path.join(SAFEfile,'GRANULE/'))[0], 'ANG_DATA')
    shutil.move(ang_dir, work_dir)
    shutil.rmtree(temp_dir)
    return sz_path, sa_path, vz_path, va_path


def main():
    if sys.argv[1].find("_MSIL2A_"):
        print("ERROR: Input uses L1C product, not L2A. Change your input file.")
    elif sys.argv[1].endswith('.SAFE'):
        gen_s2_ang_from_SAFE(sys.argv[1]) #path to SAFE
    elif sys.argv[1].endswith('MTD_TL.xml'):
        gen_s2_ang_from_xml(sys.argv[1]) #path MTD_TL.xml
    elif sys.argv[1].endswith('.zip'):
        gen_s2_ang_from_zip(sys.argv[1]) #path to .zip


if __name__ == '__main__':
    start = time.time()
    main()
    end = time.time()
    print("Duration time: {}".format(end - start))
