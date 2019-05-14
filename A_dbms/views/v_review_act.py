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


# -----------------------------保后计划ajax------------------------------#
@login_required
@authority
def review_plan_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    review_list_s = custom_obj.review_custom.filter(review_state=1)
    if review_list_s:
        response['status'] = False
        response['message'] = '还有未完成的保后计划，包后计划失败！'
    else:
        form_review_plan = forms.FormRewiewPlanAdd(post_data)
        if form_review_plan.is_valid():
            review_plan_cleaned = form_review_plan.cleaned_data
            review_plan_date = review_plan_cleaned['review_plan_date']

            date_tup = time.strptime(str(review_plan_date), "%Y-%m-%d")  # 字符串转换为元组
            date_stamp = time.mktime(date_tup)  # 元组转换为时间戳
            today_str = str(datetime.date.today())  # 元组转换为字符串
            today_tup = time.strptime(today_str, "%Y-%m-%d")  # 字符串转换为元组
            today_stamp = time.mktime(today_tup)  # 元组转换为时间戳

            if today_stamp - date_stamp > 0:
                response['status'] = False
                response['message'] = '计划失败，计划的时间不能早于现在的时间!'
            else:
                try:
                    '''REVIEW_STATE_LIST = ((1, '待保后'), (11, '待报告'), (21, '已完成'))'''
                    with transaction.atomic():
                        models.Review.objects.create(custom=custom_obj, review_plan_date=review_plan_date,
                                                     review_state=1, reviewor=request.user)
                        custom_list.update(review_plan_date=review_plan_date, review_state=1)
                    response['message'] = '保后计划成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '保后计划失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_review_plan.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------保后ajax------------------------------#
@login_required
@authority
def review_update_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    review_list_s = custom_obj.review_custom.filter(review_state=1)
    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
    if not post_data['review_id']:  # 自主保后
        form_review_add = forms.FormRewiewAdd(post_data)
        if form_review_add.is_valid():
            review_cleaned = form_review_add.cleaned_data
            today_str = str(datetime.date.today())
            try:
                with transaction.atomic():
                    review_obj = models.Review.objects.create(
                        custom=custom_obj, review_plan_date=today_str, review_state=81,
                        review_sty=review_cleaned['review_sty'],
                        analysis=review_cleaned['analysis'],
                        suggestion=review_cleaned['suggestion'],
                        classification=review_cleaned['classification'],
                        review_date=review_cleaned['review_date'],
                        reviewor=request.user)
                    custom_list.update(review_state=81, review_date=today_str,
                                       lately_date=review_cleaned['review_date'], )  # 更新客户信息
                response['message'] = '自主保后提交成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '自主保后提交失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_review_add.errors
    elif custom_obj.review_state != 1:
        response['status'] = False
        response['message'] = '没有待执行的保后计划，你可以采用自主保后功能添加！'
    else:
        review_list = models.Review.objects.filter(id=post_data['review_id'])
        review_obj = review_list.first()
        form_review_add = forms.FormRewiewAdd(post_data)
        if form_review_add.is_valid():
            review_cleaned = form_review_add.cleaned_data
            today_str = str(datetime.date.today())
            try:
                with transaction.atomic():
                    review_list.update(review_sty=review_cleaned['review_sty'],
                                       analysis=review_cleaned['analysis'],
                                       suggestion=review_cleaned['suggestion'],
                                       classification=review_cleaned['classification'],
                                       review_date=review_cleaned['review_date'],
                                       review_state=21)  # 更新保后信息
                    custom_list.update(review_state=21, review_date=today_str,
                                       lately_date=review_cleaned['review_date'])  # 更新客户信息
                response['message'] = '保后成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '保后失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_review_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消保后ajax-------------------------#
@login_required
@authority
def review_del_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    review_list = models.Review.objects.filter(id=post_data['review_id'])
    review_obj = review_list.first()
    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
    review_state = review_obj.review_state
    if review_state == 1:
        try:
            with transaction.atomic():
                review_list.delete()
                custom_list.update(review_plan_date=None, review_state=21)
            response['message'] = '保后计划删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法取消！！！' % review_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------补调ajax------------------------------#
@login_required
@authority
def investigate_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
    form_inv_add = forms.FormInvestigateAdd(post_data)
    if form_inv_add.is_valid():
        inv_cleaned = form_inv_add.cleaned_data
        try:
            with transaction.atomic():
                models.Investigate.objects.create(custom=custom_obj, inv_typ=inv_cleaned['inv_typ'],
                                                  i_analysis=inv_cleaned['i_analysis'],
                                                  i_suggestion=inv_cleaned['i_suggestion'],
                                                  i_classification=inv_cleaned['i_classification'],
                                                  inv_date=inv_cleaned['inv_date'],
                                                  invor=request.user)  # 创建补调信息
                custom_list.update(lately_date=inv_cleaned['inv_date'])  # 更新客户信息
            response['message'] = '补调成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '补调失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_inv_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)

# -----------------------删除补调ajax-------------------------#
@login_required
@authority
def investigate_del_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    investigate_list = models.Investigate.objects.filter(id=post_data['investigate_id'])
    try:
        with transaction.atomic():
                investigate_list.delete()
        response['message'] = '保后计划删除成功！'
    except Exception as e:
        response['status'] = False
        response['message'] = '删除失败：%s' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)