import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from accounts.models import User, Subscription
from students.models import Student, AcademicRecord, Prediction, Feedback

def seed():
    # Helper to create/update user with password
    def create_user(username, email, password, role, is_pro=False, is_staff=False, is_superuser=False):
        u = User.objects.filter(username=username).first()
        if not u:
            u = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                role=role,
                is_pro=is_pro,
                is_staff=is_staff,
                is_superuser=is_superuser
            )
            print(f"Created user: {username}")
        else:
            u.set_password(password)
            u.role = role
            u.is_pro = is_pro
            u.is_staff = is_staff
            u.is_superuser = is_superuser
            u.save()
            print(f"Updated user: {username}")
            
        Subscription.objects.update_or_create(user=u, defaults={'plan_name': 'Pro' if is_pro else 'Free'})
        return u

    # 1. Admin Account (Pro)
    admin = create_user('admin', 'admin@edupredict.ai', 'admin123', 'admin', is_pro=True, is_staff=True, is_superuser=True)
    
    # 2. Teacher Account (Free)
    teacher = create_user('teacher', 'teacher@demo.com', 'teacher123', 'teacher', is_pro=False)
    
    # 3. Create 5 Students (student1 to student5) - Link them to Teacher to show data in Teacher Hub
    print("\nSeeding Students...")
    depts = ['Computer Science', 'Electronics', 'Mechanical', 'Civil', 'Information Technology']
    
    for i in range(1, 6):
        username = f'student{i}'
        password = f'student{i}'
        stu_user = create_user(username, f'{username}@demo.com', password, 'student', is_pro=False)
        
        # Create Student Record for each student (owned by teacher for demo)
        s, _ = Student.objects.update_or_create(
            student_id=f'STU00{i}',
            defaults={
                'name': f'Demo Student {i}',
                'department': random.choice(depts),
                'creator': teacher, # GIVE DATA TO TEACHER
                'user_profile': stu_user
            }
        )
        
        # Add Academic Record
        ar, _ = AcademicRecord.objects.get_or_create(
            student=s,
            defaults={
                'attendance': random.uniform(60, 95),
                'internal_marks': random.uniform(40, 90),
                'assignment_scores': random.uniform(50, 90),
                'participation_level': random.randint(4, 10),
                'study_hours': random.uniform(2, 8),
                'previous_semester_result': random.uniform(55, 85)
            }
        )
        
        # Add Prediction
        score = random.uniform(40, 90)
        risk = 'at_risk' if score < 60 else 'average' if score < 80 else 'high'
        p, _ = Prediction.objects.get_or_create(
            student=s,
            academic_record=ar,
            defaults={'predicted_score': score, 'risk_level': risk}
        )
        
        # Add Feedback
        Feedback.objects.get_or_create(
            student=s,
            prediction=p,
            defaults={'recommendation': "Improve consistency in study hours."}
        )

    print("\n✅ Seeding complete. VERIFIED ACCESS:")
    print("-" * 30)
    print("ADMIN (Pro):    admin   / admin123")
    print("STUDENTS:       student1 / student1  ...to... student5 / student5")
    print("-" * 30)
    print("TEACHER (Free): teacher / teacher123 (OWNER OF ALL 5 STUDENTS)")
    print("-" * 30)

if __name__ == '__main__':
    seed()
