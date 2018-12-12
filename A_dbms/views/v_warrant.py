from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# 抵质押物信息管理
# -----------------------房产管理-------------------------#
# -----------------------房产管理-------------------------#
# -----------------------房产管理-------------------------#
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
