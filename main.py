from loguru import logger
import numpy as np
from skyfield.api import load, Topos, wgs84
import datetime as dt
import pytz
import load_tle
from timezonefinder import TimezoneFinder


class observe_satellites():
    def __init__(self, location, resolution, total_time, minimum_sat_elevation, sun_elevation):
        '''
        Description:
            The observe_satellites class is performing the main calculations to determiken the best time to observe satellites. 
            It returns a list of dictionaries with datetimes and the corresponding count of satellites 

        Args:
            location: latitude and longitude of location -> [Latitude, Longitude]
            resolution: the resolution to calculate data in minutes-> (int)
            total_time: Total time into the future to calculate data in hours -> (int)
            minimum_sat_elevation: Minimum satellite horizon elevation in degrees (minimum 5 recommended) -> (int)
            sun_elevation: Sun elevation when below the horizon
        '''
        self.location = location
        self.resolution = resolution
        self.total_time = total_time
        self.minimum_sat_elevation = minimum_sat_elevation
        self.sun_elevation = sun_elevation

        self.observer = Topos(self.location[0], self.location[1])
        #Ephemeris file (required)
        self.ephemeris = load('assets/de421.bsp')
        #Using ephemeris - define positions of Sun and Earth
        self.sun = self.ephemeris['sun']
        self.earth = self.ephemeris['earth']
        #Calculate the position of the Sun relative to LOCATION
        self.astrometric = self.earth + self.observer

        #Specify the datetime format used
        self.FORMAT_DATETIME = "%m-%d-%Y %I:%M%p"
        #Load timescale
        self.ts = load.timescale()

    #Grabs timezone based on location
    def get_timezone(self) -> pytz:
        tf = TimezoneFinder()
        local_timezone = tf.timezone_at(lat=self.location[0], lng=self.location[1])
        formatted_timezone = pytz.timezone(local_timezone)
        
        return formatted_timezone

    #Returns the current UTC time
    def convert_time(self) -> dt:
        now = dt.datetime.now(dt.timezone.utc)

        return now

    #Formats the datetime using FORMAT_DATETIME and local_timezone
    def format_time(self,input_time):
        #Use utc_timezone to format time in UTC
        #utc_timezone = pytz.utc
        input_time = input_time.astimezone(timezone)
        formatted_time = dt.datetime.strftime(input_time, self.FORMAT_DATETIME)

        return formatted_time

    #Determines separation between satellite and location as a skyfield.vectorlib.VectorSum
    def calculate_satellite_difference(self, specified_sat):
        satellite_difference = specified_sat - wgs84.latlon(self.location[0], self.location[1])
        
        return satellite_difference

    #Calculates the altitude, azimuth and distance for a given satellite
    #at a time z. 
    def calculate_diff_alt_az(self, change, z) -> int:
        fullrange = change.at(z)
        alttude, azimuth, dist = fullrange.altaz()

        return alttude.degrees


    #Create the full time range
    def set_timerange(self):
        now = self.convert_time()

        # Create the timerange from now to now + total time 
        timerange = self.ts.utc(now.year, now.month, now.day, now.hour, np.arange(now.minute, self.total_time * 60 + now.minute, self.resolution))

        return list(timerange)

    #We only care about when the sun is below the horizon (sun_altitude < 0) as well 
    #as greater than a certain threshold (SUN_ELEVATION). This function 
    #makes the final for loop much shorter.
    def get_sun_altitude(self) -> list:
        full_timerange = self.set_timerange()

        for a,b in enumerate(full_timerange):
            apparent = self.astrometric.at(b).observe(self.sun).apparent()
            alt, az, distance = apparent.altaz()
            sun_altitude = alt.degrees
            if sun_altitude < 0 and sun_altitude > self.sun_elevation:
                pass
            else:
                #Removing instances in the timerange where the altitude is too low
                #or the sun is above the horizon
                full_timerange[a] = False

        return full_timerange


    def main(self, satellite) -> list:
        sun_timespan = self.get_sun_altitude()

        # Initialize a dictionary to store counts
        timespan_counts = {time: 0 for time in sun_timespan}

        for i in satellite:
            y = self.calculate_satellite_difference(i)
            for ti in sun_timespan:
                if ti != False:
                    sat_sunlit = i.at(ti).is_sunlit(self.ephemeris)
                    apparent = self.astrometric.at(ti).observe(self.sun).apparent()
                    alt_sun, az, distance = apparent.altaz()
                    sun_altitude = alt_sun.degrees
                    if sat_sunlit:
                        sat_altitude = self.calculate_diff_alt_az(y,ti)
                        if sat_altitude > self.minimum_sat_elevation and sun_altitude < 0 and sun_altitude > self.sun_elevation:
                            #add a count if satellite is above minimum elevation, the sun is below the horizon, and sun is above
                            #the self.sun_elevation value 
                            timespan_counts[ti] += 1
                    else:
                        pass
        #Final results with the formatted time. 
        results = [{self.format_time(time): count} for time, count in timespan_counts.items() if time is not False]

        return results        

    def graph_data(self):
        pass


if __name__ == "__main__":
    #Load load_tle class with max days set to 2 
    tle_class = load_tle.fetch_tles(2)

    #load tles for ONEWEB satellites
    load_satellites = tle_class.load_select_satellites("ONEWEB")

    '''
    Use Cases:
        To load different groups of satellites, you will need to change the load_satellites variable above.
        
        Load all Active Satellites:
            load_satellites = tle_class.load_all_satellites()

        Load All Starlink Satellites:
            load_satellites = tle_class.load_select_satellites("Starlink")

        Load only the satellite "NAVSTAR 43":
            load_satellites = tle_class.load_select_satellites("NAVSTAR 43")

    '''
    
    sat_obs = observe_satellites([33.64561821100173, -117.68649668652029], 15, 12, 5, -30)
    timezone = sat_obs.get_timezone()

    logger.info(f"Timezone set to {timezone}")

    final_results = sat_obs.main(load_satellites)
    if final_results:
        for entry in final_results:
            print(entry)
    else:
        logger.warning("No satelltes visible. Enter different parameters.")

    logger.info(f"Completed script")