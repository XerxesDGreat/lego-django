import os
import shutil
from django.conf import settings
import requests
import time


_base_link = 'https://m.rebrickable.com/media/downloads/'
_tmp_dir = settings.API_UPDATE_TEMP_DIR
_api_key = '7a63f7230da51d57ede0d83357d160d9'
_delay_in_seconds = 0.75


def download_packages(packages, msg_writer):
    make_temp_dir()
    for package in packages:
        target_file_path = get_target_file_path_for_package(package)
        if os.path.isfile(target_file_path):
            continue
        msg_writer.write("downloading package %s" % package)
        source_url = get_url_source_for_package(package)
        with open(target_file_path, "wb") as target_file:
            package_file_contents = requests.get(source_url)
            if package_file_contents.status_code != 200:
                msg_writer.write("non-200 status code (%s) when fetching file %s; failing" %
                                 (package_file_contents.status_code, source_url))
            else:
                target_file.write(package_file_contents.content)


def make_temp_dir():
    tmp_dir = get_temp_dir()
    if not os.path.isdir(tmp_dir):
        os.mkdir(tmp_dir)


def delete_temp_dir():
    shutil.rmtree(get_temp_dir())


def get_temp_dir():
    return _tmp_dir


def get_target_file_path_for_package(package_name):
    return os.path.join(get_temp_dir(), "%s.csv" % package_name)


def get_url_source_for_package(package_name):
    return _base_link + "%s.csv" % package_name


def api_get(url, params=None, err_logger=None):
    # this has a limit of 2 calls per second; let's sleep a bit
    time.sleep(_delay_in_seconds)
    params = {} if params is None else params
    params.update({"key": _api_key})
    response = requests.get(url, params=params)
    if response.status_code != 200:
        err_logger = print if err_logger is None else err_logger
        err_logger("url get unsuccessful. Url: %s, status: %s" % (url, response.status_code))
        return None
    return response.json()
