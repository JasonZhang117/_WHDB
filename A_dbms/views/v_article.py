from django.shortcuts import render, redirect, HttpResponse
from .. import permissions
from _WHDB.views import MenuHelper
from .. import models
from .. import forms
import datetime, time
from _WHDB.views import authority
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------------项目列表------------------------------#
@login_required
@authority
def article(request, *args, **kwargs):  # 项目列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目列表'

    form_article_add_edit = forms.ArticlesAddForm()
    for k, v in request.GET.items():
        print(k, ' ', v)
    condition = {
        # 'article_state' : 0, #查询字段及值的字典，空字典查询所有
    }  # 建立空的查询字典
    for k, v in kwargs.items():
        # temp = int(v)
        temp = v
        kwargs[k] = temp
        if temp:
            condition[k] = temp  # 将参数放入查询字典
    '''筛选条件'''
    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 筛选条件
    article_state_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, article_state_list))
    # 列表或元组转换为字典并添加key[{'id': 1, 'name': '待反馈'}, {'id': 2, 'name': '已反馈'}]
    '''筛选'''
    article_list = models.Articles.objects.filter(**kwargs).select_related('custom', 'director', 'assistant', 'control')
    if '项目经理' in job_list:
        article_list = article_list.filter(Q(director=request.user) | Q(assistant=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['custom__name', 'director__name', 'assistant__name', 'control__name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        article_list = article_list.filter(q)
    article_acount = article_list.count()  # 信息数目
    balance = article_list.aggregate(Sum('article_balance'))['article_balance__sum']  # 在保余额
    '''分页'''
    paginator = Paginator(article_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/article/article.html', locals())


# -----------------------------项目预览------------------------------#
@login_required
@authority
def article_scan(request, article_id):  # 项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色

    PAGE_TITLE = '项目详情'
    article_obj = models.Articles.objects.get(id=article_id)
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee=article_obj) | Q(assistant_employee=article_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
    form_date = {
        'custom_id': article_obj.custom.id, 'renewal': article_obj.renewal,
        'augment': article_obj.augment, 'credit_term': article_obj.credit_term,
        'director_id': article_obj.director.id,
        'assistant_id': article_obj.assistant.id, 'control_id': article_obj.control.id,
        'article_date': str(article_obj.article_date)}
    form_article_add_edit = forms.ArticlesAddForm(form_date)
    expert_list = article_obj.expert.values_list('id')
    feedbac_list = article_obj.feedback_article.all()
    if feedbac_list:
        form_date = {
            'propose': feedbac_list[0].propose, 'analysis': feedbac_list[0].analysis,
            'suggestion': feedbac_list[0].suggestion}
        form_feedback = forms.FeedbackAddForm(initial=form_date)
    else:
        form_feedback = forms.FeedbackAddForm()

    return render(request, 'dbms/article/article-scan.html', locals())


# -----------------------------项目预览-按合同------------------------------#

@login_required
@authority
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '查看项目'

    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32]
    CHATTEL_LIST = [13]

    article_obj = models.Articles.objects.get(id=article_id)
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    return render(request, 'dbms/article/article-scan-agree.html', locals())


# -----------------------------项目预览-按发放次序------------------------------#

@login_required
@authority
def article_scan_lending(request, article_id, lending_id):  # 项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目次序'
    article_obj = models.Articles.objects.get(id=article_id)
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee=article_obj) | Q(assistant_employee=article_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                              (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    SURE_LIST = [1, 2]  # 保证类
    HOUSE_LIST = [11, 21, 42, 52]  # 房产类
    GROUND_LIST = [12, 22, 43, 53]  # 土地类
    COUNSTRUCT_LIST = [14, 23]  # 在建工程类
    RECEIVABLE_LIST = [31, ]  # 应收账款类
    STOCK_LIST = [32, 51]  # 股权类
    DRAFT_LIST = [33, 44]  # 票据类
    VEHICLE_LIST = [15, ]  # 车辆类
    CHATTEL_LIST = [13, 24, 34, 47]  # 动产类
    OTHER_LIST = [39, 49]  # 其他类
    '''反担保情况'''
    custom_lending_list = models.Customes.objects.filter(lending_custom__sure__lending=lending_obj)
    warrant_lending_h_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ__in=[1, 2])
    warrant_lending_g_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=5)
    warrant_lending_6_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=6)
    warrant_lending_r_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=11)
    warrant_lending_s_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=21)
    warrant_lending_d_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=31)
    warrant_lending_v_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=41)
    warrant_lending_c_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=51)
    warrant_lending_o_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=55)

    form_agree_add = forms.ArticleAgreeAddForm()

    return render(request, 'dbms/article/article-scan-lending.html', locals())
