from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import (MenuHelper, authority, amount_s, amount_y, convert, convert_num)


# -----------------------放款管理---------------------#
@login_required
@authority
def provide_agree(request, *args, **kwargs):  # 放款管理
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '风控落实'
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).select_related('lending', 'branch').order_by('-agree_num')
    if '项目经理' in job_list:
        agree_list = agree_list.filter(
            Q(lending__summary__director=request.user) | Q(lending__summary__assistant=request.user))
    # agree_list = agree_list.filter(agree_state__in=[21, 31, 41, 51], lending__summary__article_state__in=[5, 51, 61])
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['agree_num', 'lending__summary__custom__name', 'lending__summary__custom__short_name',
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

    return render(request, 'dbms/provide/provide-agree.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
@authority
def provide_agree_scan(request, agree_id):  # 查看放款
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '风控落实'
    response = {'status': True, 'message': None, 'forme': None, }
    COUNTER_TYP_CUSTOM = [1, 2]
    WARRANT_TYP_OWN_LIST = [1, 2, 5, 6]
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee__lending_summary__agree_lending=agree_obj) | Q(
                assistant_employee__lending_summary__agree_lending=agree_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
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
    '''检查风控落实情况'''
    warrant_storage_str = ''  # 未入库权证
    warrant_ypothec_str = ''  # 缺他权
    ypothec_storage_str = ''  # 他权未入库
    ascertain_str = ''  # 未落实情况
    agree_str = ''
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    agree_state_n = 41
    agree_lending_sure_list = agree_obj.lending.sure_lending.all()  # 反担保措施列表'LendingSures'
    sure_count = agree_lending_sure_list.count()
    sure_c = 0
    for sure in agree_lending_sure_list:
        sure_c += 1
        '''SURE_TYP_LIST = [
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''
        if sure.sure_typ not in [1, 2]:  # (1, '企业保证'), (2, '个人保证')
            sure_warrant = sure.warrant_sure.warrant.all()
            sure_warrant_count = sure_warrant.count()
            sure_warrant_c = 0
            for warrant in sure_warrant:
                sure_warrant_c += 1
                ypothec_list = warrant.ypothec_m_agree.all().filter(agree=agree_obj).distinct()  # 权证对应合同的他权
                ypothec_count = ypothec_list.count()
                ypothec_c = 0
                ''' WARRANT_STATE_LIST = [
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销')]'''
                if warrant.warrant_state in [1, 11, 21]:  # (1, '未入库'), (11, '续抵出库'), (21, '已借出')
                    warrant_storage_str += '%s' % warrant.warrant_num  # 待入库
                    if sure_warrant_c < sure_warrant_count:
                        warrant_storage_str += '，'
                '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
                if not ypothec_list:  # 权证无对应合同的他权
                    if not warrant.warrant_typ in [31, 55]:  # 票据、其他无需他权
                        if not sure.sure_typ in [42, 43, 44, 47, 49, 51, 52, 53, ]:  # 监管、预售无需他权
                            warrant_ypothec_str += '%s' % warrant.warrant_num  # 无他权
                            # if sure_warrant_c < sure_warrant_count:
                            #     warrant_ypothec_str += '，'
                            if sure_c < sure_count:
                                warrant_ypothec_str += '，'
                else:
                    for ypothec in ypothec_list:
                        ypothec_c += 1
                        warrant_state = ypothec.warrant.warrant_state
                        # (1, '未入库'), (11, '续抵出库'), (21, '已借出')
                        if warrant_state in [1, 11, 21] and not warrant.warrant_typ == 31:
                            ypothec_storage_str += '%s' % ypothec.warrant.warrant_num  # 他权未入库
                            # if ypothec_c < ypothec_count:
                            #     ypothec_storage_str += '，'
                            if sure_c < sure_count:
                                warrant_ypothec_str += '，'

    counter_list = agree_obj.counter_agree.all()
    counter_count = counter_list.count()
    counter_c = 0
    counter_agree_str = ''
    for counter in counter_list:
        '''COUNTER_STATE_LIST = [(11, '未签订'), (21, '已签订'), (31, '作废')]'''
        counter_c += 1
        if counter.counter_state == 11:
            counter_agree_str += '%s' % counter.counter_num  # 合同未签订
            if counter_c < counter_count:
                counter_agree_str += '，'
    if warrant_ypothec_str != '':
        agree_state_n = 31
        ascertain_str += '无他权：%s；\r\n' % warrant_ypothec_str
    if warrant_storage_str != '':
        agree_state_n = 31
        ascertain_str += '权证未入库：%s；\r\n' % warrant_storage_str
    if ypothec_storage_str != '':
        agree_state_n = 31
        ascertain_str += '他权未入库：%s；\r\n' % ypothec_storage_str
    if counter_agree_str != '':
        agree_state_n = 31
        ascertain_str += '合同未签订：%s；\r\n' % counter_agree_str
    if agree_state_n == 41:
        agree_str = '所有风控措施已落实，可以出具放款通知！'
    else:
        agree_str = ascertain_str
    today_str = str(datetime.date.today())
    form_notify_add = forms.FormNotifyAdd(initial={'notify_date': today_str})  # 添加放款通知
    form_ascertain_add = forms.FormAscertainAdd()  # 风控落实

    from_agree_sign = forms.FormAgreeSignAdd(initial={'sign_date': today_str})  # 反担保合同签订
    from_counter_sign = forms.FormCounterSignAdd(initial={'counter_sign_date': today_str})  # 反担保合同签订
    return render(request, 'dbms/provide/provide-agree-scan.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
@authority
def provide_agree_notify(request, agree_id, notify_id):  # 查看放款通知
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '放款通知'
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    notify_obj = models.Notify.objects.get(id=notify_id)
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee__lending_summary__agree_lending__notify_agree=notify_obj) | Q(
                director_employee__lending_summary__agree_lending__notify_agree=notify_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
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

    today_str = datetime.date.today()
    date_th_later = today_str + datetime.timedelta(days=365)
    form_provide_data = {'provide_date': str(today_str), 'due_date': str(date_th_later)}
    form_provide_add = forms.FormProvideAdd(initial=form_provide_data)

    return render(request, 'dbms/provide/provide-agree-notify.html', locals())


# -----------------------放款通知---------------------#
@login_required
@authority
def notify_show(request, notify_id):  # 查看放款通知
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '放款通知'

    notify_obj = models.Notify.objects.get(id=notify_id)
    product_name_list = ['房抵贷', '担保贷', '过桥贷', ]
    agree_amount_cn = convert(notify_obj.agree.agree_amount)
    notify_money_cn = convert(notify_obj.notify_money)
    agree_term_cn = convert_num(notify_obj.agree.agree_term)
    agree_rate_str = notify_obj.agree.agree_rate
    date_today_str = str(datetime.date.today())

    return render(request, 'dbms/provide/provide-notify-show.html', locals())


# -----------------------通知列表---------------------#
@login_required
@authority
def notify(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '放款通知'

    '''筛选'''
    notify_list = models.Notify.objects.filter(**kwargs).select_related('agree').order_by('-notify_date')
    if '项目经理' in job_list:
        notify_list = notify_list.filter(
            Q(agree__lending__summary__director=request.user) | Q(
                agree__lending__summary__director=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['agree__lending__summary__custom__name',
                         'agree__branch__name', 'agree__branch__short_name',
                         'agree__agree_num', 'contracts_lease', 'contract_guaranty']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        notify_list = notify_list.filter(q)

    balance = notify_list.aggregate(Sum('notify_balance'))['notify_balance__sum']  # 在保余额

    provide_acount = notify_list.count()
    '''分页'''
    paginator = Paginator(notify_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-notify.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
@authority
def notify_scan(request, notify_id):  # 查看放款通知
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '通知详情'

    notify_obj = models.Notify.objects.get(id=notify_id)
    agree_obj = notify_obj.agree
    lending_obj = agree_obj.lending
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee__lending_summary__agree_lending__notify_agree=notify_obj) | Q(
                director_employee__lending_summary__agree_lending__notify_agree=notify_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
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

    today_str = datetime.date.today()
    date_th_later = today_str + datetime.timedelta(days=365)
    form_provide_data = {'provide_date': str(today_str), 'due_date': str(date_th_later)}
    form_provide_add = forms.FormProvideAdd(initial=form_provide_data)
    form_data = {'contracts_lease': notify_obj.contracts_lease,
                 'contract_guaranty': notify_obj.contract_guaranty,
                 'remark': notify_obj.remark}
    form_notify_edit = forms.FormNotifyEdit(initial=form_data)  # 添加放款通知
    return render(request, 'dbms/provide/provide-notify-scan.html', locals())


# -----------------------放款列表---------------------#
@login_required
@authority
def provide(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '放款列表'
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    PROVIDE_STATUS_LIST = models.Provides.PROVIDE_STATUS_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-provide_date')
    if '项目经理' in job_list:
        provide_list = provide_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__lending__summary__custom__short_name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)

    balance = provide_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    provide_acount = provide_list.count()
    '''分页'''
    paginator = Paginator(provide_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide.html', locals())


# -----------------------------查看放款------------------------------#
@login_required
@authority
def provide_scan(request, provide_id):  # 查看放款
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '放款详情'

    provide_obj = models.Provides.objects.get(id=provide_id)
    if '项目经理' in job_list:
        user_list = models.Employees.objects.filter(
            Q(director_employee__lending_summary__agree_lending__notify_agree__provide_notify=provide_obj) | Q(
                director_employee__lending_summary__agree_lending__notify_agree__provide_notify=provide_obj)).distinct()
        if not request.user in user_list:
            return HttpResponse('你无权访问该项目')
    today_str = str(datetime.date.today())
    form_repayment_add = forms.FormRepaymentAdd(initial={'repayment_date': today_str})
    form_compensatory_add = forms.FormCompensatoryAdd(initial={'compensatory_date': today_str})
    date_th_later = datetime.date.today() + datetime.timedelta(days=30)  # 30天后的日期
    form_track_plan = forms.FormTrackPlan(initial={'plan_date': str(date_th_later)})
    form_track_add = forms.FormTrackAdd()

    return render(request, 'dbms/provide/provide-scan.html', locals())


# -----------------------逾期列表---------------------#
@login_required
@authority
def overdue(request, *args, **kwargs):  # 逾期列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '逾期项目'
    overdue_list = models.Provides.objects.filter(
        provide_status=1, due_date__lt=datetime.date.today()).order_by('due_date')  # 逾期
    if '项目经理' in job_list:
        overdue_list = overdue_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        overdue_list = overdue_list.filter(q)

    balance = overdue_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额

    provide_acount = overdue_list.count()
    '''分页'''
    paginator = Paginator(overdue_list, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-overdu.html', locals())


# -----------------------即将到期列表---------------------#
@login_required
@authority
def soondue(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '即将到期（含逾期）'
    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    soondue_list = models.Provides.objects.filter(
        provide_status=1, due_date__lte=date_th_later).order_by('due_date')  # 30天内到期
    if '项目经理' in job_list:
        soondue_list = soondue_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['notify__agree__lending__summary__custom__name',
                         'notify__agree__branch__name', 'notify__agree__branch__short_name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        soondue_list = soondue_list.filter(q)

    balance = soondue_list.aggregate(Sum('provide_balance'))['provide_balance__sum']  # 在保余额
    provide_acount = soondue_list.count()
    '''分页'''
    paginator = Paginator(soondue_list, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-overdu.html', locals())


# -----------------------风控落实跟踪---------------------#
@login_required
@authority
def provide_follow(request, *args, **kwargs):  # 放款管理
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '风控落实跟踪'
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).filter(
        agree_state=31).select_related('lending', 'branch').order_by('-agree_num')
    if '项目经理' in job_list:
        agree_list = agree_list.filter(
            Q(lending__summary__director=request.user) | Q(lending__summary__assistant=request.user))
    # agree_list = agree_list.filter(agree_state__in=[21, 31, 41, 51], lending__summary__article_state__in=[5, 51, 61])
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['agree_num', 'lending__summary__custom__name', 'lending__summary__custom__short_name',
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

    return render(request, 'dbms/provide/provide-follow.html', locals())


# -----------------------逾期跟踪---------------------#
@login_required
@authority
def track_overdue(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '逾期跟踪'
    track_overdue = models.Track.objects.filter(track_state=11, plan_date__lt=datetime.date.today())
    if '项目经理' in job_list:
        track_overdue = track_overdue.filter(
            Q(provide__notify__agree__lending__summary__director=request.user) |
            Q(provide__notify__agree__lending__summary__assistant=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['provide__notify__agree__lending__summary__custom__name',
                         'provide__notify__agree__lending__summary__custom__short_name',
                         'provide__notify__agree__branch__name',
                         'provide__notify__agree__branch__short_name',
                         'provide__notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        track_overdue = track_overdue.filter(q)

    provide_acount = track_overdue.count()
    '''分页'''
    paginator = Paginator(track_overdue, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-track-overdu.html', locals())


# -----------------------1周内跟踪---------------------#
@login_required
@authority
def track_soondue(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '一周跟踪'
    date_7_later = datetime.date.today() + datetime.timedelta(days=7)  # 7天后的日期
    track_soondue = models.Track.objects.filter(
        track_state=11, plan_date__gte=datetime.date.today(), plan_date__lt=date_7_later)
    if '项目经理' in job_list:
        track_soondue = track_soondue.filter(
            Q(provide__notify__agree__lending__summary__director=request.user) |
            Q(provide__notify__agree__lending__summary__assistant=request.user))
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['provide__notify__agree__lending__summary__custom__name',
                         'provide__notify__agree__lending__summary__custom__short_name',
                         'provide__notify__agree__branch__name',
                         'provide__notify__agree__branch__short_name',
                         'provide__notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        track_soondue = track_soondue.filter(q)

    '''分页'''
    paginator = Paginator(track_soondue, 119)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-track-overdu.html', locals())
