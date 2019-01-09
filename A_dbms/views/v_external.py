from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Max, Count


# -----------------------合作机构-------------------------#
def cooperative(request, *args, **kwargs):  # 合作机构
    print(__file__, '---->def Cooperative')
    PAGE_TITLE = '合作机构'

    COOPERATOR_STATE_LIST = models.Cooperators.COOPERATOR_STATE_LIST
    cooperator_list = models.Cooperators.objects.filter(**kwargs).order_by('-flow_credit', '-flow_limit')

    ####分页信息###
    paginator = Paginator(cooperator_list, 30)
    page = request.GET.get('page')
    try:
        cooperator_p_list = paginator.page(page)
    except PageNotAnInteger:
        cooperator_p_list = paginator.page(1)
    except EmptyPage:
        cooperator_p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/cooperative.html', locals())
