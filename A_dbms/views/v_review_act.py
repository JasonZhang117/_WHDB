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
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    review_list_s = custom_obj.review_custom.filter(review_state=1)
    provide_list = models.Provides.objects.filter(
        notify__agree__lending__summary__custom=custom_obj,
        provide_status__in=[1, 15])
    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
    today_str = str(datetime.date.today())
    if post_data['review_id'] == 'N':  # 自主保后
        form_review_add = forms.FormRewiewAdd(post_data)
        if form_review_add.is_valid():
            review_cleaned = form_review_add.cleaned_data
            classification = review_cleaned['classification']
            review_date = review_cleaned['review_date']
            try:
                with transaction.atomic():
                    review_obj = models.Review.objects.create(
                        custom=custom_obj, review_plan_date=today_str, review_state=81,
                        review_sty=review_cleaned['review_sty'],
                        analysis=review_cleaned['analysis'],
                        suggestion=review_cleaned['suggestion'],
                        classification=classification,
                        review_date=review_cleaned['review_date'],
                        reviewor=request.user)
                    custom_list.update(review_state=81, review_date=review_date,
                                       classification=classification,
                                       lately_date=review_date, )  # 更新客户信息
                    # provide_list.update(fication=classification, fic_date=review_date, providor=request.user)
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
            classification = review_cleaned['classification']
            review_date = review_cleaned['review_date']
            try:
                with transaction.atomic():
                    review_list.update(review_sty=review_cleaned['review_sty'],
                                       analysis=review_cleaned['analysis'],
                                       suggestion=review_cleaned['suggestion'],
                                       classification=classification,
                                       review_date=review_date,
                                       review_state=21)  # 更新保后信息
                    custom_list.update(review_state=21, review_date=review_date,
                                       classification=classification,
                                       lately_date=review_date)  # 更新客户信息
                    # provide_list.update(fication=classification, fic_date=review_date, providor=request.user)
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


# -----------------------分类ajax-------------------------#
@login_required
@authority
def fication_add_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    form_fication = forms.FormFicationAdd(post_data)
    if form_fication.is_valid():
        fication_cleaned = form_fication.cleaned_data
        fic_date = fication_cleaned['fic_date']
        fication = fication_cleaned['fication']
        try:
            with transaction.atomic():
                provide_list.update(fic_date=fic_date, fication=fication, )
                fication_default = {
                    'provide': provide_obj,
                    'fic_date': fic_date,
                    'fication': fication,
                    'explain': fication_cleaned['explain'],
                    'ficationor': request.user}
                fication_obj, created = models.Fication.objects.update_or_create(
                    provide=provide_obj, fic_date=fic_date,
                    defaults=fication_default)
            response['message'] = '分类成功！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '分类失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_fication.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------分类ajax-------------------------#
@login_required
@authority
def fication_all_ajax(request, *args, **kwargs):
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    ini_fication = int(post_data['ini_fication'])

    if ini_fication > 0:
        provide_list = models.Provides.objects.filter(provide_balance__gt=0, fication=ini_fication)
    else:
        response['status'] = False
        response['message'] = '不能对所有类型项目进行批量分类，请选择具体分类类型'
        result = json.dumps(response, ensure_ascii=False)
        return HttpResponse(result)

    form_fication_all = forms.FormFicationAll(post_data)
    if form_fication_all.is_valid():
        fication_all_cleaned = form_fication_all.cleaned_data
        fic_date = fication_all_cleaned['fic_date']
        fication = fication_all_cleaned['fication']
        try:
            with transaction.atomic():
                for provide in provide_list:
                    provide_list.update(fic_date=fic_date, fication=fication, )
                    fication_default = {
                        'provide': provide,
                        'fic_date': fic_date,
                        'fication': fication,
                        'ficationor': request.user}
                    fication_obj, created = models.Fication.objects.update_or_create(
                        provide=provide, fic_date=fic_date,
                        defaults=fication_default)
            response['message'] = '批量分类分类成功！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '批量分类成功失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_fication_all.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消保后ajax-------------------------#
@login_required
@authority
def review_del_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

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
                '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
                custom_review = models.Review.objects.filter(custom=custom_obj, review_state=1)
                if custom_review:  # 如有尚未完成的保后计划,(61, '补调替代')
                    '''REVIEW_STY_LIST = [(1, '现场检查'), (11, '电话回访'), (61, '补调替代'), (62, '尽调替代')]'''
                    custom_review.update(review_sty=61, review_state=21, review_date=inv_cleaned['inv_date'])
                    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
                    custom_list.update(review_state=21, review_date=inv_cleaned['inv_date'])
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
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

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
