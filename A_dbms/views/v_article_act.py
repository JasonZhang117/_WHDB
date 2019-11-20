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
from _WHDB.views import authority, article_right, sub_article_right


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
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    form = forms.ArticlesAddForm(post_data, request.FILES)  #####
    if form.is_valid():
        cleaned_data = form.cleaned_data
        custom_id = cleaned_data['custom_id']
        director_id = cleaned_data['director_id']
        renewal = round(cleaned_data['renewal'], 2)
        augment = round(cleaned_data['augment'], 2)
        article_num = creat_article_num(custom_id)
        amount = renewal + augment
        try:
            with transaction.atomic():
                article_obj = models.Articles.objects.create(
                    article_num=article_num, custom_id=custom_id,
                    product_id=cleaned_data['product_id'], renewal=renewal,
                    augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                    process_id=cleaned_data['process_id'],
                    director_id=director_id, assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'],
                    currentor_id=cleaned_data['director_id'], frontor_id=cleaned_data['director_id'],
                    article_buildor=request.user)
                models.Customes.objects.filter(id=custom_id).update(
                    lately_date=datetime.date.today(),
                    managementor_id=cleaned_data['director_id'],
                    controler_id=cleaned_data['control_id'], custom_state=11)
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


# -----------------------添加共借人ajax-------------------------#
@login_required
@authority
def borrower_add_ajax(request):  # 添加共借人ajax
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同'''
    article_obj = models.Articles.objects.get(id=article_id)
    article_meeting_obj = article_obj.appraisal_article.all().first()
    if article_obj.article_state in [1, 2, 3, 4, ]:
        form_borrower_add = forms.FormBorrowerAdd(post_data, request.FILES)
        if form_borrower_add.is_valid():
            borrower_cleaned = form_borrower_add.cleaned_data
            borrower_add_list = borrower_cleaned['borrower']
            borrower_add_obj_list = models.Customes.objects.filter(id=borrower_add_list)
            try:
                with transaction.atomic():
                    for borrower_obj in borrower_add_obj_list:
                        article_obj.borrower.add(borrower_obj)
                response['message'] = '成功为项目：%s添加共借人！' % article_obj.article_num
            except Exception as e:
                response['status'] = False
                response['message'] = '添加共借人失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_borrower_add.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法添加共借人！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除共借人ajax-------------------------#
@login_required
@authority
def borrower_del_ajax(request):  # 取消项目上会ajax
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:',post_data)
    article_id = post_data['article_id']
    borrower_id = post_data['borrower_id']
    article_obj = models.Articles.objects.get(id=article_id)
    borrower_obj = models.Customes.objects.get(id=borrower_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4]:
        try:
            with transaction.atomic():
                article_obj.borrower.remove(borrower_obj)  # 删除共借人
            response['message'] = '共借人：%s删除成功' % borrower_obj.name
        except Exception as e:
            response['status'] = False
            response['message'] = '删除共借人失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法删除共借人！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------修改项目ajax------------------------------#
@login_required
@authority
def article_edit_ajax(request):  # 修改项目ajax
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_obj.article_state in [1, 2, 3, 4, 61]:
        form = forms.ArticlesAddForm(post_data, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            renewal = cleaned_data['renewal']
            augment = cleaned_data['augment']
            amount = renewal + augment
            try:
                article_list = models.Articles.objects.filter(id=article_id)
                article_list.update(
                    custom_id=cleaned_data['custom_id'], product_id=cleaned_data['product_id'], renewal=renewal,
                    augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'], assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'], process_id=cleaned_data['process_id'],
                    currentor_id=cleaned_data['director_id'], frontor_id=cleaned_data['director_id'],
                    article_buildor=request.user)
                models.Customes.objects.filter(article_custom=article_obj).update(
                    managementor_id=cleaned_data['director_id'], controler_id=cleaned_data['control_id'], )
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
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
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


# -----------------------------项目意见ajax------------------------------#
@login_required
@authority
def article_opinion_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list[0]
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_obj.article_state in [1,]:
        form = forms.FormOpinion(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                article_list.update(opinion=cleaned_data['opinion'], )
                response['message'] = '成功提交项目意见：%s！' % article_obj.article_num
            except Exception as e:
                response['status'] = False
                response['message'] = "项目意见未提交成功：%s" % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法提交项目意见！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)

# -----------------------------反馈项目ajax------------------------------#
@login_required
@authority
def article_feedback_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list[0]
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_obj.article_state in [1, 2]:
        form = forms.FeedbackAddForm(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
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


# -----------------------项目审批-------------------------#
@login_required
# @authority  # 功能权限
# @article_right  # 访问权限
@sub_article_right  # 流程权限
def article_sub_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list.first()
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    process_article = article_obj.process  # 审批流程
    process_article_list = list(models.ProcessSet.objects.filter(process=process_article).order_by('id'))
    print('process_article:', process_article)
    print('process_article_list:', process_article_list)

    if article_obj.article_state in [99, ]:
        form = forms.FeedbackAddForm(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
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
