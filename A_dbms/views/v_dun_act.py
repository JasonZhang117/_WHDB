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
def clue_add_ajax(request):  # 添加参评项目ajax
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
def clue_del_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def dun_clue_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    warrant_obj = models.Warrants.objects.get(id=post_data['warrant_id'])

    seal_list = models.Seal.objects.filter(dun=dun_obj, warrant=warrant_obj)
    if seal_list:
        response['status'] = False
        response['message'] = '财产线索已有查封信息，无法删除！！！'
        result = json.dumps(response, ensure_ascii=False)
        return HttpResponse(result)

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


# -----------------------------查封情况ajax------------------------#
@login_required
def sealup_add_ajax(request):  # 修改项目ajax
    print(__file__, '---->def dun_sealup_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_id = int(post_data['dun_id'])
    dun_obj = models.Dun.objects.get(id=dun_id)
    warrant_id = int(post_data['warrant_id'])
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_sealup_add = forms.FormSealupAdd(post_data)
        if form_sealup_add.is_valid():
            sealup_cleaned = form_sealup_add.cleaned_data
            sealup_type = sealup_cleaned['sealup_type']
            sealup_date = sealup_cleaned['sealup_date']
            due_date = sealup_cleaned['due_date']
            sealup_remark = sealup_cleaned['sealup_remark']
            try:
                with transaction.atomic():
                    default = {
                        'dun_id': dun_id, 'warrant_id': warrant_id,
                        'seal_state': sealup_type,
                        'seal_date': sealup_date,
                        'due_date': due_date,
                        'seal_remark': sealup_remark,
                        'sealor': request.user}
                    seal_obj, created = models.Seal.objects.update_or_create(
                        dun_id=dun_id, warrant_id=warrant_id, defaults=default)
                    models.Sealup.objects.create(
                        seal=seal_obj, sealup_type=sealup_type, sealup_date=sealup_date,
                        due_date=due_date, sealup_remark=sealup_remark,
                        sealupor=request.user)
                if created:
                    response['message'] = '成功创建查封信息！'
                else:
                    response['message'] = '成功更新查封信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '查封信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_sealup_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，无法修改！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------追偿台账添加ajax------------------------#
@login_required
def standing_add_ajax(request):
    print(__file__, '---->def standing_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_id = int(post_data['dun_id'])
    dun_obj = models.Dun.objects.get(id=dun_id)
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        from_standing_add = forms.FormStandingAdd(post_data)
        if from_standing_add.is_valid():
            standing_cleaned = from_standing_add.cleaned_data
            try:
                with transaction.atomic():
                    models.Standing.objects.create(
                        dun=dun_obj, standing_detail=standing_cleaned['standing_detail'],
                        standingor=request.user)
                response['message'] = '成功创建追偿信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追偿信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = from_standing_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，追偿信息创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除追偿台账ajax-------------------------#
@login_required
def standing_del_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def standing_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    standing_obj = models.Standing.objects.get(id=post_data['standing_id'])

    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                standing_obj.delete()  # 删除追偿跟进信息
            response['message'] = '追偿跟进信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------追偿费用添加ajax------------------------#
@login_required
def charge_add_ajax(request):
    print(__file__, '---->def charge_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_id = int(post_data['dun_id'])
    dun_list = models.Dun.objects.filter(id=dun_id)
    dun_obj = dun_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_charge_add = forms.FormChargeAdd(post_data)  # 追偿费用
        if form_charge_add.is_valid():
            charge_cleaned = form_charge_add.cleaned_data
            try:
                with transaction.atomic():
                    charge_obj = models.Charge.objects.create(
                        dun=dun_obj, charge_type=charge_cleaned['charge_type'],
                        charge_amount=charge_cleaned['charge_amount'],
                        charge_date=charge_cleaned['charge_date'],
                        charge_remark=charge_cleaned['charge_remark'],
                        chargor=request.user)
                    '''dun_charge_sun，更新追偿项目追偿费用息'''
                    dun_charge_amount = models.Charge.objects.filter(
                        dun=dun_obj).aggregate(Sum('charge_amount'))['charge_amount__sum']  # 追偿项目项下费用合计
                    dun_list.update(dun_charge_sun=round(dun_charge_amount, 2))  # 追偿项目，更新追偿费用总额
                response['message'] = '成功创建追偿费用信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追偿费用信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_charge_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，追偿费用信息创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除追偿费用ajax-------------------------#
@login_required
def charge_del_ajax(request):
    print(__file__, '---->def charge_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    charge_obj = models.Charge.objects.get(id=post_data['charge_id'])

    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                charge_obj.delete()  # 删除追偿费用信息
                '''dun_charge_sun，更新追偿项目追偿费用息'''
                dun_charge_amount = models.Charge.objects.filter(
                    dun=dun_obj).aggregate(Sum('charge_amount'))['charge_amount__sum']  # 追偿项目项下费用合计
                if dun_charge_amount:
                    dun_list.update(dun_charge_sun=round(dun_charge_amount, 2))  # 追偿项目，更新追偿费用总额
                else:
                    dun_list.update(dun_charge_sun=0)  # 追偿项目，更新追偿费用总额
            response['message'] = '追偿费用删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
