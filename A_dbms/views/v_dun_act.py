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


# -----------------------添加财产线索ajax-------------------------#
@login_required
def dun_clue_add_ajax(request):  # 添加参评项目ajax
    print(__file__, '---->def dun_clue_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'),
     (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_clue_add = forms.FormClueAdd(post_data, request.FILES)
        if form_clue_add.is_valid():
            clue_cleaned = form_clue_add.cleaned_data
            clue_add_list = clue_cleaned['warrant']
            dun_clue_add_list = models.Warrants.objects.filter(id__in=clue_add_list)
            print('dun_clue_add_list:', dun_clue_add_list)
            try:
                with transaction.atomic():
                    for warrant_obj in dun_clue_add_list:
                        dun_obj.warrant.add(warrant_obj)
                response['message'] = '成功添加财产线索！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追加评审项目失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_clue_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿状态为：%s，无法追加财产线索！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除财产线索ajax-------------------------#
@login_required
def dun_clue_del_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def dun_clue_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    warrant_obj = models.Warrants.objects.get(id=post_data['warrant_id'])
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage

    if not dun_stage == 99:
        try:
            with transaction.atomic():
                dun_obj.warrant.remove(warrant_obj)  # 删除财产线索
            response['message'] = '%s，删除成功！' % warrant_obj.warrant_num
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
