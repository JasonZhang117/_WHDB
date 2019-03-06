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


# -----------------------保后列表---------------------#
@login_required
@authority
def review(request, *args, **kwargs):  # 保后列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '保后管理'

    REVIEW_STATE_LIST = models.Customes.REVIEW_STATE_LIST
    custom_list = models.Customes.objects.filter(**kwargs)
    '''
    custom_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    custom_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    custom_back = models.FloatField(verbose_name='_保函余额', default=0)
    '''
    '''设置筛选条件'''
    search_fields = ['custom_flow', 'custom_accept', 'custom_back']
    q = Q()
    q.connector = 'OR'
    for field in search_fields:
        q.children.append(("%s__gt" % field, 0))
    custom_list = custom_list.filter(q).order_by('lately_date')

    '''搜索条件'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        custom_list = custom_list.filter(q)

    flow_amount = custom_list.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    accept_amount = custom_list.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    back_amount = custom_list.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额

    if flow_amount:
        flow_amount = flow_amount
    else:
        flow_amount = 0
    if accept_amount:
        accept_amount = accept_amount
    else:
        accept_amount = 0
    if back_amount:
        back_amount = back_amount
    else:
        back_amount = 0

    balance = flow_amount + accept_amount + back_amount

    custom_acount = custom_list.count()
    paginator = Paginator(custom_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/review/review.html', locals())


# -----------------------------保后详情------------------------------#
@login_required
@authority
def review_scan(request, custom_id):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '保后详情'
    date_th_later = datetime.date.today() + datetime.timedelta(days=30)  # 30天后的日期

    form_review_plan = forms.FormRewiewPlanAdd(initial={'review_plan_date': str(date_th_later)})
    form_review_add = forms.FormRewiewAdd()

    custom_obj = models.Customes.objects.get(id=custom_id)
    review_custom_list = custom_obj.review_custom.all().order_by('-review_date', '-review_plan_date')
    article_custom_list = custom_obj.article_custom.all().order_by('-build_date')

    return render(request, 'dbms/review/review-scan.html', locals())


# -----------------------逾期保后---------------------#
@login_required
@authority
def review_overdue(request, *args, **kwargs):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '逾期保后'

    review_overdue_list = models.Customes.objects.filter(
        review_state=1, review_plan_date__lt=datetime.date.today()).order_by('review_plan_date')  # 逾期保后

    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'short_name', ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        review_overdue_list = review_overdue_list.filter(q)

    provide_acount = review_overdue_list.count()

    flow_amount = review_overdue_list.aggregate(Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    accept_amount = review_overdue_list.aggregate(Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    back_amount = review_overdue_list.aggregate(Sum('custom_back'))['custom_back__sum']  # 保函余额

    if flow_amount:
        flow_amount = flow_amount
    else:
        flow_amount = 0
    if accept_amount:
        accept_amount = accept_amount
    else:
        accept_amount = 0
    if back_amount:
        back_amount = back_amount
    else:
        back_amount = 0
    balance = flow_amount + accept_amount + back_amount

    '''分页'''
    paginator = Paginator(review_overdue_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/review/review.html', locals())
