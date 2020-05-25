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
from _WHDB.views import (authority, custom_list_screen, custom_right, provide_list_screen,
                         FICATION_LIST)


# -----------------------保后列表---------------------#
@login_required
@authority
def review(request, *args, **kwargs):  # 保后列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '保后管理'

    REVIEW_STATE_LIST = models.Customes.REVIEW_STATE_LIST
    custom_list = models.Customes.objects.exclude()

    custom_list = models.Customes.objects.filter(**kwargs).order_by('lately_date')
    custom_list = custom_list_screen(custom_list, request)
    '''
    custom_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    custom_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    custom_back = models.FloatField(verbose_name='_保函余额', default=0)
    '''
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    custom_list = custom_list.exclude(custom_state=99)
    custom_list = custom_list.filter(credit_amount__gt=0)

    '''搜索条件'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'short_name', 'district__name', 'idustry__name', 'managementor__name',
                         'controler__name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        custom_list = custom_list.filter(q)
    custom_list = custom_list.filter(credit_amount__gt=0)
    today_year = datetime.date.today().year
    today_day = datetime.date.today()
    for custom in custom_list:
        custom_lately_date = custom.lately_date
        day_space = today_day - custom_lately_date
        '''REVIEW_STY_LIST = [(1, '现场检查'), (11, '电话回访'), (61, '补调替代'), (62, '尽调替代')]'''
        review_count = custom.review_custom.filter(review_date__year=today_year, review_sty__in=[1, 11]).count()  # 保后次数
        # article_count = custom.article_custom.filter(build_date__year=today_year).count()  # 尽调次数
        inv_count = custom.inv_custom.filter(inv_date__year=today_year).count()  # 补调次数
        custom_ll = models.Customes.objects.filter(id=custom.id).update(
            review_amount=review_count, add_amount=inv_count, day_space=day_space.days)

    balance = custom_list.aggregate(Sum('amount'))['amount__sum']  # 在保余额

    custom_acount = custom_list.count()
    paginator = Paginator(custom_list, 119)
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
@custom_right
def review_scan(request, custom_id):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '保后详情'
    custom_obj = models.Customes.objects.get(id=custom_id)

    date_th_later = datetime.date.today() + datetime.timedelta(days=30)  # 30天后的日期
    form_review_plan = forms.FormRewiewPlanAdd(initial={'review_plan_date': str(date_th_later)})
    form_review_add = forms.FormRewiewAdd(initial={'review_date': str(datetime.date.today())})
    form_inv_add = forms.FormInvestigateAdd(initial={'inv_date': str(datetime.date.today())})

    article_custom_list = custom_obj.article_custom.all().order_by('-build_date')
    review_custom_list = custom_obj.review_custom.all().order_by('-review_date', '-review_plan_date')
    investigate_custom_list = custom_obj.inv_custom.all().order_by('-inv_date')

    return render(request, 'dbms/review/review-scan.html', locals())


# -----------------------逾期保后---------------------#
@login_required
@authority
def review_overdue(request, *args, **kwargs):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '逾期保后'

    review_overdue_list = models.Customes.objects.filter(
        review_state=1, review_plan_date__lt=datetime.date.today()).order_by('review_plan_date')  # 逾期保后
    review_overdue_list = custom_list_screen(review_overdue_list, request)
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'short_name', ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
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


# -----------------------分类列表---------------------#
@login_required
@authority
def classification(request, *args, **kwargs):  # 分类列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '分类列表'
    if kwargs:
        fication = kwargs['fication']
    else:
        fication = 0

    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    FICATION_LIST = [(11, '正常'), (21, '关注'), (31, '次级'), (41, '可疑'), (51, '损失')]  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(provide_balance__gt=0)
    provide_list = provide_list.filter(**kwargs).select_related('notify').order_by('-provide_date')
    provide_list = provide_list_screen(provide_list, request)
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
            q.children.append(("%s__contains" % field, search_key.strip()))
        provide_list = provide_list.filter(q)

    balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    provide_acount = provide_list.count()
    '''分页'''
    paginator = Paginator(provide_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    today_str = str(datetime.date.today())
    form_fication = forms.FormFicationAdd(initial={'fic_date': today_str})

    form_fication_all_data = {'fic_date': today_str, 'fication': fication, }
    form_fication_all = forms.FormFicationAll(initial=form_fication_all_data)

    return render(request, 'dbms/review/classification.html', locals())
