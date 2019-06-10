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
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -------------------------归档ajax-------------------------#
@login_required
@authority
def pigeonhole_add_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

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
            '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), 
            (41, '已归档'), (99, '无需归档')]'''
            if implement in [1, 11, 21, 31, 99]:
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
                if form_pigeonhole_num.is_valid():
                    num_cleaned = form_pigeonhole_num.cleaned_data
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
