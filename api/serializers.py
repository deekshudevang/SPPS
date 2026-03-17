from rest_framework import serializers
from students.models import Student, AcademicRecord, Prediction, Feedback

class AcademicRecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = AcademicRecord
        fields = '__all__'

class PredictionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prediction
        fields = '__all__'

class StudentSerializer(serializers.ModelSerializer):
    academic_records = AcademicRecordSerializer(many=True, read_only=True)
    predictions = PredictionSerializer(many=True, read_only=True)
    
    class Meta:
        model = Student
        fields = ['id', 'name', 'student_id', 'department', 'academic_records', 'predictions', 'created_at']
        read_only_fields = ['creator']
