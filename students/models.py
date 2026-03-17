from django.db import models
from django.conf import settings

class Student(models.Model):
    # Multi-tenancy: each student belongs to a user (teacher/admin)
    creator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_students')
    # Personal access: link student record to their login account
    user_profile = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='student_profile')
    name = models.CharField(max_length=255)
    student_id = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.student_id})"

class AcademicRecord(models.Model):
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='academic_records')
    attendance = models.FloatField(help_text="Attendance percentage")
    internal_marks = models.FloatField()
    assignment_scores = models.FloatField()
    participation_level = models.IntegerField(help_text="Scale 1-10")
    study_hours = models.FloatField()
    previous_semester_result = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

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
