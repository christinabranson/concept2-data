# Script to import locations from a CSV file
# We're expecting a formatted CSV of all locations in locations/csv/formatted-devils-backbone-locations.csv
# Format should be Name, Street Address, City
# With no header rows
# run with `python3 manage.py test_populate_data`

from django.core.management.base import BaseCommand
import csv
from rowdata.models import User
from rowdata.models import Workout
import time
from django.db import connection
from django.conf import settings
import random
import datetime
import pytz

class Command(BaseCommand):
    help = 'Populates users with test data'

    def handle(self, *args, **options):

        # FOR TESTING ONLY!!!
        if settings.DEBUG:

            with connection.cursor() as cursor:
                cursor.execute("delete from rowdata_workout",[])

                tz = pytz.timezone('America/New_York')

            for user in User.objects.all():
                for month in range(11):
                    month = month + 1 # we don't want month 0
                    number_workouts_this_month = random.randint(1, 15)
                    for day in range(number_workouts_this_month):
                        random_day = random.randint(1, 28)
                        random_distance = random.randint(1000,10000)
                        random_date = datetime.datetime(2019, month, random_day, random.randint(1,23), random.randint(1,59), random.randint(1,59), tzinfo=tz)
                        user.workouts.create(distance=random_distance, date=random_date)