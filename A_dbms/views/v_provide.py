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
    PAGE_TITLE = '放款管理'

    agree_state_list = models.Agrees.AGREE_STATE_LIST
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '已落实，未放款'), (41, '已落实，放款'),
                        (42, '未落实，放款'), (51, '待变更'), (61, '已解保'), (99, '已作废'))'''
    agree_list = models.Agrees.objects.filter(**kwargs).filter(agree_state__in=[21, 31, 41, 42]).select_related(
        'lending', 'branch').order_by('-agree_num')

    ####分页信息###
    paginator = Paginator(agree_list, 10)
    page = request.GET.get('page')
    try:
        p_agree_list = paginator.page(page)
    except PageNotAnInteger:
        p_agree_list = paginator.page(1)
    except EmptyPage:
        p_agree_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide-agree.html', locals())


# -----------------------------查看放款通知------------------------------#
@login_required
def provide_agree_scan(request, agree_id):  # 查看放款
    print(__file__, '---->def provide_agree_scan')
    PAGE_TITLE = '放款管理'
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    COUNTER_TYP_CUSTOM = [1, 2]
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
    sure_list = [1, 2]  # 保证反担保类型
    house_list = [11, 21, 42, 52]
    ground_list = [12, 22, 43, 53]
    receivable_list = [31]
    stock_list = [32]

    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending

    form_notify_add = forms.FormNotifyAdd()

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
    COUNTER_TYP_CUSTOM = [1, 2]
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
    sure_list = [1, 2]  # 保证反担保类型
    house_list = [11, 21, 42, 52]
    ground_list = [12, 22, 43, 53]
    receivable_list = [31]
    stock_list = [32]

    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    notify_obj = models.Notify.objects.get(id=notify_id)

    form_provide_add = forms.FormProvideAdd()

    return render(request, 'dbms/provide/provide-agree-notify.html', locals())


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
            amount = provide_money_sum + provide_money
        else:
            amount = provide_money
        if amount > notify_obj.notify_money:
            response['status'] = False
            response['message'] = '放款金额合计（%s）大于放款通知金额（%s）' % (amount, notify_obj.notify_money)
        else:
            agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)
            try:
                with transaction.atomic():
                    provide_obj = models.Provides.objects.create(
                        notify=notify_obj, provide_typ=form_provide_cleaned['provide_typ'],
                        provide_money=provide_money, provide_date=form_provide_cleaned['provide_date'],
                        due_date=form_provide_cleaned['due_date'], providor=request.user)
                    '''更新放款总额'''
                    models.Customes.objects.filter().update()  # 客户
                    models.Branches.objects.filter().update()  # 放款银行
                    models.Articles.objects.filter().update()  # 项目
                    models.LendingOrder.objects.filter().update()  # 放款次序
                    agree_list.update(agree_provide_sum=F('agree_provide_sum') + provide_money)  # 合同
                    notify_list.update(notify_provide_sum=amount)  # 放款通知

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

    provide_id = post_data['provide_id']
    provide_obj = models.Provides.objects.get(id=provide_id)
    repayment_id = post_data['repayment_id']
    repayment_obj = models.Repayments.objects.get(id=repayment_id)
    '''PROVIDE_STATUS_LIST = ((1, '在保'), (11, '解保'), (21, '代偿'))'''
    if provide_obj.provide_status == 1:
        try:
            with transaction.atomic():
                models.Customes.objects.filter().update()  # 客户
                models.Branches.objects.filter().update()  # 放款银行
                models.Articles.objects.filter().update()  # 项目
                models.LendingOrder.objects.filter().update()  # 放款次序
                models.Agrees.objects.filter().update()  # 合同
                models.Notify.objects.filter().update()  # 放款通知
                models.Provides.objects.filter().update()  # 放款
                repayment_obj.delete()  # 删除还款信息
            response['message'] = '还款信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '还款信息删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '该笔放款状态为：%s，还款信息删除失败！！！' % provide_obj.provide_status
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
            amount = repayment_money_sum + repayment_money
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
                    models.Customes.objects.filter().update()  # 客户
                    models.Branches.objects.filter().update()  # 放款银行
                    models.Articles.objects.filter().update()  # 项目
                    models.LendingOrder.objects.filter().update()  # 放款次序
                    models.Agrees.objects.filter().update()  # 合同
                    models.Notify.objects.filter().update()  # 放款通知
                    provide_list.update(provide_repayment_sum=amount)  # 放款，更新还款总额

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
    provide_obj = models.Provides.objects.get(id=provide_id)
    repayment_id = post_data['repayment_id']
    repayment_obj = models.Repayments.objects.get(id=repayment_id)
    '''PROVIDE_STATUS_LIST = ((1, '在保'), (11, '解保'), (21, '代偿'))'''
    if provide_obj.provide_status == 1:
        try:
            with transaction.atomic():
                models.Customes.objects.filter().update()  # 客户
                models.Branches.objects.filter().update()  # 放款银行
                models.Articles.objects.filter().update()  # 项目
                models.LendingOrder.objects.filter().update()  # 放款次序
                models.Agrees.objects.filter().update()  # 合同
                models.Notify.objects.filter().update()  # 放款通知
                models.Provides.objects.filter().update()  # 放款
                repayment_obj.delete()  # 删除还款信息
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

    provide_status_list = models.Provides.PROVIDE_STATUS_LIST
    provide_list = models.Provides.objects.filter(**kwargs).select_related('notify').order_by('-id')

    ####分页信息###
    paginator = Paginator(provide_list, 20)
    page = request.GET.get('page')
    try:
        provide_p_list = paginator.page(page)
    except PageNotAnInteger:
        provide_p_list = paginator.page(1)
    except EmptyPage:
        provide_p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/provide/provide.html', locals())


# -----------------------------查看放款------------------------------#
@login_required
def provide_scan(request, provide_id):  # 查看放款
    print(__file__, '---->def provide_scan')
    PAGE_TITLE = '放款详情'

    provide_obj = models.Provides.objects.get(id=provide_id)

    form_repayment_add = forms.FormRepaymentAdd()

    return render(request, 'dbms/provide/provide-scan.html', locals())
