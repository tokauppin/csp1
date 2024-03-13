from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@login_required(login_url='login')
def home_view(request):
    
    return render(request, 'polls/home.html')

def polls_view(request):
    return render(request, 'polls/create_poll.html')

def results_view(request):
    return render(request, 'polls/results.html')

def vote_view(request):
    return render(request, 'polls/vote.html')

@csrf_exempt
def login_view(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        pwd = request.POST['password']

        user = authenticate(request, username=username, password=pwd)
        if user is not None:
            print('user found')
            login(request, user)
            print('logged in')
            return redirect('home')


    return render(request, 'polls/login.html')


# @csrf_protect
@csrf_exempt
def register_view(request):
    '''
    Register a user if form data is valid
    '''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        

        if form.is_valid():
            form.save()

            return redirect('home')
    
    return render(request, 'polls/register.html')

@csrf_exempt
def logout_view(request):

    if request.user.is_authenticated:
        logout(request)
        return redirect('login')