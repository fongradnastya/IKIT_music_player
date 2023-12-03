from django.http import JsonResponse
from django.shortcuts import render, redirect

from users.forms import RegisterForm, LoginForm
from users.models import User
from users.secure import generate_dh_parameters


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
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = RegisterForm()

    return render(request, 'register.html', {'form': form})

def logout(request):
    if 'user_id' in request.session:
        del request.session['user_id']

    return redirect('login')

def get_public_key(request):
    print("started")
    public_key = generate_dh_parameters()
    return JsonResponse({'public_key': public_key})