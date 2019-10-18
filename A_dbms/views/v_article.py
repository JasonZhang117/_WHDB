from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from django.db.utils import IntegrityError
from django.db import transaction
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper, authority, article_right, article_list_screen


# -----------------------------项目列表------------------------------#
@login_required
@authority
def article(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目列表'

    form_article_add_edit = forms.ArticlesAddForm()
    for k, v in request.GET.items():  # 获取传递参数
        pass
        # print(k, ' ', v)
    condition = {
        # 'article_state' : 0, #查询字段及值的字典，空字典查询所有
    }  # 建立空的查询字典
    for k, v in kwargs.items():
        # temp = int(v)
        temp = v
        kwargs[k] = temp
        if temp:
            condition[k] = temp  # 将参数放入查询字典
    '''筛选条件'''
    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 筛选条件
    article_state_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, article_state_list))
    # 列表或元组转换为字典并添加key[{'id': 1, 'name': '待反馈'}, {'id': 2, 'name': '已反馈'}]
    '''筛选'''
    article_list = models.Articles.objects.filter(**kwargs).select_related('custom', 'director', 'assistant', 'control')
    article_list = article_list_screen(article_list, job_list, request.user)  # 项目筛选
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['article_num', 'custom__name', 'custom__name', 'director__name',
                         'assistant__name', 'control__name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        article_list = article_list.filter(q)
    article_acount = article_list.count()  # 信息数目
    balance = article_list.aggregate(Sum('article_balance'))['article_balance__sum']  # 在保余额
    '''分页'''
    paginator = Paginator(article_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/article/article.html', locals())


# -----------------------------项目预览------------------------------#
@login_required
@authority
@article_right
def article_scan(request, article_id):  # 项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目详情'
    article_obj = models.Articles.objects.get(id=article_id)  # 项目

    expert_list = article_obj.expert.values_list('id')  # 项目评委列表
    feedbac_list = article_obj.feedback_article.all()  # 项目反馈列表
    investigate_custom_list = article_obj.custom.inv_custom.all().order_by('-inv_date')  # 客户补调列表

    form_date = {
        'custom_id': article_obj.custom.id, 'product_id': article_obj.product.id,
        'renewal': article_obj.renewal, 'process_id': article_obj.process.id,
        'augment': article_obj.augment, 'credit_term': article_obj.credit_term,
        'director_id': article_obj.director.id,
        'assistant_id': article_obj.assistant.id, 'control_id': article_obj.control.id,
        'article_date': str(article_obj.article_date)}
    form_article_add_edit = forms.ArticlesAddForm(initial=form_date)  # 项目变更form
    if feedbac_list:
        form_date = {
            'propose': feedbac_list[0].propose, 'analysis': feedbac_list[0].analysis,
            'suggestion': feedbac_list[0].suggestion}
        form_feedback = forms.FeedbackAddForm(initial=form_date)  # 添加项目反馈form
    else:
        form_feedback = forms.FeedbackAddForm()  # 添加项目反馈form
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_obj.article_state in [1, 2, 3, 4]:
        form_date = {'renewal': article_obj.renewal, 'augment': article_obj.augment,
                     'sign_date': str(datetime.date.today())}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)  # 项目签批form
    else:
        form_date = {
            'summary_num': article_obj.summary_num, 'sign_type': article_obj.sign_type, 'renewal': article_obj.renewal,
            'augment': article_obj.augment, 'credit_amount': article_obj.custom.credit_amount,
            'rcd_opinion': article_obj.rcd_opinion,
            'convenor_opinion': article_obj.convenor_opinion, 'sign_detail': article_obj.sign_detail,
            'sign_date': str(article_obj.sign_date)}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)  # 项目签批form
    form_article_sub = forms.ArticleSubForm()  # 添加审批意见form
    form_comment = forms.CommentsAddForm()  # 添加评审意见form
    form_single = forms.SingleQuotaForm()  # 添加单项额度form
    form_supply = forms.FormAddSupply()  # 添加补调问题form
    form_lending = forms.FormLendingOrder()  # 添加放款次序form
    form_article_change = forms.ArticleChangeForm(initial={'change_date': str(datetime.date.today())})  # 变更项目form
    form_inv_add = forms.FormInvestigateAdd(initial={'inv_date': str(datetime.date.today())})  # 添加补充调查form

    return render(request, 'dbms/article/article-scan.html', locals())


