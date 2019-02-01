from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
import datetime


# -----------------------委托合同列表---------------------#
@login_required
def agree(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    PAGE_TITLE = '合同管理'
    operate_agree_add = True
    '''模态框'''
    form_agree_add = forms.AgreeAddForm()  # 合同添加
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).select_related('lending', 'branch').order_by('-agree_num')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['agree_num', 'lending__summary__custom__name',
                         'branch__name', 'lending__summary__summary_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        agree_list = agree_list.filter(q)
    agree_amount = agree_list.count()  # 信息数目
    '''分页'''
    paginator = Paginator(agree_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/agree/agree.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
def agree_scan(request, agree_id):  # 查看合同
    print(__file__, '---->def agree_scan')
    APPLICATION = 'agree_scan'
    PAGE_TITLE = '合同详情'
    COUNTER_TYP_CUSTOM = [1, 2]

    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
    print('warrant_agree_list:', warrant_agree_list)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=1).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=5).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_c_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=51).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    print(custom_c_lending_list, custom_p_lending_list, warrants_h_lending_list, warrants_g_lending_list,
          warrants_r_lending_list, warrants_s_lending_list)
    from_counter = forms.AddCounterForm()

    today_str = time.strftime("%Y-%m-%d", time.gmtime())
    form_agree_sign_data = {'agree_sign_date': str(today_str)}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
def agree_scan_counter(request, agree_id, counter_id):  # 查看合同
    print(__file__, '---->def agree_scan_counter')
    APPLICATION = 'agree_scan_counter'
    PAGE_TITLE = '担保合同'
    COUNTER_TYP_CUSTOM = [1, 2]

    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
    print('warrant_agree_list:', warrant_agree_list)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=1).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=2).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_c_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=51).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    print(custom_c_lending_list, custom_p_lending_list, warrants_h_lending_list, warrants_g_lending_list,
          warrants_r_lending_list, warrants_s_lending_list)
    from_counter = forms.AddCounterForm()

    today_str = time.strftime("%Y-%m-%d", time.gmtime())
    form_agree_sign_data = {'agree_sign_date': str(today_str)}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


# -------------------------合同预览-------------------------#
@login_required
def agree_preview(request, agree_id):
    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request,
                  'dbms/agree/agree-preview.html', locals())
