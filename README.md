# 🛰️ Observing Satellites 🛰️

Ever wonder what the best time to observe satellites from your location is? Whether you want to observe a specific group of satellites (ex - Starlink) or all active satellites, this repository has the answer!

## 📝 How to use 
1. Clone the repository and create a veritual environment in the command line
```
python3 -m venv .venv
```
2. Download all required packages using pip
```
pip install -r requirements.txt
```
3. Once the packages have been successfully installed, run the main.py script
```
python3 main.py
```
 
## 📚 Documentation 
The scripts reies on the 'Skyfield' module to do most the heavy lifting. This library is responsible for loading the TLEs, calculating the
separation between satellite and location, calculating the azimuth of a satellite, calculating the sun's altitude, and various other minor calculations.
See the Earth Satellite section of Skyfield for more details https://rhodesmill.org/skyfield/earth-satellites.html

## 📋 Future Improvements 
This repository is not a method that takes into account all neccessary parameters for calculating if a satellite is visible relative to an observer. It does
not account for flux from the Sun, flux from Earthshine, satellite geometry, satellite material properties, and many more parameters. In future releases of this repository, I hope
to account for more of these parameters to get more accurate data. The link below is to a paper for modeling the optical brightness of satellites using the Bidirectional Reflectance Distribution Function which takes into account these parameters. https://arxiv.org/pdf/2305.11123