# -----------------------------项目预览-按合同------------------------------#

@login_required
@authority
@article_right
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '查看项目'

    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32]
    CHATTEL_LIST = [13]

    article_obj = models.Articles.objects.get(id=article_id)
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    return render(request, 'dbms/article/article-scan-agree.html', locals())


# -----------------------------项目预览-按发放次序------------------------------#

@login_required
@authority
@article_right
def article_scan_lending(request, article_id, lending_id):  # 项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目次序'
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
    OTHER_LIST = [39, 49, 59]  # 其他类
    '''反担保情况'''
    custom_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=lending_obj) #放款次序下-反担保人列表
    warrant_lending_h_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ__in=[1, 2])  #放款次序下-房产列表
    warrant_lending_g_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=5) #放款次序下-土地列表
    warrant_lending_6_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=6) #放款次序下-在建工程列表
    warrant_lending_r_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=11) #放款次序下-应收账款列表
    warrant_lending_s_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=21) #放款次序下-股权列表
    warrant_lending_d_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=31) #放款次序下-票据列表
    warrant_lending_v_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=41) #放款次序下-车辆列表
    warrant_lending_c_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=51) #放款次序下-动产列表
    warrant_lending_o_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending_obj, warrant_typ=55) #放款次序下-其他列表
    form_agree_add = forms.ArticleAgreeAddForm()  # 创建合同form
    today_str = datetime.date.today()
    date_th_later = today_str + datetime.timedelta(days=365)
    from_letter_data = {'starting_date': str(today_str), 'due_date': str(date_th_later)}
    form_letter_add = forms.LetterGuaranteeAddForm(initial=from_letter_data)  # 创建公司保函合同
    '''GENRE_LIST = [(1, '企业'), (2, '个人')]'''
    form_lendingcustoms_c_add = models.Customes.objects.exclude(
        id=article_obj.custom.id).filter(genre=1).values_list('id', 'name') #除项目客户外的企业
    form_lendingcustoms_p_add = models.Customes.objects.exclude(
        id=article_obj.custom.id).filter(genre=2).values_list('id', 'name') #除项目客户外的个人
    form_lendingsures = forms.LendingSuresForm() #反担保类型form
    # form_lendingcustoms_c_add = forms.LendingCustomsCForm()
    # form_lendingcustoms_p_add = forms.LendingCustomsPForm()
    form_lendinghouse_add = forms.LendingHouseForm()  # 添加放担保-房产form
    form_lendingground_add = forms.LendingGroundForm()  # 添加放担保-土地form
    form_lendingconstruct_add = forms.LendingConstructForm()  # 添加放担保-在建工程form
    form_lendinggreceivable_add = forms.LendinReceivableForm()  # 添加放担保-应收账款form
    form_lendingstock_add = forms.LendinStockForm()  # 添加放担保-股权form
    form_lendingdraft_add = forms.LendinDraftForm()  # 添加放担保-票据form
    form_lendingvehicle_add = forms.LendinVehicleForm()  # 添加放担保-车辆form
    form_lendingchattel_add = forms.LendinChattelForm()  # 添加放担保-动产form
    form_lendingother_add = forms.LendinOtherForm()  # 添加放担保-其他form
    form_lending = forms.FormLendingOrder(
        initial={'order': lending_obj.order,
                 'remark': lending_obj.remark,
                 'order_amount': lending_obj.order_amount}) #放款次序变更form

    return render(request, 'dbms/article/article-scan-lending.html', locals())
