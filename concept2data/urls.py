"""concept2data URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from rowdata import views as rowdata_views

urlpatterns = [
    path('', rowdata_views.home, name='home'),
    path('about', rowdata_views.about, name='about'),
    # Monthly View
    path('months', rowdata_views.all_months, name='all_months'),
    path('months/month/<int:year>/<int:month>', rowdata_views.month, name='month'),

    # Data View
    path('months/month/data/<int:user_id>/<int:year>/<int:month>', rowdata_views.month_data, name='month_data'),

    # Race View
    path('races', rowdata_views.all_races, name='all_races'),
    path('races/race/<int:race_id>', rowdata_views.race, name='race'),

    path('admin/', admin.site.urls),
]
