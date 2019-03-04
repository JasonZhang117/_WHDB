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
def warrant(request, *args, **kwargs):  # 房产列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证列表'
    add_warrant = '添加权证'
    warrant_typ_n = 0
    '''WARRANT_STATE_LIST = (
           (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
           (31, '解保出库'), (99, '已注销'))'''
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    '''模态框'''
    form_warrant_add = forms.WarrantAddForm()  # 权证添加
    form_house_add_edit = forms.HouseAddEidtForm()  # 房产添加
    form_ground_add_edit = forms.GroundAddEidtForm()  # 土地添加
    form_receivable_add_edit = forms.FormReceivable()  # 应收添加
    form_stockes_add_edit = forms.FormStockes()  # 21股权添加
    form_draft_add_eidt = forms.FormDraft()  # 31票据添加
    form_vehicle_add_eidt = forms.FormVehicle()  # 41车辆添加
    form_chattel_add_eidt = forms.FormChattel()  # 51动产添加
    form_hypothecs_add_eidt = forms.HypothecsAddEidtForm()  # 99他权添加
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
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
def warrant_scan(request, warrant_id):  # house_scan房产预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证预览'
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    warrant_typ_n = warrant_obj.warrant_typ
    HOUSE_GROUND_TYP_LIST = [1, 5]
    '''WARRANT_TYP_LIST = [
                    (1, '房产'), (2, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
                    (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    if warrant_typ_n == 99:
        agree_lending_obj = warrant_obj.ypothec_warrant.agree.lending
        warrants_lending_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=agree_lending_obj).values_list('id', 'warrant_num')

    form_warrant_edit_date = {'warrant_num': warrant_obj.warrant_num}
    form_warrant_edit = forms.WarrantEditForm(initial=form_warrant_edit_date)  # 权证编辑form
    warrant_typ = warrant_obj.warrant_typ
    print('warrant_typ:', warrant_typ)
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
    elif warrant_typ == 11:
        form_date = {
            'receive_owner': warrant_obj.receive_warrant.receive_owner,
            'receivable_detail': warrant_obj.receive_warrant.receivable_detail}
        form_receivable_add_edit = forms.FormReceivable(form_date)
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

    return render(request, 'dbms/warrant/warrant-scan.html', locals())


# -----------------------按合同入库---------------------#
@login_required
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
def warrant_agree_scan(request, agree_id):  # 查看合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITAL = '权证管理'
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

    '''WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32, 51]
    CHATTEL_LIST = [13]
    DRAFT_LIST = [33]

    form_storage_add_edit = forms.StoragesAddEidtForm(initial={'storage_date': str(datetime.date.today())})

    return render(request, 'dbms/warrant/warrant-agree-scan.html', locals())


# --------------------------按合同入库-按合同查看(没用)--------------------------#
@login_required
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
