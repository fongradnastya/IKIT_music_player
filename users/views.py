import json

from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from users.forms import RegisterForm, LoginForm
from users.models import User
from users.secure import DiffieHellman, decrypt, hash_key

dh = DiffieHellman()

def login(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        try:
            user = User.objects.get(username=form.cleaned_data['username'])
            if user.password == form.cleaned_data['password']:
                request.session['user_id'] = user.id
                return redirect('home')
            else:
                form.add_error('password', 'Incorrect password.')
        except User.DoesNotExist:
            form.add_error('username', 'User does not exist.')
    else:
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
            pass
        return JsonResponse({'status': 'success'}, status=200)
    else:
        return JsonResponse({'status': 'failed',
                             'error': 'Invalid request method'}, status=400)