from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required


# -----------------------委托合同列表---------------------#
@login_required
def agreep(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agreep')
    agree_state_list = models.Agrees.AGREE_STATE_LIST
    '''AGREE_STATE_LIST = ((1, '待签批'), (2, '已签批'), (3, '已落实'), (4, '已放款'),
                        (7, '待变更'), (8, '已解保'), (9, '已作废'))'''
    agree_list = models.Agrees.objects.filter(**kwargs).filter(agree_state__in=[1,2,3, 4]).select_related(
        'lending', 'branch').order_by('-agree_num')

    ####分页信息###
    paginator = Paginator(agree_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/agreep.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
def agreep_scan(request, agree_id):  # 查看放款
    print(__file__, '---->def agreep_scan')

    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request, 'dbms/provide/agreep-scan.html', locals())


# ------------------------provide_scan_notice查看放款通知-------------------------#
@login_required
def agreep_scan_notify(request, agree_id, notify_id):  # 查看放款通知
    print(__file__, '---->def provide_scan_notify')

    agree_obj = models.Agrees.objects.get(id=agree_id)
    notify_obj = models.Notify.objects.get(id=notify_id)
    print('notify_obj:', notify_obj)
    return render(request, 'dbms/provide/agreep-scan-notify.html', locals())


# -----------------------放款列表---------------------#
@login_required
def provide(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def provide')
    provide_status_list = models.Provides.STATUS_LIST
    provide_list = models.Provides.objects.filter(**kwargs).select_related(
        'notify').order_by('-id')

    ####分页信息###
    paginator = Paginator(provide_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide.html', locals())


# -----------------------------查看放款------------------------------#
@login_required
def provide_scan(request, provide_id):  # 查看放款
    print(__file__, '---->def provide_scan')

    provide_obj = models.Provides.objects.get(id=provide_id)

    return render(request, 'dbms/provide/provide-scan.html', locals())
