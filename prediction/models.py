from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='student')

class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.student_id})"

class AcademicRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_records')
    attendance = models.FloatField(help_text="Attendance percentage")
    internal_marks = models.FloatField()
    assignment_scores = models.FloatField()
    participation_level = models.IntegerField(help_text="Scale 1-10")
    study_hours = models.FloatField()
    previous_semester_result = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Record for {self.student.student_id} - {self.created_at.date()}"

class Prediction(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='predictions')
    academic_record = models.OneToOneField(AcademicRecord, on_delete=models.CASCADE)
    predicted_score = models.FloatField()
    risk_level = models.CharField(max_length=20, choices=(
        ('high', 'High Performance'),
        ('average', 'Average Performance'),
        ('at_risk', 'At Risk'),
    ))
    created_at = models.DateTimeField(auto_now_add=True)

class Feedback(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='feedbacks')
    prediction = models.OneToOneField(Prediction, on_delete=models.CASCADE)
    recommendation = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
