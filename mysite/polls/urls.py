from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('polls/', views.polls_view, name='polls'),
    path('results/<poll_id>/', views.results_view, name='results'),
    path('vote/<poll_id>/', views.vote_view, name='vote'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('remove/<poll_id>/', views.remove_poll, name='remove-poll'),

]