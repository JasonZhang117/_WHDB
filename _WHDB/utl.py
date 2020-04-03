from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority, radio, epi


def provide_update(provide_obj: object, response: dict):
    '''provide_repayment_sum，更新放款还款情况'''
    provide_repayment_amount = models.Repayments.objects.filter(
        provide=provide_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 放款项下还款合计
    provide_balance = round(provide_obj.provide_money - provide_repayment_amount, 2)  # 在保余额
    provide_list.update(
        provide_repayment_sum=round(provide_repayment_amount, 2),
        provide_balance=provide_balance)  # 放款，更新还款总额，在保余额
    if provide_balance == 0:  # 在保余额为0
        '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
        provide_list.update(provide_status=11)  # 放款解保
        response['message'] = '成功还款,本次放款已全部结清！'
    else:
        response['message'] = '成功还款！'
    '''notify_repayment_sum，更新放款通知还款情况'''
    notify_list = models.Notify.objects.filter(
        provide_notify=provide_obj)  # 放款通知
    notify_obj = notify_list.first()
    notify_repayment_amount = models.Repayments.objects.filter(
        provide__notify=notify_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
    notify_provide_balance = models.Provides.objects.filter(
        notify=notify_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 通知项下在保合计
    notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2),
                       notify_balance=round(notify_provide_balance,
                                            2))  # 放款通知，更新还款总额
    '''agree_repayment_sum，更新合同还款信息'''
    agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
    agree_obj = agree_list.first()
    agree_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree=agree_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
    agree_provide_balance = models.Provides.objects.filter(
        notify__agree=agree_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 合同项下在保合计
    if round(agree_provide_balance) == 0:  # 在保余额为0
        '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'),
                        (99, '作废'))'''
        agree_list.update(
            agree_repayment_sum=round(agree_repayment_amount, 2),
            agree_balance=round(agree_provide_balance, 2),
            agree_state=61,)  # 合同，更新还款总额，在保余额，合同状态
        response['message'] = '成功还款,合同项下放款已全部结清，合同解保！'
    else:
        agree_list.update(
            agree_repayment_sum=round(agree_repayment_amount, 2),
            agree_balance=round(agree_provide_balance, 2))
        # 合同，更新还款总额，在保余额
    '''lending_repayment_sum，更新放款次序还款信息'''
    lending_list = models.LendingOrder.objects.filter(
        agree_lending=agree_obj)  # 放款次序
    lending_obj = lending_list.first()
    lending_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree__lending=lending_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']
    lending_provide_balance = models.Provides.objects.filter(
        notify__agree__lending=lending_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']
    if round(lending_provide_balance) == 0:  # 在保余额为0
        '''LENDING_STATE = [(3, '待上会'), (4, '已上会'), (5, '已签批'),
                            (51, '已放款'), (52, '已放完'), (55, '已解保'), 
                            (61, '待变更'),(99, '已注销')]'''
        lending_list.update(
            lending_repayment_sum=round(lending_repayment_amount, 2),
            lending_balance=round(lending_provide_balance, 2),
            lending_state=55)  # 放款次序，更新还款总额
    else:
        lending_list.update(
            lending_repayment_sum=round(lending_repayment_amount, 2),
            lending_balance=round(lending_provide_balance,2))  # 放款次序，更新还款总额
    '''article_repayment_sum，更新项目还款信息'''
    article_list = models.Articles.objects.filter(
        lending_summary=lending_obj)  # 项目
    article_obj = article_list.first()
    article_repayment_amount = models.Repayments.objects.filter(
        provide__notify__agree__lending__summary=article_obj).aggregate(
            Sum('repayment_money'))['repayment_money__sum']
    article_provide_balance = models.Provides.objects.filter(
        notify__agree__lending__summary=article_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']

    if round(article_provide_balance) == 0:  # 在保余额为0
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), 
        (4, '已上会'), (5, '已签批'),(51, '已放款'), (52, '已放完'), (55, '已解保'),
        (61, '待变更'), (99, '已注销'))'''
        article_list.update(article_repayment_sum=round(
            article_repayment_amount, 2),
            article_balance=round(article_provide_balance, 2),
            article_state=55)  # 项目，更新还款总额
        response['message'] = '成功还款,项目项下放款已全部结清，项目解保！'
    else:
        article_list.update(article_repayment_sum=round(
            article_repayment_amount, 2),
            article_balance=round(article_provide_balance,2))  # 项目，更新还款总额
    '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
    custom_list = models.Customes.objects.filter(article_custom=article_obj)
    custom_obj = custom_list.first()
    branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
    branch_obj = branch_list.first()
    provide_typ = provide_obj.provide_typ
    '''PROVIDE_TYP_LIST = ((1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'), (42, '小贷'))'''
    custom_provide_balance = models.Provides.objects.filter(
        notify__agree__lending__summary__custom=custom_obj,
        provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 客户及放款品种项下，在保余额
    branch_provide_balance = models.Provides.objects.filter(
        notify__agree__branch=branch_obj, provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 放款银行及放款品种项下，在保余额
    cooperator_list = models.Cooperators.objects.filter(
        branch_cooperator=branch_obj)
    cooperator_obj = cooperator_list.first()
    cooperator_provide_balance = models.Provides.objects.filter(
        notify__agree__branch__cooperator=cooperator_obj,
        provide_typ=provide_typ).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 授信银行及放款品种项下，在保余额
    if provide_typ == 1:
        custom_list.update(custom_flow=custom_provide_balance)  # 客户，更新流贷余额
        branch_list.update(branch_flow=branch_provide_balance)  # 放款银行，更新流贷余额
        cooperator_list.update(
            cooperator_flow=round(cooperator_provide_balance, 2))
    elif provide_typ == 11:
        custom_list.update(custom_accept=custom_provide_balance)  # 客户，更新承兑余额
        branch_list.update(branch_accept=branch_provide_balance)  # 放款银行，更新承兑余额
        cooperator_list.update(
            cooperator_accept=round(cooperator_provide_balance, 2))
    elif provide_typ == 21:
        custom_list.update(custom_back=custom_provide_balance)  # 客户，更新保函余额
        branch_list.update(branch_back=branch_provide_balance)  # 放款银行，更新保函余额
        cooperator_list.update(
            cooperator_back=round(cooperator_provide_balance, 2))
    elif provide_typ == 31:
        custom_list.update(entrusted_loan=custom_provide_balance)  # 客户，更新委贷余额
        branch_list.update(
            entrusted_loan=branch_provide_balance)  # 放款银行，更新委贷余额
        cooperator_list.update(
            entrusted_loan=round(cooperator_provide_balance, 2))
    elif provide_typ == 41:
        custom_list.update(petty_loan=custom_provide_balance)  # 客户，更新小贷余额
        branch_list.update(petty_loan=branch_provide_balance)  # 放款银行，更新小贷余额
        cooperator_list.update(petty_loan=round(cooperator_provide_balance, 2))
    '''更新客户、放款银行、授信银行在保总额'''
    custom_provide_balance_all = models.Provides.objects.filter(
        notify__agree__lending__summary__custom=custom_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 客户项下，在保余额
    if not custom_provide_balance_all:
        custom_provide_balance_all = 0
    v_radio = radio(custom_provide_balance_all, custom_obj.g_value)
    custom_list.update(
        amount=round(custom_provide_balance_all, 2),
        v_radio=v_radio)
    branch_provide_balance_all = models.Provides.objects.filter(
        notify__agree__branch=branch_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 放款银行项下，在保余额
    branch_list.update(amount=round(branch_provide_balance_all, 2))
    cooperator_provide_balance_all = models.Provides.objects.filter(
        notify__agree__branch__cooperator=cooperator_obj).aggregate(
            Sum('provide_balance'))['provide_balance__sum']  # 授信银行项下，在保余额
    cooperator_list.update(amount=round(cooperator_provide_balance_all, 2))

    return response