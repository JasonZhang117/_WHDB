from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.urls import resolve, reverse
from .v_agree import convert_num
from _WHDB.views import (MenuHelper, authority, article_right, article_list_screen,
                         amount_s, credit_term_c, UND, UNX, convert_str)


# -----------------------appraisal评审情况-------------------------#
@login_required
@authority
def appraisal(request, *args, **kwargs):  # 评审情况
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '评审管理'  # 页面标题
    '''模态框'''
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'),(61, '待变更'), (99, '已注销'))'''
    ARTICLE_STATE_LIST = models.Articles.ARTICLE_STATE_LIST  # 筛选条件
    '''筛选'''
    appraisal_list = models.Articles.objects.filter(**kwargs).select_related(
        'custom', 'director', 'assistant', 'control')
    appraisal_list = article_list_screen(appraisal_list, request)  # 项目筛选
    # appraisal_list = appraisal_list.filter(article_state__in=[4, 5, 51, 61])
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['article_num', 'custom__name', 'director__name', 'assistant__name',
                         'control__name', 'summary_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        appraisal_list = appraisal_list.filter(q)
    appraisal_amount = appraisal_list.count()  # 信息数目
    '''分页'''
    paginator = Paginator(appraisal_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    return render(request, 'dbms/appraisal/appraisal.html', locals())


# -----------------------appraisal_scan评审项目-------------------------#
@login_required
@authority
@article_right
def appraisal_scan(request, article_id):  # 评审项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '项目评审'
    single_operate = True
    comment_operate = True
    lending_operate = True
    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_obj.article_state in [1, 2, 3, 4]:
        form_date = {'renewal': article_obj.renewal, 'augment': article_obj.augment,
                     'sign_date': str(datetime.date.today())}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)
    else:
        form_date = {
            'summary_num': article_obj.summary_num, 'sign_type': article_obj.sign_type, 'renewal': article_obj.renewal,
            'augment': article_obj.augment, 'credit_amount': article_obj.custom.credit_amount,
            'rcd_opinion': article_obj.rcd_opinion,
            'convenor_opinion': article_obj.convenor_opinion, 'sign_detail': article_obj.sign_detail,
            'sign_date': str(article_obj.sign_date)}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)  # 项目签批form
    form_comment = forms.CommentsAddForm()  # 评委意见form
    form_single = forms.SingleQuotaForm()  # 单项额度form
    form_supply = forms.FormAddSupply()  # 补调问题form
    form_lending = forms.FormLendingOrder()  # 放款次序form
    form_article_change = forms.ArticleChangeForm(initial={'change_date': str(datetime.date.today())})  # 项目变更form
    form_inv_add = forms.FormInvestigateAdd(initial={'inv_date': str(datetime.date.today())})  # 补调添加form
    investigate_custom_list = article_obj.custom.inv_custom.all().order_by('-inv_date')  # 补调列表

    return render(request, 'dbms/appraisal/appraisal-scan.html', locals())


# -----------------------appraisal_scan_lending评审项目预览-------------------------#
@login_required
@authority
@article_right
def appraisal_scan_lending(request, article_id, lending_id):  # 评审项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款次序'
    article_obj = models.Articles.objects.get(id=article_id)
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    '''SURE_TYP_LIST = [
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')]'''
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    SURE_LIST = [1, 2]  # 保证类
    HOUSE_LIST = [11, 21, 42, 52]  # 房产类
    GROUND_LIST = [12, 22, 43, 53]  # 土地类
    COUNSTRUCT_LIST = [14, 23]  # 在建工程类
    RECEIVABLE_LIST = [31, ]  # 应收账款类
    STOCK_LIST = [32, 51]  # 股权类
    DRAFT_LIST = [33, 44]  # 票据类
    VEHICLE_LIST = [15, ]  # 车辆类
    CHATTEL_LIST = [13, 24, 34, 47]  # 动产类
    OTHER_LIST = [39, 49, 59]  # 其他类

    custom_lending_list = models.Customes.objects.filter(lending_custom__sure__lending=lending_obj)
    warrant_lending_h_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ__in=[1, 2])
    warrant_lending_g_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=5)
    warrant_lending_6_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=6)
    warrant_lending_r_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=11)
    warrant_lending_s_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=21)
    warrant_lending_d_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=31)
    warrant_lending_v_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=41)
    warrant_lending_c_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=51)
    warrant_lending_o_list = models.Warrants.objects.filter(lending_warrant__sure__lending=lending_obj,
                                                            warrant_typ=55)
    form_lendingcustoms_c_add = models.Customes.objects.exclude(
        id=article_obj.custom.id).filter(genre=1).values_list('id', 'name')
    form_lendingcustoms_p_add = models.Customes.objects.exclude(
        id=article_obj.custom.id).filter(genre=2).values_list('id', 'name')
    form_lendingsures = forms.LendingSuresForm()
    # form_lendingcustoms_c_add = forms.LendingCustomsCForm()
    # form_lendingcustoms_p_add = forms.LendingCustomsPForm()
    form_lendinghouse_add = forms.LendingHouseForm()  # 房产
    form_lendingground_add = forms.LendingGroundForm()  # 土地
    form_lendingconstruct_add = forms.LendingConstructForm()  # 在建工程
    form_lendinggreceivable_add = forms.LendinReceivableForm()  # 应收账款
    form_lendingstock_add = forms.LendinStockForm()  # 股权
    form_lendingdraft_add = forms.LendinDraftForm()  # 票据
    form_lendingvehicle_add = forms.LendinVehicleForm()  # 车辆
    form_lendingchattel_add = forms.LendinChattelForm()  # 动产
    form_lendingother_add = forms.LendinOtherForm()  # 其他

    form_lending = forms.FormLendingOrder(
        initial={'order': lending_obj.order,
                 'remark': lending_obj.remark,
                 'order_amount': lending_obj.order_amount})

    return render(request, 'dbms/appraisal/appraisal-scan-lending.html', locals())


