#!/usr/bin/env python

# Created by Rennan Marujo - rennanmarujo@gmail.com 

import numpy
import os
from osgeo import gdal, osr, ogr
import xml.etree.ElementTree as ET
import time
import glob
import sys

################################################################################
## Generate Sentinel Angle view bands
################################################################################

def get_tileid( XML_File ):
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


def get_sun_angles( XML_File ):
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
						zen = float( values[cindex][0] )
						az = float( values[cindex][1] )
						solar_zenith_values[rindex,cindex] = zen
						solar_azimuth_values[rindex,cindex] = az
	return (solar_zenith_values, solar_azimuth_values)


def get_sensor_angles( XML_File ):
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
    outRaster.SetProjection( proj )
    outband.FlushCache()


def generate_anglebands( XMLfile ):
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

	scenename = get_tileid( XMLfile )
	solar_zenith, solar_azimuth = get_sun_angles( XMLfile )
	sensor_zenith, sensor_azimuth = get_sensor_angles( XMLfile )

	rasterOrigin = (geotrans[0],geotrans[3])

	write_intermediary((angFolder + scenename + "solar_zenith"),rasterOrigin,proj,solar_zenith)
	write_intermediary((angFolder + scenename + "solar_azimuth"),rasterOrigin,proj,solar_azimuth)
	for num_band in (range(len(sensor_azimuth))):
		write_intermediary((angFolder + scenename + "sensor_zenith_b" + str(num_band)),rasterOrigin,proj,sensor_zenith[num_band])
		write_intermediary((angFolder + scenename + "sensor_azimuth_b" + str(num_band)),rasterOrigin,proj,sensor_azimuth[num_band])

	del tmp_ds
	
def resampled_anglebands(ang_matrix, imgref, filename):
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

def generate_resampled_anglebands( XMLfile ):
	path = os.path.split(XMLfile)[0]
	imgFolder = path + "/IMG_DATA/"
	angFolder = path + "/ANG_DATA/"
	os.makedirs(angFolder, exist_ok=True)
	
	#use band 4 as reference due to 10m spatial resolution
	imgref = [f for f in glob.glob(imgFolder + "**/*04.jp2", recursive=True)][0]

	scenename = get_tileid( XMLfile )
	solar_zenith, solar_azimuth = get_sun_angles( XMLfile )
	sensor_zenith, sensor_azimuth = get_sensor_angles( XMLfile )

	sensor_zenith_mean = sensor_zenith[0]
	sensor_azimuth_mean = sensor_azimuth[0]
	for num_band in (range(1,len(sensor_azimuth))):
		sensor_zenith_mean += sensor_zenith[num_band]
		sensor_azimuth_mean += sensor_azimuth[num_band]
	sensor_zenith_mean /= len(sensor_azimuth)
	sensor_azimuth_mean /= len(sensor_azimuth)

	resampled_anglebands(solar_zenith, imgref, (angFolder + scenename + '_solar_zenith_resampled.tif'))
	resampled_anglebands(solar_azimuth, imgref, (angFolder + scenename + 'solar_azimuth_resampled.tif'))
	resampled_anglebands(sensor_zenith_mean, imgref, (angFolder + scenename + 'sensor_zenith_mean_resampled.tif'))
	resampled_anglebands(sensor_azimuth_mean, imgref, (angFolder + scenename + 'sensor_azimuth_mean_resampled.tif'))


def main():
	XMLfile = "/home/marujo/sensor_harmonization/S2A_MSIL1C_20190425T132241_N0207_R038_T23LLF_20190425T164208.SAFE/GRANULE/L1C_T23LLF_A020055_20190425T132236/MTD_TL.xml"
	
	### Generates angle bands from the XML file (no resampling) and no sensor mean calculation
	# generate_anglebands( XMLfile )

	### Generates resampled anglebands (to 10m)
	generate_resampled_anglebands( XMLfile )

	
if __name__ == '__main__':
	start = time.time()
	main()
	end = time.time()
	print("Duration time: {}".format(end - start))
	print("END :]")

#sys.exit(0)