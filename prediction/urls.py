from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard_router, name='dashboard_router'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('student/dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('mission-control/', views.admin_dashboard, name='admin_dashboard'),
    path('predict/<int:student_id>/', views.run_prediction, name='run_prediction'),
    path('record/add/', views.add_record, name='add_record'),
    path('analytics/', views.analytics_view, name='analytics'),
    path('lab/', views.lab_simulation, name='faculty_lab'),
    path('settings/', views.settings_view, name='settings'),
]
