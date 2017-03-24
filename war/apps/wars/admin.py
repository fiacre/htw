from django.contrib import admin
from .models import HashTag, Tweet


class TweetAdmin(admin.ModelAdmin):
    pass


class HashTagAdmin(admin.ModelAdmin):
    pass


admin.site.register(Tweet, TweetAdmin)
admin.site.register(HashTag, HashTagAdmin)
