import json

from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q
from django.core import serializers

from music.forms import AddPostForm
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
        key = dh.get_shared_secret()
        key_hash = hash_key(key)
        iv = data.get('iv')
        username = decrypt(data.get('username'), key_hash, iv)
        email = decrypt(data.get('email'), key_hash, iv)
        password = decrypt(data.get('password'), key_hash, iv)
        print(username, email, password)
        if username and email and password:
            if User.objects.filter(email=email).exists():
                return JsonResponse({'status': 'failed',
                                     'error': 'A user with this email already exists.'},
                                    status=400)
            if User.objects.filter(username=username).exists():
                return JsonResponse({'status': 'failed',
                                     'error': 'A user with this username already exists.'},
                                    status=400)
            else:
                password = hash_password(password)
                print(password)
                user = User(username=username, email=email, password=password)
                user.save()
                return JsonResponse({'status': 'success',
                                     'message': 'User created successfully. You can now log in.'},
                                    status=200)
        return JsonResponse({'status': 'failed',
                             'error': 'Impossible to decrypt'}, status=400)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)

@csrf_exempt
def receive_login_data(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        key = dh.get_shared_secret()
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
                                     'error': 'Invalid password'},
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
        # Get the user from the sessions
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid session ID'},
                            status=400)
    public_key, p, q = dh.get_public_key()
    shared_secret = hash_key(dh.get_shared_secret())
    username, iv = encrypt(user.username, shared_secret)
    playlists = Playlist.objects.all().filter(owner=user)
    playlist_names = []
    for playlist in playlists:
        playlist_name, _ = encrypt(playlist.name, shared_secret, iv)
        playlist_names.append(playlist_name)
    data = json.dumps(playlist_names)
    context = {
        'status': 'success',
        'playlists': data,
        'username': username,
        'publicKey': public_key,
        'p': p,
        'q': q,
        'iv': iv
    }
    return JsonResponse(context, status=200)

@csrf_exempt
def get_username(request):
    session_id = request.COOKIES.get('sessionid')
    if not session_id:
        return JsonResponse({'status': 'failed',
                             'error': 'No session ID provided'},
                            status=400)
    try:
        session = Session.objects.get(session_id=session_id)
        user = session.user
    except Session.DoesNotExist:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid session ID'},
                            status=400)
    public_key, p, q = dh.get_public_key()
    shared_secret = hash_key(dh.get_shared_secret())
    username, iv = encrypt(user.username, shared_secret)
    context = {
        'status': 'success',
        'username': username,
        'publicKey': public_key,
        'p': p,
        'q': q,
        'iv': iv
    }
    return JsonResponse(context, status=200)

@csrf_exempt
def logout(request):
    if request.method == 'POST':
        session_id = request.COOKIES.get('sessionid')
        if session_id:
            try:
                session = Session.objects.get(session_id=session_id)
                session.delete()

                response = JsonResponse({'status': 'success',
                                         'message': 'User logged out successfully'},
                                        status=200)
                response.delete_cookie('sessionid')
                return response
            except Session.DoesNotExist:
                return JsonResponse({'status': 'failed',
                                     'error': 'Invalid session ID'}, status=400)
        else:
            return JsonResponse({'status': 'failed',
                                 'error': 'No session ID found in cookies'}, status=400)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)

def index(request):
    session_id = request.COOKIES.get('sessionid')
    if session_id:
        try:
            Session.objects.get(session_id=session_id)
            return render(request, 'index.html')
        except Session.DoesNotExist:
            print("Redirecting")
    return redirect('login')

def create_playlist(request):
    session_id = request.COOKIES.get('sessionid')
    if session_id:
        try:
            Session.objects.get(session_id=session_id)
            form = AddPostForm()
            return render(request, 'create.html',
                          {'form': form})
        except Session.DoesNotExist:
            print("Redirecting")
    return redirect('login')

@csrf_exempt
def receive_playlist_data(request):
    session_id = request.COOKIES.get('sessionid')
    if request.method == 'POST' and session_id:
        session = Session.objects.get(session_id=session_id)
        user = session.user
        data = json.loads(request.body)
        key = dh.get_shared_secret()
        key_hash = hash_key(key)
        iv = data.get('iv')
        name = decrypt(data.get('name'), key_hash, iv)
        description = decrypt(data.get('description'), key_hash, iv)
        print(name, description)
        if name and description:
            playlist = Playlist(name=name, description=description,
                                is_default=False, owner=user)
            playlist.save()
            return JsonResponse({'status': 'success',
                                     'error': 'Playlist created successfully.'}, status=200)
        return JsonResponse({'status': 'failed',
                             'error': 'Impossible to decrypt'}, status=400)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)

