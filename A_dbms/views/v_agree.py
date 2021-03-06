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
from _WHDB.views import (MenuHelper, authority, credit_term_c, convert,
                         convert_num, un_dex, amount_s, amount_y,
                         agree_list_screen, agree_right, convert_num_4)


# -----------------------委托合同列表---------------------#
@login_required
@authority
def agree(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '合同列表'
    operate_agree_add = True
    '''模态框'''
    form_agree_add = forms.AgreeAddForm()  # 合同添加
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).select_related(
        'lending', 'branch').order_by('-agree_num')
    agree_list = agree_list_screen(agree_list, request)
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'agree_num', 'lending__summary__custom__name',
            'lending__summary__custom__short_name', 'branch__name',
            'branch__short_name', 'lending__summary__summary_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        agree_list = agree_list.filter(q)

    balance = agree_list.aggregate(
        Sum('agree_balance'))['agree_balance__sum']  # 在保余额

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
@agree_right
def agree_scan(request, agree_id):  # 查看合同
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    APPLICATION = 'agree_scan'
    PAGE_TITLE = '合同详情'
    COUNTER_TYP_CUSTOM = [1, 2]
    WARRANT_TYP_OWN_LIST = [1, 2, 5, 6]
    AGREE_TYP_GZ = models.Agrees.AGREE_TYP_G

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending
    lending_obj = agree_lending_obj

    warrant_agree_list = models.Warrants.objects.filter(
        counter_warrant__counter__agree=agree_obj)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
            counter_custome__counter__agree=agree_obj).values_list(
                'id', 'name').order_by('name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
            counter_custome__counter__agree=agree_obj).values_list(
                'id', 'name').order_by('name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ__in=[
            1, 2
        ]).exclude(counter_warrant__counter__agree=agree_obj).values_list(
            'id', 'warrant_num').order_by('warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=5).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_6_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=6).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=11).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=21).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_d_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=31).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_v_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=41).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_c_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=51).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_o_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=55).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    from_counter = forms.AddCounterForm()  # 添加反担保合同form
    form_agree_sign_data = {'agree_sign_date': str(datetime.date.today())}
    form_agree_sign = forms.FormAgreeSign(
        initial=form_agree_sign_data)  # 添加反担保合同form
    form_agree_edit_date = {
        'branch': agree_obj.branch,
        'agree_typ': agree_obj.agree_typ,
        'agree_amount': agree_obj.agree_amount,
        'amount_limit': agree_obj.amount_limit,
        'agree_rate': agree_obj.agree_rate,
        'investigation_fee': agree_obj.investigation_fee,
        'agree_term': agree_obj.agree_term,
        'agree_term_typ': agree_obj.agree_term_typ,
        'guarantee_typ': agree_obj.guarantee_typ,
        'agree_copies': agree_obj.agree_copies,
        'other': agree_obj.other,
    }
    form_agree_edit = forms.AgreeEditForm(
        initial=form_agree_edit_date)  # 添加反担保合同form
    if agree_obj.agree_typ == 22:  # (22, 'D-公司保函')
        from_letter_data = {
            'starting_date': str(agree_obj.guarantee_agree.starting_date),
            'due_date': str(agree_obj.guarantee_agree.due_date),
            'letter_typ': agree_obj.guarantee_agree.letter_typ,
            'beneficiary': agree_obj.guarantee_agree.beneficiary,
            'basic_contract': agree_obj.guarantee_agree.basic_contract,
            'basic_contract_num': agree_obj.guarantee_agree.basic_contract_num,
        }
        form_letter_add = forms.LetterGuaranteeAddForm(
            initial=from_letter_data)  # 创建公司保函合同
    else:
        today_str = datetime.date.today()
        date_th_later = today_str + datetime.timedelta(days=365)
        from_letter_data = {
            'starting_date': str(today_str),
            'due_date': str(date_th_later)
        }
        form_letter_add = forms.LetterGuaranteeAddForm(
            initial=from_letter_data)  # 创建公司保函合同
    from_jk_data = {
        'agree_start_date': str(agree_obj.agree_start_date),
        'agree_due_date': str(agree_obj.agree_due_date),
        'acc_name': agree_obj.acc_name,
        'acc_num': agree_obj.acc_num,
        'acc_bank': agree_obj.acc_bank,
        'repay_method': agree_obj.repay_method,
        'repay_ex': agree_obj.repay_ex,
    }
    form_agree_jk_add = forms.AgreeJkAddForm(
        initial=from_jk_data)  # 创建小贷借款合同扩展
    form_promise_add = forms.PromiseAddForm()
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    custom_list = [
        agree_obj.lending.summary.custom,
    ]
    custom_c_lending_c = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj)
    warrants_hg6_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ__in=[1, 2, 5, 6])
    warrants_r_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11)
    warrants_s_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21)
    warrants_d_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=31)
    warrants_v_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=41)
    warrants_c_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=51)
    warrants_o_lending_l = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=55)

    SURE_LIST = [1, 2]  # 保证类
    HOUSE_LIST = [11, 21, 42, 52]  # 房产类
    GROUND_LIST = [12, 22, 43, 53]  # 土地类
    COUNSTRUCT_LIST = [14, 23]  # 在建工程类
    RECEIVABLE_LIST = [
        31,
    ]  # 应收账款类
    STOCK_LIST = [32, 51]  # 股权类
    DRAFT_LIST = [33, 44]  # 票据类
    VEHICLE_LIST = [
        15,
    ]  # 车辆类
    CHATTEL_LIST = [13, 24, 34, 47]  # 动产类
    OTHER_LIST = [39, 49]  # 其他类

    custom_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj)
    warrant_lending_h_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ__in=[1, 2])
    warrant_lending_g_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=5)
    warrant_lending_6_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=6)
    warrant_lending_r_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11)
    warrant_lending_s_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21)
    warrant_lending_d_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=31)
    warrant_lending_v_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=41)
    warrant_lending_c_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=51)
    warrant_lending_o_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=55)

    if custom_c_lending_c:
        for custom in custom_c_lending_c:
            custom_list.append(custom)
    if warrants_hg6_lending_l:
        for warrant in warrants_hg6_lending_l:
            for owership in warrant.ownership_warrant.all():
                custom_list.append(owership.owner)
    if warrants_r_lending_l:
        for r in warrants_r_lending_l:
            custom_list.append(r.receive_warrant.receive_owner)
    if warrants_s_lending_l:
        for s in warrants_s_lending_l:
            custom_list.append(s.stock_warrant.stock_owner)
    if warrants_d_lending_l:
        for d in warrants_d_lending_l:
            custom_list.append(d.draft_warrant.draft_owner)
    if warrants_v_lending_l:
        for v in warrants_v_lending_l:
            custom_list.append(v.vehicle_warrant.vehicle_owner)
    if warrants_c_lending_l:
        for c in warrants_c_lending_l:
            custom_list.append(c.chattel_warrant.chattel_owner)
    if warrants_o_lending_l:
        for o in warrants_o_lending_l:
            custom_list.append(o.other_warrant.other_owner)
    custom_list_w = []
    for custom in custom_list:
        if custom not in custom_list_w:
            custom_list_w.append(custom)

    return render(request, 'dbms/agree/agree-scan.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
@authority
@agree_right
def agree_scan_counter(request, agree_id, counter_id):  # 查看合同
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    APPLICATION = 'agree_scan_counter'
    PAGE_TITLE = '担保合同'

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(
        counter_warrant__counter__agree=agree_obj)
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
            counter_custome__counter__agree=agree_obj).values_list(
                'id', 'name').order_by('name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
            counter_custome__counter__agree=agree_obj).values_list(
                'id', 'name').order_by('name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=1).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=2).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=11).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=21).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')
    warrants_c_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj,
        warrant_typ=51).exclude(
            counter_warrant__counter__agree=agree_obj).values_list(
                'id', 'warrant_num').order_by('warrant_num')

    from_counter = forms.AddCounterForm()

    form_agree_sign_data = {'agree_sign_date': str(datetime.date.today())}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


