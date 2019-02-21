from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count


# -----------------------放款管理---------------------#
@login_required
def provide_agree(request, *args, **kwargs):  # 放款管理
    print(__file__, '---->def provide_agree')
    PAGE_TITLE = '风控落实'
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).select_related('lending', 'branch').order_by('-agree_num')
    agree_list = agree_list.filter(agree_state__in=[21, 31, 41, 51], lending__summary__article_state__in=[5, 51, 61])
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

    provide_amount = agree_list.aggregate(Sum('agree_provide_sum'))['agree_provide_sum__sum']  # 放款金额合计
    repayment_amount = agree_list.aggregate(
        Sum('agree_repayment_sum'))['agree_repayment_sum__sum']  # 还款金额合计
    if provide_amount:
        provide_amount = provide_amount
    else:
        provide_amount = 0

    if repayment_amount:
        repayment_amount = repayment_amount
    else:
        repayment_amount = 0
    balance = provide_amount - repayment_amount

    agree_amount = agree_list.count()  # 信息数目
    '''分页'''
    paginator = Paginator(agree_list, 18)
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
def provide_agree_scan(request, agree_id):  # 查看放款
    print(__file__, '---->def provide_agree_scan')
    PAGE_TITLE = '风控落实'
    response = {'status': True, 'message': None, 'forme': None, }

    COUNTER_TYP_CUSTOM = [1, 2]

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

    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    warrant_storage_str = ''  # 未入库权证
    warrant_ypothec_str = ''  # 缺他权
    ypothec_storage_str = ''  # 他权未入库
    ascertain_str = ''  # 未落实情况
    agree_str = ''
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    agree_state_n = 41
    agree_lending_sure_list = agree_obj.lending.sure_lending.all()  # 反担保措施列表'LendingSures'
    for sure in agree_lending_sure_list:
        '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
        if sure.sure_typ not in [1, 2]:  # (1, '企业保证'), (2, '个人保证')
            sure_warrant = sure.warrant_sure.warrant.all()
            for warrant in sure_warrant:
                ypothec_list = warrant.ypothec_m_agree.all().filter(agree=agree_obj).distinct()
                '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
         (99, '已注销'))'''
                if warrant.warrant_state in [1, 11, 21]:  # (1, '未入库'), (11, '续抵出库'), (21, '已借出')
                    warrant_storage_str += '%s，' % warrant.warrant_num  # 待入库
                '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
                if not ypothec_list:  # 票据无需他权
                    warrant_ypothec_str += '%s，' % warrant.warrant_num  # 无他权
                else:
                    for ypothec in ypothec_list:
                        warrant_state = ypothec.warrant.warrant_state
                        # (1, '未入库'), (11, '续抵出库'), (21, '已借出')
                        if warrant_state in [1, 11, 21] and not warrant.warrant_typ == 31:
                            ypothec_storage_str += '%s，' % ypothec.warrant.warrant_num  # 他权未入库

    counter_list = agree_obj.counter_agree.all()
    counter_agree_str = ''
    for counter in counter_list:
        '''COUNTER_STATE_LIST = ((11, '未签订'), (21, '已签订'), (31, '作废'))'''
        if counter.counter_state == 11:
            counter_agree_str += '%s，' % counter.counter_num  # 合同未签订
    print('warrant_ypothec_str:', warrant_ypothec_str)
    print('warrant_storage_str:', warrant_storage_str)
    print('ypothec_storage_str:', ypothec_storage_str)
    print('counter_agree_str:', counter_agree_str)

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
    print('ascertain_str:', ascertain_str)
    if agree_state_n == 41:
        agree_str = '所有风控措施已落实，可以出具放款通知！'
    else:
        agree_str = '以下风控措施未落实：\r\n' + ascertain_str + '如确定后可以放款，请后续持续跟进，否者点击取消！'
    print('agree_str:', agree_str)

    form_notify_add = forms.FormNotifyAdd()  # 添加放款通知
    form_ascertain_add = forms.FormAscertainAdd()  # 风控落实
    from_counter_sign = forms.FormCounterSignAdd()  # 反担保合同签订
    print('form_notify_add:', form_notify_add)
    return render(request, 'dbms/provide/provide-agree-scan.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
def provide_agree_notify(request, agree_id, notify_id):  # 查看放款通知
    print(__file__, '---->def provide_agree_notify')
    PAGE_TITLE = '放款通知'
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''SURE_TYP_LIST = (
                    (1, '企业保证'), (2, '个人保证'),
                    (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
                    (21, '房产顺位'), (22, '土地顺位'),
                    (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
                    (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
                    (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''WARRANT_TYP_LIST = [
           (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
           (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    COUNTER_TYP_CUSTOM = [1, 2]
    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32]
    CHATTEL_LIST = [13]

    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    notify_obj = models.Notify.objects.get(id=notify_id)

    form_provide_add = forms.FormProvideAdd()
    print('form_provide_add:', form_provide_add)

    return render(request, 'dbms/provide/provide-agree-notify.html', locals())


# -----------------------放款列表---------------------#
@login_required
def provide(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def provide')
    PAGE_TITLE = '放款管理'
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    PROVIDE_STATUS_LIST = models.Provides.PROVIDE_STATUS_LIST  # 筛选条件
    '''筛选'''
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-provide_date')

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
        provide_list = provide_list.filter(q)

    provide_amount = provide_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额合计
    repayment_amount = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  # 还款金额合计
    if provide_amount:
        provide_amount = provide_amount
    else:
        provide_amount = 0

    if repayment_amount:
        repayment_amount = repayment_amount
    else:
        repayment_amount = 0
    balance = provide_amount - repayment_amount

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
def provide_scan(request, provide_id):  # 查看放款
    print(__file__, '---->def provide_scan')
    PAGE_TITLE = '放款详情'

    provide_obj = models.Provides.objects.get(id=provide_id)

    form_repayment_add = forms.FormRepaymentAdd()
    form_compensatory_add = forms.FormCompensatoryAdd()
    return render(request, 'dbms/provide/provide-scan.html', locals())


# -----------------------逾期列表---------------------#
@login_required
def overdue(request, *args, **kwargs):  # 逾期列表
    print(__file__, '---->def provide')
    PAGE_TITLE = '逾期项目'
    overdue_list = models.Provides.objects.filter(
        provide_status=1, due_date__lt=datetime.date.today()).order_by('due_date')  # 逾期
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

    provide_amount = overdue_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额合计
    repayment_amount = overdue_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  # 还款金额合计
    if provide_amount:
        provide_amount = provide_amount
    else:
        provide_amount = 0

    if repayment_amount:
        repayment_amount = repayment_amount
    else:
        repayment_amount = 0
    balance = provide_amount - repayment_amount

    provide_acount = overdue_list.count()
    '''分页'''
    paginator = Paginator(overdue_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/overdu.html', locals())


# -----------------------即将到期列表---------------------#
@login_required
def soondue(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def provide')
    PAGE_TITLE = '即将到期（含逾期）'
    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    soondue_list = models.Provides.objects.filter(
        provide_status=1, due_date__lte=date_th_later).order_by('due_date')  # 30天内到期
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

    provide_amount = soondue_list.aggregate(Sum('provide_money'))['provide_money__sum']  # 放款金额合计
    repayment_amount = soondue_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  # 还款金额合计
    if provide_amount:
        provide_amount = provide_amount
    else:
        provide_amount = 0

    if repayment_amount:
        repayment_amount = repayment_amount
    else:
        repayment_amount = 0
    balance = provide_amount - repayment_amount

    provide_acount = soondue_list.count()
    '''分页'''
    paginator = Paginator(soondue_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/overdu.html', locals())
