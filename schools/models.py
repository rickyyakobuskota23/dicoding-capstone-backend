from django.db import models
from users.models import Teacher

class School(models.Model):
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Classroom(models.Model):
    school = models.ForeignKey(School, on_delete=models.CASCADE, related_name='classrooms')
    name = models.CharField(max_length=100) # e.g., "Grade 5A"
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='classrooms')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.school.name}"

class Student(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='students')
    name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=50, blank=True) # Official student ID
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
