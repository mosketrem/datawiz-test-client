from django.shortcuts import render, redirect

from .forms import LoginForm


def index(request):
    # request.session['test'] = 'test_value'
    return render(request, 'client/index.html', {})


def login(request):
    if request.session.get('creds'):
        return redirect('client:index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            request.session['creds'] = email + '|' + password
            return redirect('client:index')
    else:
        form = LoginForm()
    return render(request, 'client/login.html', {'form': form})


def logout(request):
    request.session.flush()
    return redirect('client:index')
