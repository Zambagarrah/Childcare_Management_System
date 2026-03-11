from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),  # <-- new home route
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

urlpatterns += [
    path('children/', views.child_list, name='child_list'),
    path('children/create/', views.child_create, name='child_create'),
    path('children/<int:child_id>/update/', views.child_update, name='child_update'),
    path('children/<int:child_id>/delete/', views.child_delete, name='child_delete'),

]

urlpatterns += [
    path('reports/children/', views.child_report, name='child_report'),
    # path('reports/children/<int:child_id>/notes/', views.care_notes_report, name='care_notes_report'),
    path('children/<int:child_id>/notes/', views.care_notes, name='care_notes'),
]

urlpatterns += [
    path('inbox/', views.inbox, name='inbox'),
    path('send/<int:recipient_id>/', views.send_message, name='send_message'),
    path('sent/', views.sent_messages, name='sent_messages'),
]

urlpatterns += [
    path('children/<int:child_id>/activities/', views.activity_list, name='activity_list'),
    path('children/<int:child_id>/activities/add/', views.add_activity, name='add_activity'),
]

urlpatterns += [
    path('reports/summary/', views.reporting_summary, name='reporting_summary'),
    path('reports/summary/export/csv/', views.export_summary_csv, name='export_summary_csv'),
    path('reports/summary/export/pdf/', views.export_summary_pdf, name='export_summary_pdf'),
]

urlpatterns += [
    path('dashboard/', views.dashboard, name='dashboard'),
]

