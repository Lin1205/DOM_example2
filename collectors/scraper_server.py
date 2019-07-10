#
#   scraper_server.py
#   ~~~~~~~~~~~~~~~~~
#
#   Servers to periodically run scraper data collectors
#
import os
import time

from apscheduler.schedulers.background import BlockingScheduler

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from collectors.rentals import CraigsList
from core.util import load_config

DEBUG = True

# Find the project root assuming we are one dir deep.
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CONFIG_PATH = os.path.join(PROJECT_ROOT, 'config/scraper_config.yml')

# def date_tomorrow(hour, minute, interval=24):
#     """ Return date for tomorrow at hour and minute passed """
#
#     date_now = datetime.datetime.now()
#
#     tomorrow = date_now + datetime.timedelta(hours=interval)
#
#     return datetime.datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day,
#                              hour=hour, minute=minute)
#
# def date_jitter(date_in, jitter_minutes=59):
#     """ Add some random jitter to configed dates """
#
#     r = random.random()
#
#     jitter = (r - 0.5) * jitter_minutes
#
#     return date_in + datetime.timedelta(minutes=jitter)
#
#
# def load_config(conf):
#     """
#     Load yml config file return contents
#
#     :param conf: Path to yaml file config
#     :return: config
#     """
#
#     with open(conf, 'r') as yf:
#
#         config = yaml.safe_load(yf)
#
#     return config


def run_cl_job(**kwargs):
    """
    Run CL job

    :param **kwargs: keys are job_details, config, session
    :return:
    """
    hood = kwargs['job_neighborhood']
    config = kwargs['config']
    session = kwargs['session']

    job = CraigsList(hood, 'house', config)
    job.get_listings(session)


def run_all_cl_jobs(**kwargs):
    """
    Run each CL job defined by config

    :param kwargs:
    :return:
    """

    config = kwargs['config']
    session = kwargs['session']
    first = True

    for hood in config['job_neighborhood']:

        kwargs_pass = {'job_neighborhood': hood,
                       'config': config,
                       'session': session}

        if not first:
            time.sleep(3, 59)
            first = False

        run_cl_job(**kwargs_pass)

        print('Completed job {}'.format(hood))

        # TODO: Add random wait


if __name__ == "__main__":

    config = load_config(CONFIG_PATH)
    cl_config = config['scrapers']['craigslist']

    # DB Setup. Create an engine to store data at specified path
    # By default SQLite expects one thread, but multithread is supported:
    #   https://docs.sqlalchemy.org/en/13/dialects/sqlite.html
    engine = create_engine(config['db_path'], echo=True,
                           connect_args={'check_same_thread': False})
    Session = sessionmaker(bind=engine)
    session = Session()

    # Job Scheduler
    # scheduler = BackgroundScheduler() #executors=executors)
    sched = BlockingScheduler()

    kwargs_pass = {'config': cl_config,
                   'session': session}

    if not DEBUG:
        # Schedule job that has form of: run_all_cl_jobs(**kwargs_pass)
        sched.add_job(run_all_cl_jobs, 'cron', hour=cl_config['job_hour'], minute=cl_config['job_minute'],
                      jitter=3600, kwargs=kwargs_pass)

        sched.start()

    else:
        # If DEBUG, run immediately
        run_all_cl_jobs(**kwargs_pass)

    # Enrich new records with census geography

    session.close()
