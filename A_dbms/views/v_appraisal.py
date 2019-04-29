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
from _WHDB.views import MenuHelper
from _WHDB.views import authority
from .v_agree import convert_num


# -----------------------appraisal评审情况-------------------------#
@login_required
@authority
def appraisal(request, *args, **kwargs):  # 评审情况
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '评审管理'  # 页面标题
    '''模态框'''
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'),(61, '待变更'), (99, '已注销'))'''
    ARTICLE_STATE_LIST = models.Articles.ARTICLE_STATE_LIST  # 筛选条件
    '''筛选'''
    appraisal_list = models.Articles.objects.filter(**kwargs).select_related(
        'custom', 'director', 'assistant', 'control').order_by('-review_date')
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
def appraisal_scan(request, article_id):  # 评审项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
        form_article_sign = forms.ArticlesSignForm(initial=form_date)
    form_comment = forms.CommentsAddForm()
    form_single = forms.SingleQuotaForm()
    form_lending = forms.FormLendingOrder()
    form_article_change = forms.ArticleChangeForm(initial={'change_date': str(datetime.date.today())})
    return render(request, 'dbms/appraisal/appraisal-scan.html', locals())


# -----------------------appraisal_scan_lending评审项目预览-------------------------#
@login_required
@authority
def appraisal_scan_lending(request, article_id, lending_id):  # 评审项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款次序'
    article_obj = models.Articles.objects.get(id=article_id)
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
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
    OTHER_LIST = [39, 49]  # 其他类
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
        initial={'order': lending_obj.order, 'order_amount': lending_obj.order_amount})

    return render(request, 'dbms/appraisal/appraisal-scan-lending.html', locals())


def convert_str(n):
    units = ['', '万', '亿']
    nums = ['0', '一', '二', '三', '四', '五', '六', '七', '八', '九']
    small_int_label = ['', '十', '百', '千']
    int_part, decimal_part = str(int(n)), str(round(n - int(n), 2))[2:]  # 分离整数和小数部分
    res = []
    if int_part != '0':
        while int_part:
            small_int_part, int_part = int_part[-4:], int_part[:-4]
            tmp = ''.join(
                [nums[int(x)] + (y if x != '0' else '') for x, y in
                 list(zip(small_int_part[::-1], small_int_label))[::-1]])
            tmp = tmp.rstrip('0').replace('000', '0').replace('00', '0')
            unit = units.pop(0)
            if tmp:
                tmp += unit
                res.append(tmp)
    result = ''.join(res[::-1])

    return result


