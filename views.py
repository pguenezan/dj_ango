from django.conf import settings
from django.db import IntegrityError
from django.http import JsonResponse
from django.views.generic import View
from django.shortcuts import redirect, render

from . import models

import requests
from isodate import parse_duration
import datetime

def get_default_context():
    context = {}
    context['title'] = 'DJ Ango'
    return context

class IndexView(View):
    template_name = 'front/index.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        context['video'] = models.QueuedVideo.objects.first()
        return render(request, self.template_name, context)

class VoteView(View):
    template_name = 'front/vote.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        context['queued'] = models.QueuedVideo.objects.all()
        return render(request, self.template_name, context)

class VoteInlineView(View):
    template_name = 'front/vote_iframe.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        context['queued'] = models.QueuedVideo.objects.all()
        return render(request, self.template_name, context)

def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0]
    return request.META.get('REMOTE_ADDR')

class SubmitVoteView(View):

    def get(self, request, *args, **kwargs):
        if kwargs['way'] != 'up' and kwargs['way'] != 'down':
            return redirect('vote')
        video = models.QueuedVideo.objects.filter(id = kwargs['id']).first()
        if video is None:
            return redirect('vote')
        if 'ip' in request.GET:
            ip = request.GET['ip']
        else:
            ip = get_client_ip(request)
        if not ip.startswith('10.224.32.'):
            return redirect('vote')
        vote_weight = 2 if kwargs['way'] == 'up' else -1
        old_vote = models.Vote.objects.filter(video = video, ip = ip).first()
        if old_vote is not None:
            if old_vote.vote == vote_weight:
                return redirect('vote')
            video.total_vote -= old_vote.vote
            if old_vote.vote > 0:
                video.up_vote -= 1
            else:
                video.down_vote -= 1
            old_vote.delete()
        vote = models.Vote(video = video, ip = ip, vote = vote_weight)
        vote.save()
        if vote_weight > 0:
            video.up_vote += 1
        else:
            video.down_vote += 1
        video.total_vote += vote_weight
        video.save()
        return redirect('vote')

def get_video_details(video_id):
    r = requests.get(f'https://www.googleapis.com/youtube/v3/videos?id={ video_id }&key={ settings.YOUTUBE_API_KEY }&part=snippet,ContentDetails')
    json = r.json()['items'][0]
    return (json['snippet']['title'], json['snippet']['channelTitle'], json['contentDetails']['duration'])

class SuggestView(View):
    template_name = 'front/suggest.html'

    def get(self, request, *args, **kwargs):
        if 'url' in request.GET:
            if len(request.GET['url']) < 11:
                return redirect('vote')
            video_id = request.GET['url'][-11:]
            video = models.Video.objects.filter(video_id = video_id).first()
            if video is None:
                try:
                    title, channel, duration = get_video_details(video_id)
                except IndexError:
                    return redirect('vote')
                duration = parse_duration(duration)
                if duration.total_seconds() > 10 * 60:
                    duration = datetime.timedelta(minutes = 10)
                video = models.Video(video_id = video_id, title = title, duration = duration, channel = channel)
                video.save()
            if video.banned:
                return redirect('vote')
            queued = models.QueuedVideo.objects.filter(video = video).first()
            if queued is not None:
                return redirect('submit-vote', queued.id, 'up')
            queued = models.QueuedVideo(video = video)
            queued.save()
            return redirect('vote')
        return render(request, self.template_name, get_default_context())

class FullscreenView(View):
    template_name = 'front/fullscreen.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        context['video'] = models.QueuedVideo.objects.first()
        return render(request, self.template_name, context)

class InfoView(View):

    def get(selt, request, *args, **kwargs):
        json = {}
        queued = models.QueuedVideo.objects.first()
        if queued is None:
            json['seek_to'] = -1
            return JsonResponse(json)
        json['seek_to'] = queued.seek_to
        json['video_id'] = queued.video.video_id
        return JsonResponse(json)

class SkipView(View):

    def get(selt, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('index')
        queued = models.QueuedVideo.objects.first()
        if queued is not None:
            msg = request.user.username + ' has skip ' + queued.video.title
            log = models.Log(message = msg)
            log.save()
            queued.delete()
        return redirect('index')

class PresenceView(View):

    def get(selt, request, *args, **kwargs):
        if not request.user.is_staff:
            return redirect('index')
        video = models.Video.objects.get(id = 2)
        queue = models.QueuedVideo(video = video)
        queue.total_vote = 999
        queue.is_playing = True
        queue.save()
        return redirect('index')

class LogView(View):
    template_name = 'front/log.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        context['logs'] = models.Log.objects.order_by('-time')
        return render(request, self.template_name, context)

class ChatView(View):
    template_name = 'front/chat.html'

    def get(self, request, *args, **kwargs):
        context = get_default_context()
        return render(request, self.template_name, context)
