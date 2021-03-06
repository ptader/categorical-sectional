# Self-Test file that makes sure all
# off the station identifiers are OK.

import logging
import time

import configuration
import weather
from lib.logger import Logger
from safe_logging import safe_log, safe_log_warning

python_logger = logging.getLogger("check_config_files")
python_logger.setLevel(logging.DEBUG)
LOGGER = Logger(python_logger)


def terminal_error(
    error_message
):
    safe_log_warning(LOGGER, error_message)
    exit(0)


try:
    airport_render_config = configuration.get_airport_configs()
except Exception as e:
    terminal_error(
        f'Unable to fetch the airport configuration. Please check the JSON files. Error={e}')

if len(airport_render_config) == 0:
    terminal_error('No airports found in the configuration file.')

stations_unable_to_fetch_weather = []

for station_id in airport_render_config:
    safe_log(LOGGER, f'Checking configuration for {station_id}')

    led_index = airport_render_config[station_id]

    # Validate the index for the LED is within bounds
    if led_index < 0:
        terminal_error(
            f'Found {station_id} has an LED at a negative position {led_index}')

    # Validate that the station is in the CSV file
    try:
        data_file_icao_code = weather.get_faa_csv_identifier(station_id)
    except Exception as e:
        terminal_error(
            'Unable to fetch the station {} from the CSV data file. Please check that the station is in the CSV file. Error={}'.format(station_id, e))

    if data_file_icao_code is None or data_file_icao_code == '' or weather.INVALID in data_file_icao_code:
        terminal_error(
            f'Unable to fetch the station {station_id} from the CSV data file. Please check that the station is in the CSV file. Error={e}')

    # Validate that the station can have weather fetched
    metar = weather.get_metar(station_id, logger=LOGGER)

    if metar is None or weather.INVALID in metar:
        stations_unable_to_fetch_weather.append(station_id)
        safe_log_warning(
            LOGGER,
            f'Unable to fetch weather for {station_id}/{led_index}')

    # Validate that the station can have Sunrise/Sunset fetched
    day_night_info = weather.get_civil_twilight(station_id)

    if day_night_info is None:
        terminal_error(
            f'Unable to fetch day/night info for {station_id}/{led_index}')

    if len(day_night_info) != 6:
        terminal_error(
            f'Unknown issue fetching day/night info for {station_id}/{led_index}')

safe_log(LOGGER, '')
safe_log(LOGGER, '')
safe_log(LOGGER, '-------------------------')
safe_log(LOGGER, 'Finished testing configuration files. No fatal issues were found.')
safe_log(LOGGER, '')
safe_log(LOGGER, 'Unable to fetch the weather for the following stations:')

for station in stations_unable_to_fetch_weather:
    safe_log(LOGGER, f'\t {station}')

safe_log(LOGGER, 'Please check the station identifier. The station may be out of service, temporarily down, or may not exist.')
