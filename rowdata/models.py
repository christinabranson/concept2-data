from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.base_user import AbstractBaseUser
from django.utils.translation import ugettext_lazy as _
from django.contrib.auth.base_user import BaseUserManager
from django.conf import settings

class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """
        Creates and saves a User with the given email and password.
        """
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_staff', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(_('email address'), unique=True)
    first_name = models.CharField(_('first name'), max_length=255, blank=True)
    last_name = models.CharField(_('last name'), max_length=255, blank=True)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)
    is_active = models.BooleanField(_('active'), default=True)
    is_staff = models.BooleanField( _('staff status'), default=False, help_text=_('Designates whether the user can log into this site.'))
    monthly_goal = models.IntegerField(default=100000, help_text=_('Monthly goal (m)'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def get_full_name(self):
        '''
        Returns the first_name plus the last_name, with a space in between.
        '''
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        '''
        Returns the short name for the user.
        '''
        return self.first_name

    def get_total_distance(self, start_date, end_date):
        from django.db.models import Sum
        return self.workouts.filter(date__gte=start_date).filter(date__lt=end_date).aggregate(Sum('distance'))

    def get_icon_name(self):
        return "boatr.png"
        if self.pk == 1:
            return "C-sprite.png"
        else:
            return "I-sprite.png"

# Create your models here.
class Workout(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='workouts', on_delete=models.CASCADE, null=False)
    date = models.DateTimeField(auto_now=False)
    distance = models.CharField(max_length=255)
    time = models.CharField(max_length=255, blank=True)
    pace = models.CharField(max_length=255, blank=True)

    def __str__(self):
        dateString = str(self.date)
        return dateString

# Create your models here.
class Race(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='races', on_delete=models.CASCADE, null=False)
    name = models.CharField(max_length=255, blank=False)
    description = models.TextField(blank=True)
    start_date = models.DateTimeField(auto_now=False)
    end_date = models.DateTimeField(auto_now=False, blank=True, null=True)
    distance = models.CharField(max_length=255, blank=True, help_text=_('Optional. If entered, race will end once one user reaches the distance'))

    def __str__(self):
        return self.name