from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time, json
from django.urls import resolve

from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------评审会-------------------------#
@login_required
@authority
def meeting(request, *args, **kwargs):  # 评审会
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    # print('kwargs:', kwargs)
    '''模态框'''
    form_meeting_add = forms.MeetingAddForm()  # 评审会添加
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    meeting_state_list = models.Appraisals.MEETING_STATE_LIST  # 筛选条件
    review_model_list = models.Appraisals.REVIEW_MODEL_LIST
    '''筛选'''
    meeting_list = models.Appraisals.objects.filter(**kwargs).order_by('-review_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['num', 'article__article_num', 'article__custom__name', 'article__custom__short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        meeting_list = meeting_list.filter(q)
    meeting_acount = meeting_list.count()
    '''分页'''
    paginator = Paginator(meeting_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    return render(request, 'dbms/meeting/meeting.html', locals())


# -----------------------评审会预览-------------------------#
@login_required
@authority
def meeting_scan(request, meeting_id):  # 评审会预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    expert_list = models.Experts.objects.filter(article_expert__appraisal_article=meeting_obj).distinct()
    expert_article_count = {}
    article_count = list()
    for expert_obj in expert_list:
        article_count = models.Articles.objects.filter(expert=expert_obj, appraisal_article=meeting_obj).count()
        expert_article_count['id'] = expert_obj.id
        expert_article_count['count'] = article_count

    expert_ll = models.Experts.objects.filter(article_expert__appraisal_article=meeting_obj).count()
    form_meeting_article_add = forms.MeetingArticleAddForm()

    meeting_edit_form_data = {'review_model': meeting_obj.review_model,
                              'review_date': str(meeting_obj.review_date),
                              'compere': meeting_obj.compere, }
    form_meeting_edit = forms.MeetingEditForm(initial=meeting_edit_form_data)

    return render(request, 'dbms/meeting/meeting-scan.html', locals())


# -----------------------评审会通知-------------------------#
@login_required
@authority
def meeting_notice(request, meeting_id):  # 评审会通知
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    return render(request, 'dbms/meeting/meeting-notice.html', locals())


# -----------------------参评项目预览-------------------------#
@login_required
@authority
def meeting_scan_article(request, meeting_id, article_id):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    edit_article_state_list = [1, 2, 3]
    article_obj = models.Articles.objects.get(id=article_id)
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    expert_list = article_obj.expert.values_list('id')
    if expert_list:
        expert_id_list = list(zip(*expert_list))[0]
        form_date = {'expert': expert_id_list}
        form_allot_expert = forms.MeetingAllotForm(initial=form_date)
    else:
        form_allot_expert = forms.MeetingAllotForm()

    return render(request, 'dbms/meeting/meeting-scan-article.html', locals())


# -----------------------评委列表-------------------------#
@login_required
@authority
def experts(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '合作机构'

    COOPERATOR_TYPE_LIST = models.Cooperators.COOPERATOR_TYPE_LIST
    cooperator_list = models.Cooperators.objects.filter(**kwargs).order_by('-flow_credit', '-flow_limit')

    ####分页信息###
    paginator = Paginator(cooperator_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/external/cooperative.html', locals())
