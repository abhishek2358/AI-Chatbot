from django.db import models

# Create your models here.

class chatSessions(models.Model):
    session_id = models.AutoField(primary_key=True)
    session_name = models.CharField(max_length=50)
    session_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.session_name

class chatMessages(models.Model):
    message_id = models.AutoField(primary_key=True)
    session_id = models.ForeignKey(chatSessions, on_delete=models.CASCADE)
    message = models.TextField()
    message_time = models.DateTimeField(auto_now_add=True)
    SENDER_CHOICES = (
        ('user', 'User'),
        ('bot', 'Bot')
    )
    sender = models.CharField(max_length=4, choices=SENDER_CHOICES)
    def __str__(self):
        return f'{self.sender}: {self.message[:20]}... ({self.message_time})'

class patient(models.Model):
    patient_id = models.AutoField(primary_key=True)
    patient_name = models.CharField(max_length=50)
    patient_email = models.EmailField()
    patient_phone = models.CharField(max_length=10)
    patient_dob = models.DateField(default='1999-05-19')
    patient_summary = models.TextField(default='No summary yet')
    patient_last_appointment = models.DateTimeField(default='2024-02-19')
    patient_next_appointment = models.DateTimeField(default='2024-03-19')
    patient_treatment_plan = models.TextField(default='Aspirin')
    patient_doctor = models.CharField(max_length=50, default='Dr. Adam Smith')


    def __str__(self):
        return self.patient_name


