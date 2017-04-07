from django.contrib import admin
from .models import HashTag, Battle


class HashTagAdmin(admin.ModelAdmin):
    pass


class BattleAdmin(admin.ModelAdmin):
    pass

admin.site.register(Battle, BattleAdmin)
admin.site.register(HashTag, HashTagAdmin)
