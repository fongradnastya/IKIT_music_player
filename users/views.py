import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q

from music.models import Playlist
from users.forms import RegisterForm, LoginForm
from users.models import User, Session
from users.secure import *

dh = DiffieHellman()

def login(request):
    form = LoginForm()
    return render(request, 'login.html', {'form': form})


def register(request):
    form = RegisterForm()
    return render(request, 'register.html', {'form': form})


def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']
    return redirect('login')


def get_public_key(request):
    public_key, p, q = dh.generate_public_key()
    print(public_key, p, q)
    return JsonResponse({'public_key': public_key, 'p': p, 'q': q})


@csrf_exempt
def receive_public_key(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        other_public_key = data.get('publicKey')
        # Compute the shared secret
        shared_secret = dh.compute_shared_secret(other_public_key)
        print('Shared secret:', shared_secret)
        return JsonResponse({'status': 'success'})
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'})


@csrf_exempt
def receive_registration_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        key = dh.get_key()
        key_hash = hash_key(key)
        iv = data.get('iv')
        username = decrypt(data.get('username'), key_hash, iv)
        email = decrypt(data.get('email'), key_hash, iv)
        password = decrypt(data.get('password'), key_hash, iv)
        print(username, email, password)
        if username and email and password:
            try:
                # Check if a user with the same username or email already exists
                User.objects.get(Q(username=username) | Q(email=email))
                return JsonResponse({'status': 'failed',
                                        'error': 'A user with this username or email already exists.'},
                                    status=400)
            except ObjectDoesNotExist:
                password = hash_password(password)
                print(password)
                user = User(username=username, email=email, password=password)
                user.save()
                return JsonResponse({'status': 'success',
                                     'message': 'User created successfully. You can now log in.'}, status=200)
        return JsonResponse({'status': 'failed',
                             'error': 'Impossible to decrypt'}, status=400)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)

@csrf_exempt
def receive_login_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        key = dh.get_key()
        key_hash = hash_key(key)
        iv = data.get('iv')
        username = decrypt(data.get('username'), key_hash, iv)
        password = decrypt(data.get('password'), key_hash, iv)
        print(username, password)
        try:
            user = User.objects.get(username=username)
            is_correct = check_password(user.password, password)
            if is_correct:
                session_id = create_session_id(username)
                new_session = Session(user=user, session_id=session_id)
                new_session.save()

                # Send the session ID to the client as a cookie
                response = JsonResponse({'status': 'success',
                                         'message': 'User login successfully'},
                                        status=200)
                response.set_cookie('sessionid', session_id)
                return response
            else:
                return JsonResponse({'status': 'failed',
                                     'message': 'Invalid password'},
                                    status=400)
        except ObjectDoesNotExist:
            return JsonResponse({'status': 'failed',
                                 'error': 'Invalid username'}, status=400)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)

@csrf_exempt
def get_home_data(request):
    # Get the session ID from the cookies
    session_id = request.COOKIES.get('sessionid')
    if not session_id:
        return JsonResponse({'status': 'failed',
                             'error': 'No session ID provided'},
                            status=400)
    try:
        # Get the session from the database
        session = Session.objects.get(session_id=session_id)
        # Get the user from the session
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid session ID'},
                            status=400)

    """playlists = Playlist.objects.all().filter(owner=user)
    context = {
        'playlists': playlists,
        "username": user.username,
    }"""
    return JsonResponse({'status': 'success', 'username': user.username},
                        status=200)

def index(request):
    return render(request, 'index.html')