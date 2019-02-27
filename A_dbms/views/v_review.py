from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Avg, Min, Sum, Max, Count


# -----------------------保后列表---------------------#
@login_required
def review(request, *args, **kwargs):  # 保后列表
    print(__file__, '---->def review')
    PAGE_TITLE = '保后管理'

    REVIEW_STATE_LIST = models.Customes.REVIEW_STATE_LIST
    custom_list = models.Customes.objects.filter(**kwargs)
    '''
    custom_flow = models.FloatField(verbose_name='_流贷余额', default=0)
    custom_accept = models.FloatField(verbose_name='_承兑余额', default=0)
    custom_back = models.FloatField(verbose_name='_保函余额', default=0)
    '''
    custom_list = custom_list.filter(
        Q(custom_flow__gt=0) | Q(custom_accept__gt=0) | Q(custom_back__gt=0)).order_by('lately_date')
    print('custom_list.count()', custom_list.count())
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'short_name','contact_addr', 'linkman', 'contact_num']
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


# -----------------------------保后预览------------------------------#
@login_required
def review_scan(request, custom_id):  # 保后预览
    print(__file__, '---->def review_scan')
    PAGE_TITLE = '保后管理'

    form_review_plan = forms.FormRewiewPlanAdd()
    form_review_add = forms.FormRewiewAdd()

    custom_obj = models.Customes.objects.get(id=custom_id)
    review_custom_list = custom_obj.review_custom.all().order_by('-review_date', '-review_plan_date')
    article_custom_list = custom_obj.article_custom.all().order_by('-build_date')

    return render(request, 'dbms/review/review-scan.html', locals())


# -----------------------------保后计划ajax------------------------------#
@login_required
def review_plan_ajax(request):
    print(__file__, '---->def review_plan_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    review_list_s = custom_obj.review_custom.filter(review_state=1)
    print('review_list_s:', review_list_s)
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
            today_str = time.strftime("%Y-%m-%d", time.localtime())  # 元组转换为字符串
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
def review_update_ajax(request):
    print(__file__, '---->def review_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    review_list = models.Review.objects.filter(id=post_data['review_id'])
    review_obj = review_list.first()

    review_list_s = custom_obj.review_custom.filter(review_state=1)
    print('review_list_s:', review_list_s)
    '''REVIEW_STATE_LIST = ((1, '待保后'), (11, '待报告'), (21, '已完成'))'''
    if review_obj.review_state != 1:
        response['status'] = False
        response['message'] = '没有待执行的保后计划，你可以采用自主保后功能添加！'
    else:
        form_review_add = forms.FormRewiewAdd(post_data)
        if form_review_add.is_valid():
            review_cleaned = form_review_add.cleaned_data
            today_str = time.strftime("%Y-%m-%d", time.localtime())  # 元组转换为字符串
            try:
                with transaction.atomic():
                    review_list.update(review_sty=review_cleaned['review_sty'],
                                       analysis=review_cleaned['analysis'],
                                       suggestion=review_cleaned['suggestion'],
                                       classification=review_cleaned['classification'],
                                       review_date=today_str,
                                       review_state=21)  # 更新保后信息
                    custom_list.update(review_state=21, review_date=today_str, lately_date=today_str)  # 更新客户信息
                response['message'] = '保后计划成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '保后计划失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_review_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
