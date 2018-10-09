from django.contrib import admin
from django.urls import path

from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.IndexView.as_view(), name = 'index'),
    path('fullscreen', views.FullscreenView.as_view(), name = 'fullscreen'),
    path('vote', views.VoteView.as_view(), name = 'vote'),
    path('vote-inline', views.VoteInlineView.as_view(), name = 'vote-inline'),
    path('suggest', views.SuggestView.as_view(), name = 'suggest'),
    path('submit-vote/<int:id>/<str:way>/', views.SubmitVoteView.as_view(), name = 'submit-vote'),
    path('info', views.InfoView.as_view(), name = 'info'),
    path('skip', views.SkipView.as_view(), name = 'skip'),
    path('presence', views.PresenceView.as_view(), name = 'presence'),
    path('log', views.LogView.as_view(), name = 'log'),
    path('chat', views.ChatView.as_view(), name = 'chat'),
]