# -------------------------合同预览-------------------------#
@login_required
@authority
@agree_right
def agree_preview(request, agree_id):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    agree_obj = models.Agrees.objects.get(id=agree_id)

    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型

    agree_amount_cn = convert(agree_obj.agree_amount)  # 转换为金额大写
    agree_amount_str = amount_s(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_amount_y = amount_y(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_term_cn = convert_num(agree_obj.agree_term)  # 合同期限转大写
    agree_copy_cn = convert_num(agree_obj.agree_copies)

    UN, ADD, CNB = un_dex(agree_obj.agree_typ)  # 不同合同种类下主体适用

    if agree_obj.agree_typ in [
            22,
    ]:  # (22, 'D-公司保函'),
        page_home_y_y = '申请人（乙方）'
        page_home_y_j = '担保人（甲方）'
    elif agree_obj.agree_typ in [
            21,
    ]:  # (21, 'D-分离式保函'),
        page_home_y_y = '乙方'
        page_home_y_j = '甲方'
    else:
        page_home_y_y = '被担保人（乙方）'
        page_home_y_j = '担保人（甲方）'

    notarization_typ = False  # 是否公证
    if agree_obj.agree_typ in [1, 2, 3, 4, 21, 22, 23]:
        agree_copy_jy_cn = convert_num(agree_obj.agree_copies - 2)
    else:
        notarization_typ = True
        agree_copy_jy_cn = convert_num(agree_obj.agree_copies - 3)
    '''利率（费率）处理'''
    agree_rate_cn_q = ''
    try:
        rate_b = True
        single_quota_rate = float(agree_obj.agree_rate)
        charge = round(agree_obj.agree_amount * single_quota_rate / 100, 2)
        agree_rate_cn_q = convert_num(float(
            agree_obj.agree_rate))  # 合同利率转换为千分之，大写
        agree_rate_p = round(((20 - float(agree_obj.agree_rate)) / 30 * 10), 4)
        agree_rate_w = convert_num_4(agree_rate_p)
        charge_cn = convert(charge)
    except ValueError:
        rate_b = False
        single_quota_rate = agree_obj.agree_rate
        agree_rate_cn_q = agree_obj.agree_rate
        agree_rate_w = '叁点叁叁叁叁'

    return render(request, 'dbms/agree/preview-agree.html', locals())


# -------------------------补充协议预览-------------------------#
@login_required
@authority
@agree_right
def supplementary_preview(request, agree_id):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    agree_obj = models.Agrees.objects.get(id=agree_id)

    agree_amount_cn = convert(agree_obj.agree_amount)  # 转换为金额大写
    agree_copy_cn = convert_num(agree_obj.agree_copies)
    investigation_fee_cn = '零'
    if agree_obj.investigation_fee > 0:
        investigation_fee_cn = convert(
            round(agree_obj.agree_amount * agree_obj.investigation_fee / 100,
                  2))  # 调查费大写

    return render(request, 'dbms/agree/preview-supplementary.html', locals())


# -------------------------反担保合同预览-------------------------#
@login_required
@authority
@agree_right
def counter_preview(request, agree_id, counter_id):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)  # 委托合同
    counter_obj = models.Counters.objects.get(id=counter_id)  # 反担保合同

    AGREE_TYP_H = models.Agrees.AGREE_TYP_H  # 最高额合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型
    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型
    X_COUNTER_TYP_LIST = models.Counters.COUNTER_TYP_X  # 保证类（反）担保合同类型
    D_COUNTER_TYP_LIST = models.Counters.COUNTER_TYP_D  # 抵押类（反）担保合同类型
    Z_COUNTER_TYP_LIST = models.Counters.COUNTER_TYP_Z  # 质押类（反）担保合同类型
    # credit_term_cn = credit_term_c(agree_obj.agree_term)  # 授信期限（月）
    credit_term_cn = convert_num(agree_obj.agree_term)  # 授信期限（月）
    counter_copy_cn = convert_num(counter_obj.counter_copies)  # 合同份数（大写）
    agree_amount = agree_obj.agree_amount
    agree_amount_cn = convert(agree_obj.agree_amount)  # 转换为货币大写
    agree_amount_str = amount_s(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_amount_y = amount_y(agree_obj.agree_amount)  # 元去掉小数点后面的零
    agree_term = agree_obj.agree_term
    agree_term_str = convert_num(agree_obj.agree_term)  # 转换为数字大写

    UN, ADD, CNB = un_dex(agree_obj.agree_typ)  # 不同合同种类下主体适用
    notarization_typ = False
    if agree_obj.agree_typ in [41, 42, 51, 52]:
        notarization_typ = True

    co_owner_list = []  # 共有人列表
    ownership_owner_list = []  # 产权人列表
    if counter_obj.counter_typ not in X_COUNTER_TYP_LIST:
        ownership_list = counter_obj.warrant_counter.warrant.all().first(
        ).ownership_warrant.all()
        for ownership in ownership_list:
            ownership_owner_list.append(ownership.owner)
        for ownership in ownership_list:
            if ownership.owner.genre == 2:
                if ownership.owner.person_custome.spouses and ownership.owner.person_custome.spouses not in ownership_owner_list:
                    co_owner_list.append(
                        ownership.owner.person_custome.spouses)

    j_typ = ''
    if counter_obj.counter_typ in X_COUNTER_TYP_LIST:  # 保证类（反）担保合同类型
        j_typ = '担保人'
    elif counter_obj.counter_typ in D_COUNTER_TYP_LIST:  # 抵押类（反）担保合同类型
        j_typ = '抵押权人'
    elif counter_obj.counter_typ in Z_COUNTER_TYP_LIST:  # 抵押类（反）担保合同类型
        j_typ = '质权人'

    if counter_obj.counter_typ in [1, 2]:  # 个人反担保
        assure_counter_obj = counter_obj.assure_counter
        custom_obj = assure_counter_obj.custome
    else:
        warrant_counter_obj = counter_obj.warrant_counter  # 抵质押（反）担保合同
        counter_warrant_count = warrant_counter_obj.warrant.count(
        )  # （反）担保合同项下抵质押物数量
        counter_warrant_list = warrant_counter_obj.warrant.all(
        )  # （反）担保合同项下抵质押物列表
        counter_warrant_obj = counter_warrant_list.first()  # （反）担保合同项下抵质押物（首个）
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        counter_warrant_typ = counter_warrant_obj.warrant_typ  # （反）担保合同项下抵质押物种类
        counter_warrant_list_count = counter_warrant_list.count()
        for counter_warrant in counter_warrant_list:
            if counter_warrant.warrant_typ == 2:  # (2, '房产包')
                counter_warrant_list_count += counter_warrant.housebag_warrant.all(
                ).count() - 1
        counter_property_type = ''
        if counter_warrant_typ in [1, 2]:  # (1, '房产'), (2, '房产包'),
            counter_property_type = '房产'
        elif counter_warrant_typ in [
                5,
        ]:  # (5, '土地'),
            counter_property_type = '国有土地使用权'
        elif counter_warrant_typ in [
                6,
        ]:  # (6, '在建工程'),
            counter_property_type = '在建工程'
        elif counter_warrant_typ in [
                11,
        ]:  # (11, '应收账款'),
            counter_property_type = '应收账款'
            counter_receive_obj = counter_warrant_obj.receive_warrant
            receive_extend_list = counter_receive_obj.extend_receiveable.all()
        elif counter_warrant_typ in [
                21,
        ]:  # (21, '股权'),
            counter_stock_obj = counter_warrant_obj.stock_warrant
            stock_registe_str = str(
                counter_stock_obj.registe).rstrip('0').rstrip('.')
            stock_share_str = str(
                counter_stock_obj.share).rstrip('0').rstrip('.')
            agree_share_cn = convert(counter_stock_obj.share * 10000)
        elif counter_warrant_typ in [
                31,
        ]:  # (31, '票据'),
            DRAFT_TYP_DIC = dict(models.Draft.TYP_LIST)
            counter_property_type = DRAFT_TYP_DIC[counter_warrant_list[0].draft_warrant.typ]
            counter_draft_obj = counter_warrant_obj.draft_warrant
            counter_draft_bag_list = counter_draft_obj.extend_draft.all()
            counter_draft_list_count = counter_draft_bag_list.count() #票据张数
            denomination_str = str(
                round(counter_draft_obj.denomination / 10000,
                      6)).rstrip('0').rstrip('.')
            denomination_cn = convert(round(counter_draft_obj.denomination, 2))
        elif counter_warrant_typ in [
                41,
        ]:  # (41, '车辆'),
            counter_vehicle_obj = counter_warrant_obj.vehicle_warrant
            counter_property_type = '车辆'
        elif counter_warrant_typ in [
                51,
        ]:  # (51, '动产'),
            '''CHATTEL_TYP_LIST = [(1, '存货'), (11, '机器设备'), (99, '其他')]'''
            chattel_typ = counter_warrant_obj.chattel_warrant.chattel_typ  # 动产种类
            if chattel_typ == 1:
                counter_property_type = '存货'
            elif chattel_typ == 11:
                counter_property_type = '机器设备'
        elif counter_warrant_typ in [
                55,
        ]:
            '''OTHER_TYP_LIST = [(11, '购房合同'), (21, '车辆合格证'), (31, '专利'), 
            (41, '商标'), (71, '账户'), (99, '其他')]'''
            counter_other_list = [
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                8,
                9,
                10,
            ]
            counter_other_obj = counter_warrant_obj.other_warrant
            other_typ = counter_other_obj.other_typ  # 其他种类
            cost_str = str(counter_other_obj.cost /
                           10000).rstrip('0').rstrip('.')
            cost_cn = convert(counter_other_obj.cost)
            if counter_other_obj.other_typ in [
                    11,
            ]:
                counter_property_type = '购房合同'
            elif counter_other_obj.other_typ in [
                    21,
            ]:
                counter_property_type = '车辆合格证'
    counter_home_b_b = ''
    if agree_obj.agree_typ == 21 or agree_obj.agree_typ == 22:  # (21, 'D-分离式保函'), (22, 'D-公司保函'),
        counter_home_b_b = '被担保人'
    else:
        counter_home_b_b = '借款人'

    agree_rate_cn_q = ''
    try:
        rate_b = True
        single_quota_rate = float(agree_obj.agree_rate)
        charge = round(agree_obj.agree_amount * single_quota_rate / 100, 2)
        agree_rate_cn_q = convert_num(float(
            agree_obj.agree_rate))  # 合同利率转换为千分之，大写
        agree_rate_w = convert_num(
            round(((20 - float(agree_obj.agree_rate)) / 30 * 10), 4))
        charge_cn = convert(charge)
    except ValueError:
        rate_b = False
        single_quota_rate = agree_obj.agree_rate
        agree_rate_cn_q = agree_obj.agree_rate
        agree_rate_w = '叁点叁叁叁叁'
    return render(request, 'dbms/agree/preview-counter.html', locals())


# -------------------------审签表预览-------------------------#
@login_required
@authority
@agree_right
def agree_sign_preview(request, agree_id):
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
    agree_typ = agree_obj.agree_typ
    '''AGREE_TYP_LIST = [(1, '单笔'), (2, '最高额'), (3, '保函'), (7, '小贷'),
                      (41, '单笔(公证)'), (42, '最高额(公证)'), (47, '小贷(公证)')]'''
    AGREE_TYP_GZ = models.Agrees.AGREE_TYP_G
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型
    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    # credit_term_cn = credit_term_c(agree_obj.agree_term)
    credit_term_cn = convert_num(agree_obj.agree_term)
    agree_amount_str = amount_s(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    article_amount_str = amount_s(round(agree_obj.lending.summary.amount, 2))
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    agree_article = agree_obj.lending.summary
    article_agree_list = models.Agrees.objects.filter(
        lending__summary=agree_article,
        id__lt=agree_obj.id).exclude(agree_state=99)
    article_agree_amount = article_agree_list.aggregate(
        Sum('agree_amount'))['agree_amount__sum']
    if not article_agree_amount:
        article_agree_amount_ar = 0
    else:
        article_agree_amount_ar = round(article_agree_amount)
        # article_agree_amount_ar = round(article_agree_amount - agree_obj.agree_amount, 2)
    article_agree_amount_ar_str = amount_s(article_agree_amount_ar)
    '''RESULT_TYP_LIST = [(11, '股东会决议'), (21, '董事会决议'), (31, '弃权声明'), (41, '单身声明')]'''
    counter_list = agree_obj.counter_agree.all()
    counter_count = counter_list.count() + 1
    '''RESULT_TYP_LIST = [(11, '股东会决议'), (13, '合伙人会议决议'), 
    (15, '举办者会议决议'),  (21, '董事会决议'), (23, '管委会决议'),
    (31, '声明书'), (41, '个人婚姻状况及财产申明')]'''
    result_list = agree_obj.result_agree.all()
    result_count = result_list.count()

    return render(request, 'dbms/agree/preview-sign.html', locals())


# -------------------------决议声明预览-------------------------#
@login_required
@authority
@agree_right
def result_preview(request, agree_id, result_id):
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    agree_obj = models.Agrees.objects.get(id=agree_id)  # 委托合同
    result_obj = models.ResultState.objects.get(id=result_id)  # 反担保合同
    result_detail = result_obj.result_detail

    return render(request, 'dbms/agree/preview-result.html', locals())


# -------------------------抵押申请预览-------------------------#
@login_required
@authority
@agree_right
def mortgage_app(request, agree_id, warrant_id):  # 抵押申请预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    agree_obj = models.Agrees.objects.get(id=agree_id)
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型

    agree_amount_cn = convert(agree_obj.agree_amount)  # 转换为金额大写
    agree_amount_str = amount_s(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_amount_y = amount_y(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_term_cn = convert_num(agree_obj.agree_term)  # 合同期限转大写
    agree_copy_cn = convert_num(agree_obj.agree_copies)

    UN, ADD, CNB = un_dex(agree_obj.agree_typ)  # 不同合同种类下主体适用

    return render(request, 'dbms/agree/preview-mortgage_app.html', locals())


# -------------------------顺位抵押知晓函预览-------------------------#
@login_required
@authority
@agree_right
def letter_knowing(request, agree_id, warrant_id):  # 顺位抵押知晓函预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    agree_obj = models.Agrees.objects.get(id=agree_id)
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型

    agree_amount_cn = convert(agree_obj.agree_amount)  # 转换为金额大写
    agree_amount_str = amount_s(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_amount_y = amount_y(agree_obj.agree_amount)  # 元转换为万元并去掉小数点后面的零
    agree_term_cn = convert_num(agree_obj.agree_term)  # 合同期限转大写
    agree_copy_cn = convert_num(agree_obj.agree_copies)
    UN, ADD, CNB = un_dex(agree_obj.agree_typ)  # 不同合同种类下主体适用

    return render(request, 'dbms/agree/preview-letter-knowing.html', locals())