# -----------------------房产列表-------------------------#
def house_d(house_list):
    summ = '<tr class="it"><td colspan="4"><table class="tbi" cellspacing="0" cellpadding="0" >'
    summ += '<tr class="it">' \
            '<td class="bb" align="center">所有权人</td> ' \
            '<td class="bb" align="center">处所</td> ' \
            '<td class="bb" align="center">面积(㎡)</td> ' \
            '<td class="bb" align="center">产权证编号</td> ' \
            '</tr>'
    for warrant_house in house_list:
        owership_list = warrant_house.ownership_warrant.all()
        owership_list_count = owership_list.count()
        owership_name = ''
        owership_num = ''
        owership_list_order = 0
        for owership in owership_list:
            owership_name += '%s' % owership.owner.name
            owership_num += '%s' % owership.ownership_num
            owership_list_order += 1
            if owership_list_order < owership_list_count:
                owership_name += '、'
                owership_num += '、'
        if warrant_house.warrant_typ == 1:
            # rowspan_count += 1
            house = warrant_house.house_warrant
            house_locate = house.house_locate
            house_app = house.house_app
            house_area = house.house_area
            summ += '<tr class="it">' \
                    '<td class="bb">%s</td> ' \
                    '<td class="bb">%s</td> ' \
                    '<td class="bb" align="right">%s</td> ' \
                    '<td class="bb">%s</td> ' \
                    '</tr>' % (owership_name, house_locate, house_area, owership_num)
        else:
            housebag_list = warrant_house.housebag_warrant.all()
            housebag_count = housebag_list.count()
            housebag_num = 1
            for housebag in housebag_list:
                # rowspan_count += 1
                housebag_locate = housebag.housebag_locate
                housebag_app = housebag.housebag_app
                housebag_area = housebag.housebag_area
                if housebag_num == 1:
                    summ += '<tr class="it">' \
                            '<td class="bb" rowspan="%s">%s</td> ' \
                            '<td class="bb">%s</td> ' \
                            '<td class="bb" align="right">%s</td> ' \
                            '<td class="bb" rowspan="%s">%s</td> ' \
                            '</tr>' % (
                                housebag_count, owership_name, housebag_locate,
                                housebag_area, housebag_count, owership_num)
                    housebag_num += 1
                else:
                    summ += '<tr class="it">' \
                            '<td class="bb">%s</td> ' \
                            '<td class="bb" align="right">%s</td> ' \
                            '</tr>' % (
                                housebag_locate, housebag_area)
    summ += '</table></td></tr>'
    return summ


# -----------------------监管房产列表-------------------------#
def house_j(house_list):
    summ = '<tr class="it"><td colspan="4"><table class="tbi" cellspacing="0" cellpadding="0" >'
    summ += '<tr class="it">' \
            '<td class="bb" align="center">所有权人</td> ' \
            '<td class="bb" align="center">处所</td> ' \
            '<td class="bb" align="center">面积(㎡)</td> ' \
            '</tr>'
    for warrant_house in house_list:
        owership_list = warrant_house.ownership_warrant.all()
        owership_list_count = owership_list.count()
        owership_name = ''
        owership_num = ''
        owership_list_order = 0
        for owership in owership_list:
            owership_name += '%s' % owership.owner.name
            owership_num += '%s' % owership.ownership_num
            owership_list_order += 1
            if owership_list_order < owership_list_count:
                owership_name += '、'
                owership_num += '、'
        if warrant_house.warrant_typ == 1:
            # rowspan_count += 1
            house = warrant_house.house_warrant
            house_locate = house.house_locate
            house_app = house.house_app
            house_area = house.house_area
            summ += '<tr class="it">' \
                    '<td class="bb">%s</td> ' \
                    '<td class="bb">%s</td> ' \
                    '<td class="bb" align="right">%s(具体面积以产权证为准)</td> ' \
                    '</tr>' % (owership_name, house_locate, house_area)
        else:
            housebag_list = warrant_house.housebag_warrant.all()
            housebag_count = housebag_list.count()
            housebag_num = 1
            for housebag in housebag_list:
                # rowspan_count += 1
                housebag_locate = housebag.housebag_locate
                housebag_app = housebag.housebag_app
                housebag_area = housebag.housebag_area
                if housebag_num == 1:
                    summ += '<tr class="it">' \
                            '<td class="bb" rowspan="%s">%s</td> ' \
                            '<td class="bb">%s</td> ' \
                            '<td class="bb" align="right">%s(具体面积以产权证为准)</td> ' \
                            '</tr>' % (
                                housebag_count, owership_name, housebag_locate,
                                housebag_area)
                    housebag_num += 1
                else:
                    summ += '<tr class="it">' \
                            '<td class="bb">%s</td> ' \
                            '<td class="bb" align="right">%s(具体面积以产权证为准)</td> ' \
                            '</tr>' % (
                                housebag_locate, housebag_area)
    summ += '</table></td></tr>'
    return summ


