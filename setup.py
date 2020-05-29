from setuptools import find_packages, setup

packages = find_packages()

install_requires = [
    # 'GDAL',
    'numpy'
]

setup(
    # Needed to silence warnings (and to be a worthwhile package)
    name='s2-angs',
    url='https://github.com/marujore/sentinel2_angle_bands',
    author='Rennan Marujo',
    author_email='rennanmarujo@gmail.com',
    # Needed to actually package something
    packages=packages,
    # Needed for dependencies
    install_requires=install_requires,
    # *strongly* suggested for sharing
    version='0.1',
    # The license can be anything you like
    license='MIT',
    description='Script to calculate Sentinel-2 (A-B) view_zenith, view_azimuth, sun_zenith and sun_azimuth',
    # We will also need a readme eventually (there will be a warning)
    # long_description=open('README.txt').read(),
)
