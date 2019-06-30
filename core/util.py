#
#   util.py
#   ~~~~~~~
#
#   Utilities used by multiple modules
#
import yaml
import datetime
import random


def date_tomorrow(hour, minute, interval=24):
    """ Return date for tomorrow at hour and minute passed """

    date_now = datetime.datetime.now()

    tomorrow = date_now + datetime.timedelta(hours=interval)

    return datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
                             hour=hour, minute=minute)

def date_jitter(date_in, jitter_minutes=59):
    """ Add some random jitter to configed dates """

    r = random.random()

    jitter = (r - 0.5) * jitter_minutes

    return date_in + datetime.timedelta(minutes=jitter)


def load_config(conf):
    """
    Load yml config file return contents

    :param conf: Path to yaml file config
    :return: config
    """

    with open(conf, 'r') as yf:

        config = yaml.safe_load(yf)

    return config