# -----------------------土地列表-------------------------#
def ground_d(ground_list):
    summ = '<tr class="it"><td colspan="4"><table class="tbi" cellspacing="0" cellpadding="0" >'
    summ += '<tr class="it">' \
            '<td class="bb" align="center">所有权人</td> ' \
            '<td class="bb" align="center">座落</td> ' \
            '<td class="bb" align="center">面积(㎡)</td> ' \
            '<td class="bb" align="center">产权证编号</td> ' \
            '</tr>'
    for warrant_ground in ground_list:
        # rowspan_count += 1
        owership_list = warrant_ground.ownership_warrant.all()
        owership_list_count = owership_list.count()
        owership_name = ''
        owership_num = ''
        owership_list_order = 0
        for owership in owership_list:
            owership_name += '%s' % owership.owner.name
            owership_num += '%s' % owership.ownership_num
            owership_list_order += 1
            if owership_list_order < owership_list_count:
                owership_name += '、'
                owership_num += '、'
        ground = warrant_ground.ground_warrant
        ground_locate = ground.ground_locate
        ground_app = ground.ground_app
        ground_area = ground.ground_area
        summ += '<tr class="it">' \
                '<td class="bb">%s</td> ' \
                '<td class="bb">%s</td> ' \
                '<td class="bb" align="right">%s</td> ' \
                '<td class="bb">%s</td> ' \
                '</tr>' % (
                    owership_name, ground_locate, ground_area, owership_num)
    summ += '</table></td></tr>'
    return summ


# -----------------------在建工程列表-------------------------#
def create_d(create_list):
    summ = '<tr class="it"><td colspan="4"><table class="tbi" cellspacing="0" cellpadding="0" >'
    summ += '<tr class="it">' \
            '<td class="bb" align="center">所有权人</td> ' \
            '<td class="bb" align="center">座落</td> ' \
            '<td class="bb" align="center">面积(㎡)</td> ' \
            '<td class="bb" align="center">备注</td> ' \
            '</tr>'
    for warrant_c in create_list:
        # rowspan_count += 1
        owership_list = warrant_c.ownership_warrant.all()
        owership_list_count = owership_list.count()
        owership_name = ''
        owership_list_order = 0
        for owership in owership_list:
            owership_name += '%s' % owership.owner.name
            owership_list_order += 1
            if owership_list_order < owership_list_count:
                owership_name += '、'
        coustruct = warrant_c.coustruct_warrant
        coustruct_locate = coustruct.coustruct_locate
        coustruct_area = coustruct.coustruct_area
        summ += '<tr class="it">' \
                '<td class="bb">%s</td> ' \
                '<td class="bb">%s</td> ' \
                '<td class="bb" align="right">%s</td> ' \
                '<td class="bb">最终以实际抵押面积为准</td> ' \
                '</tr>' % (owership_name, coustruct_locate, coustruct_area)
    summ += '</table></td></tr>'
    return summ


def sum_g(lending):
    custom_c_count = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=1).count()  # 企业
    custom_p_count = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=2).count()  # 个人
    warrant_h_11_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=11).count()  # 抵押房产
    warrant_g_12_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=12).count()  # 土地抵押
    warrant_c_14_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=14).count()  # 在建工程抵押
    warrant_c_13_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=13).count()  # 动产抵押
    warrant_v_15_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=15).count()  # 车辆抵押
    warrant_h_21_countt = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=21).count()  # 房产顺位
    warrant_g_22_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=22).count()  # 土地顺位
    warrant_c_23_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=23).count()  # 在建工程顺位
    warrant_c_24_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=24).count()  # 动产顺位
    warrant_r_31_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=31).count()  # 应收质押
    warrant_s_32_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=32).count()  # 股权质押
    warrant_d_33_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=33).count()  # 票据质押
    warrant_c_34_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=34).count()  # 动产质押
    warrant_o_39_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=39).count()  # 其他权利质押
    warrant_h_42_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=42).count()  # 房产监管
    warrant_g_43_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=43).count()  # 土地监管
    warrant_d_44_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=44).count()  # 票据监管
    warrant_c_47_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=47).count()  # 动产监管
    warrant_o_49_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=49).count()  # 其他监管
    warrant_s_51_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=51).count()  # 股权预售
    warrant_h_52_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=52).count()  # 房产预售
    warrant_g_53_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=53).count()  # 土地预售
    warrant_o_59_count = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=59).count()  # 其他预售
    sum_gg = (custom_c_count + custom_p_count + warrant_h_11_count + warrant_g_12_count +
              warrant_c_14_count + warrant_c_13_count + warrant_v_15_count + warrant_h_21_countt +
              warrant_g_22_count + warrant_c_23_count + warrant_c_24_count + warrant_r_31_count +
              warrant_s_32_count + warrant_d_33_count + warrant_c_34_count +
              warrant_o_39_count + warrant_h_42_count + warrant_g_43_count +
              warrant_d_44_count + warrant_c_47_count + warrant_o_49_count +
              warrant_s_51_count + warrant_h_52_count + warrant_g_53_count + warrant_o_59_count)
    return sum_gg


