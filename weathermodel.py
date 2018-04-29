from .noaamodel import NOAAModel
from .location import Location
from . import tools
from . import units
from datetime import datetime
import pytz


class GFSModel(NOAAModel):

    _base_gfs_ascii_url = 'http://nomads.ncep.noaa.gov:9090/dods/{0}/gfs{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'
    _base_gfs_grib_url = 'http://nomads.ncep.noaa.gov/cgi-bin/filter_gfs_0p50.pl?file=gfs.t00z.pgrb2full.0p50.f000&var_GUST=on&var_PRES=on&var_TMP=on&var_UGRD=on&var_VGRD=on&subregion=&leftlon=0&rightlon=360&toplat=90&bottomlat=-90&dir=%2Fgfs.2018042000'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_gfs_ascii_url.format(self.name, datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

    def _to_buoy_data_ascii(self, buoy_data_point, i):
        if buoy_data_point.unit != units.Units.metric:
            buoy_data_point.change_units(units.Units.metric)

        # Make sure the timestamp exists and is the same as the data we are trying to fill
        raw_time = (self.data['time'][i] - units.epoch_days_since_zero) * 24 * 60 * 60
        raw_date = pytz.utc.localize(datetime.utcfromtimestamp(raw_time))
        if buoy_data_point.date == None:
            buoy_data_point.date = raw_date
        elif buoy_data_point.date != raw_date:
            return False

        buoy_data_point.wind_speed, buoy_data_point.wind_direction = tools.scalar_from_uv(self.data['ugrd10m'][i], self.data['vgrd10m'][i])
        buoy_data_point.wind_compass_direction = units.degree_to_direction(buoy_data_point.wind_direction)
        buoy_data_point.wind_gust = self.data['gustsfc'][i]

        return True


class NAMModel(NOAAModel):

    _base_nam_url = 'http://nomads.ncep.noaa.gov:9090/dods/nam/nam{1}/{0}_{2}.ascii?time[{6}:{7}],ugrd10m[{6}:{7}][{4}][{5}],vgrd10m[{6}:{7}][{4}][{5}],gustsfc[{6}:{7}][{4}][{5}]'

    def create_ascii_url(self, location, start_time_index, end_time_index):
        timestamp = self.latest_model_time()
        datestring = timestamp.strftime('%Y%m%d')
        hourstring = timestamp.strftime('%Hz')

        lat_index, lon_index = self.location_index(location)
        alt_index = self.altitude_index(location.altitude)
        url = self._base_nam_url.format(datestring, hourstring, alt_index, lat_index, lon_index, start_time_index, end_time_index)
        return url

def global_gfs_model():
    return GFSModel('gfs_0p50', 'Global GFS 0.5 deg', Location(-90.00000, 0.00000), Location(90.0000, 359.5000), 0.5, 0.125, min_alt=1000.0, max_alt=1.0, alt_res=21.717)