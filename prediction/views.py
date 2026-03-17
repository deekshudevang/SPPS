from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from django.db.models import Avg, Count
from django.http import JsonResponse, HttpResponse
from accounts.models import User
from students.models import Student, AcademicRecord, Prediction, Feedback
from .predictor import Predictor
import json
import os

predictor = Predictor()



def login_view(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = authenticate(username=data.get('username'), password=data.get('password'))
        if user:
            login(request, user)
            return JsonResponse({'status': 'success', 'role': user.role})
        return JsonResponse({'status': 'error', 'message': 'Invalid credentials'}, status=400)
    return render(request, 'login.html')

@never_cache
@login_required
def logout_view(request):
    request.session.flush()
    request.session.clear()
    logout(request)
    response = redirect('login')
    response['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0'
    response['Pragma'] = 'no-cache'
    response['Expires'] = '0'
    return response

@login_required
def add_record(request):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('dashboard_router')
    
    if request.method == 'POST':
        # SaaS: Check student limit
        if not request.user.is_pro:
            count = Student.objects.filter(creator=request.user).count()
            if count >= request.user.get_student_limit():
                return HttpResponse("Student limit reached for Free plan. Upgrade to Pro for more.", status=403)
        
        try:
            student_id = request.POST.get('student_id')
            student = Student.objects.get(id=student_id, creator=request.user)
            
            record = AcademicRecord.objects.create(
                student=student,
                attendance=float(request.POST.get('attendance')),
                internal_marks=float(request.POST.get('internal_marks')),
                assignment_scores=float(request.POST.get('assignment_scores')),
                participation_level=int(request.POST.get('participation_level')),
                study_hours=float(request.POST.get('study_hours')),
                previous_semester_result=float(request.POST.get('previous_semester_result'))
            )
            
            # Automatically trigger prediction after adding record
            result_risk, result_score = predictor.predict(record)
            
            # Create a new prediction linked to the SPECIFIC record created
            prediction = Prediction.objects.create(
                student=student,
                academic_record=record,
                predicted_score=result_score,
                risk_level=result_risk
            )
            
            recommendation_text = predictor.get_recommendation(result_score)
            feedback = Feedback.objects.create(
                student=student,
                prediction=prediction,
                recommendation=recommendation_text
            )
            
            return render(request, 'prediction_result.html', {
                'prediction': prediction,
                'feedback': feedback
            })
        except Student.DoesNotExist:
            return HttpResponse("Error: Student not found.", status=404)
        except Exception as e:
            return HttpResponse(f"Error saving record: {e}", status=400)
            
    students = Student.objects.filter(creator=request.user)
    return render(request, 'add_record.html', {'students': students})

from django.db.models import Avg, Count

@login_required
def analytics_view(request):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('dashboard_router')
    
    # 1. Correlation Data: Attendance vs Predicted Score
    predictions = Prediction.objects.filter(student__creator=request.user).select_related('student', 'academic_record')
    correlation_data = []
    for p in predictions:
        if p.academic_record:
            correlation_data.append({
                'x': p.academic_record.attendance,
                'y': p.predicted_score,
                'label': p.student.name
            })
    
    # 2. Departmental Analytics
    dept_stats = Student.objects.filter(creator=request.user).values('department').annotate(
        avg_score=Avg('predictions__predicted_score'),
        student_count=Count('id')
    )
    
    # 3. Engagement Matrix: Study Hours vs Score
    engagement_data = []
    for p in predictions:
        if p.academic_record:
            engagement_data.append({
                'x': p.academic_record.study_hours,
                'y': p.predicted_score
            })
            
    # 4. Risk Breakdown by Attendance Brackets
    risk_brackets = {
        'Low (<75%)': Prediction.objects.filter(student__creator=request.user, academic_record__attendance__lt=75, risk_level='at_risk').count(),
        'Moderate (75-85%)': Prediction.objects.filter(student__creator=request.user, academic_record__attendance__range=(75, 85), risk_level='at_risk').count(),
        'High (>85%)': Prediction.objects.filter(student__creator=request.user, academic_record__attendance__gt=85, risk_level='at_risk').count(),
    }

    context = {
        'correlation_json': json.dumps(correlation_data),
        'engagement_json': json.dumps(engagement_data),
        'dept_stats': dept_stats,
        'risk_brackets': risk_brackets,
        'total_analyzed': predictions.count()
    }
    return render(request, 'analytics.html', context)

@login_required
def settings_view(request):
    return render(request, 'settings.html')

@login_required
def lab_simulation(request):
    if request.user.role not in ['teacher', 'admin']:
        return redirect('dashboard_router')
    
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Mock record for predictor
            from collections import namedtuple
            SimRecord = namedtuple('SimRecord', ['attendance', 'internal_marks', 'assignment_scores', 'participation_level', 'study_hours', 'previous_semester_result'])
            record = SimRecord(
                attendance=float(data.get('attendance', 0)),
                internal_marks=float(data.get('internal_marks', 0)),
                assignment_scores=float(data.get('assignment_scores', 0)),
                participation_level=int(data.get('participation_level', 0)),
                study_hours=float(data.get('study_hours', 0)),
                previous_semester_result=float(data.get('previous_semester_result', 0))
            )
            
            risk, score = predictor.predict(record)
            recommendation = predictor.get_recommendation(score)
            
            return JsonResponse({
                'status': 'success',
                'risk_level': risk,
                'score': round(score, 1),
                'recommendation': recommendation
            })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
            
    return render(request, 'teacher_lab.html')

def get_institutional_metrics(user):
    # Filter by creator for multi-tenancy, but if admin, show all
    if user.role == 'admin':
        students_qs = Student.objects.all()
        predictions_qs = Prediction.objects.all()
    else:
        students_qs = Student.objects.filter(creator=user)
        predictions_qs = Prediction.objects.filter(student__creator=user)
        
    total_students = students_qs.count()
    at_risk_count = predictions_qs.filter(risk_level='at_risk').count()
    high_perf_count = predictions_qs.filter(risk_level='high').count()
    average_count = predictions_qs.filter(risk_level='average').count()
    
    avg_score = predictions_qs.aggregate(Avg('predicted_score'))['predicted_score__avg'] or 0
    
    # For the bar chart: Top 5 students by score
    top_students = predictions_qs.select_related('student').order_by('-predicted_score')[:5]
    top_students_data = [
        {'name': p.student.name, 'score': round(p.predicted_score, 1)} 
        for p in top_students
    ]
    
    performance_counts = {
        'at_risk': at_risk_count,
        'average': average_count,
        'high': high_perf_count
    }
    
    dept_stats = list(students_qs.values('department').annotate(
        avg_score=Avg('predictions__predicted_score'),
        student_count=Count('id')
    ).order_by('-avg_score'))
    
    return {
        'total_students': total_students,
        'performance_counts': performance_counts,
        'avg_score': round(avg_score, 1),
        'top_students_json': json.dumps(top_students_data),
        'predictions': predictions_qs.select_related('student')[:10],  # Limit for dashboard
        'dept_stats': dept_stats
    }

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        return redirect('dashboard_router')
    
    metrics_data = get_institutional_metrics(request.user)
    
    # Load ML metrics and pre-calculate percentages
    metrics_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'ml', 'metrics.json')
    ml_metrics = {}
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r', encoding='utf-8') as f:
            raw_metrics = json.load(f)
            for name, m in raw_metrics.items():
                acc = m.get('accuracy') or m.get('precision') or 0
                ml_metrics[name] = {
                    'accuracy': f"{acc*100:.1f}%",
                    'precision': f"{m.get('precision', 0)*100:.1f}%",
                    'recall': f"{m.get('recall', 0)*100:.1f}%",
                    'f1_score': f"{m.get('f1_score', 0)*100:.1f}%",
                    'precision_raw': m.get('precision', 0) * 100
                }
            
    # Calculate percentages for Risk Matrix
    perf_counts = metrics_data['performance_counts']
    total_perf = sum(perf_counts.values()) or 1
    performance_percentages = {
        k: (v / total_perf) * 100 for k, v in perf_counts.items()
    }

    context = {
        **metrics_data,
        'performance_percentages': performance_percentages,
        'at_risk_count': perf_counts['at_risk'],
        'ml_metrics': ml_metrics
    }
    return render(request, 'dashboard_admin.html', context)

@never_cache
@login_required
def dashboard_router(request):
    if request.user.role == 'student':
        return redirect('student_dashboard')
    elif request.user.role == 'teacher':
        return redirect('admin_dashboard' if request.user.role == 'admin' else 'teacher_dashboard')
    elif request.user.role == 'admin':
        return redirect('admin_dashboard')
    else:
        return redirect('admin_dashboard')

@never_cache
@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        return redirect('dashboard_router')
    
    student = request.user.student_profile
    latest_prediction = Prediction.objects.filter(student=student).order_by('-created_at').first()
    latest_feedback = Feedback.objects.filter(student=student).order_by('-created_at').first()
    academic_records = AcademicRecord.objects.filter(student=student).order_by('-created_at')
    
    context = {
        'student': student,
        'prediction': latest_prediction,
        'feedback': latest_feedback,
        'academic_records': academic_records
    }
    return render(request, 'dashboard_student.html', context)

@never_cache
@login_required
def faculty_dashboard(request):
    if request.user.role != 'teacher':
        return redirect('dashboard_router')
    
    metrics_data = get_institutional_metrics(request.user)
    students = Student.objects.filter(creator=request.user)
    # Using Predictions filtered by the metrics logic
    
    context = {
        **metrics_data,
        'at_risk_count': metrics_data['performance_counts']['at_risk'],
        'students': students,
    }
    return render(request, 'dashboard_teacher.html', context)

@login_required
def run_prediction(request, student_id):
    if request.user.role not in ['teacher', 'admin']:
        return JsonResponse({'error': 'Unauthorized'}, status=403)
    
    student = Student.objects.get(id=student_id)
    latest_record = AcademicRecord.objects.filter(student=student).order_by('-created_at').first()
    
    if not latest_record:
        return JsonResponse({'error': 'No academic records found for this student'}, status=400)
    
    data = {
        'attendance': latest_record.attendance,
        'internal_marks': latest_record.internal_marks,
        'assignment_scores': latest_record.assignment_scores,
        'participation_level': latest_record.participation_level,
        'study_hours': latest_record.study_hours,
        'previous_semester_result': latest_record.previous_semester_result
    }
    
    result = predictor.predict(data)
    
    prediction = Prediction.objects.create(
        student=student,
        academic_record=latest_record,
        predicted_score=result['predicted_score'],
        risk_level=result['risk_level']
    )
    
    rec_text = predictor.get_recommendation(result['predicted_score'])
    Feedback.objects.create(
        student=student,
        prediction=prediction,
        recommendation=rec_text
    )
    
    return JsonResponse({
        'status': 'success',
        'risk_level': result['risk_level'],
        'score': result['predicted_score']
    })
