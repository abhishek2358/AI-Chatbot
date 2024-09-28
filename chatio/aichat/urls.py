from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("home/", views.home, name="home"),
    path("chat/session/<int:session_id>/", views.chat_session, name="chat_session"),
    path("chat/new/", views.create_chat_session, name="create_chat_session"),
]