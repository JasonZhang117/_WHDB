from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------------合同签订ajax------------------------------#
@login_required
@authority
def counter_sign_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def ascertain_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def notify_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
            agree_term = agree_obj.agree_term  # 合同期限
            form_notify_cleaned = form_notify_add.cleaned_data
            time_limit = form_notify_cleaned['time_limit']  # 通知期限
            if time_limit > agree_term:
                response['status'] = False
                response['message'] = '通知期限（%s个月）大于合同期限（%s个月），放款通知添加失败！'
            else:
                notify_money = form_notify_cleaned['notify_money']  # 通知金额
                weighting_money = round((time_limit / agree_term) * notify_money, 2)  # 时间加权通知金额
                weighting_amount = models.Notify.objects.filter(agree=agree_obj).aggregate(Sum('weighting'))
                weighting_money_sum = weighting_amount['weighting__sum']  # 时间加权通知金额合计（已有）
                if weighting_money_sum:
                    amount = weighting_money_sum + weighting_money  # 时间加权通知金额合计（含当前）
                else:
                    amount = weighting_money  # 时间加权通知金额合计（含当前）
                amount_limit = agree_obj.amount_limit  # 合同放款限额
                '''合同项下放款合计'''
                agree_provide_amount = models.Provides.objects.filter(
                    notify__agree=agree_obj).aggregate(Sum('provide_money'))['provide_money__sum']
                if agree_provide_amount:
                    agree_provide_amount = agree_provide_amount
                else:
                    agree_provide_amount = 0
                '''#合同项下还款合计'''
                agree_repayment_amount = models.Repayments.objects.filter(
                    provide__notify__agree=agree_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']
                if agree_repayment_amount:
                    agree_repayment_amount = agree_repayment_amount
                else:
                    agree_repayment_amount = 0

                agree_balance = agree_provide_amount - agree_repayment_amount
                agree_balance_notify = agree_balance + notify_money
                if amount > amount_limit:
                    response['status'] = False
                    response['message'] = '加权放款通知金额合计（%s）大于合同放款限额（%s）' % (amount, amount_limit)
                elif agree_balance_notify > amount_limit:
                    response['status'] = False
                    response['message'] = '担保余额与通知金额合计（%s）大于合同放款限额（%s）' % (agree_balance_notify, amount_limit)
                else:
                    try:
                        with transaction.atomic():
                            notify_obj = models.Notify.objects.create(
                                agree=agree_obj, notify_money=notify_money, time_limit=time_limit,
                                weighting=weighting_money, notify_date=form_notify_cleaned['notify_date'],
                                contracts_lease=form_notify_cleaned['contracts_lease'],
                                contract_guaranty=form_notify_cleaned['contract_guaranty'],
                                remark=form_notify_cleaned['remark'], notifyor=request.user)
                            '''agree_notify_sum，更新合同加权通知总额'''
                            agree_list.update(agree_notify_sum=amount)
                            '''article_notify_sum，更新项目加权通知总额'''
                            article_list = models.Articles.objects.filter(
                                lending_summary__agree_lending=agree_obj)  # 项目
                            article_obj = article_list.first()
                            article_notify_amount = models.Notify.objects.filter(
                                agree__lending__summary=article_obj).aggregate(
                                Sum('weighting'))['weighting__sum']
                            print('article_notify_amount:', article_notify_amount)
                            article_list.update(article_notify_sum=round(article_notify_amount, 2))

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
@authority
def notify_del_ajax(request):  # 反担保人删除ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
                models.Articles.objects.filter(
                    lending_summary__agree_lending__notify_agree=notify_obj).update(
                    article_notify_sum=F('article_notify_sum') - notify_obj.notify_money)  # 项目
                notify_obj.delete()
            response['message'] = '放款通知删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '放款通知删除失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------添加放款ajax------------------------------#
@login_required
@authority
def provide_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    notify_list = models.Notify.objects.filter(id=post_data['notify_id'])
    notify_obj = notify_list.first()
    form_provide_add = forms.FormProvideAdd(post_data)

    if form_provide_add.is_valid():
        form_provide_cleaned = form_provide_add.cleaned_data

        provide_money = round(form_provide_cleaned['provide_money'], 2)
        notify_provide_amount = models.Provides.objects.filter(notify=notify_obj).aggregate(Sum('provide_money'))
        notify_provide_sum = notify_provide_amount['provide_money__sum']
        if notify_provide_sum:
            amount = round(notify_provide_sum + provide_money, 2)
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
                        due_date=form_provide_cleaned['due_date'], provide_balance=provide_money,
                        providor=request.user)
                    '''notify_provide_sum，更新放款通知放款情况'''
                    notify_provide_balance = models.Provides.objects.filter(
                        notify=notify_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
                    notify_list.update(notify_provide_sum=amount,
                                       notify_balance=round(notify_provide_balance, 2))  # 放款通知，更新放款总额
                    '''agree_provide_sum，更新合同放款信息'''
                    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                    agree_obj = agree_list.first()
                    agree_provide_amount = models.Provides.objects.filter(
                        notify__agree=agree_obj).aggregate(Sum('provide_money'))['provide_money__sum']  # 合同项下放款合计
                    agree_provide_balance = models.Provides.objects.filter(
                        notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
                    agree_list.update(agree_provide_sum=round(agree_provide_amount, 2),
                                      agree_balance=round(agree_provide_balance, 2))  # 合同，更新放款总额
                    '''lending_provide_sum，更新放款次序还款信息'''
                    lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                    lending_obj = lending_list.first()
                    lending_provide_amount = models.Provides.objects.filter(
                        notify__agree__lending=lending_obj).aggregate(Sum('provide_money'))['provide_money__sum']
                    lending_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending=lending_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
                    lending_list.update(lending_provide_sum=round(lending_provide_amount, 2),
                                        lending_balance=round(lending_provide_balance, 2))  # 放款次序，更新放款总额
                    '''article_provide_sum，更新项目放款信息'''
                    article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                    article_obj = article_list.first()
                    article_provide_amount = models.Provides.objects.filter(
                        notify__agree__lending__summary=article_obj).aggregate(
                        Sum('provide_money'))['provide_money__sum']
                    article_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending__summary=article_obj).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']
                    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                                              (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), 
                                              (99, '已注销'))'''
                    article_weighting_amount = models.Notify.objects.filter(
                        agree__lending__summary=article_obj).aggregate(Sum('weighting'))['weighting__sum']
                    if round(article_weighting_amount, 2) == round(article_obj.amount, 2):
                        article_list.update(article_provide_sum=round(article_provide_amount, 2), article_state=52,
                                            article_balance=round(article_provide_balance, 2))  # 项目，更新放款总额
                    else:
                        article_list.update(article_provide_sum=round(article_provide_amount, 2), article_state=51,
                                            article_balance=round(article_provide_balance, 2))  # 项目，更新放款总额
                    '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                    custom_list = models.Customes.objects.filter(article_custom=article_obj)
                    custom_obj = custom_list.first()
                    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                    branch_obj = branch_list.first()
                    provide_typ = provide_obj.provide_typ
                    '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
                    custom_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending__summary__custom=custom_obj, provide_typ=provide_typ).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
                    branch_provide_balance = models.Provides.objects.filter(
                        notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
                    cooperator_list = models.Cooperators.objects.filter(branch_cooperator=branch_obj)
                    cooperator_obj = cooperator_list.first()
                    if provide_typ == 1:
                        custom_list.update(custom_flow=round(custom_provide_balance, 2))  # 客户，更新流贷余额
                        branch_list.update(branch_flow=round(branch_provide_balance, 2))  # 放款银行，更新流贷余额
                        cooperator_branch_flow_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
                    elif provide_typ == 11:
                        custom_list.update(custom_accept=round(custom_provide_balance, 2))  # 客户，更新承兑余额
                        branch_list.update(branch_accept=round(branch_provide_balance, 2))  # 放款银行，更新承兑余额
                        cooperator_branch_accept_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))

                    else:
                        custom_list.update(custom_back=round(custom_provide_balance, 2))  # 客户，更新保函余额
                        branch_list.update(branch_back=round(branch_provide_balance, 2))  # 放款银行，更新保函余额
                        cooperator_branch_back_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_back'))['branch_back__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))

                response['message'] = '成功放款！'
            except Exception as e:
                response['status'] = False
                response['message'] = '放款添加失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_provide_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除放款ajax-------------------------#
@login_required
@authority
def provide_del_ajax(request):  # 删除放款ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    '''PROVIDE_STATUS_LIST = ((1, '在保'), (11, '解保'), (21, '代偿'))'''
    try:
        with transaction.atomic():
            provide_m = provide_obj.provide_money
            provide_obj.delete()  # 删除放款信息
            '''notify_provide_sum，更新放款通知放款信息'''
            notify_list = models.Notify.objects.filter(id=post_data['notify_id'])
            notify_obj = notify_list.first()
            notify_provide_amount = models.Provides.objects.filter(notify=notify_obj).aggregate(
                Sum('provide_money'))['provide_money__sum']  # 通知项下放款合计
            notify_provide_balance = models.Provides.objects.filter(notify=notify_obj).aggregate(
                Sum('provide_balance'))['provide_balance__sum']
            if notify_provide_amount:
                notify_list.update(notify_provide_sum=round(notify_provide_amount, 2),
                                   notify_balance=round(notify_provide_balance, 2))  # 放款通知，更新放款总额
            else:
                notify_list.update(notify_provide_sum=0, notify_balance=0)  # 放款通知，更新放款总额
            '''agree_provide_sum，更新合同放款信息'''
            agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
            agree_obj = agree_list.first()
            agree_provide_amount = models.Provides.objects.filter(
                notify__agree=agree_obj).aggregate(Sum('provide_money'))['provide_money__sum']  # 合同项下放款合计
            agree_provide_balance = models.Provides.objects.filter(
                notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
            if agree_provide_amount:
                agree_list.update(agree_provide_sum=round(agree_provide_amount, 2),
                                  agree_balance=round(agree_provide_balance, 2))  # 合同，更新放款总额
            else:
                agree_list.update(agree_provide_sum=0, agree_balance=0)  # 合同，更新放款总额
            '''lending_provide_sum，更新放款次序放款信息'''
            lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
            lending_obj = lending_list.first()
            lending_provide_amount = models.Provides.objects.filter(
                notify__agree__lending=lending_obj).aggregate(Sum('provide_money'))['provide_money__sum']
            lending_provide_balance = models.Provides.objects.filter(
                notify__agree__lending=lending_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
            if lending_provide_amount:
                lending_list.update(lending_provide_sum=round(lending_provide_amount, 2),
                                    lending_balance=round(lending_provide_balance, 2))  # 放款次序，更新放款总额
            else:
                lending_list.update(lending_provide_sum=0, lending_balance=0)  # 放款次序，更新放款总额
            '''article_provide_sum，更新项目放款信息'''
            article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
            article_obj = article_list.first()
            article_provide_amount = models.Provides.objects.filter(
                notify__agree__lending__summary=article_obj).aggregate(Sum('provide_money'))['provide_money__sum']
            article_provide_balance = models.Provides.objects.filter(
                notify__agree__lending__summary=article_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
            if article_provide_amount:
                '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
                article_list.update(article_provide_sum=round(article_provide_amount, 2),
                                    article_balance=round(article_provide_balance, 2), article_state=51)  # 项目，更新放款总额
            else:
                article_list.update(article_provide_sum=0, article_balance=0)  # 项目，更新放款总额
            '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
            '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
            custom_list = models.Customes.objects.filter(article_custom=article_obj)
            custom_obj = custom_list.first()
            branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
            branch_obj = branch_list.first()
            provide_typ = provide_obj.provide_typ
            '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
            custom_provide_balance = models.Provides.objects.filter(
                notify__agree__lending__summary__custom=custom_obj, provide_typ=provide_typ).aggregate(
                Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
            branch_provide_balance = models.Provides.objects.filter(
                notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
                Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
            if custom_provide_balance:
                if provide_typ == 1:
                    custom_list.update(custom_flow=custom_provide_balance)  # 客户，更新流贷余额
                elif provide_typ == 11:
                    custom_list.update(custom_accept=custom_provide_balance)  # 客户，更新承兑余额
                else:
                    custom_list.update(custom_back=custom_provide_balance)  # 客户，更新保函余额
            else:
                if provide_typ == 1:
                    custom_list.update(custom_flow=0)  # 客户，更新流贷余额
                elif provide_typ == 11:
                    custom_list.update(custom_accept=0)  # 客户，更新承兑余额
                else:
                    custom_list.update(custom_back=0)  # 客户，更新保函余额
            if branch_provide_balance:
                if provide_typ == 1:
                    branch_list.update(branch_flow=branch_provide_balance)  # 放款银行，更新流贷余额
                elif provide_typ == 11:
                    branch_list.update(branch_accept=branch_provide_balance)  # 放款银行，更新承兑余额
                else:
                    branch_list.update(branch_back=branch_provide_balance)  # 放款银行，更新保函余额
            else:
                if provide_typ == 1:
                    branch_list.update(branch_flow=0)  # 放款银行，更新流贷余额
                elif provide_typ == 11:
                    branch_list.update(branch_accept=0)  # 放款银行，更新承兑余额
                else:
                    branch_list.update(branch_back=0)  # 放款银行，更新保函余额
            '''更新授信银行余额信息,branch_flow,branch_accept,branch_back'''
            cooperator_list = models.Cooperators.objects.filter(branch_cooperator=branch_obj)
            cooperator_obj = cooperator_list.first()
            if provide_typ == 1:
                cooperator_branch_flow_balance = models.Branches.objects.filter(
                    cooperator=cooperator_obj).aggregate(
                    Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
                if cooperator_branch_flow_balance:
                    cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
                else:
                    cooperator_list.update(cooperator_flow=0)
            elif provide_typ == 11:
                cooperator_branch_accept_balance = models.Branches.objects.filter(
                    cooperator=cooperator_obj).aggregate(
                    Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，流贷余额
                if cooperator_branch_accept_balance:
                    cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))
                else:
                    cooperator_list.update(cooperator_accept=0)
            else:
                custom_list.update(custom_back=round(custom_provide_balance, 2))  # 客户，更新保函余额
                branch_list.update(branch_back=round(branch_provide_balance, 2))  # 放款银行，更新保函余额
                cooperator_branch_back_balance = models.Branches.objects.filter(
                    cooperator=cooperator_obj).aggregate(
                    Sum('branch_back'))['branch_back__sum']  # 授信银行项下，流贷余额
                if cooperator_branch_back_balance:
                    cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))
                else:
                    cooperator_list.update(cooperator_back=0)

        response['message'] = '借款信息删除成功！'
    except Exception as e:
        response['status'] = False
        response['message'] = '还款信息删除失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------添加还款ajax------------------------------#
@login_required
@authority
def repayment_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    form_repayment_add = forms.FormRepaymentAdd(post_data)

    if form_repayment_add.is_valid():
        repayment_cleaned = form_repayment_add.cleaned_data
        repayment_money = round(repayment_cleaned['repayment_money'], 2)
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
                    '''provide_repayment_sum，更新放款还款情况'''
                    provide_balance = round(provide_obj.provide_money - amount, 2)  # 在保余额
                    provide_list.update(provide_repayment_sum=amount, provide_balance=provide_balance)  # 放款，更新还款总额，在保余额
                    if provide_balance == 0:  # 在保余额为0
                        '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
                        provide_list.update(provide_status=11)  # 放款解保
                        response['message'] = '成功还款,本次放款已全部结清！'
                    else:
                        response['message'] = '成功还款！'
                    '''notify_repayment_sum，更新放款通知还款情况'''
                    notify_list = models.Notify.objects.filter(provide_notify=provide_obj)  # 放款通知
                    notify_obj = notify_list.first()
                    notify_repayment_amount = models.Repayments.objects.filter(provide__notify=notify_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
                    notify_provide_balance = models.Provides.objects.filter(notify=notify_obj).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']
                    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2),
                                       notify_balance=round(notify_provide_balance, 2))  # 放款通知，更新还款总额
                    '''agree_repayment_sum，更新合同还款信息'''
                    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                    agree_obj = agree_list.first()
                    agree_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree=agree_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
                    agree_provide_balance = models.Provides.objects.filter(
                        notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
                    if round(agree_provide_balance) == 0:  # 在保余额为0
                        '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                                            (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
                        agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2), agree_state=61,
                                          agree_balance=round(agree_provide_balance, 2))  # 合同，更新还款总额
                        response['message'] = '成功还款,合同项下放款已全部结清，合同解保！'
                    else:
                        agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2),
                                          agree_balance=round(agree_provide_balance, 2))  # 合同，更新还款总额
                    '''lending_repayment_sum，更新放款次序还款信息'''
                    lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                    lending_obj = lending_list.first()
                    lending_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree__lending=lending_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']
                    lending_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending=lending_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
                    lending_list.update(lending_repayment_sum=round(lending_repayment_amount, 2),
                                        lending_balance=round(lending_provide_balance, 2))  # 放款次序，更新还款总额
                    '''article_repayment_sum，更新项目还款信息'''
                    article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                    article_obj = article_list.first()
                    article_repayment_amount = models.Repayments.objects.filter(
                        provide__notify__agree__lending__summary=article_obj).aggregate(
                        Sum('repayment_money'))['repayment_money__sum']
                    article_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending__summary=article_obj).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']
                    if round(article_provide_balance) == 0:  # 在保余额为0
                        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
                        article_list.update(article_repayment_sum=round(article_repayment_amount, 2), article_state=55,
                                            article_balance=round(article_provide_balance, 2))  # 项目，更新还款总额
                        response['message'] = '成功还款,项目项下放款已全部结清，项目解保！'
                    else:
                        article_list.update(article_repayment_sum=round(article_repayment_amount, 2),
                                            article_balance=round(article_provide_balance, 2))  # 项目，更新还款总额
                    '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                    custom_list = models.Customes.objects.filter(article_custom=article_obj)
                    custom_obj = custom_list.first()
                    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                    branch_obj = branch_list.first()
                    provide_typ = provide_obj.provide_typ
                    '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
                    custom_provide_balance = models.Provides.objects.filter(
                        notify__agree__lending__summary__custom=custom_obj, provide_typ=provide_typ).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
                    branch_provide_balance = models.Provides.objects.filter(
                        notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
                        Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
                    cooperator_list = models.Cooperators.objects.filter(branch_cooperator=branch_obj)
                    cooperator_obj = cooperator_list.first()

                    if provide_typ == 1:
                        custom_list.update(custom_flow=custom_provide_balance)  # 客户，更新流贷余额
                        branch_list.update(branch_flow=branch_provide_balance)  # 放款银行，更新流贷余额
                        cooperator_branch_flow_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
                    elif provide_typ == 11:
                        custom_list.update(custom_accept=custom_provide_balance)  # 客户，更新承兑余额
                        branch_list.update(branch_accept=branch_provide_balance)  # 放款银行，更新承兑余额
                        cooperator_branch_accept_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))
                    else:
                        custom_list.update(custom_back=custom_provide_balance)  # 客户，更新保函余额
                        branch_list.update(branch_back=branch_provide_balance)  # 放款银行，更新保函余额
                        cooperator_branch_back_balance = models.Branches.objects.filter(
                            cooperator=cooperator_obj).aggregate(
                            Sum('branch_back'))['branch_back__sum']  # 授信银行项下，流贷余额
                        cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))
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
@authority
def repayment_del_ajax(request):  # 删除还款信息ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
                    provide_balance = round(provide_obj.provide_money - provide_repayment_amount, 2)
                    provide_list.update(provide_repayment_sum=round(provide_repayment_amount, 2),
                                        provide_balance=provide_balance)  # 放款，更新还款总额
                else:
                    provide_balance = round(provide_obj.provide_money, 2)
                    provide_list.update(provide_repayment_sum=0, provide_balance=provide_balance)  # 放款，更新还款总额
                '''notify_repayment_sum，更新放款通知还款情况'''
                notify_list = models.Notify.objects.filter(provide_notify=provide_obj)  # 放款通知
                notify_obj = notify_list.first()
                notify_repayment_amount = models.Repayments.objects.filter(provide__notify=notify_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
                notify_provide_balance = models.Provides.objects.filter(notify=notify_obj).aggregate(
                    Sum('provide_balance'))['provide_balance__sum']
                if notify_repayment_amount:
                    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2),
                                       notify_balance=round(notify_provide_balance, 2))  # 放款通知，更新还款总额
                else:
                    notify_list.update(notify_repayment_sum=0,
                                       notify_balance=round(notify_provide_balance, 2))  # 放款通知，更新还款总额
                '''agree_repayment_sum，更新合同还款信息'''
                agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                agree_obj = agree_list.first()
                agree_repayment_amount = models.Repayments.objects.filter(provide__notify__agree=agree_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
                agree_provide_balance = models.Provides.objects.filter(
                    notify__agree=agree_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保余额合计
                '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                                                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
                if agree_repayment_amount:
                    agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2), agree_state=31,
                                      agree_balance=round(agree_provide_balance, 2))  # 合同，更新还款总额
                else:
                    agree_list.update(agree_repayment_sum=0, agree_state=31,
                                      agree_balance=round(agree_provide_balance, 2))  # 合同，更新还款总额
                '''lending_repayment_sum，更新放款次序还款信息'''
                lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                lending_obj = lending_list.first()
                lending_repayment_amount = models.Repayments.objects.filter(
                    provide__notify__agree__lending=lending_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']
                lending_provide_balance = models.Provides.objects.filter(
                    notify__agree__lending=lending_obj).aggregate(Sum('provide_balance'))['provide_balance__sum']
                if lending_repayment_amount:
                    lending_list.update(lending_repayment_sum=round(lending_repayment_amount, 2),
                                        lending_balance=round(lending_provide_balance, 2))  # 放款次序，更新还款总额
                else:
                    lending_list.update(lending_repayment_sum=0,
                                        lending_balance=round(lending_provide_balance, 2))  # 放款次序，更新还款总额
                '''article_repayment_sum，更新项目还款信息'''
                article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                article_obj = article_list.first()
                article_repayment_amount = models.Repayments.objects.filter(
                    provide__notify__agree__lending__summary=article_obj).aggregate(
                    Sum('repayment_money'))['repayment_money__sum']
                article_provide_balance = models.Provides.objects.filter(
                    notify__agree__lending__summary=article_obj).aggregate(
                    Sum('provide_balance'))['provide_balance__sum']
                '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                                      (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
                if article_repayment_amount:
                    article_list.update(article_repayment_sum=round(article_repayment_amount, 2), article_state=51,
                                        article_balance=round(article_provide_balance, 2))  # 项目，更新还款总额
                else:
                    article_list.update(article_repayment_sum=0, article_state=51,
                                        article_balance=round(article_provide_balance, 2))  # 项目，更新还款总额
                '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                custom_list = models.Customes.objects.filter(article_custom=article_obj)
                custom_obj = custom_list.first()
                branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                branch_obj = branch_list.first()
                provide_typ = provide_obj.provide_typ
                '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'))'''
                custom_provide_balance = models.Provides.objects.filter(
                    notify__agree__lending__summary__custom=custom_obj, provide_typ=provide_typ).aggregate(
                    Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
                branch_provide_balance = models.Provides.objects.filter(
                    notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
                    Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
                cooperator_list = models.Cooperators.objects.filter(branch_cooperator=branch_obj)
                cooperator_obj = cooperator_list.first()

                if provide_typ == 1:
                    custom_list.update(custom_flow=custom_provide_balance)  # 客户，更新流贷余额
                    branch_list.update(branch_flow=branch_provide_balance)  # 放款银行，更新流贷余额
                    cooperator_branch_flow_balance = models.Branches.objects.filter(
                        cooperator=cooperator_obj).aggregate(
                        Sum('branch_flow'))['branch_flow__sum']  # 授信银行项下，流贷余额
                    cooperator_list.update(cooperator_flow=round(cooperator_branch_flow_balance, 2))
                elif provide_typ == 11:
                    custom_list.update(custom_accept=custom_provide_balance)  # 客户，更新承兑余额
                    branch_list.update(branch_accept=branch_provide_balance)  # 放款银行，更新承兑余额
                    cooperator_branch_accept_balance = models.Branches.objects.filter(
                        cooperator=cooperator_obj).aggregate(
                        Sum('branch_accept'))['branch_accept__sum']  # 授信银行项下，承兑余额
                    cooperator_list.update(cooperator_accept=round(cooperator_branch_accept_balance, 2))
                else:
                    custom_list.update(custom_back=custom_provide_balance)  # 客户，更新保函余额
                    branch_list.update(branch_back=branch_provide_balance)  # 放款银行，更新保函余额
                    cooperator_branch_back_balance = models.Branches.objects.filter(
                        cooperator=cooperator_obj).aggregate(
                        Sum('branch_back'))['branch_back__sum']  # 授信银行项下，保函余额
                    cooperator_list.update(cooperator_back=round(cooperator_branch_back_balance, 2))
            response['message'] = '还款信息删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '还款信息删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '该笔放款状态为：%s，还款信息删除失败！！！' % provide_obj.provide_status
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
