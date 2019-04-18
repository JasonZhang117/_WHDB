from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.contrib.auth.decorators import login_required
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q, F
from django.urls import resolve
from _WHDB.views import MenuHelper
from django.views import View
from _WHDB.views import authority


# -----------------------权证列表-------------------------#
@login_required
@authority
def warrant(request, *args, **kwargs):  # 房产列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证列表'
    add_warrant = '添加权证'
    warrant_typ_n = 0
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销'))'''
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地使用权'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    '''模态框'''
    form_warrant_add = forms.WarrantAddForm()  # 权证添加
    form_house_add_edit = forms.HouseAddEidtForm()  # 房产添加
    form_ground_add_edit = forms.GroundAddEidtForm()  # 土地添加
    form_construct_add_edit = forms.ConstructionAddForm()  # 在建工程
    form_receivable_add = forms.FormReceivable()  # 应收添加
    form_stockes_add_edit = forms.FormStockes()  # 21股权添加
    form_draft_add_eidt = forms.FormDraft()  # 31票据添加
    form_vehicle_add_eidt = forms.FormVehicle()  # 41车辆添加
    form_chattel_add_eidt = forms.FormChattel()  # 51动产添加
    form_other_add_eidt = forms.FormOthers()  # 55其他添加
    form_hypothecs_add_eidt = forms.HypothecsAddEidtForm()  # 99他权添加

    warrant_typ_list = models.Warrants.WARRANT_TYP_LIST  # 筛选条件
    '''筛选'''
    warrant_list = models.Warrants.objects.filter(**kwargs).order_by('warrant_num')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['warrant_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        warrant_list = warrant_list.filter(q)
    warrant_acount = warrant_list.count()
    '''分页'''
    paginator = Paginator(warrant_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/warrant.html', locals())


# ---------------------warrant_scan权证预览------------------------#
@login_required
@authority
def warrant_scan(request, warrant_id):  # house_scan房产预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证预览'
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    warrant_typ_n = warrant_obj.warrant_typ
    HOUSE_GROUND_TYP_LIST = [1, 5, 6]
    if warrant_typ_n == 99:
        agree_lending_obj = warrant_obj.ypothec_warrant.agree.lending
        warrants_lending_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=agree_lending_obj).values_list('id', 'warrant_num')
    form_warrant_edit_date = {'warrant_num': warrant_obj.warrant_num}
    form_warrant_edit = forms.WarrantEditForm(initial=form_warrant_edit_date)  # 权证编辑form
    warrant_typ = warrant_obj.warrant_typ
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    if warrant_typ == 1:  # 房产
        form_date = {
            'house_locate': warrant_obj.house_warrant.house_locate,
            'house_app': warrant_obj.house_warrant.house_app,
            'house_area': warrant_obj.house_warrant.house_area}
        form_house_add_edit = forms.HouseAddEidtForm(form_date)
    elif warrant_typ == 5:  # 土地form
        form_date = {
            'ground_locate': warrant_obj.ground_warrant.ground_locate,
            'ground_app': warrant_obj.ground_warrant.ground_app,
            'ground_area': warrant_obj.ground_warrant.ground_area}
        form_ground_add_edit = forms.GroundAddEidtForm(form_date)
    elif warrant_typ == 6:  # 在建工程
        form_date = {
            'coustruct_locate': warrant_obj.coustruct_warrant.coustruct_locate,
            'coustruct_app': warrant_obj.coustruct_warrant.coustruct_app,
            'coustruct_area': warrant_obj.coustruct_warrant.coustruct_area}
        form_construct_add_edit = forms.ConstructionAddForm(form_date)
    elif warrant_typ == 11:  # 应收账款
        form_date = {'receivable_detail': warrant_obj.receive_warrant.receivable_detail}
        form_receivable_edit = forms.FormReceivableEdit(form_date)
    elif warrant_typ == 21:  # 股权
        form_date = {
            'target': warrant_obj.stock_warrant.target,
            'share': warrant_obj.stock_warrant.share,
            'ratio': warrant_obj.stock_warrant.ratio,
            'stock_typ': warrant_obj.stock_warrant.stock_typ}
        form_stockes_edit = forms.FormStockesEdit(form_date)
    elif warrant_typ == 31:  # 31票据添加
        form_date = {'draft_detail': warrant_obj.draft_warrant.draft_detail}
        form_draft_eidt = forms.FormDraftEdit(form_date)  # 31票据添加
    elif warrant_typ == 41:  # 41车辆添加
        form_date = {
            'frame_num': warrant_obj.vehicle_warrant.frame_num,
            'plate_num': warrant_obj.vehicle_warrant.plate_num}
        form_vehicle_eidt = forms.FormVehicleEdit(form_date)  # 41车辆添加
    elif warrant_typ == 51:  # 51动产添加
        form_date = {
            'chattel_typ': warrant_obj.chattel_warrant.chattel_typ,
            'chattel_detail': warrant_obj.chattel_warrant.chattel_detail}
        form_chattel_eidt = forms.FormChattelEdit(form_date)  # 51动产添加
    elif warrant_typ == 55:  # 55其他添加
        form_date = {
            'other_typ': warrant_obj.other_warrant.other_typ,
            'other_detail': warrant_obj.other_warrant.other_detail}
        form_other_eidt = forms.FormOthersEdit(form_date)  # 55其他添加
    elif warrant_typ == 99:  # 他权form
        form_date = {
            'agree': warrant_obj.ypothec_warrant.agree}
        form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(initial=form_date)
    form_storage_add_edit = forms.StoragesAddEidtForm(initial={'storage_date': str(datetime.date.today())})  # 出入库
    form_owership_add_edit = forms.OwerShipAddForm()  # 所有权证form
    form_housebag_add_edit = forms.HouseBagAddEidtForm()  # 房产包form
    form_draftbag_add_edit = forms.FormDraftExtend()  # 票据包form
    form_evaluate_add_edit = forms.EvaluateAddEidtForm(initial={'evaluate_date': str(datetime.date.today())})  # 评估
    storage_warrant_list = warrant_obj.storage_warrant.all()  # 出入库信息
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    in_article_list = warrant_obj.lending_warrant.all().filter(
        sure__lending__summary__article_state__in=[1, 2, 3, 4, 5, 51, 52, 61])

    return render(request, 'dbms/warrant/warrant-scan.html', locals())


# -----------------------按合同入库---------------------#
@login_required
@authority
def warrant_agree(request, *args, **kwargs):  # 按合同入库
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证-按合同'
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    # agree_list = models.Agrees.objects.filter(**kwargs).filter(agree_state__in=[21, 31, 51]).select_related(
    #     'lending', 'branch').order_by('-agree_num')
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
    agree_acount = agree_list.count()
    '''分页'''
    paginator = Paginator(agree_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/warrant-agree.html', locals())


# --------------------------按合同入库-按合同查看--------------------------#
@login_required
@authority
def warrant_agree_scan(request, agree_id):  # 查看合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '权证管理'
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
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
    '''反担保情况'''
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
    '''他权情况'''
    hypothec_agree_list = models.Hypothecs.objects.filter(agree=agree_obj)

    form_storage_add_edit = forms.StoragesAddEidtForm(initial={'storage_date': str(datetime.date.today())})

    return render(request, 'dbms/warrant/warrant-agree-scan.html', locals())


# --------------------------按合同入库-按合同查看(没用)--------------------------#
@login_required
@authority
def warrant_agree_warrant(request, agree_id, warrant_id):  # 查看合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    page_title = '权证管理'
    '''SURE_TYP_LIST = (
            (1, '企业保证'), (2, '个人保证'),
            (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
            (21, '房产顺位'), (22, '土地顺位'),
            (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
            (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
            (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    print('agree_obj.ypothec_agree.all():', agree_obj.ypothec_agree.all())
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    sure_list = [1, 2]  # 保证反担保类型
    house_list = [11, 21, 42, 52]
    ground_list = [12, 22, 43, 53]
    receivable_list = [31]
    stock_list = [32]

    form_storage_add_edit = forms.StoragesAddEidtForm()

    return render(request, 'dbms/warrant/warrant-agree-warrant.html', locals())


# -----------------------house房产列表-------------------------#
@login_required
@authority
def house(request, *args, **kwargs):  # 房产列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    print('**kwargs:', kwargs)

    PAGE_TITAL = '权证-房产'
    add_warrant = '添加房产'
    warrant_typ_n = 1

    form_warrant_edit = forms.WarrantEditForm()
    form_house_add_edit = forms.HouseAddEidtForm()

    house_app_list = models.Houses.HOUSE_APP_LIST
    house_list = models.Houses.objects.filter(**kwargs).order_by('warrant')
    '''分页'''
    paginator = Paginator(house_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/house.html', locals())


# -----------------------房产列表-------------------------#
@login_required
@authority
def ground(request, *args, **kwargs):  # 房产列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()

    PAGE_TITAL = '权证-土地'
    add_warrant = '添加土地'
    warrant_typ_n = 5

    form_warrant_edit = forms.WarrantEditForm()
    form_ground_add_edit = forms.GroundAddEidtForm()

    ground_app_list = models.Grounds.GROUND_APP_LIST
    ground_list = models.Grounds.objects.filter(**kwargs).order_by('warrant')
    '''分页'''
    paginator = Paginator(ground_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/ground.html', locals())


# -----------------------即将到期票据列表-------------------------#
@login_required
@authority
def soondue_draft(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '票据列表'

    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    soondue_draft_list = models.DraftExtend.objects.filter(draft_state__in=[1, 2], due_date__gte=datetime.date.today(),
                                                           due_date__lt=date_th_later)  # 30天内到期
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['draft_num', 'draft_acceptor',
                         'draft__draft_owner__name', 'draft__draft_owner__short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        soondue_draft_list = soondue_draft_list.filter(q)

    provide_acount = soondue_draft_list.count()
    '''分页'''
    paginator = Paginator(soondue_draft_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/overdu-draft.html', locals())


# -----------------------即将到期票据列表-------------------------#
@login_required
@authority
def overdue_draft(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '票据列表'

    overdue_draft_list = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__lt=datetime.date.today())  # 逾期票据
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['draft_num', 'draft_acceptor',
                         'draft__draft_owner__name', 'draft__draft_owner__short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        overdue_draft_list = overdue_draft_list.filter(q)

    provide_acount = overdue_draft_list.count()
    '''分页'''
    paginator = Paginator(overdue_draft_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/overdu-draft.html', locals())


# -----------------------评估跟踪列表-------------------------#
@login_required
@authority
def overdue_evaluate(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '评估跟踪'
    warrant_typ_n = 0
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销'))'''
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地使用权'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

    EVALUATE_STATE_LIST = models.Warrants.EVALUATE_STATE_LIST  # 筛选条件
    '''筛选'''
    warrant_list = models.Warrants.objects.filter(**kwargs).exclude(
        evaluate_state__in=[41, 99])
    '''EVALUATE_STATE_LIST = [(0, '待评估'), (5, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'),
                               (41, '拍卖评估'), (99, '无需评估')]'''
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    warrant_list = warrant_list.filter(
        lending_warrant__sure__lending__summary__article_state__in=[4, 5, 51, 52, 61]).distinct()
    ddd = []
    for warrant in warrant_list:
        if warrant.evaluate_state == 0:
            ddd.append(warrant.id)
        else:
            cccc = warrant.meeting_date - warrant.evaluate_date
            if cccc.days > 365:
                ddd.append(warrant.id)
    warrant_list = models.Warrants.objects.filter(id__in=ddd).order_by('-meeting_date')

    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['warrant_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        warrant_list = warrant_list.filter(q)
    warrant_acount = warrant_list.count()
    '''分页'''
    paginator = Paginator(warrant_list, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/overdu-evaluate.html', locals())


# -----------------------未入库列表-------------------------#
@login_required
@authority
def overdue_storage(request, *args, **kwargs):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '入库跟踪'
    warrant_typ_n = 0
    '''WARRANT_STATE_LIST = [
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销')]'''
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地使用权'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
    '''STORAGE_TYP_LIST = [(1, '入库'), (2, '续抵出库'), (6, '无需入库'), (11, '借出'), (12, '归还'), (31, '解保出库')]'''
    WARRANT_STATE_LIST = models.Warrants.WARRANT_STATE_LIST  # 筛选条件
    '''筛选'''
    warrant_list = models.Warrants.objects.filter(**kwargs).filter(warrant_state__in=[1, 11, 21])
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                              (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    warrant_list = warrant_list.filter(
        lending_warrant__sure__lending__summary__article_state__in=[51, 52, 61]).distinct()
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['warrant_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        warrant_list = warrant_list.filter(q)
    warrant_acount = warrant_list.count()
    '''分页'''
    paginator = Paginator(warrant_list, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/overdu-storage.html', locals())
