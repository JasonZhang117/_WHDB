from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# -----------------------归档---------------------#
@login_required
def pigeonhole(request, *args, **kwargs):  # 归档
    print(__file__, '---->def pigeonhole')
    PAGE_TITLE = '归档管理'
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '暂存风控'), (21, '已归档')]'''
    IMPLEMENT_LIST = models.Provides.IMPLEMENT_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name', 'notify__agree__branch__name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)
    '''分页'''
    paginator = Paginator(provide_list, 18)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/pigeonhole/pigeonhole.html', locals())
