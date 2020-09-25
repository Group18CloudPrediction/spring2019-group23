import time
from datetime import datetime
from threading import Thread, Event
import pymongo
import credentials.creds as creds
from datalogger.datalogger import Datalogger


class DataloggerThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        # setup db here
        print("setup db here")

        # creds will need to be created on each system
        self.client = pymongo.MongoClient("mongodb+srv://" + creds.username + ":" +
                                          creds.password + "@cluster0.lgezy.mongodb.net/<dbname>?retryWrites=true&w=majority")
        self.db = self.client.cloudTrackingData
        datalogger_connected = False

        while(not datalogger_connected):
            try:
                print("looking for datalogger")
                # path will need to change per system
                self.datalogger = Datalogger('/dev/ttyS5')
                datalogger_connected = True
                print("datalogger connected")
            except:
                # wait 10 seconds then check if datalogger has been connected
                time.sleep(10)
                print("datalogger not connected")

        self.sleep_time = 60  # 60 seconds

    def run(self):
        while(True):
            starttime = time.time()
            self.the_date = datetime.utcnow()
            self.datalogger.poll()  # get the current weather data
            self.send_weather_data_to_db()
            time.sleep(self.sleep_time -
                       ((time.time() - starttime) % self.sleep_time))

    def send_weather_data_to_db(self):
        print("sending data to db")
        the_date = self.the_date
        post = {"author": "datalogger",
                "slrFD_W": self.datalogger.weather_data.slrFD_W,
                "rain_mm": self.datalogger.weather_data.rain_mm,
                "strikes": self.datalogger.weather_data.strikes,
                "dist_km": self.datalogger.weather_data.dist_km,
                "ws_ms": self.datalogger.weather_data.ws_ms,
                "windDir": self.datalogger.weather_data.windDir,
                "maxWS_ms": self.datalogger.weather_data.maxWS_ms,
                "airT_C": self.datalogger.weather_data.airT_C,
                "vp_mmHg": self.datalogger.weather_data.vp_mmHg,
                "bp_mmHg": self.datalogger.weather_data.bp_mmHg,
                "rh": self.datalogger.weather_data.rh,
                "rht_c": self.datalogger.weather_data.rht_c,
                "tiltNS_deg": self.datalogger.weather_data.tiltNS_deg,
                "tiltWE_deg": self.datalogger.weather_data.tiltWE_deg,
                "tags": ["weather_data", "datalogger", "weather", "weather_station", "verified_data"],
                "date": self.the_date,
                "date_mins_only": the_date.replace(second=0, microsecond=0),
                "system_num": "PLACEHOLDER_REPLACE"}

        posts = self.db.WeatherData
        post_id = posts.insert_one(post).inserted_id
        print("post_id: " + str(post_id))


def main():
    datalogger_runner = DataloggerThread()
    datalogger_runner.start()


if __name__ == "__main__":
    main()
