from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
import datetime
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve, reverse
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------委托合同列表---------------------#
@login_required
@authority
def agree(request, *args, **kwargs):  # 委托合同列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '合同列表'
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
                         'branch__name', 'branch__short_name', 'lending__summary__summary_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        agree_list = agree_list.filter(q)

    balance = agree_list.aggregate(Sum('agree_balance'))['agree_balance__sum']  # 在保余额

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
@authority
def agree_scan(request, agree_id):  # 查看合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    APPLICATION = 'agree_scan'
    PAGE_TITLE = '合同详情'
    COUNTER_TYP_CUSTOM = [1, 2]
    WARRANT_TYP_OWN_LIST = [1, 2, 5, 6]
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ__in=[1, 2]).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=5).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_6_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=6).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_d_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=31).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_v_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=41).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_c_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=51).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_o_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=55).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    from_counter = forms.AddCounterForm()
    form_agree_sign_data = {'agree_sign_date': str(datetime.date.today())}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    form_agree_edit_date = {
        'branch': agree_obj.branch,
        'agree_typ': agree_obj.agree_typ,
        'agree_amount': agree_obj.agree_amount,
        'amount_limit': agree_obj.amount_limit,
        'agree_rate': agree_obj.agree_rate,
        'agree_term': agree_obj.agree_term,
        'guarantee_typ': agree_obj.guarantee_typ,
        'agree_copies': agree_obj.agree_copies}
    form_agree_edit = forms.AgreeEditForm(initial=form_agree_edit_date)

    return render(request, 'dbms/agree/agree-scan.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
@authority
def agree_scan_counter(request, agree_id, counter_id):  # 查看合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    APPLICATION = 'agree_scan_counter'
    PAGE_TITLE = '担保合同'
    COUNTER_TYP_CUSTOM = [1, 2]
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    WARRANT_TYP_OWN_LIST = [1, 2, 5, 6]

    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
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

    from_counter = forms.AddCounterForm()

    form_agree_sign_data = {'agree_sign_date': str(datetime.date.today())}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


def convert(n):
    units = ['', '万', '亿']
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    decimal_label = ['角', '分']
    small_int_label = ['', '拾', '佰', '仟']
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 2))[2:]  # 分离整数和小数部分
    res = []
    if decimal_part:
        res.append(''.join([nums[int(x)] + y for x, y in list(zip(decimal_part, decimal_label)) if x != '0']))
    if int_part != '0':
        res.append('圆')
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
            tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    result = ''.join(res[::-1])
    # print('len(result):',len(result),result,result[-1])
    if not result[-1] == '分':
        result += '整'
    return result


def convert_num(n):
    units = ['', '万', '亿']
    nums = ['零', '壹', '贰', '叁', '肆', '伍', '陆', '柒', '捌', '玖']
    small_int_label = ['', '拾', '佰', '仟']
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 2))[2:]  # 分离整数和小数部分
    res = []
    if int_part != '0':
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
            tmp = tmp.rstrip('零').replace('零零零', '零').replace('零零', '零')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    result = ''.join(res[::-1])

    return result


