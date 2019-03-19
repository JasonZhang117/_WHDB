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
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4]:
        form_date = {'renewal': article_obj.renewal, 'augment': article_obj.augment,
                     'sign_date': str(datetime.date.today())}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)
    else:
        form_date = {
            'summary_num': article_obj.summary_num, 'sign_type': article_obj.sign_type, 'renewal': article_obj.renewal,
            'augment': article_obj.augment, 'rcd_opinion': article_obj.rcd_opinion,
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
    page_title = '放款次序'
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

    return render(request, 'dbms/appraisal/appraisal-scan-lending.html', locals())


# -----------------------summary_scan纪要预览-------------------------#
@login_required
@authority
def summary_scan(request, article_id):  # 评审项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    page_title = '纪要预览'

    article_obj = models.Articles.objects.get(id=article_id)

    credit_term = article_obj.credit_term
    renewal_str = str(article_obj.renewal / 10000).rstrip('0').rstrip('.')  # 续贷（万元）
    augment_str = str(article_obj.augment / 10000).rstrip('0').rstrip('.')  # 新增（万元）
    amount_str = str(article_obj.amount / 10000).rstrip('0').rstrip('.')  # 总额（万元）

    single_list = article_obj.single_quota_summary.values_list('credit_model', 'credit_amount')  # 单项额度
    single_dic_list = list(
        map(lambda x: {'credit_model': x[0], 'credit_amount': str(x[1] / 10000).rstrip('0').rstrip('.')}, single_list))
    print('single_dic_list:', single_dic_list)  # 单项额度

    order_amount_list = article_obj.lending_summary.values_list('order', 'order_amount')
    order_amount_dic_list = list(
        map(lambda x: {'order': x[0], 'order_amount': str(x[1] / 10000).rstrip('0').rstrip('.')},
            order_amount_list))
    print('order_amount_dic_list:', order_amount_dic_list)  # 放款次序

    review_model = article_obj.appraisal_article.all().first().review_model  # ((1, '内审'), (2, '外审'))
    expert_amount = article_obj.expert.count()  # 评委个数
    '''COMMENT_TYPE_LIST = ((1, '同意'), (2, '复议'), (3, '不同意'))'''
    comment_type_1 = article_obj.comment_summary.filter(comment_type=1).count()  # 同意票数
    comment_type_2 = article_obj.comment_summary.filter(comment_type=2).count()  # 复议票数
    comment_type_3 = article_obj.comment_summary.filter(comment_type=3).count()  # 不同意票数
    lending_count = article_obj.lending_summary.count()  # 放款笔数
    lending_list = article_obj.lending_summary.all()  # 放款次序列表

    for lending in lending_list:
        sure_lending_list = lending.sure_lending.all()
        print('sure_lending_list:', sure_lending_list)
    print('comment_type_1:', comment_type_1)
    return render(request, 'dbms/appraisal/appraisal-summary-scan.html', locals())
