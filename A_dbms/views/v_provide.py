from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required


# -----------------------委托合同列表---------------------#
@login_required
def provide(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def provide')
    agree_state_list = models.Agrees.AGREE_STATE_LIST
    agree_list = models.Agrees.objects.filter(**kwargs).select_related(
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

    return render(request, 'dbms/provide/provide.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
def provide_scan(request, agree_id):  # 查看放款
    print(__file__, '---->def provide_scan')

    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request, 'dbms/provide/provide-scan.html', locals())


# ------------------------provide_scan_notice查看放款通知-------------------------#
@login_required
def provide_scan_notify(request, agree_id, notify_id):  # 查看放款通知
    print(__file__, '---->def provide_scan_notify')

    agree_obj = models.Agrees.objects.get(id=agree_id)
    notify_obj = models.Notify.objects.get(id=notify_id)
    print('notify_obj:', notify_obj)
    return render(request, 'dbms/provide/provide-scan-notify.html', locals())


# -----------------------放款列表---------------------#
@login_required
def grant(request, *args, **kwargs):  # 委托合同列表
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

    return render(request, 'dbms/provide/grant.html', locals())


# -----------------------------查看放款------------------------------#
@login_required
def grant_scan(request, grant_id):  # 查看放款
    print(__file__, '---->def grant_scan')

    grant_obj = models.Provides.objects.get(id=grant_id)

    return render(request, 'dbms/provide/grant-scan.html', locals())
