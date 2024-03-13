from django.urls import path
from . import views


urlpatterns = [
    path('', views.home_view, name='home'),
    path('create_poll/', views.polls_view, name='create-poll'),
    path('results/', views.results_view, name='results'),
    path('vote/', views.vote_view, name='vote'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

]