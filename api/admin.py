from django.contrib import admin

from .models import Category, News, Tag, User

# Register your models here.

admin.site.register(User)
admin.site.register(Category)
admin.site.register(Tag)
admin.site.register(News)
