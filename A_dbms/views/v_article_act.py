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
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------------项目管理-------------------------------#
def creat_article_num(custom_id):
    custom = models.Customes.objects.get(id=custom_id)
    ###时间处理
    article_date = time.localtime()  # 时间戳--》元组(像gmtime())
    n_year = article_date.tm_year
    if article_date.tm_mon < 10:
        n_mon = '0' + str(article_date.tm_mon)
    else:
        n_mon = str(article_date.tm_mon)
    r_order = models.Articles.objects.filter(
        custom=custom_id, article_date__year=n_year).count() + 1
    article_num = '%s-%s%s-%s' % (custom.short_name, str(n_year), n_mon, r_order)
    return article_num


# -----------------------------添加项目ajax------------------------------#
@login_required
@authority
def article_add_ajax(request):  # 添加项目
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    form = forms.ArticlesAddForm(post_data, request.FILES)  #####
    if form.is_valid():
        cleaned_data = form.cleaned_data
        custom_id = cleaned_data['custom_id']
        renewal = cleaned_data['renewal']
        augment = cleaned_data['augment']
        article_num = creat_article_num(custom_id)
        amount = renewal + augment
        try:
            with transaction.atomic():
                article_obj = models.Articles.objects.create(
                    article_num=article_num, custom_id=custom_id, renewal=renewal,
                    augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'], assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'], article_buildor=request.user)
                today_str = time.strftime("%Y-%m-%d", time.localtime())  # 元组转换为字符串
                models.Customes.objects.filter(article_custom=article_obj).update(
                    lately_date=today_str, managementor_id=cleaned_data['director_id'])
            response['message'] = '成功创建项目：%s！' % article_obj.article_num
            response['skip'] = "/dbms/article/"
        except Exception as e:
            response['status'] = False
            response['message'] = '项目未创建成功：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------修改项目ajax------------------------------#
@login_required
@authority
def article_edit_ajax(request):  # 修改项目ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))
        (5, '已签批')-->才能出合同'''
    if article_obj.article_state in [1, 2, 3, 4]:
        form = forms.ArticlesAddForm(post_data, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            renewal = cleaned_data['renewal']
            augment = cleaned_data['augment']
            amount = renewal + augment
            try:
                article_list = models.Articles.objects.filter(id=article_id)
                article_list.update(
                    custom_id=cleaned_data['custom_id'], renewal=renewal,
                    augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'], assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'], article_buildor=request.user)
                models.Customes.objects.filter(article_custom=article_obj).update(
                    managementor_id=cleaned_data['director_id'])
                response['message'] = '成功修改项目：%s！' % article_obj.article_num
            except Exception as e:
                response['status'] = False
                response['message'] = '项目未修改成功:%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法修改！！！' % article_obj.article_state

    result = json.dumps(response, ensure_ascii=False)

    return HttpResponse(result)


# -----------------------------删除项目ajax------------------------------#
@login_required
@authority
def article_del_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))
        (5, '已签批')-->才能出合同'''
    if article_obj.article_state == 1:
        article_obj.delete()  # 删除评审会
        response['message'] = '%s，删除成功！' % article_obj.article_num
    else:
        response['status'] = False
        response['message'] = '状态为：%s，删除失败！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------反馈项目ajax------------------------------#
@login_required
@authority
def article_feedback_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list[0]
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2]:
        form = forms.FeedbackAddForm(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print('cleaned_data:', cleaned_data)
            try:
                today_str = time.strftime("%Y-%m-%d", time.gmtime())
                default = {
                    'article_id': article_id, 'propose': cleaned_data['propose'],
                    'analysis': cleaned_data['analysis'], 'suggestion': cleaned_data['suggestion'],
                    'feedback_date': today_str, 'feedback_buildor': request.user}
                article, created = models.Feedback.objects.update_or_create(
                    article_id=article_id, defaults=default)
                article_list.update(article_state=2, article_date=today_str)  # 更新项目状态
                if created:
                    response['message'] = '成功成功反馈项目%s！' % article_obj.article_num
                else:
                    response['message'] = '成功更新反馈信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = "项目未反馈成功：%s" % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法反馈！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)

#
# @login_required
# def article_scan_lending(request, article_id, lending_id):  # 项目预览
#     print(__file__, '---->def article_scan_lending')
#     print('request.path:', request.path)
#
#     sure_list = [1, 2]
#     house_list = [11, 21, 42, 52]
#     ground_list = [12, 22, 43, 53]
#     receivable_list = [31]
#     stock_list = [32, 51]
#     lending_operate = False
#
#     article_obj = models.Articles.objects.get(id=article_id)
#     lending_obj = models.LendingOrder.objects.get(id=lending_id)
#     print(article_obj, lending_obj)
#     return render(request, 'dbms/article/article-scan-lending.html', locals())
