from django.contrib import admin

from . import models

class VideoAdmin(admin.ModelAdmin):
    pass

class QueuedVideoAdmin(admin.ModelAdmin):
    pass

class VoteAdmin(admin.ModelAdmin):
    list_display = ('video', 'ip', 'vote', )

class LogAdmin(admin.ModelAdmin):
    pass

admin.site.register(models.Video, VideoAdmin)
admin.site.register(models.QueuedVideo, QueuedVideoAdmin)
admin.site.register(models.Vote, VoteAdmin)
admin.site.register(models.Log, LogAdmin)
