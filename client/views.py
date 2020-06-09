from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.core.cache import cache
from django.urls import reverse

import pandas as pd
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


def login(request):
    if request.session.get('creds'):
        return redirect('client:index')
    if request.method == 'POST':
        form = LoginForm(request.POST)
        value_next = request.POST.get('next', '')
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
            
            if value_next:
                return HttpResponseRedirect(value_next)
            return redirect('client:index')
    else:
        form = LoginForm()
        value_next = request.GET.get('next', '')
    return render(request, 'client/login.html', {'form': form, 'next': value_next})


def logout(request):
    request.session.flush()
    cache.clear()
    return redirect('client:login')


def if_creds_valid(view_func):
    def wrapper(*args, **kwargs):
        request = args[0]
        if not request.session.get('creds'):
            return redirect(reverse('client:login') + "?next=" + request.get_full_path())
        creds = request.session['creds']
        try:
            dw = datawiz.DW(creds['email'], creds['password'])
        except InvalidGrantError:
            return render(request, 'client/error.html', {'error_msg': 'Provided credentials were not accepted by DataWiz.'})
        kwargs['dw'] = dw
        return view_func(*args, **kwargs)
    return wrapper


@if_creds_valid
def index(request, dw):
    context = {}
    # get month sales report made by categories
    df = dw.get_categories_sale()
    df.sort_values(by=['date'], inplace=True, ascending=True)
    # taking last two days
    df = df[-2:]
    df['sum'] = df[list(df.columns)].sum(axis=1)
    first_line = ['Показник', df.iloc[[1]].index.values[0], df.iloc[[0]].index.values[0], 'Різниця, %', 'Різниця']
    # calculate amounts of operated money
    a1, a0 = df.iloc[[1]]['sum'].values[0], df.iloc[[0]]['sum'].values[0]
    second_line = ['Обсяг задіяних коштів', '{:.2f}'.format(a1), '{:.2f}'.format(a0), '{:.2f}'.format((a1 - a0) / a0 * 100.0), '{:.2f}'.format(a1 - a0)]

    # fentching detailed sales info
    items = [i for i in dw.sale_items()]
    df = pd.DataFrame(columns=items[0][0].keys())
    for i in items:
        df = df.append(pd.DataFrame(i))
    # adding simple date column
    df['day'] = df['date'].apply(lambda x: x[:10])
    days = df.day.unique()
    days.sort()
    # filtering sales of two last days
    last_day = df.loc[df['day'] == days[-1]]
    before_last_day = df.loc[df['day'] == days[-2]]

    # adding up amount of sold goods
    qty1, qty0 = last_day.qty.sum(), before_last_day.qty.sum()
    diff = qty1 - qty0
    third_line = ['Кількість проданого', '{:.2f}'.format(qty1), '{:.2f}'.format(qty0), '{:.2f}'.format(diff / qty0 * 100.0), '{:.2f}'.format(diff)]
    # getting amount of receipts for each of last two days
    receipts1, receipts0 = len(last_day.receipt_id.unique()), len(before_last_day.receipt_id.unique())
    forth_line = ['Кількість чеків', receipts1, receipts0, '{:.2f}'.format((receipts1 - receipts0) / receipts0 * 100.0), receipts1 - receipts0]

    # calculating the mean value of an average receipt
    mean1, mean0 = last_day.groupby('receipt_id')['total_price'].sum().mean(), before_last_day.groupby('receipt_id')['total_price'].sum().mean()
    fifth_line = ['Середній чек', '{:.2f}'.format(mean1), '{:.2f}'.format(mean0), '{:.2f}'.format((mean1 - mean0) / mean0 * 100.0), '{:.2f}'.format(mean1 - mean0)]

    # the data for the template
    main_table = [first_line, second_line, third_line, forth_line, fifth_line]

    # fetching descriptions of goods (because sales info has only id-s, and we need names)
    products = dw.get_product()
    products = {i['identifier']: i['product_name'] for i in products}

    # calculating money per product's id (for each of two last days)
    sales_per_product1 = last_day.groupby('product_id')[['qty', 'total_price']].sum()
    sales_per_product0 = before_last_day.groupby('product_id')[['qty', 'total_price']].sum()
    diff = sales_per_product1.subtract(sales_per_product0, fill_value=0).sort_values('total_price')
    increase, drop = diff[-5:][::-1], diff[:5]

    # the data for the template
    first_line = ['Назва краму', 'Зміна кількості продажів', 'Зміна задіяних коштів']
    increase_table = [first_line,]
    
    form_row = lambda x, i: [products[x.index[i]], x.values[i][0], '{:.2f}'.format(x.values[i][1])]

    for i in range(len(increase)):
        increase_table.append(form_row(increase, i))

    # the data for the template
    drop_table = [first_line,]
    for i in range(len(drop)):
        drop_table.append(form_row(drop, i))

    context = {'main_table': main_table,
                'increase_table': increase_table,
                'drop_table': drop_table
    }

    return render(request, 'client/index.html', context)


@if_creds_valid
def profile(request, dw):    
    info = dw.get_client_info()
    return render(request, 'client/user_profile.html', {'info': info})
