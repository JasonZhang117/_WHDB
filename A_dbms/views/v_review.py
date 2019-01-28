from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q


# -----------------------保后列表---------------------#
@login_required
def review(request, *args, **kwargs):  # 保后列表
    print(__file__, '---->def review')
    PAGE_TITLE = '保后管理'

    REVIEW_STATE_LIST = models.Customes.REVIEW_STATE_LIST
    custom_list = models.Customes.objects.filter(**kwargs)

    custom_list = custom_list.filter(
        Q(custom_flow__gt=0) | Q(custom_accept__gt=0) | Q(custom_back__gt=0)).order_by('-credit_amount')

    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'contact_addr', 'linkman', 'contact_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        custom_list = custom_list.filter(q)
    '''分页'''
    paginator = Paginator(custom_list, 10)
    page = request.GET.get('page')
    try:
        custom_list = paginator.page(page)
    except PageNotAnInteger:
        custom_list = paginator.page(1)
    except EmptyPage:
        custom_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/review/review.html', locals())


# -----------------------------保后预览------------------------------#
@login_required
def review_scan(request, custom_id):  # 保后预览
    print(__file__, '---->def review_scan')
    PAGE_TITLE = '保后管理'

    form_review_plan = forms.FormRewiewPlanAdd()
    custom_obj = models.Customes.objects.get(id=custom_id)

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
    print('custom_obj:', custom_obj)
    form_review_plan = forms.FormRewiewPlanAdd(post_data)

    if form_review_plan.is_valid():
        review_plan_cleaned = form_review_plan.cleaned_data
        try:
            custom_list.update(review_plan_date=review_plan_cleaned['review_plan_date'],
                               review_state=1)
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
