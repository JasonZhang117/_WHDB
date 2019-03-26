from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------在保列表---------------------#
@login_required
# @authority
def report_provide_list(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保明细'
    PROVIDE_TYP_LIST = models.Provides.PROVIDE_TYP_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(provide_status=1).filter(
        **kwargs).select_related('notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__lending__summary__custom__short_name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)

    balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    return render(request, 'dbms/report/provide_list.html', locals())
