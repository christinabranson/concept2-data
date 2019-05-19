from django.shortcuts import render
from django.shortcuts import render, redirect
import logging
from .models import Race
from .models import User
from .models import Workout
from django.conf import settings
import datetime
import pytz

logger = logging.getLogger(__name__)

def home(request):
    from django.db.models import Sum, Q
    logger.debug("rowdata.views.home")

    tz = pytz.timezone('America/New_York')
    start_date = datetime.datetime(2019, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as >=
    end_date = datetime.datetime(2020, 1, 1, 0, 0, 0, tzinfo=tz) # will be treated as strictly <

    users = User.objects.annotate(totalDistance=Sum('workouts__distance', filter=Q(workouts__date__gte=start_date, workouts__date__lt=end_date)))

    return render(request, 'home.html', {
        'users': users,
        'start_date': start_date,
        'end_date': end_date,
    })
