from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CreatePollForm
from .models import Poll, Vote
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


@csrf_protect
@login_required(login_url='login')
def home_view(request):
    '''
    Users can create polls with this.
    Takes the form inputs from home.html.
    The function binds the created poll to the authenticated user
    '''
    if request.method == 'POST':
        form = CreatePollForm(request.POST)

        if form.is_valid():
            poll = form.save(commit=False)
            poll.user = request.user
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


def verify_login(request):





    return redirect('')
# csrf protection
# page restriction

from django.db import connection

#SELECT * FROM poll WHERE id = '0'; DELETE FROM poll; --'
''''
testing sql injection for insecure design
'''
def search_poll(request):
    # Get the user can search for a poll by its id
    user_input = request.GET.get("search_id")

    with connection.cursor() as cursor:
        #find any polls with the id
        query = f"SELECT * FROM polls_poll WHERE question LIKE '%{user_input}%'"

        # query = f"SELECT * FROM polls_poll WHERE id = '{user_input}'"
        cursor.execute(query)
        # results = cursor.fetchall()
        # print(results)
    # Process results and return response
        rows = cursor.fetchall()

    # Assuming your Poll model has these fields
    polls = [{'id': row[0], 'question': row[1], 'option_one': row[2], 'option_two': row[3],
              'option_three': row[4], 'option_one_votes': row[5], 'option_two_votes': row[6],
              'option_three_votes': row[7]} for row in rows]
    print(polls)

    context = {'polls': polls}
    return render(request, 'polls/search.html', context)