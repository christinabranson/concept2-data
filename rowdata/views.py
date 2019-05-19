from django.shortcuts import render
from django.shortcuts import render, redirect, get_object_or_404
import logging
from .models import Race
from .models import User
from .models import Workout
from django.conf import settings
import datetime
import pytz
from django.db import connection
from django.db.models import Sum, Q
import calendar
import collections

logger = logging.getLogger(__name__)

# Global functions to get all data
def getGlobalVariables():
    return {
        'races': getRacesForNavigation(),
        'valid_months': getValidMonths()
    }

def getRacesForNavigation():
    return Race.objects.all()

def dictfetchall(cursor):
    "Return all rows from a cursor as a dict"
    columns = [col[0] for col in cursor.description]
    return [
        dict(zip(columns, row))
        for row in cursor.fetchall()
    ]

def getValidMonths():
    query = 'SELECT strftime("%Y", date) AS year, strftime("%m", date) AS month, case strftime("%m", date) when "01" then "January" when "02" then "Febuary" when "03" then "March" when "04" then "April" when "05" then "May" when "06" then "June" when "07" then "July" when "08" then "August" when "09" then "September" when "10" then "October" when "11" then "November" when "12" then "December" else "" end AS prettyMonth  FROM rowdata_workout GROUP BY strftime("%Y", date), strftime("%m", date);'

    with connection.cursor() as cursor:
        cursor.execute(query, [])
        return dictfetchall(cursor)

#######################################
# Home & Static
#######################################

def home(request):
    logger.debug("rowdata.views.home")

    # TODO: get current year
    now = datetime.datetime.now()

    tz = pytz.timezone('America/New_York')
    start_date = datetime.datetime(now.year, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as >=
    #end_date = datetime.datetime(now.year + 1, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as strictly <
    end_date = now

    users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))

    return render(request, 'home.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
    })

def about(request):
    logger.debug("rowdata.views.about")

    return render(request, 'about.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
    })

#######################################
# Monthly Data
#######################################

def all_months(request):
    logger.debug("rowdata.views.all_months")

    # TODO: get current year
    tz = pytz.timezone('America/New_York')
    start_date = datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as >=
    end_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as strictly <

    users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))

    return render(request, 'months/all.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
    })

def month(request, year, month):
    logger.debug("rowdata.views.month: " + str(month) + "/" + str(year))

    # TODO: get current year
    tz = pytz.timezone('America/New_York')
    start_date = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=tz) # will be treated as >=
    if start_date.month <= 11:
        end_date = datetime.datetime(year, month + 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as strictly <
    else:
        end_date = datetime.datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=tz)  # will be treated as strictly <

    users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))

    return render(request, 'months/month.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
    })

def month_data(request, user_id, year, month):
    logger.debug("rowdata.views.month_data: " + str(user_id) + ": " + str(month) + "/" + str(year))

    # TODO: get current year
    tz = pytz.timezone('America/New_York')
    start_date = datetime.datetime(year, month, 1, 0, 0, 0, tzinfo=tz) # will be treated as >=
    if start_date.month <= 11:
        end_date = datetime.datetime(year, month + 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as strictly <
    else:
        end_date = datetime.datetime(year + 1, 1, 1, 0, 0, 0, tzinfo=tz)  # will be treated as strictly <

    user = User.objects.filter(pk=user_id).annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))[0]

    logger.debug(user)

    user_workouts = user.workouts.filter(date__gte=start_date).filter(date__lt=end_date)

    logger.debug(user_workouts)
    logger.debug(start_date)

    daysInMonth = calendar.monthrange(start_date.year, start_date.month)[1]

    logger.debug("days in month: " + str(daysInMonth))

    workout_data = collections.defaultdict(list)
    for day in range(daysInMonth):
        day = day + 1
        distanceObj = user_workouts.filter(date__day=day).aggregate(totalDistance=Sum('distance'))
        distance = distanceObj['totalDistance']
        if distance is None:
            distance = 0
        workout_data[day].append({'distance': distance})

    logger.debug(workout_data)


    return render(request, 'months/data.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'user': user,
        'workout_data': workout_data,
        'start_date': start_date,
        'end_date': end_date,
    })


#######################################
# Race Data
#######################################

def all_races(request):
    logger.debug("rowdata.views.all_races")

    all_races = Race.objects.all()

    return render(request, 'races/all.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'all_races': all_races,
    })

def race(request, race_id):
    logger.debug("rowdata.views.race: " + str(race_id))

    race = get_object_or_404(Race, pk=race_id)

    tz = pytz.timezone('America/New_York')

    # start date should always exist
    if race.start_date:
        start_date = datetime.datetime(race.start_date.year, race.start_date.month, race.start_date.day, 0, 0, 0, tzinfo=tz) # will be treated as >=

    # end date might not exist
    if race.end_date:
        end_date = datetime.datetime(race.end_date.year, race.end_date.month, race.end_date.day, 0, 0, 0, tzinfo=tz) # will be treated as >=
        users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))
    else:
        users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date)))

    return render(request, 'races/race.html', {
        # Global variables
        'global': getGlobalVariables(),
        # Template variables
        'race': race,
        'users': users,
    })