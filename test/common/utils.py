#! /usr/bin/python

import os
import random
from datetime import datetime
import iso8601

class Utils(object):

    @staticmethod
    def open_temp_file():
        ts = (datetime.utcnow() - datetime(1970, 1, 1)).total_seconds()
        new_file = "/tmp/{0}-{1}".format(ts, random.random())
        if os.path.isfile(new_file):
            os.remove(new_file)
        return open(new_file, "w")

    @staticmethod
    def read_file(file_path):
        with open(file_path, "r") as f:
            return f.readlines()

    @staticmethod
    def get_utc_now_seconds():
        now = datetime.utcnow().replace(tzinfo=iso8601.iso8601.UTC)
        epoch = datetime(1970, 1, 1).replace(tzinfo=iso8601.iso8601.UTC)
        return (now - epoch).total_seconds()