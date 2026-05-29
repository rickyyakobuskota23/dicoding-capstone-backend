from django.db import models
from users.models import Teacher

class Resource(models.Model):
    RESOURCE_TYPE_CHOICES = [
        ('worksheet', 'Worksheet'),
        ('presentation', 'Presentation'),
        ('video', 'Video'),
        ('article', 'Article'),
        ('other', 'Other'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    resource_type = models.CharField(max_length=20, choices=RESOURCE_TYPE_CHOICES)
    file_url = models.URLField(max_length=500, blank=True)
    content = models.TextField(blank=True) # For AI generated text content
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='resources')
    
    subject = models.CharField(max_length=100, blank=True)
    grade_level = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title
