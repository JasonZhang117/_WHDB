from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
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
                         'branch__name', 'lending__summary__summary_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        agree_list = agree_list.filter(q)
    '''分页'''
    paginator = Paginator(agree_list, 20)
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
    PAGE_TITLE = '放款管理'
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


# -----------------------------合同签订ajax------------------------------#
@login_required
def counter_sign_ajax(request):
    print(__file__, '---->def counter_sign_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    counter_list = models.Counters.objects.filter(id=post_data['counter_id'])
    counter_obj = counter_list.first()
    print('counter_list:', counter_list)
    from_counter_sign = forms.FormCounterSignAdd(post_data)

    if from_counter_sign.is_valid():
        counter_sign_cleaned = from_counter_sign.cleaned_data
        print('counter_sign_cleaned:', counter_sign_cleaned)
        '''COUNTER_STATE_LIST = ((11, '未签订'), (21, '已签订'), (31, '已作废'))'''
        if counter_obj.counter_state in [31]:
            response['status'] = False
            response['message'] = '合同状态为（%s），签订失败' % counter_obj.counter_state
        else:
            try:
                counter_list.update(
                    counter_state=counter_sign_cleaned['counter_state'],
                    counter_sign_date=counter_sign_cleaned['counter_sign_date'],
                    counter_remark=counter_sign_cleaned['counter_remark'])
                response['message'] = '合同签订成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '合同签订成功：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = from_counter_sign.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------风控落实ajax------------------------------#
@login_required
def ascertain_add_ajax(request):
    print(__file__, '---->def ascertain_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    agree_list = models.Agrees.objects.filter(id=post_data['agree_id'])
    agree_obj = agree_list.first()
    print('agree_obj:', agree_obj)
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    form_ascertain_add = forms.FormAscertainAdd(post_data)
    if form_ascertain_add.is_valid():
        ascertain_cleaned = form_ascertain_add.cleaned_data
        agree_state = ascertain_cleaned['agree_state']
        agree_remark = ascertain_cleaned['agree_remark']
        '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                    (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
        agree_state_y = agree_obj.agree_state
        if agree_state_y in [21, 31, 51]:
            try:
                today_str = time.strftime("%Y-%m-%d", time.gmtime())
                agree_list.update(
                    agree_state=agree_state, ascertain_date=today_str, agree_remark=agree_remark)
                response['message'] = '风控落实手续办理成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '风控落实手续办理失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '合同状态为：%s，风控落实失败!!!' % agree_state_y
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_ascertain_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------添加放款通知ajax------------------------------#
@login_required
def notify_add_ajax(request):
    print(__file__, '---->def notify_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    agree_list = models.Agrees.objects.filter(id=post_data['agree_id'])
    agree_obj = agree_list.first()
    form_notify_add = forms.FormNotifyAdd(post_data)
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    agree_state = agree_obj.agree_state
    if agree_state in [31, 41]:
        if form_notify_add.is_valid():
            form_notify_cleaned = form_notify_add.cleaned_data
            notify_money = form_notify_cleaned['notify_money']
            notify_amount = models.Notify.objects.filter(agree=agree_obj).aggregate(Sum('notify_money'))
            notify_money_sum = notify_amount['notify_money__sum']
            if notify_money_sum:
                amount = notify_money_sum + notify_money
            else:
                amount = notify_money
            if amount > agree_obj.agree_amount:
                response['status'] = False
                response['message'] = '放款通知金额合计（%s）大于合同金额（%s）' % (amount, agree_obj.agree_amount)
            else:
                try:
                    with transaction.atomic():
                        notify_obj = models.Notify.objects.create(
                            agree=agree_obj, notify_money=notify_money, notify_date=form_notify_cleaned['notify_date'],
                            contracts_lease=form_notify_cleaned['contracts_lease'],
                            contract_guaranty=form_notify_cleaned['contract_guaranty'],
                            remark=form_notify_cleaned['remark'], notifyor=request.user)
                        agree_list.update(agree_notify_sum=amount)
                    response['message'] = '成功添加放款通知！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '放款通知添加失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_notify_add.errors
    else:
        response['status'] = False
        response['message'] = '委托合同状态为:%s,添加放款通知失败！！！' % agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除放款通知ajax-------------------------#
@login_required
def notify_del_ajax(request):  # 反担保人删除ajax
    print(__file__, '---->def notify_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    notify_id = post_data['notify_id']
    notify_obj = models.Notify.objects.get(id=notify_id)
    provide_notify_list = notify_obj.provide_notify.all()

    if provide_notify_list:
        response['status'] = False
        response['message'] = '该放款通知已经放款，删除失败！！！'
    else:
        try:
            with transaction.atomic():
                models.Agrees.objects.filter(notify_agree=notify_obj).update(
                    agree_notify_sum=F('agree_notify_sum') - notify_obj.notify_money)
                notify_obj.delete()
            response['message'] = '放款通知删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '放款通知删除失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------添加放款ajax------------------------------#
@login_required
def provide_add_ajax(request):
    print(__file__, '---->def provide_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    notify_list = models.Notify.objects.filter(id=post_data['notify_id'])
    notify_obj = notify_list.first()
    print('notify_obj:', notify_obj)
    form_provide_add = forms.FormProvideAdd(post_data)

    if form_provide_add.is_valid():
        form_provide_cleaned = form_provide_add.cleaned_data

        provide_money = form_provide_cleaned['provide_money']
        provide_amount = models.Provides.objects.filter(notify=notify_obj).aggregate(Sum('provide_money'))
        provide_money_sum = provide_amount['provide_money__sum']
        if provide_money_sum:
            amount = round(provide_money_sum + provide_money, 2)
        else:
            amount = provide_money
        if amount > notify_obj.notify_money:
            response['status'] = False
            response['message'] = '放款金额合计（%s）大于放款通知金额（%s）' % (amount, notify_obj.notify_money)
        else:
            try:
                with transaction.atomic():
                    provide_obj = models.Provides.objects.create(
                        notify=notify_obj, provide_typ=form_provide_cleaned['provide_typ'],
                        provide_money=provide_money, provide_date=form_provide_cleaned['provide_date'],
                        due_date=form_provide_cleaned['due_date'], providor=request.user)
                    '''notify_provide_sum，更新放款通知放款情况'''
                    notify_list.update(notify_provide_sum=amount)  # 放款通知，更新放款总额
                    '''agree_provide_sum，更新合同放款信息'''
                    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                    agree_obj = agree_list.first()
                    agree_provide_amount = models.Provides.objects.filter(
                        notify__agree=agree_obj).aggregate(Sum('provide_money'))['provide_money__sum']  # 合同项下放款合计
                    print('agree_provide_amount:', agree_provide_amount)
                    agree_list.update(agree_provide_sum=round(agree_provide_amount, 2))  # 合同，更新放款总额
                    '''lending_provide_sum，更新放款次序还款信息'''
                    lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                    lending_obj = lending_list.first()
                    lending_provide_amount = models.Provides.objects.filter(
                        notify__agree__lending=lending_obj).aggregate(Sum('provide_money'))['provide_money__sum']
                    print('lending_provide_amount:', lending_provide_amount)
                    lending_list.update(lending_provide_sum=round(lending_provide_amount, 2))  # 放款次序，更新放款总额
                    '''article_provide_sum，更新项目放款信息'''
                    article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                    article_obj = article_list.first()
                    article_provide_amount = models.Provides.objects.filter(
                        notify__agree__lending__summary=article_obj).aggregate(
                        Sum('provide_money'))['provide_money__sum']
                    print('article_provide_amount:', article_provide_amount)
                    article_list.update(article_provide_sum=round(article_provide_amount, 2))  # 项目，更新放款总额
                    '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                    custom_list = models.Customes.objects.filter(article_custom=article_obj)
                    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                    provide_typ = provide_obj.provide_typ
                    '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
                    if provide_typ == 1:
                        custom_list.update(custom_flow=F('custom_flow') + provide_money)  # 客户，更新流贷余额
                        branch_list.update(branch_flow=F('branch_flow') + provide_money)  # 放款银行，更新流贷余额
                    elif provide_typ == 11:
                        custom_list.update(custom_accept=F('custom_accept') + provide_money)  # 客户，更新承兑余额
                        branch_list.update(branch_accept=F('branch_accept') + provide_money)  # 放款银行，更新承兑余额
                    else:
                        custom_list.update(custom_back=F('custom_back') + provide_money)  # 客户，更新保函余额
                        branch_list.update(branch_back=F('branch_back') + provide_money)  # 放款银行，更新保函余额

                response['message'] = '成功添加放款通知！'
            except Exception as e:
                response['status'] = False
                response['message'] = '放款通知添加失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_provide_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除放款ajax-------------------------#
@login_required
def provide_del_ajax(request):  # 删除放款ajax
    print(__file__, '---->def provide_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    print('provide_obj:', provide_obj)

    '''PROVIDE_STATUS_LIST = ((1, '在保'), (11, '解保'), (21, '代偿'))'''
    try:
        with transaction.atomic():
            provide_m = provide_obj.provide_money
            provide_obj.delete()  # 删除放款信息
            '''notify_provide_sum，更新放款通知放款信息'''
            notify_list = models.Notify.objects.filter(id=post_data['notify_id'])
            notify_obj = notify_list.first()
            print('notify_obj:', notify_obj)
            notify_provide_amount = models.Provides.objects.filter(notify=notify_obj).aggregate(
                Sum('provide_money'))['provide_money__sum']  # 通知项下放款合计
            if notify_provide_amount:
                print('notify_provide_amount:', notify_provide_amount)
                notify_list.update(notify_provide_sum=round(notify_provide_amount, 2))  # 放款通知，更新放款总额
            else:
                notify_list.update(notify_provide_sum=0)  # 放款通知，更新放款总额
            '''agree_provide_sum，更新合同放款信息'''
            agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
            agree_obj = agree_list.first()
            agree_provide_amount = models.Provides.objects.filter(
                notify__agree=agree_obj).aggregate(Sum('provide_money'))['provide_money__sum']  # 合同项下放款合计
            print('agree_provide_amount:', agree_provide_amount)
            if agree_provide_amount:
                print('agree_provide_amount:', agree_provide_amount)
                agree_list.update(agree_provide_sum=round(agree_provide_amount, 2))  # 合同，更新放款总额
            else:
                agree_list.update(agree_provide_sum=0)  # 合同，更新放款总额
            '''lending_provide_sum，更新放款次序放款信息'''
            lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
            lending_obj = lending_list.first()
            lending_provide_amount = models.Provides.objects.filter(
                notify__agree__lending=lending_obj).aggregate(Sum('provide_money'))['provide_money__sum']
            print('lending_provide_amount:', lending_provide_amount)
            if lending_provide_amount:
                print('lending_repayment_amount:', lending_provide_amount)
                lending_list.update(lending_provide_sum=round(lending_provide_amount, 2))  # 放款次序，更新放款总额
            else:
                lending_list.update(lending_provide_sum=0)  # 放款次序，更新放款总额
            '''article_provide_sum，更新项目放款信息'''
            article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
            article_obj = article_list.first()
            article_provide_amount = models.Provides.objects.filter(
                notify__agree__lending__summary=article_obj).aggregate(Sum('provide_money'))['provide_money__sum']
            print('article_provide_amount:', article_provide_amount)
            if article_provide_amount:
                print('article_provide_amount:', article_provide_amount)
                article_list.update(article_provide_sum=round(article_provide_amount, 2))  # 项目，更新放款总额
            else:
                article_list.update(article_provide_sum=0)  # 项目，更新放款总额
            '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
            '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
            custom_list = models.Customes.objects.filter(article_custom=article_obj)
            branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
            provide_typ = provide_obj.provide_typ
            if provide_typ == 1:
                custom_list.update(custom_flow=F('custom_flow') - provide_m)  # 客户，更新流贷余额
                branch_list.update(branch_flow=F('branch_flow') - provide_m)  # 放款银行，更新流贷余额
            elif provide_typ == 11:
                custom_list.update(custom_accept=F('custom_accept') - provide_m)  # 客户，更新承兑余额
                branch_list.update(branch_accept=F('branch_accept') - provide_m)  # 放款银行，更新承兑余额
            else:
                custom_list.update(custom_back=F('custom_back') - provide_m)  # 客户，更新保函余额
                branch_list.update(branch_back=F('branch_back') - provide_m)  # 放款银行，更新保函余额
        response['message'] = '借款信息删除成功！'
    except Exception as e:
        response['status'] = False
        response['message'] = '还款信息删除失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------添加还款ajax------------------------------#
@login_required
def repayment_add_ajax(request):
    print(__file__, '---->def repayment_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    form_repayment_add = forms.FormRepaymentAdd(post_data)

    if form_repayment_add.is_valid():
        repayment_cleaned = form_repayment_add.cleaned_data
        repayment_money = repayment_cleaned['repayment_money']
        repayment_amount = models.Repayments.objects.filter(provide=provide_obj).aggregate(Sum('repayment_money'))
        repayment_money_sum = repayment_amount['repayment_money__sum']
        if repayment_money_sum:
            amount = round(repayment_money_sum + repayment_money, 2)
        else:
            amount = repayment_money
        if amount > provide_obj.provide_money:
            response['status'] = False
            response['message'] = '还款金额合计（%s）大于放款金额（%s）' % (amount, provide_obj.provide_money)
        else:
            try:
                with transaction.atomic():
                    repayment_obj = models.Repayments.objects.create(
                        provide=provide_obj, repayment_money=repayment_money, repaymentor=request.user,
                        repayment_date=repayment_cleaned['repayment_date'])  # 创建还款记录

                    '''provide_repayment_sum，更新放款通知还款情况'''
                    provide_list.update(provide_repayment_sum=amount)  # 放款，更新还款总额
                    '''notify_repayment_sum，更新放款通知还款情况'''
                    notify_list = models.Notify.objects.filter(provide_notify=provide_obj)  # 放款通知
                    print('notify_list:', notify_list)
                    notify_obj = notify_list.first()
                    notify_repayment_amount = models.Repayments.objects.filter(provide__notify=notify_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
                    print('notify_repayment_amount:', notify_repayment_amount)
                    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2))  # 放款通知，更新还款总额
                    '''agree_repayment_sum，更新合同还款信息'''
                    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                    agree_obj = agree_list.first()
                    agree_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree=agree_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
                    print('agree_repayment_amount:', agree_repayment_amount)
                    agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2))  # 合同，更新还款总额
                    '''lending_repayment_sum，更新放款次序还款信息'''
                    lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                    lending_obj = lending_list.first()
                    lending_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree__lending=lending_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']
                    print('lending_repayment_amount:', lending_repayment_amount)
                    lending_list.update(lending_repayment_sum=round(lending_repayment_amount, 2))  # 放款次序，更新还款总额
                    '''article_repayment_sum，更新项目还款信息'''
                    article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                    article_obj = article_list.first()
                    article_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree__lending__summary=article_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']
                    print('article_repayment_amount:', article_repayment_amount)
                    article_list.update(article_repayment_sum=round(article_repayment_amount, 2))  # 项目，更新还款总额
                    '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                    custom_list = models.Customes.objects.filter(article_custom=article_obj)
                    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                    provide_typ = provide_obj.provide_typ
                    if provide_typ == 1:
                        custom_list.update(custom_flow=F('custom_flow') - repayment_money)  # 客户，更新流贷余额
                        branch_list.update(branch_flow=F('branch_flow') - repayment_money)  # 放款银行，更新流贷余额
                    elif provide_typ == 11:
                        custom_list.update(custom_accept=F('custom_accept') - repayment_money)  # 客户，更新承兑余额
                        branch_list.update(branch_accept=F('branch_accept') - repayment_money)  # 放款银行，更新承兑余额
                    else:
                        custom_list.update(custom_back=F('custom_back') - repayment_money)  # 客户，更新保函余额
                        branch_list.update(branch_back=F('branch_back') - repayment_money)  # 放款银行，更新保函余额

                    if provide_obj.provide_money == provide_obj.provide_repayment_sum:  # 放款金额=还款金额合计
                        provide_list.update(provide_status=11)  # 放款解保
                        response['message'] = '成功还款,本次放款已全部结清！'
                    else:
                        response['message'] = '成功还款！'

            except Exception as e:
                response['status'] = False
                response['message'] = '还款失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_repayment_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除还款信息ajax-------------------------#
@login_required
def repayment_del_ajax(request):  # 删除还款信息ajax
    print(__file__, '---->def repayment_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    provide_id = post_data['provide_id']
    provide_list = models.Provides.objects.filter(id=provide_id)
    provide_obj = provide_list.first()
    repayment_id = post_data['repayment_id']
    repayment_obj = models.Repayments.objects.get(id=repayment_id)
    '''PROVIDE_STATUS_LIST = ((1, '在保'), (11, '解保'), (21, '代偿'))'''
    if provide_obj.provide_status == 1:
        try:
            with transaction.atomic():
                repayment_m = repayment_obj.repayment_money
                repayment_obj.delete()  # 删除还款信息
                '''provide_repayment_sum，更新放款记录还款情况'''
                provide_repayment_amount = models.Repayments.objects.filter(provide=provide_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']  # 放款项下还款合计
                if provide_repayment_amount:
                    print('provide_repayment_amount:', provide_repayment_amount)
                    provide_list.update(provide_repayment_sum=round(provide_repayment_amount, 2))  # 放款，更新还款总额
                else:
                    provide_list.update(provide_repayment_sum=0)  # 放款，更新还款总额
                '''notify_repayment_sum，更新放款通知还款情况'''
                notify_list = models.Notify.objects.filter(provide_notify=provide_obj)  # 放款通知
                print('notify_list:', notify_list)
                notify_obj = notify_list.first()
                notify_repayment_amount = models.Repayments.objects.filter(provide__notify=notify_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
                if notify_repayment_amount:
                    print('notify_repayment_amount:', notify_repayment_amount)
                    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2))  # 放款通知，更新还款总额
                else:
                    notify_list.update(notify_repayment_sum=0)  # 放款通知，更新还款总额
                '''agree_repayment_sum，更新合同还款信息'''
                agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                agree_obj = agree_list.first()
                agree_repayment_amount = models.Repayments.objects.filter(provide__notify__agree=agree_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
                if agree_repayment_amount:
                    print('agree_repayment_amount:', agree_repayment_amount)
                    agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2))  # 合同，更新还款总额
                else:
                    agree_list.update(agree_repayment_sum=0)  # 合同，更新还款总额
                '''lending_repayment_sum，更新放款次序还款信息'''
                lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                lending_obj = lending_list.first()
                lending_repayment_amount = models.Repayments.objects.filter(
                    provide__notify__agree__lending=lending_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']
                if lending_repayment_amount:
                    print('lending_repayment_amount:', lending_repayment_amount)
                    lending_list.update(lending_repayment_sum=round(lending_repayment_amount, 2))  # 放款次序，更新还款总额
                else:
                    lending_list.update(lending_repayment_sum=0)  # 放款次序，更新还款总额
                '''article_repayment_sum，更新项目还款信息'''
                article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                article_obj = article_list.first()
                article_repayment_amount = models.Repayments.objects.filter(
                    provide__notify__agree__lending__summary=article_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']
                if article_repayment_amount:
                    print('article_repayment_amount:', article_repayment_amount)
                    article_list.update(article_repayment_sum=round(article_repayment_amount, 2))  # 项目，更新还款总额
                else:
                    article_list.update(article_repayment_sum=0)  # 项目，更新还款总额
                '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                custom_list = models.Customes.objects.filter(article_custom=article_obj)
                branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                provide_typ = provide_obj.provide_typ
                if provide_typ == 1:
                    custom_list.update(custom_flow=F('custom_flow') + repayment_m)  # 客户，更新流贷余额
                    branch_list.update(branch_flow=F('branch_flow') + repayment_m)  # 放款银行，更新流贷余额
                elif provide_typ == 11:
                    custom_list.update(custom_accept=F('custom_accept') + repayment_m)  # 客户，更新承兑余额
                    branch_list.update(branch_accept=F('branch_accept') + repayment_m)  # 放款银行，更新承兑余额
                else:
                    custom_list.update(custom_back=F('custom_back') + repayment_m)  # 客户，更新保函余额
                    branch_list.update(branch_back=F('branch_back') + repayment_m)  # 放款银行，更新保函余额

            response['message'] = '还款信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '还款信息删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '该笔放款状态为：%s，还款信息删除失败！！！' % provide_obj.provide_status
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


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
        search_fields = ['notify__agree__lending__summary__custom__name', 'notify__agree__branch__name',
                         'notify__agree__agree_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        provide_list = provide_list.filter(q)
    '''分页'''
    paginator = Paginator(provide_list, 18)
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
    return render(request, 'dbms/provide/provide-scan.html', locals())
