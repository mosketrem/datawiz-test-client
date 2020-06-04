from django.shortcuts import render, redirect
from dwapi import datawiz_auth, datawiz
from oauthlib.oauth2.rfc6749.errors import InvalidGrantError

from .forms import LoginForm


test_creds = {
    "API_KEY": datawiz_auth.TEST_USERNAME,
    "CLIENT_SECRET": datawiz_auth.CLIENT_SECRET,
    "CLIENT_ID": datawiz_auth.CLIENT_ID,
    "email": datawiz_auth.TEST_USERNAME,
    "password": datawiz_auth.TEST_PASSWORD,
}


def index(request):
    return render(request, 'client/index.html', {})


def login(request):
    if request.session.get('creds'):
        return redirect('client:index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                dw = datawiz.DW(email, password)
                creds = dw.generate_secret(email, password)
            except InvalidGrantError:
                return render(request, 'client/login.html', {'form': form, 'error_msg': 'No such email and password.'})
            creds['email'] = email
            creds['password'] = password
            if "CLIENT_ID" not in creds:
                creds = test_creds
            creds['name'] = dw.get_client_info().get('name', 'Empty Name')
            request.session['creds'] = creds
            return redirect('client:index')
    else:
        form = LoginForm()
    return render(request, 'client/login.html', {'form': form})


def logout(request):
    request.session.flush()
    return redirect('client:index')


def profile(request):
    if not request.session.get('creds'):
        return redirect('client:index')
    creds = request.session['creds']
    try:
        dw = datawiz.DW(creds['email'], creds['password'])
    except InvalidGrantError:
        return render(request, 'client/error.html', {'error_msg': 'Provided credentials were not accepted by DataWiz.'})
    info = dw.get_client_info()
    return render(request, 'client/user_profile.html', {'info': info})