# -------------------------合同预览-------------------------#
@login_required
@authority
def agree_preview(request, agree_id):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_typ = agree_obj.agree_typ
    agree_amount = agree_obj.agree_amount
    agree_amount_cn = convert(agree_amount)
    '''AGREE_TYP_LIST = [(1, '单笔'), (2, '最高额'), (3, '保函'), (7, '小贷'),
                      (41, '单笔(公证)'), (42, '最高额(公证)'), (47, '小贷(公证)')]'''
    agree_amount_str = str(agree_amount / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    agree_copy_cn = convert_num(agree_obj.agree_copies)
    notarization_typ = False
    if agree_typ in [1, 2, 3, 7]:
        agree_copy_jy_cn = convert_num(agree_obj.agree_copies - 2)
    else:
        notarization_typ = True
        agree_copy_jy_cn = convert_num(agree_obj.agree_copies - 3)
    try:
        rate_b = True
        single_quota_rate = float(agree_obj.agree_rate)
        charge = round(agree_amount * single_quota_rate / 100, 2)
        charge_cn = convert(charge)
    except ValueError:
        rate_b = False
        single_quota_rate = agree_obj.agree_rate

    return render(request, 'dbms/agree/preview-agree.html', locals())


# -------------------------反担保合同预览-------------------------#
@login_required
@authority
def counter_preview(request, agree_id, counter_id):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)  # 委托合同
    counter_obj = models.Counters.objects.get(id=counter_id)  # 反担保合同
    '''AGREE_TYP_LIST = [(1, '单笔'), (2, '最高额'), (3, '保函'), (7, '小贷'),
                      (41, '单笔(公证)'), (42, '最高额(公证)'), (47, '小贷(公证)')]'''
    agree_typ = agree_obj.agree_typ
    notarization_typ = False
    if agree_typ in [41, 42, 47]:
        notarization_typ = True
    '''COUNTER_TYP_LIST = [
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''
    counter_typ = counter_obj.counter_typ
    X_COUNTER_TYP_LIST = [1, 2, ]
    D_COUNTER_TYP_LIST = [11, 12, 13, 14, 15, ]
    Z_COUNTER_TYP_LIST = [31, 32, 33, 34, 41, ]

    credit_term = agree_obj.agree_term  # 授信期限（月）
    credit_term_exactly = credit_term % 12
    credit_term_cn = ''
    if credit_term_exactly == 0:
        credit_term_cn = '%s年' % convert_num(credit_term / 12)
    else:
        credit_term_cn = '%s个月' % convert_num(credit_term)

    if counter_typ in [1, 2]:
        assure_counter_obj = counter_obj.assure_counter
        custom_obj = assure_counter_obj.custome
    else:
        warrant_counter_obj = counter_obj.warrant_counter  # 抵质押反担保合同
        counter_warrant_count = warrant_counter_obj.warrant.count()  # 反担保合同项下抵质押物数量
        counter_warrant_list = warrant_counter_obj.warrant.all()  # 反担保合同项下抵质押物列表
        counter_warrant_obj = counter_warrant_list.first()  # 反担保合同项下抵质押物（首个）
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        counter_warrant_typ = counter_warrant_obj.warrant_typ  # 反担保合同项下抵质押物种类
        counter_warrant_list_count = counter_warrant_list.count()
        for counter_warrant in counter_warrant_list:
            if counter_warrant.warrant_typ == 2:
                counter_warrant_list_count += counter_warrant.housebag_warrant.all().count() - 1

        counter_property_type = ''
        if counter_warrant_typ in [1, 2]:
            counter_property_type = '房产'
        elif counter_warrant_typ == 5:
            counter_property_type = '土地使用权'
        elif counter_warrant_typ == 6:
            counter_property_type = '在建工程'
        elif counter_warrant_typ == 11:
            counter_receive_obj = counter_warrant_obj.receive_warrant
            receive_extend_list = counter_receive_obj.extend_receiveable.all()
        elif counter_warrant_typ == 21:
            counter_stock_obj = counter_warrant_obj.stock_warrant
            stock_registe_str = str(counter_stock_obj.registe).rstrip('0').rstrip('.')
            stock_share_str = str(counter_stock_obj.share).rstrip('0').rstrip('.')
            agree_share_cn = convert(counter_stock_obj.share * 10000)
        elif counter_warrant_typ == 31:
            counter_draft_obj = counter_warrant_obj.draft_warrant
            counter_draft_bag_list = counter_draft_obj.extend_draft.all()
            denomination_str = str(counter_draft_obj.denomination / 10000).rstrip('0').rstrip('.')
            denomination_cn = convert(counter_draft_obj.denomination)
        elif counter_warrant_typ == 41:
            counter_vehicle_obj = counter_warrant_obj.vehicle_warrant
        elif counter_warrant_typ == 51:
            '''CHATTEL_TYP_LIST = [(1, '存货'), (11, '机器设备'), (99, '其他')]'''
            chattel_typ = counter_warrant_obj.chattel_warrant.chattel_typ  # 动产种类
            if chattel_typ == 1:
                counter_property_type = '存货'
            elif chattel_typ == 11:
                counter_property_type = '机器设备'
        elif counter_warrant_typ == 55:
            '''OTHER_TYP_LIST = [(11, '购房合同'), (21, '车辆合格证'), (31, '专利'), (41, '商标'), (71, '账户'),
                      (99, '其他')]'''
            counter_other_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, ]
            counter_other_obj = counter_warrant_obj.other_warrant
            other_typ = counter_other_obj.other_typ  # 其他种类
            cost_str = str(counter_other_obj.cost / 10000).rstrip('0').rstrip('.')
            cost_cn = convert(counter_other_obj.cost)
            if other_typ == 11:
                counter_property_type = '购房合同'
            elif other_typ == 21:
                counter_property_type = '车辆合格证'

    agree_amount = agree_obj.agree_amount
    agree_amount_cn = convert(agree_amount)
    agree_amount_str = str(agree_amount / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    agree_term = agree_obj.agree_term
    agree_term_str = convert_num(agree_term)

    return render(request, 'dbms/agree/preview-counter.html', locals())


# -------------------------审签表预览-------------------------#
@login_required
@authority
def agree_sign_preview(request, agree_id):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)
    '''COUNTER_TYP_LIST = [
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''

    agree_amount = agree_obj.agree_amount
    agree_amount_str = str(agree_amount / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    article_amount = agree_obj.lending.summary.amount
    article_amount_str = str(article_amount / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    agree_article = agree_obj.lending.summary
    article_agree_list = models.Agrees.objects.filter(lending__summary=agree_article).exclude(agree_state=99)
    article_agree_amount = article_agree_list.aggregate(Sum('agree_amount'))['agree_amount__sum']
    article_agree_amount_ar = round(article_agree_amount - agree_amount, 2)
    article_agree_amount_ar_str = str(article_agree_amount_ar / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    '''RESULT_TYP_LIST = [(11, '股东会决议'), (21, '董事会决议'), (31, '弃权声明'), (41, '单身声明')]'''
    counter_list = agree_obj.counter_agree.all()
    counter_count = counter_list.count() + 1
    result_list = agree_obj.result_agree.filter(result_typ__in=[31, 41])
    result_count = result_list.count()

    return render(request, 'dbms/agree/preview-sign.html', locals())


# -------------------------决议声明预览-------------------------#
@login_required
@authority
def result_preview(request, agree_id, result_id):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)  # 委托合同
    result_obj = models.ResultState.objects.get(id=result_id)  # 反担保合同
    result_detail = result_obj.result_detail

    return render(request, 'dbms/agree/preview-result.html', locals())
