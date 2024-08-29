from loguru import logger
from skyfield.api import load
import sys

class fetch_tles():
    def __init__(self, max_days):
        '''
        Description:
            The fetch_tles class will pull new TLEs from Celestrak and place them in a csv. 

        Args:
            max_days: how often you want to download a new tle list from Celestrak in days (2 recommended) -> (int)
        '''
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
            except Exception as e:
                logger.error(f"Failed to load new tle list from Celestrak - error {e}")
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
      