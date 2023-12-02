from django.urls import path
from . import views

urlpatterns = [
    # Define your app's URL patterns here
    path('', views.index, name='index'),
    path('login/', views.login_user, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_user, name='logout'),
    path('users/', views.show_users, name='users'),
    path('note/', views.create_note, name='create_note'),
    path('note/<int:pk>/delete', views.delete_note, name='delete_note'),
    path('note/<int:pk>/edit', views.edit_note, name='edit_note'),
    path('note/<int:pk>/print', views.print_note, name='print_note'),

    path('user/<int:id_user>/delete', views.delete_user, name='delete_user'),
    path('user/<int:id_user>/edit', views.edit_user, name='edit_user'),
    path('print-notes/',views.print_all_notes,name='print_all_notes')

    # Add more paths as needed print_all_notes
]