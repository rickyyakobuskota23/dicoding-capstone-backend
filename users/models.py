from django.db import models

class Teacher(models.Model):
    clerk_id = models.IntegerField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    avatar = models.CharField(max_length=10, blank=True) # e.g., "SJ"
    color = models.CharField(max_length=100, default="from-blue-500 to-blue-600")
    subjects = models.JSONField(default=list)

    def __str__(self):
        return self.name