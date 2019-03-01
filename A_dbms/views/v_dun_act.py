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


# -----------------------新建追偿项目ajax-------------------------#
@login_required
def dun_add_ajax(request):  # 添加参评项目ajax
    print(__file__, '---->def dun_clue_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    form_dun_add = forms.FormDunAdd(post_data)  # 新建追偿项目
    if form_dun_add.is_valid():
        dun_cleaned = form_dun_add.cleaned_data
        dun_add_list = dun_cleaned['cmpensatory']
        dun_com_add_list = models.Compensatories.objects.filter(id__in=dun_add_list)
        print('dun_com_add_list:', dun_com_add_list)
        costom_short_name = dun_com_add_list.first().provide.notify.agree.lending.summary.custom.short_name
        dun_charge_amount = dun_com_add_list.aggregate(Sum('compensatory_amount'))['compensatory_amount__sum']
        dun_title = '追偿-%s-%s' % (costom_short_name, dun_charge_amount)
        try:
            with transaction.atomic():
                dun_obj = models.Dun.objects.create(title=dun_title, dun_amount=dun_charge_amount, dunor=request.user)
                for com_obj in dun_com_add_list:
                    dun_obj.compensatory.add(com_obj)
                '''DUN_STATE_LIST = ((1, '已代偿'), (3, '诉前'), (11, '已起诉'), (21, '已判决'), (31, '已和解'),
                      (41, '执行中'), (91, '结案'))'''
                dun_com_add_list.update(dun_state=3)
            response['message'] = '成功创建追偿项目！'
        except Exception as e:
            response['status'] = False
            response['message'] = '追偿项目创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_dun_add.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------添加财产线索ajax-------------------------#
@login_required
def clue_add_ajax(request):  #
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
                    '''AUCTION_STATE_LIST = (
                        (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                        (31, '回转'), (99, '注销'))'''
                    dun_clue_add_list.update(auction_state=2)
                response['message'] = '成功添加财产线索！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追添加财产线索失败：%s' % str(e)
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
    warrant_list = models.Warrants.objects.filter(id=post_data['warrant_id'])
    warrant_obj = warrant_list.first()

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
                '''AUCTION_STATE_LIST = (
                    (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                    (31, '回转'), (99, '注销'))'''
                warrant_list.update(auction_state=1)
            response['message'] = '%s，删除成功！' % warrant_obj.warrant_num
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------添加被告人ajax-------------------------#
@login_required
def defendant_add_ajax(request):  #
    print(__file__, '---->def defendant_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'),
     (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        from_custom_add = forms.FormCustomAdd(post_data, request.FILES)
        if from_custom_add.is_valid():
            custom_cleaned = from_custom_add.cleaned_data
            custom_add_list = custom_cleaned['custom']
            dun_custom_add_list = models.Customes.objects.filter(id__in=custom_add_list)
            print('dun_custom_add_list:', dun_custom_add_list)
            try:
                with transaction.atomic():
                    for custom_obj in dun_custom_add_list:
                        dun_obj.custom.add(custom_obj)
                    '''CUSTOM_DUN_LIST = ((1, '正常'), (11, '被告'), (99, '注销'))'''
                    dun_custom_add_list.update(custom_dun_state=11)
                response['message'] = '成功添加被告人！'
            except Exception as e:
                response['status'] = False
                response['message'] = '添加被告人失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = from_custom_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿状态为：%s，无法添加被告人！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除被告人ajax-------------------------#
@login_required
def defendant_del_ajax(request):  # 删除被告人ajax
    print(__file__, '---->def defendant_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    custom_list = models.Customes.objects.filter(id=post_data['custom_id'])
    custom_obj = custom_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                dun_obj.custom.remove(custom_obj)  # 删除财产线索
                '''CUSTOM_DUN_LIST = ((1, '正常'), (11, '被告'), (99, '注销'))'''
                custom_list.update(custom_dun_state=1)
            response['message'] = '%s，删除成功！' % custom_obj.name
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
    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    warrant_list = models.Warrants.objects.filter(id=post_data['warrant_id'])
    warrant_obj = warrant_list.first()
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
                    seal_default = {
                        'dun': dun_obj, 'warrant': warrant_obj, 'seal_state': sealup_type,
                        'seal_date': sealup_date, 'due_date': due_date,
                        'seal_remark': sealup_remark, 'sealor': request.user}
                    seal_obj, created = models.Seal.objects.update_or_create(
                        dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                    sealup_default = {
                        'seal': seal_obj, 'sealup_type': sealup_type, 'sealup_date': sealup_date,
                        'due_date': due_date, 'sealup_remark': sealup_remark,
                        'sealupor': request.user}
                    sealup_obj, created = models.Sealup.objects.update_or_create(
                        seal=seal_obj, sealup_type=sealup_type, sealup_date=sealup_date, defaults=sealup_default)
                    '''SEALUP_TYPE_LIST = ((1, '诉前保全'), (5, '首次首封'), (11, '首次轮封'), (21, '续查封'),
                        (51, '解除查封'), (99, '注销'))'''
                    '''AUCTION_STATE_LIST = (
                        (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), 
                        (21, '流拍'), (31, '回转'), (99, '注销'))'''
                    warrant_list.update(auction_state=2)
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


# -----------------------------查询情况ajax------------------------#
@login_required
def inquiry_add_ajax(request):
    print(__file__, '---->def inquiry_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    warrant_list = models.Warrants.objects.filter(id=post_data['warrant_id'])
    warrant_obj = warrant_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_inquiry_add = forms.FormInquiryAdd(post_data)  # 查询
        if form_inquiry_add.is_valid():
            inquiry_cleaned = form_inquiry_add.cleaned_data
            inquiry_type = inquiry_cleaned['inquiry_type']
            inquiry_detail = inquiry_cleaned['inquiry_detail']
            '''INQUIRY_TYPE_LIST = (
            (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'), 
            (31, '执行回转'), (99, '注销'))'''
            if inquiry_type == 1:
                try:
                    with transaction.atomic():
                        seal_default = {
                            'dun': dun_obj, 'warrant': warrant_obj, 'inquiry_date': datetime.date.today(),
                            'sealor': request.user}
                        seal_obj, created = models.Seal.objects.update_or_create(
                            dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                        inquiry_default = {
                            'seal': seal_obj, 'inquiry_type': inquiry_type, 'inquiry_detail': inquiry_detail,
                            'inquiryor': request.user}
                        inquiry_obj, created = models.Inquiry.objects.update_or_create(
                            seal__warrant=warrant_obj, inquiry_type=inquiry_type, inquiryor_date=datetime.date.today(),
                            defaults=inquiry_default)
                        warrant_list.update(
                            inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail)
                    if created:
                        response['message'] = '成功创建查询信息！'
                    else:
                        response['message'] = '成功更新查询信息！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '查询信息创建失败：%s！' % str(e)
            elif inquiry_type == 3:  # (3, '拍卖评估')
                form_evaluate_add = forms.FormInquiryEvaluateAdd(post_data)  # 评估
                if form_evaluate_add.is_valid():
                    evaluate_cleaned = form_evaluate_add.cleaned_data
                    evaluate_date = evaluate_cleaned['evaluate_date']
                    evaluate_value = evaluate_cleaned['evaluate_value']
                    try:
                        with transaction.atomic():
                            seal_default = {
                                'dun': dun_obj, 'warrant': warrant_obj,
                                'inquiry_date': datetime.date.today(),
                                'sealor': request.user}
                            seal_obj, created = models.Seal.objects.update_or_create(
                                dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                            inquiry_default = {
                                'seal': seal_obj,
                                'inquiry_type': inquiry_type,
                                'inquiry_detail': inquiry_detail,
                                'evaluate_date': evaluate_date,
                                'evaluate_value': evaluate_value,
                                'inquiryor': request.user}
                            inquiry_obj, created = models.Inquiry.objects.update_or_create(
                                seal__warrant=warrant_obj, inquiry_type=inquiry_type, evaluate_date=evaluate_date,
                                defaults=inquiry_default)
                            ''' INQUIRY_TYPE_LIST = (
                            (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
                            (31, '执行回转'), (99, '注销'))'''
                            '''AUCTION_STATE_LIST = (
                            (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                            (31, '回转'), (99, '注销'))'''
                            warrant_list.update(
                                inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail,
                                evaluate_state=41, auction_state=3, evaluate_date=evaluate_date,
                                evaluate_value=evaluate_value)
                        if created:
                            response['message'] = '成功创建查询信息！'
                        else:
                            response['message'] = '成功更新查询信息！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '查询信息创建失败：%s！' % str(e)
                else:
                    response['status'] = False
                    response['message'] = '表单信息有误！！！'
                    response['forme'] = form_evaluate_add.errors
            elif inquiry_type == 5:  # (5, '拍卖挂网')
                form_hanging_add = forms.FormInquiryHangingAdd()  # 挂网
                if form_hanging_add.is_valid():
                    hanging_cleaned = form_hanging_add.cleaned_data
                    auction_date = hanging_cleaned['auction_date']
                    listing_price = hanging_cleaned['listing_price']
                    try:
                        with transaction.atomic():
                            seal_default = {
                                'dun': dun_obj, 'warrant': warrant_obj,
                                'inquiry_date': datetime.date.today(),
                                'sealor': request.user}
                            seal_obj, created = models.Seal.objects.update_or_create(
                                dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                            inquiry_default = {
                                'seal': seal_obj,
                                'inquiry_type': inquiry_type,
                                'inquiry_detail': inquiry_detail,
                                'auction_date': auction_date,
                                'listing_price': listing_price,
                                'inquiryor': request.user}
                            inquiry_obj, created = models.Inquiry.objects.update_or_create(
                                seal__warrant=warrant_obj, inquiry_type=inquiry_type, auction_date=auction_date,
                                defaults=inquiry_default)
                            ''' INQUIRY_TYPE_LIST = (
                            (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
                            (31, '执行回转'), (99, '注销'))'''
                            '''AUCTION_STATE_LIST = (
                            (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                            (31, '回转'), (99, '注销'))'''
                            warrant_list.update(
                                inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail,
                                auction_state=5, auction_date=auction_date, listing_price=listing_price)
                        if created:
                            response['message'] = '成功创建查询信息！'
                        else:
                            response['message'] = '成功更新查询信息！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '查询信息创建失败：%s！' % str(e)
                else:
                    response['status'] = False
                    response['message'] = '表单信息有误！！！'
                    response['forme'] = form_hanging_add.errors
            elif inquiry_type == 11:  # (11, '拍卖成交')
                form_turn_add = forms.FormInquiryTurnAdd()  # 成交
                if form_turn_add.is_valid():
                    turn_cleaned = form_turn_add.cleaned_data
                    transaction_date = turn_cleaned['transaction_date']
                    auction_amount = turn_cleaned['auction_date']
                    try:
                        with transaction.atomic():
                            seal_default = {
                                'dun': dun_obj, 'warrant': warrant_obj, 'inquiry_date': datetime.date.today(),
                                'sealor': request.user}
                            seal_obj, created = models.Seal.objects.update_or_create(
                                dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                            inquiry_default = {
                                'seal': seal_obj, 'inquiry_type': inquiry_type, 'inquiry_detail': inquiry_detail,
                                'transaction_date': transaction_date, 'auction_amount': auction_amount,
                                'inquiryor': request.user}
                            inquiry_obj, created = models.Inquiry.objects.update_or_create(
                                seal__warrant=warrant_obj, inquiry_type=inquiry_type, transaction_date=transaction_date,
                                defaults=inquiry_default)
                            ''' INQUIRY_TYPE_LIST = (
                            (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
                            (31, '执行回转'), (99, '注销'))'''
                            '''AUCTION_STATE_LIST = (
                            (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                            (31, '回转'), (99, '注销'))'''
                            warrant_list.update(
                                inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail,
                                auction_state=11, transaction_date=transaction_date, auction_amount=auction_amount)
                        if created:
                            response['message'] = '成功创建查询信息！'
                        else:
                            response['message'] = '成功更新查询信息！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '查询信息创建失败：%s！' % str(e)
                else:
                    response['status'] = False
                    response['message'] = '表单信息有误！！！'
                    response['forme'] = form_turn_add.errors
            elif inquiry_type == 21:  # (21, '拍卖流拍'):
                try:
                    with transaction.atomic():
                        seal_default = {
                            'dun': dun_obj, 'warrant': warrant_obj,
                            'inquiry_date': datetime.date.today(),
                            'sealor': request.user}
                        seal_obj, created = models.Seal.objects.update_or_create(
                            dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                        inquiry_default = {
                            'seal': seal_obj,
                            'inquiry_type': inquiry_type,
                            'inquiry_detail': inquiry_detail,
                            'inquiryor': request.user}
                        inquiry_obj, created = models.Inquiry.objects.update_or_create(
                            seal__warrant=warrant_obj, inquiry_type=inquiry_type, defaults=inquiry_default)
                        ''' INQUIRY_TYPE_LIST = (
                        (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
                        (31, '执行回转'), (99, '注销'))'''
                        '''AUCTION_STATE_LIST = (
                        (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                        (31, '回转'), (99, '注销'))'''
                        warrant_list.update(
                            inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail,
                            auction_state=21)
                    if created:
                        response['message'] = '成功创建查询信息！'
                    else:
                        response['message'] = '成功更新查询信息！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '查询信息创建失败：%s！' % str(e)
            elif inquiry_type == 31:  # (31, '执行回转'):
                try:
                    with transaction.atomic():
                        seal_default = {
                            'dun': dun_obj, 'warrant': warrant_obj,
                            'inquiry_date': datetime.date.today(),
                            'sealor': request.user}
                        seal_obj, created = models.Seal.objects.update_or_create(
                            dun=dun_obj, warrant=warrant_obj, defaults=seal_default)
                        inquiry_default = {
                            'seal': seal_obj,
                            'inquiry_type': inquiry_type,
                            'inquiry_detail': inquiry_detail,
                            'inquiryor': request.user}
                        inquiry_obj, created = models.Inquiry.objects.update_or_create(
                            seal__warrant=warrant_obj, inquiry_type=inquiry_type, defaults=inquiry_default)
                        ''' INQUIRY_TYPE_LIST = (
                        (1, '日常跟踪'), (3, '拍卖评估'), (5, '拍卖挂网'), (11, '拍卖成交'), (21, '拍卖流拍'),
                        (31, '执行回转'), (99, '注销'))'''
                        '''AUCTION_STATE_LIST = (
                        (1, '正常'), (2, '查封'), (3, '评估'), (5, '挂网'), (11, '成交'), (21, '流拍'), 
                        (31, '回转'), (99, '注销'))'''
                        warrant_list.update(
                            inquiry_date=datetime.date.today(), inquiry_detail=inquiry_detail,
                            auction_state=31)
                    if created:
                        response['message'] = '成功创建查询信息！'
                    else:
                        response['message'] = '成功更新查询信息！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '查询信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_inquiry_add.errors
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
def standing_del_ajax(request):
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


# -----------------------------案款回收添加ajax------------------------#
@login_required
def retrieve_add_ajax(request):
    print(__file__, '---->def retrieve_add_ajax')
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
        form_retrieve_add = forms.FormRetrieveAdd(post_data)  # 案款回收

        if form_retrieve_add.is_valid():
            retrieve_cleaned = form_retrieve_add.cleaned_data
            try:
                with transaction.atomic():
                    retrieve_obj = models.Retrieve.objects.create(
                        dun=dun_obj, retrieve_type=retrieve_cleaned['retrieve_type'],
                        retrieve_amount=retrieve_cleaned['retrieve_amount'],
                        retrieve_date=retrieve_cleaned['retrieve_date'],
                        retrieve_remark=retrieve_cleaned['retrieve_remark'],
                        retrievor=request.user)
                    '''dun_retrieve_sun，更新追偿项目案款回收'''
                    dun_retrieve_amount = models.Retrieve.objects.filter(
                        dun=dun_obj).aggregate(Sum('retrieve_amount'))['retrieve_amount__sum']  # 追偿项目项下回款合计
                    dun_list.update(dun_retrieve_sun=round(dun_retrieve_amount, 2))  # 追偿项目，更新回款总额
                response['message'] = '成功创建案款回收信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '案款回收信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_retrieve_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，案款回收信息创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除案款回收ajax-------------------------#
@login_required
def retrieve_del_ajax(request):
    print(__file__, '---->def retrieve_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    retrieve_obj = models.Retrieve.objects.get(id=post_data['retrieve_id'])

    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                retrieve_obj.delete()  # 删除案款回收信息
                '''dun_retrieve_sun，更新追偿项目案款回收'''
                dun_retrieve_amount = models.Retrieve.objects.filter(
                    dun=dun_obj).aggregate(Sum('retrieve_amount'))['retrieve_amount__sum']  # 追偿项目项下回款合计
                if dun_retrieve_amount:
                    dun_list.update(dun_retrieve_sun=round(dun_retrieve_amount, 2))  # 追偿项目，更新追偿费用总额
                else:
                    dun_list.update(dun_retrieve_sun=0)  # 追偿项目，更新追偿费用总额
            response['message'] = '案款回收信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '案款回收信息删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------资料目录添加ajax------------------------#
@login_required
def stage_add_ajax(request):
    print(__file__, '---->def stage_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_stage_add = forms.FormStageAdd(post_data)  # 目录
        if form_stage_add.is_valid():
            stage_cleaned = form_stage_add.cleaned_data
            stage_type = stage_cleaned['stage_type']
            '''STAGE_TYPE_LIST = ((1, '证据及财产线索资料'), (11, '诉前资料'), (21, '一审资料'),
                       (31, '上诉及再审'), (41, '案外之诉'),
                       (51, '执行资料'), (99, '其他'))'''
            stage_type_count = str(models.Stage.objects.filter(dun=dun_obj, stage_type=stage_type).count() + 1)
            '''DUN_STATE_LIST = ((1, '已代偿'), (3, '诉前'), (11, '一审'), (21, '上诉及再审'), (31, '案外之诉'),
                      (41, '执行'), (91, '结案'))'''
            stage_remark = ''
            if stage_type == 1:
                stage_remark = 'A-%s' % stage_type_count
            elif stage_type == 11:
                stage_remark = 'B-%s' % stage_type_count
            elif stage_type == 21:
                stage_remark = 'C-%s' % stage_type_count
                dun_state_n = 11
            elif stage_type == 31:
                stage_remark = 'D-%s' % stage_type_count
                dun_state_n = 21
            elif stage_type == 41:
                stage_remark = 'E-%s' % stage_type_count
                dun_state_n = 31
            elif stage_type == 51:
                stage_remark = 'F-%s' % stage_type_count
                dun_state_n = 41
            print('stage_remark:', stage_remark, type(stage_remark))
            try:
                with transaction.atomic():
                    stage_obj = models.Stage.objects.create(
                        dun=dun_obj, stage_type=stage_type, stage_file=stage_cleaned['stage_file'],
                        stage_date=stage_cleaned['stage_date'], stage_state=stage_cleaned['stage_state'],
                        stage_remark=stage_remark, stagor=request.user)
                    '''STAGE_TYPE_LIST = ((1, '证据及财产线索资料'), (11, '诉前资料'), (21, '一审资料'),
                        (31, '上诉及再审'), (41, '案外之诉'), (51, '执行资料'), (99, '其他'))'''
                    '''DUN_STATE_LIST = ((1, '已代偿'), (3, '诉前'), (11, '一审'), (21, '上诉及再审'), (31, '案外之诉'),
                      (41, '执行'), (91, '结案'))'''
                    if stage_type in [21, 31, 41, 51]:
                        dun_obj.compensatory.all().update(dun_state=dun_state_n)

                response['message'] = '成功创建资料目录信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追偿资料目录创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_stage_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，资料目录创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除资料目录ajax-------------------------#
@login_required
def stage_del_ajax(request):  #
    print(__file__, '---->def stage_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    stage_obj = models.Stage.objects.get(id=post_data['stage_id'])

    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                stage_obj.delete()  # 删除
            response['message'] = '追偿资料目录信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------判决添加ajax------------------------#
@login_required
def judgment_add_ajax(request):
    print(__file__, '---->def judgment_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_judgment_add = forms.FormJudgmentAdd(post_data)  # 判决裁定
        if form_judgment_add.is_valid():
            judgment_cleaned = form_judgment_add.cleaned_data
            try:
                with transaction.atomic():
                    judgment_obj = models.Judgment.objects.create(
                        dun=dun_obj,
                        judgment_file=judgment_cleaned['judgment_file'],
                        judgment_detail=judgment_cleaned['judgment_detail'],
                        judgment_unit=judgment_cleaned['judgment_unit'],
                        judgment_date=judgment_cleaned['judgment_date'],
                        judgmentor=request.user)
                response['message'] = '成功创建判决信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '判决信息创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_judgment_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，判决信息创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除判决ajax-------------------------#
@login_required
def judgment_del_ajax(request):  #
    print(__file__, '---->def judgment_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    dun_obj = models.Dun.objects.get(id=post_data['dun_id'])
    judgment_obj = models.Judgment.objects.get(id=post_data['judgment_id'])

    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        try:
            with transaction.atomic():
                judgment_obj.delete()  # 删除
            response['message'] = '判决书信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '状态为：%s，无法删除！！！' % dun_stage
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------委托代理添加ajax------------------------#
@login_required
def agent_add_ajax(request):
    print(__file__, '---->def agent_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_agent_add = forms.FormAgentAdd(post_data)  # 代理合同
        if form_agent_add.is_valid():
            agent_cleaned = form_agent_add.cleaned_data
            try:
                with transaction.atomic():
                    agent_obj = models.Agent.objects.create(
                        dun=dun_obj,
                        agent_agree=agent_cleaned['agent_agree'],
                        agent_item=agent_cleaned['agent_item'],
                        fee_scale=agent_cleaned['fee_scale'],
                        agent_date=agent_cleaned['agent_date'],
                        due_date=agent_cleaned['due_date'],
                        agent_remark=agent_cleaned['agent_remark'],
                        agentor=request.user)
                response['message'] = '成功创建委托代理信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '委托代理创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agent_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，委托代理创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------联系人添加ajax------------------------#
@login_required
def staff_add_ajax(request):
    print(__file__, '---->def staff_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    dun_list = models.Dun.objects.filter(id=post_data['dun_id'])
    dun_obj = dun_list.first()
    '''DUN_STAGE_LIST = ((1, '起诉'), (11, '判决'), (21, '执行'), (31, '和解结案'), 
    (41, '终止执行'), (99, '注销'))'''
    dun_stage = dun_obj.dun_stage
    if not dun_stage == 99:
        form_staff_add = forms.FormStaffAdd(post_data)  # 联系人
        if form_staff_add.is_valid():
            staff_cleaned = form_staff_add.cleaned_data
            try:
                with transaction.atomic():
                    staff_obj = models.Staff.objects.create(
                        dun=dun_obj,
                        staff_name=staff_cleaned['staff_name'],
                        staff_type=staff_cleaned['staff_type'],
                        contact_number=staff_cleaned['contact_number'],
                        staff_remark=staff_cleaned['staff_remark'],
                        staffor=request.user)
                response['message'] = '成功创建联系人理信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = '联系人创建失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_staff_add.errors
    else:
        response['status'] = False
        response['message'] = '追偿项目状态为：%s，联系人创建失败！！！' % dun_stage

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
