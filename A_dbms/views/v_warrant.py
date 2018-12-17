from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# 抵质押物信息管理
# -----------------------房产列表-------------------------#
def house(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')
    print('**kwargs:', kwargs)
    form_house_add = forms.HouseAddForm()

    house_app_list = models.Houses.HOUSE_APP_LIST
    house_list = models.Houses.objects.filter(**kwargs)
    print('house_list:', house_list)
    ####分页信息###
    paginator = Paginator(house_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/house.html',
                  locals())


# -----------------------房产列表-------------------------#
def ground(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')
    print('**kwargs:', kwargs)

    ground_app_list = models.Grounds.GROUND_APP_LIST
    ground_list = models.Grounds.objects.filter(**kwargs)
    print('ground_list:', ground_list)
    ####分页信息###
    paginator = Paginator(ground_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/ground.html',
                  locals())


# -----------------------房产列表-------------------------#
def warrant(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')

    warrant_typ_list = models.Warrants.WARRANT_TYP_LIST
    warrant_list = models.Warrants.objects.filter(**kwargs)

    ####分页信息###
    paginator = Paginator(warrant_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/warrant.html',
                  locals())
