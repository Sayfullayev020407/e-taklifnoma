from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('create_invitation/<int:category_id>/', views.create_invitation, name='create_invitation'),
    path('my_invitations/', views.my_invitations, name='my_invitations'),
    path('invitation/<int:invitation_id>/', views.invitation_detail, name='invitation_detail'),
    path('invitation/<int:invitation_id>/edit/', views.edit_invitation, name='edit_invitation'),
    path('invitation/<int:invitation_id>/delete/', views.delete_invitation, name='delete_invitation'),
    path('invitation/<str:unique_url>/', views.invitation_page, name='invitation_page'),
    path('invitation/<int:invitation_id>/send/image/', views.send_image, name='send_image'),
    path('invitation/<int:invitation_id>/send/video/', views.send_image, name='send_video'),
    path('profile/', views.profile, name='profile'),
]