# -----------------------summary_scan意见书-------------------------#
@login_required
@authority
@article_right
def summary_scan(request, article_id):  # 评审项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '意见书'

    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list.first()
    review_date = article_obj.review_date  # 上会日期
    review_year = article_obj.appraisal_article.all()[0].review_year  # 上会年份
    review_order = article_obj.appraisal_article.all()[0].review_order
    review_order_cn = convert_str(review_order)
    single_list = article_obj.single_quota_summary.all()
    single_count = single_list.count()
    product_name = article_obj.product.name
    PROCESS_LIST_XD = ['房抵贷', '担保贷', '过桥贷', ]
    UN = '？？？？？？？？？？？'
    if product_name in PROCESS_LIST_XD:  # 小贷
        UN = UNX
        UN_I = '贷款审查委员会项目审查意见书'
        UN_F = '成武兴贷审会'
        TH_I = '贷审会'
        DF = ''
        TEXT_O = '授信'
        SIGN_G = '贷审会协调人审核意见'
    else:
        UN = UND
        UN_I = '担保审查委员会项目审查意见书'
        UN_F = '成武担审保会'
        TH_I = '审保会'
        DF = '反'
        TEXT_O = '担保'
        SIGN_G = '审保会召集人审核意见'

    credit_term = article_obj.credit_term  # 授信期限（月）
    credit_term_cn = credit_term_c(credit_term)  # 授信期限转换

    renewal_str = amount_s(round(article_obj.renewal, 6))  # 新增金额
    augment_str = amount_s(round(article_obj.augment, 6))  # 续贷金额
    amount_str = amount_s(round(article_obj.amount, 6))  # 金额合计

    CREDIT_MODEL_LIST = models.SingleQuota.CREDIT_MODEL_LIST
    CREDIT_MODEL_DIC = {}
    for MODEL in CREDIT_MODEL_LIST:
        CREDIT_MODEL_DIC[MODEL[0]] = MODEL[1]
    single_val_list = article_obj.single_quota_summary.values_list('credit_model', 'credit_amount', 'flow_rate')
    single_dic_list = list(
        map(lambda x: {'credit_model': x[0],
                       'credit_amount': str(round(x[1] / 10000, 6)).rstrip('0').rstrip('.'),
                       'flow_rate': x[2]}, single_val_list))
    for single_dic in single_dic_list:
        single_dic['credit_model_cn'] = CREDIT_MODEL_DIC[single_dic['credit_model']]
    order_amount_list = article_obj.lending_summary.values_list('order', 'order_amount')  # 发放次序
    order_amount_dic_list = list(
        map(lambda x: {'order': x[0], 'order_amount': str(x[1] / 10000).rstrip('0').rstrip('.')}, order_amount_list))
    REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
    REVIEW_MODEL_DEC = {}
    for MODEL in REVIEW_MODEL_LIST:
        REVIEW_MODEL_DEC[MODEL[0]] = MODEL[1]
    review_model = article_obj.appraisal_article.all().first().review_model  # ((1, '内审'), (2, '外审'))
    expert_amount = article_obj.expert.count()  # 评委个数
    '''COMMENT_TYPE_LIST = ((1, '同意'), (2, '复议'), (3, '不同意'))'''
    comment_type_1 = article_obj.comment_summary.filter(comment_type=1).count()  # 同意票数
    comment_type_2 = article_obj.comment_summary.filter(comment_type=2).count()  # 复议票数
    comment_type_3 = article_obj.comment_summary.filter(comment_type=3).count()  # 不同意票数
    lending_list = article_obj.lending_summary.all()  # 放款次序列表
    lending_count = lending_list.count()  # 放款笔数
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    new = round(article_obj.augment, 2)

    # if True:
    if article_obj.article_state in [1, 2, 3, 4, 61]:
        rowspan_count = 2
        ss = 0
        for lending in lending_list:
            ss += sum_g(lending)
        if ss:
            tt = '一、'
        else:
            tt = ''
        summary = ''
        summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s同意为该客户' % tt
        single_dic_count = len(single_dic_list)
        single_dic_c = 0

        for single in single_dic_list:
            single_dic_c += 1
            summary += '%s万元%s' % (single['credit_amount'], single['credit_model_cn'])
            if single_dic_c < single_dic_count:
                summary += '、'
        if lending_count == 1:  # 放款笔数
            if lending_list.first().remark:
                lk = lending_list.first().remark
            else:
                lk = ''
            # summary += '提供%s%s。期限%s,' % (TEXT_O, lk, credit_term_cn)
            summary += '提供%s%s' % (TEXT_O, lk)
        else:
            # summary += '提供%s。期限%s,' % (TEXT_O, credit_term_cn)
            summary += '提供%s。' % (TEXT_O)

        # single_dic_c = 0
        # for single in single_dic_list:
        #     if single_dic_count > 1:
        #         single_dic_c += 1
        #         summary += '%s%s' % (single['credit'], single['flow_rate'])
        #         if single_dic_c < single_dic_count:
        #             summary += '、'
        #     else:
        #         summary += '%s' % (single['flow_rate'])

        if lending_count > 1:
            # rowspan_count += lending_count
            summary += '贷款分%s次发放，' % convert_str(lending_count)
            lending_c = 0
            for lending in lending_list:
                lending_c += 1
                summary += '第%s次发放%s万元' % (convert_str(lending_c),
                                           str(lending.order_amount / 10000).rstrip('0').rstrip('.'))
                if lending_c < lending_count:
                    summary += '、'
        summary += '。</td></tr>'

        if ss:
            rowspan_count += 1
            summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp二、落实以下%s担保措施</td></tr>' % DF
        lend_or = 0
        for lending in lending_list:
            order_amount = lending.order_amount
            if lending.remark:
                lk = lending.remark
            else:
                lk = ''
            sure_list = lending.sure_lending.all()
            sure_count = sure_list.count()
            sure_or = 1
            if lending_count > 1:
                rowspan_count += 1
                lend_or += 1
                lend_oz = convert_str(lend_or)
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp（%s）第%s次发放%s万元%s，' \
                           '并落实以下%s担保措施</td></tr>' % (
                               lend_oz, lend_oz, str(order_amount / 10000).rstrip('0').rstrip('.'), lk, DF)
            custom_c_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=1)  # 企业
            if custom_c_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=1).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、企业保证%s：' % (
                    sure_or, sure_remark)
                custom_c_count = custom_c_list.count()
                custom_c_c = 1
                for custom_c in custom_c_list:
                    summary += '%s' % custom_c.name
                    if custom_c_c < custom_c_count:
                        summary += '、'
                    custom_c_c += 1
                summary += '提供企业连带责任保证%s担保。</td></tr>' % DF
                sure_or += 1
            custom_p_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=2)  # 个人
            if custom_p_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=2).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、个人保证%s：' % (
                    sure_or, sure_remark)
                custom_p_count = custom_p_list.count()
                custom_p_c = 1
                for custom_p in custom_p_list:
                    summary += '%s' % custom_p.name
                    if custom_p.person_custome.spouses:
                        summary += '、%s夫妇' % custom_p.person_custome.spouses.name
                    if custom_p_c < custom_p_count:
                        summary += '，'
                    custom_p_c += 1
                summary += '提供个人连带责任保证%s担保。</td></tr>' % DF
                sure_or += 1
            '''SURE_TYP_LIST = [
            (1, '企业保证'), (2, '个人保证'),
            (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
            (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
            (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
            (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
            (51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')]'''
            ''' WARRANT_TYP_LIST = [
            (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
            (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
            warrant_h_11_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=11)  # 抵押房产
            if warrant_h_11_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=11).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、房产抵押：' \
                           '以下房产抵押给我公司，签订抵押%s担保合同并办理抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += house_d(warrant_h_11_list)  # 房产列表
                sure_or += 1
            warrant_g_12_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=12)  # 土地抵押
            if warrant_g_12_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=12).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">' \
                           '&nbsp&nbsp%s、土地抵押：以下国有土地使用权抵押给我公司，签订抵押%s担保合同并办' \
                           '理抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += ground_d(warrant_g_12_list)
                sure_or += 1
            warrant_c_14_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=14)  # 在建工程抵押
            if warrant_c_14_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=14).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">' \
                           '&nbsp&nbsp%s、在建工程抵押：以下在建工程抵押给我公司，签订抵押%s担保合同并' \
                           '办理抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += create_d(warrant_c_14_list)
                sure_or += 1
            warrant_c_13_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=13)  # 动产抵押
            if warrant_c_13_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=13).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、动产抵押%s：' % (
                    sure_or, sure_remark)
                warrant_c_count = warrant_c_13_list.count()
                warrant_c_c = 0
                for warrant_c in warrant_c_13_list:
                    warrant_c_c += 1
                    summary += '%s提供%s' % (warrant_c.chattel_warrant.chattel_owner.name,
                                           warrant_c.chattel_warrant.chattel_detail)
                    if warrant_c_c < warrant_c_count:
                        summary += '、'
                summary += '抵押给我公司，签订抵押%s担保合同并办理抵押登记。</td></tr>' % DF
                sure_or += 1
            warrant_v_15_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=15)  # 车辆抵押
            if warrant_v_15_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=15).sure_remark
                if not sure_remark:
                    sure_remark = ''
                warrant_count = warrant_v_15_list.count()
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">' \
                           '&nbsp&nbsp%s、车辆抵押抵押：以下车辆抵押给我公司，签订抵押%s担保合同并办' \
                           '理抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += '<tr class="it"><td colspan="4"><table class="tbi" cellspacing="0" cellpadding="0" >'
                summary += '<tr class="it">' \
                           '<td class="bb" align="center">所有权人</td> ' \
                           '<td class="bb" align="center">车架号</td> ' \
                           '<td class="bb" align="center">车牌号</td> ' \
                           '<td class="bb" align="center">备注</td> ' \
                           '</tr>'
                for warrant_v in warrant_v_15_list:
                    # rowspan_count += 1
                    vehicle = warrant_v.vehicle_warrant
                    vehicle_owner = vehicle.vehicle_owner.name
                    frame_num = vehicle.frame_num
                    plate_num = vehicle.plate_num
                    vehicle_remark = vehicle.vehicle_remark
                    summary += '<tr class="it">' \
                               '<td class="bb">%s</td> ' \
                               '<td class="bb">%s</td> ' \
                               '<td class="bb" align="right">%s</td> ' \
                               '<td class="bb">%s</td> ' \
                               '</tr>' % (vehicle_owner, frame_num, plate_num, vehicle_remark)
                summary += '</table></td></tr>'
                sure_or += 1
            warrant_h_21_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=21)  # 房产顺位
            if warrant_h_21_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=21).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、房产顺位抵押：' \
                           '以下房产抵押给我公司，签订抵押%s担保合同并办理顺位' \
                           '抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += house_d(warrant_h_21_list)  # 房产列表
                sure_or += 1
            warrant_g_22_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=22)  # 土地顺位
            if warrant_g_22_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=22).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">' \
                           '&nbsp&nbsp%s、土地顺位抵押：以下国有土地使用权抵押给我公司，签' \
                           '订抵押%s担保合同并办理顺位抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += ground_d(warrant_g_22_list)
                sure_or += 1
            warrant_c_23_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=23)  # 在建工程顺位
            if warrant_c_23_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=23).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">' \
                           '&nbsp&nbsp%s、在建工程顺位抵押：以下在建工程抵押给我公司，签' \
                           '订抵押%s担保合同并办理顺位抵押登记%s</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += create_d(warrant_c_23_list)
                sure_or += 1
            warrant_c_24_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=24)  # 动产顺位
            if warrant_c_24_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=24).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、动产顺位抵押%s：' % (
                    sure_or, sure_remark)
                warrant_c_count = warrant_c_24_list.count()
                warrant_c_c = 0
                for warrant_c in warrant_c_24_list:
                    warrant_c_c += 1
                    summary += '%s提供%s' % (warrant_c.chattel_warrant.chattel_owner.name,
                                           warrant_c.chattel_warrant.chattel_detail)
                    if warrant_c_c < warrant_c_count:
                        summary += '、'
                summary += '抵押给我公司，签订抵押%s担保合同并办理顺位抵押登记。</td></tr>' % DF
                sure_or += 1
            warrant_r_31_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=31)  # 应收质押
            if warrant_r_31_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=31).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、应收账款质押%s：' % (
                    sure_or, sure_remark)
                warrant_r_count = warrant_r_31_list.count()
                warrant_r_c = 0
                for warrant_r in warrant_r_31_list:
                    warrant_r_c += 1
                    summary += '%s将%s' % (warrant_r.receive_warrant.receive_owner.name,
                                          warrant_r.receive_warrant.receivable_detail)
                    if warrant_r_c < warrant_r_count:
                        summary += '、'
                summary += '质押给我公司，签订质押%s担保合同并办理质押登记。</td></tr>' % DF
                sure_or += 1
            warrant_s_32_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=32)  # 股权质押
            if warrant_s_32_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=32).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、股权质押%s：' % (
                    sure_or, sure_remark)
                warrant_s_count = warrant_s_32_list.count()
                warrant_s_c = 0
                for warrant_s in warrant_s_32_list:
                    warrant_s_c += 1
                    '''STOCK_TYP_LIST = ((1, '有限公司股权'), (11, '股份公司股份'), (21, '举办者权益'))'''
                    if warrant_s.stock_warrant.stock_typ == 1:
                        summary += '%s持有的%s%s' % (warrant_s.stock_warrant.stock_owner.name,
                                                  warrant_s.stock_warrant.target,
                                                  warrant_s.stock_warrant.share)
                        summary = summary + '万元股权（占注册资本'
                        summary = summary + '%s' % warrant_s.stock_warrant.ratio
                        summary = summary + '%）'
                    elif warrant_s.stock_warrant.stock_typ == 11:
                        summary += '%s持有的%s%s' % (warrant_s.stock_warrant.stock_owner.name,
                                                  warrant_s.stock_warrant.target,
                                                  warrant_s.stock_warrant.share)
                        summary = summary + '万股股权（占注册资本'
                        summary = summary + '%s' % warrant_s.stock_warrant.ratio
                        summary = summary + '%）'
                        if warrant_s.stock_warrant.remark:
                            summary = summary + '（%s）' % warrant_s.stock_warrant.remark
                    if warrant_s_c < warrant_s_count:
                        summary += '、'
                summary += '质押给我公司，签订质押%s担保合同并办理质押登记。</td></tr>' % DF
                sure_or += 1
            warrant_d_33_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=33)  # 票据质押
            if warrant_d_33_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=33).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、票据质押%s：' % (
                    sure_or, sure_remark)
                warrant_d_count = warrant_d_33_list.count()
                warrant_d_c = 0
                for warrant_d in warrant_d_33_list:
                    warrant_d_c += 1
                    summary += '%s提供%s' % (warrant_d.draft_warrant.draft_owner.name,
                                           warrant_d.draft_warrant.draft_detail)
                    if warrant_d_c < warrant_d_count:
                        summary += '、'
                summary += '质押给我公司，签订质押%s担保合同并办理质押登记。</td></tr>' % DF
                sure_or += 1
            warrant_c_34_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=34)  # 动产质押
            if warrant_c_34_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=34).sure_remark
                if not sure_remark:
                    sure_remark = ''
            warrant_o_39_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=39)  # 其他权利质押
            if warrant_o_39_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=39).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、其他权利质押%s：' % (
                    sure_or, sure_remark)
                warrant_o_39_count = warrant_o_39_list.count()
                warrant_o_39_c = 0
                for warrant_o_39 in warrant_o_39_list:
                    warrant_o_39_c += 1
                    summary += '%s提供%s' % (warrant_o_39.other_warrant.other_owner.name,
                                           warrant_o_39.other_warrant.other_detail)
                    if warrant_o_39_c < warrant_o_39_count:
                        summary += '、'
                summary += '</td></tr>'
                sure_or += 1
            warrant_h_42_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=42)  # 房产监管
            if warrant_h_42_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=42).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、房产监管%s：' \
                           '以下房产签订抵押%s担保合同，收取购房合同等资料并承诺配合我公司' \
                           '办理相抵押登记关手续</td></tr>' % (
                               sure_or, DF, sure_remark)
                summary += house_j(warrant_h_42_list)  # 房产列表
                sure_or += 1
            warrant_g_43_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=43)  # 土地监管
            if warrant_g_43_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=43).sure_remark
                if not sure_remark:
                    sure_remark = ''
                warrant_count = warrant_g_43_list.count()
                rowspan_count += warrant_count
            warrant_d_44_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=44)  # 票据监管
            if warrant_d_44_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=44).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、票据监管%s：' % (
                    sure_or, sure_remark)
                warrant_d_count = warrant_d_44_list.count()
                warrant_d_c = 0
                for warrant_d in warrant_d_44_list:
                    warrant_d_c += 1
                    summary += '%s提供%s' % (warrant_d.draft_warrant.draft_owner.name,
                                           warrant_d.draft_warrant.draft_detail)
                    if warrant_d_c < warrant_d_count:
                        summary += '、'
                summary += '存放于我公司进行监管。</td></tr>'
                sure_or += 1
            warrant_c_47_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=47)  # 动产监管
            if warrant_c_47_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=47).sure_remark
                if not sure_remark:
                    sure_remark = ''
            warrant_o_49_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=49)  # 其他监管
            if warrant_o_49_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=49).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、其他监管%s：' % (
                    sure_or, sure_remark)
                warrant_o_49_count = warrant_o_49_list.count()
                warrant_o_49_c = 0
                for warrant_o_49 in warrant_o_49_list:
                    warrant_o_49_c += 1
                    summary += '%s提供%s' % (warrant_o_49.other_warrant.other_owner.name,
                                           warrant_o_49.other_warrant.other_detail)
                    if warrant_o_49_c < warrant_o_49_count:
                        summary += '、'
                summary += '</td></tr>'
                sure_or += 1
            warrant_s_51_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=51)  # 股权预售
            if warrant_s_51_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=51).sure_remark
                if not sure_remark:
                    sure_remark = ''
            warrant_h_52_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=52)  # 房产预售
            if warrant_h_52_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=52).sure_remark
                if not sure_remark:
                    sure_remark = ''
                warrant_count = warrant_h_52_list.count()
                rowspan_count += warrant_count
            warrant_g_53_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=53)  # 土地预售
            if warrant_g_53_list:
                rowspan_count += 2
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=53).sure_remark
                if not sure_remark:
                    sure_remark = ''
                warrant_count = warrant_g_53_list.count()
                rowspan_count += warrant_count
            warrant_o_59_list = models.Warrants.objects.filter(
                lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=59)  # 其他预售
            if warrant_o_59_list:
                rowspan_count += 1
                sure_remark = models.LendingSures.objects.get(lending=lending, sure_typ=59).sure_remark
                if not sure_remark:
                    sure_remark = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s、其他%s：' % (
                    sure_or, sure_remark)
                warrant_o_59_count = warrant_o_59_list.count()
                warrant_o_59_c = 0
                for warrant_o_59 in warrant_o_59_list:
                    warrant_o_59_c += 1
                    summary += '%s' % (warrant_o_59.other_warrant.other_detail)
                    if warrant_o_59_c < warrant_o_59_count:
                        summary += '、'
                summary += '</td></tr>'
                sure_or += 1
        supply_list = article_obj.supply_summary.all()
        if supply_list:
            rowspan_count += 1
            summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp三、落实以下问题</td></tr>'
            supply_count = supply_list.count()
            supply_c = 0
            for supply in supply_list:
                rowspan_count += 1
                supply_c += 1
                if supply_count > 1:
                    supply_c_c = str(supply_c) + '、'
                else:
                    supply_c_c = ''
                summary += '<tr class="ot tbp"><td class="oi" colspan="4">&nbsp&nbsp%s%s' % (
                    supply_c_c, supply.supply_detail)
                if supply_c < supply_count:
                    summary += '；</td></tr>'
                else:
                    summary += '。</td></tr>'
        head = ''
        # ----------------项目成员
        head += '<tr class="ot"><td class="bb">项目成员</td>'
        head += '<td class="bb tbp" colspan="4">A角：%s&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp' \
                'B角：%s&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp风控专员：%s</td>' % (
                    article_obj.director.name, article_obj.assistant.name, article_obj.control.name)
        # ----------------评审结论
        head += '<tr class="otr"><td class="bb" rowspan="%s">评审结论</td>'
        head += '<td class="bb tbp" colspan="4">同意为该客户'
        single_c = 0
        if product_name in PROCESS_LIST_XD:  # 小贷
            for single_dic in single_dic_list:
                single_c += 1
                head += '提供%s万元%s' % (single_dic['credit_amount'], single_dic['credit_model_cn'])
                if single_c < single_count:
                    head += '、'
            head += '</td></tr>'
        else:  # 担保
            for single_dic in single_dic_list:
                single_c += 1
                head += '%s万元%s' % (single_dic['credit_amount'], single_dic['credit_model_cn'])
                if single_c < single_count:
                    head += '、'
            head += '提供担保</td></tr>'

        # ----------------业务品种
        head += '<tr class="otr"><td class="bb" rowspan="%s">业务品种</td>'
        head += '<td class="bb tbp" colspan="4">'
        single_c = 0
        for single_dic in single_dic_list:
            single_c += 1
            head += '%s' % single_dic['credit_model_cn']
            if single_c < single_count:
                head += '、'
        head += '</td></tr>'
        # ----------------金额
        head += '<tr class="otr"><td class="bb" rowspan="%s">金额</td>'
        head += '<td class="bb tbp" colspan="4">%s万元' % amount_str
        if article_obj.renewal > 0 and article_obj.augment > 0:
            head += '（其中：存量%s万元、新增%s万元）</td></tr>' % (renewal_str, augment_str)
        elif article_obj.renewal > 0:
            head += '（存量）</td></tr>'
        else:
            head += '（新增）</td></tr>'
            # ----------------期限
        head += '<tr class="otr"><td class="bb" rowspan="%s">期限</td>'
        head += '<td class="bb tbp" colspan="4">%s期</td></tr>' % credit_term_cn
        # ----------------费率及收费方式
        head += '<tr class="otr"><td class="bb" rowspan="%s">费率及收费方式</td>'
        head += '<td class="bb tbp" colspan="4">'
        if single_count > 1:
            single_c = 0
            for single_dic in single_dic_list:
                single_c += 1
                head += '%s%s' % (single_dic['credit_model_cn'], single_dic['flow_rate'])
                if single_c < single_count:
                    head += '、'
        else:
            for single_dic in single_dic_list:
                head += '%s' % (single_dic['flow_rate'])
        head += '</td></tr>'
        # -----------------评审意见
        head += '<tr class="ot"><td class="bb" rowspan="%s">评审意见</td>' % rowspan_count
        if product_name in PROCESS_LIST_XD:  # 小贷
            head += '<td class="tbp" colspan="4">&nbsp&nbsp根据公司成武贷发[2019]3号《成都武兴小额贷款有限责任公司' \
                    '贷款审查委员会组织与运行制度》规定，该项目符合公司评审程序，参会人员%s人，' \
                    '其中' % (expert_amount)
        else:
            head += '<td class="tbp" colspan="4">&nbsp&nbsp根据公司成武担[2019]27号文件《成都武侯中小企业融资担' \
                    '保有限责任公司担保审查委员会组织与管理办法》规定，该项目符合公司%s评审程序，参会人员%s人，' \
                    '其中' % (REVIEW_MODEL_DEC[review_model], expert_amount)

        if comment_type_1:
            head += '%s人同意，' % comment_type_1
        if comment_type_2:
            head += '%s人复议，' % comment_type_2
        if comment_type_3:
            head += '%s人不同意，' % comment_type_3
        head += '会议形成如下结论：</td></tr>'
        summary = head + summary
        article_list.update(summary=summary)

    return render(request, 'dbms/appraisal/appraisal-summary-scan.html', locals())


# -----------------------sign_scan签批单-------------------------#
@login_required
@authority
@article_right
def summary_sign_scan(request, article_id):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '签批单'

    article_obj = models.Articles.objects.get(id=article_id)
    amount_str = amount_s(article_obj.amount)
    new = round(article_obj.augment, 2)

    return render(request, 'dbms/appraisal/appraisal-sign-scan.html', locals())
