from os import O_NDELAY

from django.conf import settings
from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)
from django.db import models

# Create your models here.


def upload_profile_path(instance, filename):
    ext = filename.split('.')[-1]
    return '/'.join(['profiles', str(instance.target_user.id)+str(instance.profile_name)+str(".")+str(ext)])


class UserManager(BaseUserManager):
    def create_user(self, email, password=None):
        if not email:
            raise ValueError('email is must')

        user = self.model(email=self.normalize_email(email))
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email, password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    last_name = models.CharField(max_length=50, blank=True, null=True)
    objects = UserManager()
    USERNAME_FIELD = 'email'

    def __str__(self):
        return self.email


class Category(models.Model):
    category_name = models.CharField(max_length=50, unique=True)


class Tag(models.Model):
    tag_name = models.CharField(max_length=50, unique=True)


class News(models.Model):
    select_category = models.ForeignKey(
        to=Category, related_name='select_category', on_delete=models.PROTECT)
    url = models.URLField(unique=True)
    title = models.CharField(max_length=200)
    summary = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    tags = models.ManyToManyField(to=Tag, related_name='tags', default=[])