# -----------------------summary_scan纪要预览-------------------------#
@login_required
@authority
def summary_scan(request, article_id):  # 评审项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '纪要预览'

    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list.first()

    review_year = article_obj.appraisal_article.all()[0].review_year
    review_order = article_obj.appraisal_article.all()[0].review_order
    review_order_cn = convert_str(review_order)
    credit_term = article_obj.credit_term
    single_list = article_obj.single_quota_summary.all()
    single_count = single_list.count()
    credit_term = article_obj.credit_term  # 授信期限（月）
    renewal_str = str(article_obj.renewal / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    augment_str = str(article_obj.augment / 10000).rstrip('0').rstrip('.')  # 新增（万元）
    amount_str = str(article_obj.amount / 10000).rstrip('0').rstrip('.')  # 总额（万元）

    CREDIT_MODEL_LIST = models.SingleQuota.CREDIT_MODEL_LIST
    CREDIT_MODEL_DIC = list(
        map(lambda x: {'credit_model': x[0], 'credit': x[1]}, CREDIT_MODEL_LIST))
    single_list = article_obj.single_quota_summary.values_list('credit_model', 'credit_amount')  # 单项额度
    single_dic_list = list(
        map(lambda x: {'credit_model': x[0], 'credit_amount': str(x[1] / 10000).rstrip('0').rstrip('.')}, single_list))
    for single in single_dic_list:
        for CREDIT in CREDIT_MODEL_DIC:
            if single['credit_model'] == CREDIT['credit_model']:
                single['credit'] = CREDIT['credit']

    order_amount_list = article_obj.lending_summary.values_list('order', 'order_amount')  # 发放次序
    order_amount_dic_list = list(
        map(lambda x: {'order': x[0], 'order_amount': str(x[1] / 10000).rstrip('0').rstrip('.')}, order_amount_list))
    review_model = article_obj.appraisal_article.all().first().review_model  # ((1, '内审'), (2, '外审'))
    expert_amount = article_obj.expert.count()  # 评委个数
    '''COMMENT_TYPE_LIST = ((1, '同意'), (2, '复议'), (3, '不同意'))'''
    comment_type_1 = article_obj.comment_summary.filter(comment_type=1).count()  # 同意票数
    comment_type_2 = article_obj.comment_summary.filter(comment_type=2).count()  # 复议票数
    comment_type_3 = article_obj.comment_summary.filter(comment_type=3).count()  # 不同意票数
    lending_count = article_obj.lending_summary.count()  # 放款笔数
    lending_list = article_obj.lending_summary.all()  # 放款次序列表
    rowspan_count = 3
    if lending_count > 1:
        rowspan_count += lending_count
    summary = ''
    lend_or = 1
    for lending in lending_list:
        order_amount = lending.order_amount
        sure_list = lending.sure_lending.all()
        sure_count = sure_list.count()
        sure_or = 1
        if lending_count > 0:
            lend_or += 1
            lend_oz = convert_str(lend_or)
            summary += '<tr><td colspan="4">（%s）第%s次发放%s万元，并落实以下反担保措施</td></tr>' % (
                lend_oz, lend_oz, str(order_amount / 10000).rstrip('0').rstrip('.'))
            rowspan_count += 1
        custom_c_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=1)  # 企业
        if custom_c_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）企业保证：' % sure_or
            custom_c_count = custom_c_list.count()
            custom_c_c = 1
            for custom_c in custom_c_list:
                summary += '%s' % custom_c.name
                if custom_c_c < custom_c_count:
                    summary += '、'
                custom_c_c += 1
            summary += '提供企业连带责任保证反担保。</td></tr>'
            sure_or += 1
        custom_p_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=2)  # 个人
        if custom_p_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）个人保证：' % sure_or
            custom_p_count = custom_p_list.count()
            custom_p_c = 1
            for custom_p in custom_p_list:
                summary += '%s' % custom_p.name
                if custom_p.person_custome.spouses:
                    summary += '、%s夫妇' % custom_p.person_custome.spouses.name
                if custom_p_c < custom_p_count:
                    summary += '，'
                custom_p_c += 1
            summary += '提供个人连带责任保证反担保。</td></tr>'
            sure_or += 1
        '''SURE_TYP_LIST = [
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''
        ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        warrant_h_11_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=11)  # 抵押房产
        if warrant_h_11_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">（%s）房产抵押：' \
                       '以下房产抵押给我公司，签订抵押反担保合同并办理抵押登记</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">处所</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">产权证编号</td> ' \
                       '</tr>'
            for warrant_house in warrant_h_11_list:
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
                    rowspan_count += 1
                    house = warrant_house.house_warrant
                    house_locate = house.house_locate
                    house_app = house.house_app
                    house_area = house.house_area
                    summary += '<tr>' \
                               '<td>%s</td> ' \
                               '<td>%s</td> ' \
                               '<td align="right">%s</td> ' \
                               '<td>%s</td> ' \
                               '</tr>' % (owership_name, house_locate, house_area, owership_num)
                else:
                    housebag_list = warrant_house.housebag_warrant.all()
                    housebag_count = housebag_list.count()
                    rowspan_count += housebag_count
                    housebag_num = 1
                    for housebag in housebag_list:
                        housebag_locate = housebag.housebag_locate
                        housebag_app = housebag.housebag_app
                        housebag_area = housebag.housebag_area
                        if housebag_num == 1:
                            summary += '<tr>' \
                                       '<td rowspan="%s">%s</td> ' \
                                       '<td>%s</td> ' \
                                       '<td align="right">%s</td> ' \
                                       '<td rowspan="%s">%s</td> ' \
                                       '</tr>' % (
                                           housebag_count, owership_name, housebag_locate,
                                           housebag_area, housebag_count, owership_num)
                            housebag_num += 1
                        else:
                            summary += '<tr>' \
                                       '<td>%s</td> ' \
                                       '<td align="right">%s</td> ' \
                                       '</tr>' % (
                                           housebag_locate, housebag_area)
            sure_or += 1
        warrant_g_12_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=12)  # 土地抵押
        if warrant_g_12_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">' \
                       '（%s）土地抵押：以下国有土地使用权抵押给我公司，签订抵押反担保合同并办理抵押登记' \
                       '</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">座落</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">产权证编号</td> ' \
                       '</tr>'
            for warrant_ground in warrant_g_12_list:
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
                summary += '<tr>' \
                           '<td>%s</td> ' \
                           '<td>%s</td> ' \
                           '<td align="right">%s</td> ' \
                           '<td>%s</td> ' \
                           '</tr>' % (
                               owership_name, ground_locate, ground_area, owership_num)
            sure_or += 1
        warrant_c_14_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=14)  # 在建工程抵押
        if warrant_c_14_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">' \
                       '（%s）在建工程抵押：以下在建工程抵押给我公司，签订抵押反担保合同并办理抵押登记' \
                       '</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">座落</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">备注</td> ' \
                       '</tr>'
            for warrant_c in warrant_c_14_list:
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
                summary += '<tr>' \
                           '<td>%s</td> ' \
                           '<td>%s</td> ' \
                           '<td align="right">%s</td> ' \
                           '<td>最终以实际抵押面积为准</td> ' \
                           '</tr>' % (owership_name, coustruct_locate, coustruct_area)
            sure_or += 1
        warrant_c_13_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=13)  # 动产抵押
        if warrant_c_13_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）动产抵押：' % sure_or
            warrant_c_count = warrant_c_13_list.count()
            warrant_c_c = 0
            for warrant_c in warrant_c_13_list:
                warrant_c_c += 1
                summary += '%s提供%s' % (warrant_c.chattel_warrant.chattel_owner.name,
                                       warrant_c.chattel_warrant.chattel_detail)
                if warrant_c_c < warrant_c_count:
                    summary += '、'
            summary += '抵押给我公司，签订抵押反担保合同并办理抵押登记。</td></tr>'
        warrant_v_15_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=15)  # 车辆抵押
        if warrant_v_15_list:
            rowspan_count += 2
            warrant_count = warrant_v_15_list.count()
            rowspan_count += warrant_count
            summary += '<tr><td colspan="4">' \
                       '（%s）车辆抵押抵押：以下车辆抵押给我公司，签订抵押反担保合同并办理抵押登记' \
                       '</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">车架号</td> ' \
                       '<td align="center">车牌号</td> ' \
                       '<td align="center">备注</td> ' \
                       '</tr>'
            for warrant_v in warrant_v_15_list:
                vehicle = warrant_v.vehicle_warrant
                vehicle_owner = vehicle.vehicle_owner.name
                frame_num = vehicle.frame_num
                plate_num = vehicle.plate_num
                vehicle_remark = vehicle.vehicle_remark
                summary += '<tr>' \
                           '<td>%s</td> ' \
                           '<td>%s</td> ' \
                           '<td align="right">%s</td> ' \
                           '<td>%s</td> ' \
                           '</tr>' % (vehicle_owner, frame_num, plate_num, vehicle_remark)
            sure_or += 1
        warrant_h_21_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=21)  # 房产顺位
        if warrant_h_21_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">（%s）房产顺位抵押：' \
                       '以下房产抵押给我公司，签订抵押反担保合同并办理顺位抵押登记</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">处所</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">产权证编号</td> ' \
                       '</tr>'
            for warrant_house in warrant_h_21_list:
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
                    rowspan_count += 1
                    house = warrant_house.house_warrant
                    house_locate = house.house_locate
                    house_app = house.house_app
                    house_area = house.house_area
                    summary += '<tr>' \
                               '<td>%s</td> ' \
                               '<td>%s</td> ' \
                               '<td align="right">%s</td> ' \
                               '<td>%s</td> ' \
                               '</tr>' % (owership_name, house_locate, house_area, owership_num)
                else:
                    housebag_list = warrant_house.housebag_warrant.all()
                    housebag_count = housebag_list.count()
                    rowspan_count += housebag_count
                    housebag_num = 1
                    for housebag in housebag_list:
                        housebag_locate = housebag.housebag_locate
                        housebag_app = housebag.housebag_app
                        housebag_area = housebag.housebag_area
                        if housebag_num == 1:
                            summary += '<tr>' \
                                       '<td rowspan="%s">%s</td> ' \
                                       '<td>%s</td> ' \
                                       '<td align="right">%s</td> ' \
                                       '<td rowspan="%s">%s</td> ' \
                                       '</tr>' % (
                                           housebag_count, owership_name, housebag_locate,
                                           housebag_area, housebag_count, owership_num)
                            housebag_num += 1
                        else:
                            summary += '<tr>' \
                                       '<td>%s</td> ' \
                                       '<td align="right">%s</td> ' \
                                       '</tr>' % (
                                           housebag_locate, housebag_area)
            sure_or += 1
        warrant_g_22_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=22)  # 土地顺位
        if warrant_g_22_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">' \
                       '（%s）土地顺位抵押：以下国有土地使用权抵押给我公司，签订抵押反担保合同并办理顺位抵押登记' \
                       '</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">座落</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">产权证编号</td> ' \
                       '</tr>'
            for warrant_ground in warrant_g_22_list:
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
                summary += '<tr>' \
                           '<td>%s</td> ' \
                           '<td>%s</td> ' \
                           '<td align="right">%s</td> ' \
                           '<td>%s</td> ' \
                           '</tr>' % (
                               owership_name, ground_locate, ground_area, owership_num)
            sure_or += 1
        warrant_c_23_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=23)  # 在建工程顺位
        if warrant_c_23_list:
            rowspan_count += 2
            summary += '<tr><td colspan="4">' \
                       '（%s）在建工程顺位抵押：以下在建工程抵押给我公司，签订抵押反担保合同并办理顺位抵押登记' \
                       '</td></tr>' % sure_or
            summary += '<tr>' \
                       '<td align="center">所有权人</td> ' \
                       '<td align="center">座落</td> ' \
                       '<td align="center">面积(㎡)</td> ' \
                       '<td align="center">备注</td> ' \
                       '</tr>'
            for warrant_c in warrant_c_23_list:
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
                summary += '<tr>' \
                           '<td>%s</td> ' \
                           '<td>%s</td> ' \
                           '<td align="right">%s</td> ' \
                           '<td>最终以实际抵押面积为准</td> ' \
                           '</tr>' % (owership_name, coustruct_locate, coustruct_area)
            sure_or += 1
        warrant_c_24_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=24)  # 动产顺位
        if warrant_c_24_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）动产顺位抵押：' % sure_or
            warrant_c_count = warrant_c_24_list.count()
            warrant_c_c = 0
            for warrant_c in warrant_c_24_list:
                warrant_c_c += 1
                summary += '%s提供%s' % (warrant_c.chattel_warrant.chattel_owner.name,
                                       warrant_c.chattel_warrant.chattel_detail)
                if warrant_c_c < warrant_c_count:
                    summary += '、'
            summary += '抵押给我公司，签订抵押反担保合同并办理顺位抵押登记。</td></tr>'
        warrant_r_31_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=31)  # 应收质押
        if warrant_r_31_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）应收账款质押：' % sure_or
            warrant_r_count = warrant_r_31_list.count()
            warrant_r_c = 0
            for warrant_r in warrant_r_31_list:
                warrant_r_c += 1
                summary += '%s提供%s' % (warrant_r.receive_warrant.receive_owner.name,
                                       warrant_r.receive_warrant.receivable_detail)
                if warrant_r_c < warrant_r_count:
                    summary += '、'
            summary += '质押给我公司，签订质押反担保合同并办理质押登记。</td></tr>'
            sure_or += 1
        warrant_s_32_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=32)  # 股权质押
        if warrant_s_32_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）股权质押：' % sure_or
            warrant_s_count = warrant_s_32_list.count()
            warrant_s_c = 0
            for warrant_s in warrant_s_32_list:
                warrant_s_c += 1
                summary += '%s持有的%s%s' % (warrant_s.stock_warrant.stock_owner.name,
                                          warrant_s.stock_warrant.target,
                                          warrant_s.stock_warrant.ratio)
                summary = summary + '%股权'
                if warrant_s_c < warrant_s_count:
                    summary += '、'
            summary += '质押给我公司，签订质押反担保合同并办理质押登记。</td></tr>'
            sure_or += 1
        warrant_d_33_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=33)  # 票据质押
        if warrant_d_33_list:
            rowspan_count += 1
            summary += '<tr><td colspan="4">（%s）票据质押：' % sure_or
            warrant_d_count = warrant_d_33_list.count()
            warrant_d_c = 0
            for warrant_d in warrant_d_33_list:
                warrant_d_c += 1
                summary += '%s提供%s' % (warrant_d.draft_warrant.draft_owner.name,
                                       warrant_d.draft_warrant.draft_detail)
                if warrant_d_c < warrant_d_count:
                    summary += '、'
            summary += '质押给我公司，签订质押反担保合同并办理质押登记。</td></tr>'
            sure_or += 1
        warrant_c_34_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=34)  # 动产质押
        if warrant_c_34_list:
            rowspan_count += 1
        warrant_o_39_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=39)  # 其他权利质押
        if warrant_o_39_list:
            rowspan_count += 1
        warrant_h_42_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=42)  # 房产监管
        if warrant_h_42_list:
            rowspan_count += 2
            warrant_count = warrant_h_42_list.count()
            rowspan_count += warrant_count
        warrant_g_43_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=43)  # 土地监管
        if warrant_g_43_list:
            rowspan_count += 2
            warrant_count = warrant_g_43_list.count()
            rowspan_count += warrant_count
        warrant_d_44_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=44)  # 票据监管
        if warrant_d_44_list:
            rowspan_count += 1
        warrant_c_47_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=47)  # 动产监管
        if warrant_c_47_list:
            rowspan_count += 1
        warrant_o_49_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=49)  # 其他监管
        if warrant_o_49_list:
            rowspan_count += 1
        warrant_s_51_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=51)  # 股权预售
        if warrant_s_51_list:
            rowspan_count += 1
        warrant_h_52_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=52)  # 房产预售
        if warrant_h_52_list:
            rowspan_count += 2
            warrant_count = warrant_h_52_list.count()
            rowspan_count += warrant_count
        warrant_g_53_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=53)  # 土地预售
        if warrant_g_53_list:
            rowspan_count += 2
            warrant_count = warrant_g_53_list.count()
            rowspan_count += warrant_count

    article_list.update(summary=summary)
    article_summary = article_obj.summary
    return render(request, 'dbms/appraisal/appraisal-summary-scan.html', locals())
