from loguru import logger
from skyfield.api import load
import sys


class fetch_tles():
    def __init__(self, max_days: int):
        #Change max_days to set the limit of how often you want to download a new tle list from Celestrak.
        self.max_days = max_days
        #location where the tle list is stored
        self.full_tle_list = 'assets/full_tle_list.csv'
        self.celestrak_url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=active&FORMAT=tle"

        if not load.exists(self.full_tle_list) or load.days_old(self.full_tle_list) >= self.max_days:
            #Attempt to download latest tle data from Celestrak. The file holds tles 
            #for all active satellites
            try:
                load.download(self.celestrak_url, filename=self.full_tle_list)
                logger.info("Downloading new tle list from Celestrak")
            except:
                logger.error("Failed to load new tle list from Celestrak")
                sys.exit(1)
        else:
            logger.info(f"Using local {self.full_tle_list} to load tles")

    #Load all satellites found in self.full_tle_list
    def load_all_satellites(self) -> list:
        sats = load.tle_file(self.full_tle_list)

        logger.info(f"Loaded a total of {len(sats)} Satellites")

        return sats

    #Load a group of satellites (ex - "Starlink" or "ONEWEB") or a
    #single satellite (ex - "NAVSTAR 43")
    def load_select_satellites(self, select_sat: str) -> list:
        all_sats = load.tle_file(self.full_tle_list)
        by_name = {sat.name: sat for sat in all_sats}

        satellite_full_list = []
        specify_sats = []
        
        for i in all_sats:
            i = str(i)
            if i.startswith(select_sat.upper()):
                specify_sats.append(i.split("catalog")[0])

        for z in specify_sats:
            z = z.strip()
            satellite_full_list.append(by_name[z])

        logger.info(f"Loaded a total of {len(satellite_full_list)} Satellites")

        return satellite_full_list
    

'''
#LOCATION = [LATITUDE, LONGITUDE]
LOCATION = [60.190218214929615, 24.627632861112218]
#Define Observers location
observer = Topos(LOCATION[0], LOCATION[1])

#Ephemeris file (required)
ephemeris = load('assets/de421.bsp')
#Using ephemeris - define positions of Sun and Earth
sun = ephemeris['sun']
earth = ephemeris['earth']
#Calculate the position of the Sun relative to LOCATION
astrometric = earth + observer

#Specify the datetime format used
FORMAT_DATETIME = "%m-%d-%Y %I:%M%p"

#Resolution (minutes)
RESOLUTION = 15

#Total time into the future (hours)
TOTAL_TIME = 12

#Minimum satellite horizon elevation in degrees (minimum 5 recommended)
MINIMUM_SATELLITE_ELEVATION = 10

#Sun elevation when below the horizon. Twighlight ends when the sun is
#at -18 degrees below the horizon so roughly -20 to -30 is recommended
#(this value can be lowered as there are a lot of other factors that
#can be taken into account).
SUN_ELEVATION = -20

#Load timescale
ts = load.timescale()


#Grabs timezone based on location
def get_timezone(latitude: float, longitude: float) -> pytz:
    tf = TimezoneFinder()
    timezone = tf.timezone_at(lat=latitude, lng=longitude)
    formatted_timezone = pytz.timezone(timezone)
    
    return formatted_timezone

local_timezone = get_timezone(LOCATION[0], LOCATION[1])

#Converts the time from UTC to local time using timezone
def convert_time() -> dt:
    now = dt.datetime.now(local_timezone)

    return now


#Formats the datetime using FORMAT_DATETIME and local_timezone
def format_time(input_time):
    #Use utc_timezone to format time in UTC
    #utc_timezone = pytz.utc
    input_time = input_time.astimezone(local_timezone)
    formatted_time = dt.datetime.strftime(input_time, FORMAT_DATETIME)

    return formatted_time


#Determines separation between satellite and location
def calculate_satellite_difference(specified_sat):
    satellite_difference = specified_sat - wgs84.latlon(LOCATION[0], LOCATION[1])

    return satellite_difference


def calculate_diff_alt_az(change, z) -> int:
    fullrange = change.at(z)
    alttude, azimuth, dist = fullrange.altaz()

    return alttude.degrees


#Create the full time range
def set_timerange():
    now = convert_time()
    end_time = now + dt.timedelta(hours=TOTAL_TIME)
    
    # Generate minutes from now to TOTAL_TIME hours into the future
    total_minutes = int((end_time - now).total_seconds() / 60)
    minutes = np.arange(now.minute, now.minute + total_minutes + 1, RESOLUTION)

    # Create the timerange
    timerange = ts.utc(now.year, now.month, now.day, now.hour, minutes)

    #timerange is a tuple so format as list to be used in get_sun_altitude function
    timerange_list = list(timerange)
    
    return timerange, timerange_list

timerange, timerange_list = set_timerange()


#We only care about when the sun is below the horizon (sun_altitude < 0) as well 
#as greater than a certain threshold (SUN_ELEVATION). This function 
#makes the final for loop much shorter.
def get_sun_altitude() -> list:
    for a,b in enumerate(timerange_list):
        apparent = astrometric.at(b).observe(sun).apparent()
        alt, az, distance = apparent.altaz()
        sun_altitude = alt.degrees
        if sun_altitude < 0 and sun_altitude > SUN_ELEVATION:
            pass
        else:
            #Removing instances in the timerange where the altitude is too low
            #or the sun is above the horizon
            timerange_list[a] = False

    return timerange_list


def observe_satellites(satellite):
    sun_timespan = get_sun_altitude()

    # Initialize a dictionary to store counts
    timespan_counts = {time: 0 for time in sun_timespan}

    for i in satellite:
        y = calculate_satellite_difference(i)
        for ti in sun_timespan:
            if ti != False:
                sat_sunlit = i.at(ti).is_sunlit(ephemeris)
                apparent = astrometric.at(ti).observe(sun).apparent()
                alt_sun, az, distance = apparent.altaz()
                sun_altitude = alt_sun.degrees
                if sat_sunlit:
                    sat_altitude = calculate_diff_alt_az(y,ti)
                    if sat_altitude > MINIMUM_SATELLITE_ELEVATION and sun_altitude < 0 and sun_altitude > SUN_ELEVATION:
                        timespan_counts[ti] += 1
                else:
                    pass
    
    results = [{format_time(time): count} for time, count in timespan_counts.items() if time is not False]

    return results


if __name__ == "__main__":
    tle_class = load_tle.fetch_tles(2)
    #new_tles = tle_class.grab_celestrak_tles()
    load_satellites = tle_class.load_select_satellites("ICEYE")

    logger.info(f"Timezone set to {local_timezone}")

    y = observe_satellites(load_satellites)
    for i in y:
        print(i)

    logger.info(f"Completed script")
'''