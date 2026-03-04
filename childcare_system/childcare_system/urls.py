from django.contrib import admin
from django.urls import path
from django.contrib.auth import views as auth_views
from core import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
]

urlpatterns += [
    path('children/', views.child_list, name='child_list'),
    path('children/create/', views.child_create, name='child_create'),
    path('children/<int:pk>/update/', views.child_update, name='child_update'),
    path('children/<int:pk>/delete/', views.child_delete, name='child_delete'),
]
