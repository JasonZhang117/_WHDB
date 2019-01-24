from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# -----------------------归档列表---------------------#
@login_required
def pigeonhole(request, *args, **kwargs):  # 归档
    print(__file__, '---->def pigeonhole')
    PAGE_TITLE = '归档管理'
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '暂存风控'), (21, '已归档')]'''
    IMPLEMENT_LIST = models.Provides.IMPLEMENT_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name', 'notify__agree__branch__name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)
    '''分页'''
    paginator = Paginator(provide_list, 18)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/pigeonhole/pigeonhole.html', locals())


# -----------------------------查看归档------------------------------#
@login_required
def pigeonhole_scan(request, provide_id):  # 查看放款
    print(__file__, '---->def pigeonhole_scan')
    PAGE_TITLE = '归档管理'

    provide_obj = models.Provides.objects.get(id=provide_id)

    form_implement_add = forms.FormImplementAdd()
    form_pigeonhole_add = forms.FormPigeonholeAdd()
    form_pigeonhole_num = forms.FormPigeonholeNumAdd()

    return render(request, 'dbms/pigeonhole/pigeonhole-scan.html', locals())


# -------------------------归档ajax-------------------------#
@login_required
def pigeonhole_add_ajax(request):
    print(__file__, '---->def pigeonhole_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    provide_id = post_data['provide_id']
    provide_list = models.Provides.objects.filter(id=provide_id)
    provide_obj = provide_list.first()
    provide_implement = provide_obj.implement
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
    if provide_implement == 41:
        response['status'] = False
        response['message'] = '已归档，无法重复提交归档信息！！！'
    else:
        form_implement_add = forms.FormImplementAdd(post_data)
        if form_implement_add.is_valid():
            implement_cleaned = form_implement_add.cleaned_data
            implement = implement_cleaned['implement']
            print('implement:', implement)
            '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
            if implement in [1, 11, 21, 31]:
                form_pigeonhole_add = forms.FormPigeonholeAdd(post_data)
                if form_pigeonhole_add.is_valid():
                    pigeonhole_cleaned = form_pigeonhole_add.cleaned_data
                    try:
                        with transaction.atomic():
                            models.Pigeonholes.objects.create(
                                provide=provide_obj, implement=implement,
                                pigeonhole_explain=pigeonhole_cleaned['pigeonhole_explain'],
                                pigeonhole_transfer=pigeonhole_cleaned['pigeonhole_transfer'],
                                pigeonholor=request.user)
                            provide_list.update(implement=implement)
                        response['message'] = '成功提交归档信息！！！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '归档信息提交失败：%s！' % str(e)
                else:
                    response['status'] = False
                    response['message'] = '表单信息有误！！！'
                    response['forme'] = form_implement_add.errors
            else:
                form_pigeonhole_num = forms.FormPigeonholeNumAdd(post_data)
                print('form_pigeonhole_num:', form_pigeonhole_num)
                if form_pigeonhole_num.is_valid():
                    num_cleaned = form_pigeonhole_num.cleaned_data
                    print('num_cleaned:', num_cleaned)
                    try:
                        provide_list.update(implement=implement, file_num=num_cleaned['file_num'])
                        response['message'] = '完成归档！！！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '归档信息提交失败：%s！' % str(e)
                else:
                    response['status'] = False
                    response['message'] = '表单信息有误！！！'
                    response['forme'] = form_pigeonhole_num.errors
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_implement_add.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
