from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CreatePollForm
from .models import Poll, Vote
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
import random

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


def generate_poll_id(request) -> int:
    '''Generates a unique, random 8-digit id for a poll'''
    id = random.randint(10_000_000, 99_999_999)

    print('this is generated id:', id)
    for poll in Poll.objects.all():
        print(poll.id)
        if poll.id == id:
            generate_poll_id(request)

    return id

@csrf_protect
@login_required(login_url='login')
def home_view(request):
    '''
    Users can create polls with this.
    Takes the form inputs from home.html.
    The function binds the created poll to the authenticated user
    A random unique 8-digit id is generated for the poll 
    '''
    if request.method == 'POST':
        form = CreatePollForm(request.POST)

        if form.is_valid():
            poll = form.save(commit=False)
            poll.user = request.user
            poll.id = generate_poll_id(request)        
            poll.save()    
            return redirect('polls') # redirect to polls page after creating a poll

    return render(request, 'polls/home.html')

@csrf_protect
@login_required(login_url='login')
def polls_view(request):
    '''
    Users can see and vote for existing polls
    Users can remove their own polls (see remove_poll)
    '''
    polls = Poll.objects.all()
    context = {'polls': polls}

    return render(request, 'polls/polls.html', context)


@csrf_protect
@login_required(login_url='login')
def results_view(request, poll_id):
    '''
    Shows the voting result for selected poll.
    Uses the poll id to get the information for selected poll
    '''

    poll = Poll.objects.get(pk=poll_id)
    context =  {
        'poll': poll ,
        
    }

    return render(request, 'polls/results.html', context)


def user_has_voted(request : HttpResponse, poll_id : int) -> bool:
    '''
    Checks if a user has voted on the poll in question
    '''

    user = request.user
    poll = get_object_or_404(Poll, pk=poll_id)
    has_voted = Vote.objects.filter(user=user, poll=poll).exists()

    if has_voted:
        return True
    
    return False

@csrf_protect
@login_required(login_url='login')
def vote_view(request, poll_id):
    '''
    A vote view for selected poll
    Function keeps track if a user has voted for the poll in question.
    Users can only vote once per poll
    '''
    user = request.user
    poll = Poll.objects.get(pk=poll_id)
    context =  {
        'poll': poll ,
        'has_voted': False,
    }
    print('this is poll_id:', poll_id)
    #check the status if user voted
    if user_has_voted(request, poll.id):
            context =  {
            'poll': poll ,
            'has_voted': True,
            }
            return render(request, 'polls/vote.html', context) # return true to vote page if user has voted

    if request.method == 'POST':
        vote = request.POST['poll']
            
        if vote == 'option1': 
            poll.option_one_votes += 1 
            
        if vote == 'option2':
            poll.option_two_votes += 1
        
        if vote == 'option3':
            poll.option_three_votes += 1
        
        Vote.objects.get_or_create(user=user, poll=poll) # create an entry that a user has voted for a poll
        poll.save() #save the vote for poll and voting status for user
        
        return redirect('results', poll_id=poll_id)

    return render(request, 'polls/vote.html', context)


@csrf_protect
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

@csrf_protect
def login_view(request):
    '''
    Logs in a user if the credentials match with a user in database
    '''
    if request.method == 'POST':
        username = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=username, password=pwd)
        
        if user is not None:
            login(request, user)
            #otc logic here or redirect to otc page that redirects to home or login depending on success 
            return redirect('home')

    return render(request, 'polls/login.html')

@csrf_protect
@login_required(login_url='login')
def logout_view(request):
    '''
    Log out a user if there is a user logged in
    '''

    if request.user.is_authenticated:
        logout(request)
        return redirect('login')


def remove_poll(request, poll_id):
    ''' 
    Removes a poll from the polls list
    Users can only delete their own polls
    The ownership of the poll is checked in polls.html
    '''
    
    poll = Poll.objects.get(pk=poll_id)
    poll.delete()
    
    return redirect('polls')


def verify_login(request)-> int:
    '''
    Generate a one time code to login a user that has provided correct credentials
    Returns the code for now, might add it so that this function does the verif logic too
    '''
    # one-time code for the user
    # would be used with a 2FA app or via email, in this case just print the code
    otc = random.randint(10000, 99999)

    return otc


# This is sql injectable and should not be used in the correct version
from django.db import connection
def search_poll(request): #insecure example
    '''
    The function returns the search result of an ID that a user provides
    It returns a poll with a matching id or no poll at all
    Any user can search for a poll and vote for it
    '''

    user_input = request.GET.get("search_id")

    with connection.cursor() as cursor:
        
        #query the user input to find a matching poll
        query = "SELECT * FROM polls_poll WHERE id = '{}'".format(user_input)

        cursor.execute(query)
        connection.commit()
        rows = cursor.fetchall()

    polls = [{'id': row[0], 'question': row[1], 'option_one': row[2], 'option_two': row[3],
              'option_three': row[4], 'option_one_votes': row[5], 'option_two_votes': row[6],
              'option_three_votes': row[7]} for row in rows]

    context = {'polls': polls}
    return render(request, 'polls/search.html', context)



@csrf_exempt
def bad_vote_view(request, poll_id):
    '''
    Registers a user vote for a poll
    No login needed to vote 
    '''
    poll = Poll.objects.get(pk=poll_id)
    context =  {
        'poll': poll ,
        
    }

    if request.method == 'POST':
        vote = request.POST['poll']
            
        if vote == 'option1': 
            poll.option_one_votes += 1 
            
        if vote == 'option2':
            poll.option_two_votes += 1
        
        if vote == 'option3':
            poll.option_three_votes += 1
        
        poll.save() #save the vote for the poll
        
        return redirect('results', poll_id=poll_id)

    return render(request, 'polls/vote.html', context) #create a bad_vote.html and use it