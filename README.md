# 🛰️ Observing Satellites 🛰️

Ever wonder what the best time to observe satellites from your location is? Whether you want to observe a specific group of satellites (ex - Starlink) or all active satellites, this repository has the answer!

## 📝 How to use 
1. Clone the repository and create a viritual environment in the command line
```
python3 -m venv .venv
```

2. Download all required packages using pip
```
pip install -r requirements.txt
```

3. (Optional) Change arguments in the observe_satellites class to fit your needs (line 160). Descriptions for each argument can be found on line 17
in main.py

4. (Optional) If you would like to change the satellite group to observe, see line 145 (Use Cases) in main.py

5. Once the packages have been successfully installed and parameters changed, run the main.py script
```
python3 main.py
```

## 📚 Documentation 
1. This repository relies on the 'Skyfield' module to do most of the heavy lifting. This library is responsible for loading the TLEs, calculating the
separation between satellite and location, calculating the azimuth of a satellite, calculating the sun's altitude, and various other minor calculations.
See the 'Earth Satellite' section of Skyfield for more details https://rhodesmill.org/skyfield/earth-satellites.html

2. The get_sun_altitude() function in main.py only calculates values for satellites when the sun's altitude is between -3 and -27 degrees below the horizon
(although the user is welcome to change these values). The values were determined based on Section 6.4 in the paper linked in #2 of the Future Improvements 
Section.

## 📋 Future Improvements 
1. Currently loading all satellites takes a long time. Eventually I would like to add multi-threading to speed up this process.
```
Loading ~600 satellites -> ~15 second load time (Ex - OneWeb)
Loading ~6500 satellites -> ~2 minute load time (Ex - Starlink)
```

2. This repository is not a method that takes into account all neccessary parameters for calculating if a satellite is visible relative to an observer. It does
not account for flux from the Sun, flux from Earthshine, satellite geometry, satellite material properties, and many more parameters. In future releases of this repository, I hope to account for more of these parameters to get more accurate data. The link below is to a paper for modeling the optical brightness of satellites using the Bidirectional Reflectance Distribution Function which takes into account these parameters. https://arxiv.org/pdf/2305.11123