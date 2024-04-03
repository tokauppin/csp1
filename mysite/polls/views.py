from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from .forms import CustomUserCreationForm, CreatePollForm
from .models import Poll, Vote, CustomUser
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required

import random
import pyotp
from datetime import datetime, timedelta

def generate_poll_id(request) -> int:
    '''Generates a unique, random 8-digit id for a poll'''
    id = random.randint(10_000_000, 99_999_999)

    for poll in Poll.objects.all():
        if poll.id == id:
            generate_poll_id(request)

    return id

#we need to replace all functions that have @csrf_exempt with @csrf_protect
@csrf_exempt
@login_required(login_url='login')
def home_view(request):
    '''
    Users can create polls with this.
    Takes the form inputs from home.html.
    The function binds the created poll to the authenticated user
    A random unique 8-digit id is generated for the poll 
    '''

    try:

        if request.session['username']:
            #delete the extra session created
            del request.session['username']

    except KeyError:
        pass
    if request.method == 'POST':
        form = CreatePollForm(request.POST)

        if form.is_valid():
            poll = form.save(commit=False)
            poll.user = request.user
            poll.id = generate_poll_id(request)        
            poll.save()    
            return redirect('polls') # redirect to polls page after creating a poll

    return render(request, 'polls/home.html')

@csrf_exempt
@login_required(login_url='login')
def polls_view(request):
    '''
    Users can see and vote for existing polls
    Users can remove their own polls (see remove_poll)
    '''

    # polls = Poll.objects.filter(user=request.user) #returns only the polls of the authenticated user
    polls = Poll.objects.all() #remove this

    context = {'polls': polls}
    
    return render(request, 'polls/polls.html', context)


@csrf_exempt
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


def user_has_voted(request, poll_id) -> bool:
    '''
    Checks if a user has voted on the poll in question using sessions
    Function keeps track if a user has voted for the poll in question.
    Users can only vote once per poll
    '''

    
    if request.session.get(f'has_voted_{poll_id}', False):
        return True
    
    return False

    #This checks for authenticated users if they have voted
    # user = request.user
    # poll = get_object_or_404(Poll, pk=poll_id)
    # has_voted = Vote.objects.filter(user=user, poll=poll).exists()

    # if has_voted:
    #     return True
    
    # return False

@csrf_exempt
# @login_required(login_url='login')
def vote_view(request, poll_id):
    '''
    A vote view for selected poll

    '''
    user = request.user
    poll = Poll.objects.get(pk=poll_id)
    context =  {
        'poll': poll ,
        'has_voted': False,
    }
    
    #check the status if user voted
    # if user_has_voted(request, poll.id): #un-commenting this will enable the check if a user has voted
    #         context =  {
    #         'poll': poll ,
    #         'has_voted': True,
    #         }
    #         return render(request, 'polls/vote.html', context) # return true to vote page if user has voted

    if request.method == 'POST':
        vote = request.POST['poll']
            
        if vote == 'option1': 
            poll.option_one_votes += 1 
            
        if vote == 'option2':
            poll.option_two_votes += 1
        
        if vote == 'option3':
            poll.option_three_votes += 1

        # request.session[f'has_voted_{poll_id}'] = True #marks that the current user session has voted
        # Vote.objects.get_or_create(user=user, poll=poll) # create an entry that an authenticated user has voted for a poll
        poll.save() #save the vote for poll and voting status for user
        
        return redirect('results', poll_id=poll_id)

    return render(request, 'polls/vote.html', context)


@csrf_exempt
def register_view(request):
    '''
    Register a user if form data is valid
    '''
    #redirect users if they are already logged in
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        
        if form.is_valid():
            form.save()
            return redirect('login')

    return render(request, 'polls/register.html')

@csrf_exempt
def login_view(request):
    '''
    If credentials matches, the user will be directed to a login verification
    page where a one time code needs to be provided in order to login
    '''
    #redirect users if they are already logged in
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        username = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(request, username=username, password=pwd)
        
        if user is not None:
            # create the 2FA code and redirect to the verification page
            generate_verification_code(request)
            request.session['username'] = username
            return redirect('verify')

    return render(request, 'polls/login.html')

@csrf_exempt
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
    The ownership of the poll is checked in polls_view
    '''
    
    poll = Poll.objects.get(pk=poll_id)
    poll.delete()
    
    return redirect('polls')


def generate_verification_code(request):
    '''
    Generates a one time code OTC that is valid for x seconds defined in the interval
    Assigns the secret key and time created to the request session
    '''
    totp = pyotp.TOTP(pyotp.random_base32(), interval=60) #code is valid for 60s
    otc = totp.now()
    request.session['otc_secret_key'] = totp.secret
    valid_until = datetime.now() + timedelta(minutes=1)
    request.session['otc_valid_until'] = str(valid_until) 

    # would be used with a 2FA app or via email, in this case just print the code
    print(f'Your verification code: {otc} ')

@csrf_exempt
def verify_login(request):
    '''
    verify the login of a user with a one time code generated in 'generate_verification_code'
    '''
    err_msg = None
    if request.method == 'POST':
        otc = request.POST['otc']
        try:
            username = request.session['username']
            otc_secret_key = request.session['otc_secret_key']
            otc_valid_until = request.session['otc_valid_until']
        except KeyError:
            err_msg = 'Enter your login credentials in the login page first'
            return render(request, 'polls/verifylogin.html', {'err_msg': err_msg})
        

        if otc_secret_key and otc_valid_until is not None:
            valid_until = datetime.fromisoformat(otc_valid_until)
            
            if valid_until > datetime.now():
                # the time interval has not exceeded the current time yet

                totp = pyotp.TOTP(otc_secret_key, interval=60)
                if totp.verify(otc): # check if user input matches with the generated code
                    user = get_object_or_404(CustomUser, username=username)
                    if user is None:
                        err_msg = 'There was an error verifying the user'
                        return render(request, 'polls/verifylogin.html', {'err_msg': err_msg})
                    
                    login(request, user)

                    del request.session['otc_secret_key']
                    del request.session['otc_valid_until']

                    return redirect('home')
                
                else:
                    err_msg = 'Wrong verification code'
            else:
                err_msg = 'You verification code has expired'

        else:
            err_msg = 'There was an error generating the verification code or session'


    return render(request, 'polls/verifylogin.html', {'err_msg': err_msg})


# sql injectable 
def search_poll(request): #insecure example, replace this function
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


#safe query
# def search_poll(request): #use this function instead
#     '''
#     The function returns the search result of an ID that a user provides
#     It returns a poll with a matching id or no poll at all
#     Any user can search for a poll and vote for it
#     '''

#     user_input = request.GET.get("search_id")

#     with connection.cursor() as cursor:
        
#         # Using parameterized query to prevent SQL injection
#         query = "SELECT * FROM polls_poll WHERE id = %s"
#         cursor.execute(query, [user_input])
        
#         rows = cursor.fetchall()

#     polls = [{'id': row[0], 'question': row[1], 'option_one': row[2], 'option_two': row[3],
#               'option_three': row[4], 'option_one_votes': row[5], 'option_two_votes': row[6],
#               'option_three_votes': row[7]} for row in rows]

#     context = {'polls': polls}
#     return render(request, 'polls/search.html', context)
