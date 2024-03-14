from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CreatePollForm
from .models import Poll
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


'''
ngfdsngdsljnGLKSD
'''
@csrf_exempt
@login_required(login_url='login')
def home_view(request):
    '''
    Users can create a question and the answers to it 
    '''
    if request.method == 'POST':
        form = CreatePollForm(request.POST)

        if form.is_valid():
            poll = form.save(commit=False)
            poll.user = request.user
            poll.save()            
            return redirect('polls')

    return render(request, 'polls/home.html')


def polls_view(request):
    '''
    Flaw design: see all polls and edit all polls
    correct: See your own polls and search for polls with certain poll id to vote 
    or only remove your own polls, you can vote on all polls
    '''
    polls = Poll.objects.all()
    context = {'polls': polls}

    return render(request, 'polls/polls.html', context)


@csrf_exempt
def results_view(request, poll_id):
    return render(request, 'polls/results.html')

@csrf_exempt
def vote_view(request, poll_id):
    '''
    vote view for selected poll
    Users can only vote once per poll
    
    '''
    
    poll = Poll.objects.get(pk=poll_id)
    context =  {
        'poll': poll ,
        'has_voted': poll.user_has_voted
    }
    
    if poll.user_has_voted:
            print('you have voted')
            return render(request, 'polls/vote.html', context)

    if request.method == 'POST':

        vote = request.POST['poll']
            
        if vote == 'option1': 
            poll.option_one_votes += 1 
            
        if vote == 'option2':
            poll.option_two_votes += 1
        
        if vote == 'option3':
            poll.option_three_votes += 1
        poll.user_has_voted = True
        poll.save()
        
        return redirect('results', poll_id=poll_id)

    return render(request, 'polls/vote.html', context)

@csrf_exempt
def login_view(request):
    '''
    Logs in a user if the credentials match with a user in database
    '''
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

@csrf_exempt
def register_view(request):
    '''
    Register a user if form data is valid
    '''
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        

        if form.is_valid():
            form.save()

            return redirect('login')

    return render(request, 'polls/register.html')

@csrf_exempt
def logout_view(request):
    '''
    Logs out the user if the user is auhtenticated
    '''
    if request.user.is_authenticated:
        logout(request)
        return redirect('login')

def remove_poll(request, poll_id):
    ''' remove selected poll, add verification lol :D '''
    
    poll = Poll.objects.get(pk=poll_id)
    poll.delete()
    
    return redirect('polls')
'''
Corrected version
'''

# csrf protection
# page restriction


