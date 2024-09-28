from django.contrib import admin
from .models import chatSessions, chatMessages, patient

# Register your models here.
admin.site.register(chatSessions)
admin.site.register(chatMessages)
admin.site.register(patient)

