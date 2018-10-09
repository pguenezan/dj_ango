from django.db import models

from datetime import datetime, timedelta


class Video(models.Model):
    title = models.TextField()
    video_id = models.CharField(max_length=11, unique=True)
    banned = models.BooleanField(default=False)
    duration = models.DurationField()
    channel = models.CharField(max_length=120)

    def __str__(self):
        return self.title


class QueuedVideoManager(models.Manager):

    def get_queryset(self):
        return super(QueuedVideoManager, self).get_queryset().
    order_by('-is_playing', '-total_vote', '-queued')


class QueuedVideo(models.Model):
    video = models.OneToOneField('Video',
                                 on_delete=models.CASCADE, unique=True)
    up_vote = models.PositiveIntegerField(default=0)
    down_vote = models.PositiveIntegerField(default=0)
    total_vote = models.IntegerField(default=0)
    queued = models.DateTimeField(auto_now_add=True)

    seek_to = models.FloatField(default=0)
    is_playing = models.BooleanField(default=False)

    objects = QueuedVideoManager()

    def __str__(self):
        return self.video.title


class Vote(models.Model):
    video = models.ForeignKey('QueuedVideo', on_delete=models.CASCADE)
    ip = models.GenericIPAddressField()
    vote = models.IntegerField()

    def __str__(self):
        return str(self.video) + '@' + self.ip

    class Meta:
        unique_together = ('video', 'ip', )


class Log(models.Model):
    message = models.TextField()
    time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
