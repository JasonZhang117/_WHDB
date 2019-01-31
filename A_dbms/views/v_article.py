from django.shortcuts import render, redirect, HttpResponse
from .. import permissions
from .. import models
from .. import forms
import datetime, time
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from django.db.utils import IntegrityError
from django.db import transaction


@login_required
def article(request, *args, **kwargs):  # 项目列表
    print(__file__, '---->def article')
    print('**kwargs:', kwargs)
    # print('request.path:', request.path)
    # print('request.get_host:', request.get_host())
    # print('resolve(request.path):', resolve(request.path))
    # print('type(request.user):', type(request.user))
    # print('request.user:', request.user)
    # print('request.GET.items():', request.GET.items())
    # request.GET.items()获取get传递的参数对
    print('request.GET:', request.GET)

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
    print('article_state_list_dic:', article_state_list_dic)
    # 列表或元组转换为字典并添加key[{'id': 1, 'name': '待反馈'}, {'id': 2, 'name': '已反馈'}]
    '''筛选'''
    article_list = models.Articles.objects.filter(**kwargs).select_related(
        'custom', 'director', 'assistant', 'control').order_by('-build_date')
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
def article_scan(request, article_id):  # 项目预览
    print(__file__, '---->def article_scan')
    PAGE_TITLE = '查看项目'

    article_obj = models.Articles.objects.get(id=article_id)

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
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    print(__file__, '---->def article_scan_agree')
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
def article_scan_lending(request, article_id, lending_id):  # 项目预览
    print(__file__, '---->def article_scan_lending')
    PAGE_TITLE = '查看项目'

    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32]
    CHATTEL_LIST = [13]

    article_obj = models.Articles.objects.get(id=article_id)
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    return render(request, 'dbms/article/article-scan-lending.html', locals())
