from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, datetime, json
from dateutil.relativedelta import relativedelta
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.db.models import Avg, Min, Sum, Max, Count
from django.urls import resolve
from _WHDB.views import (MenuHelper, authority, FICATION_LIST, amount_s)


def tt_article(t_typ, tf_r, tl_r):
    dt_today = datetime.date.today()
    if t_typ == 0:
        article_groups = models.Articles.objects.filter(
            article_balance__gt=0).order_by('build_date')
        tf_r = article_groups.first().build_date.isoformat()  # 在保第一笔日期
        tl_r = article_groups.last().build_date.isoformat()  # 在保最后一笔日期
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year,
                             dt_today.month - (dt_today.month - 1) % 3,
                             1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (
            datetime.date(dt_today.year, dt_today.month -
                          (dt_today.month - 1) % 3 + 2, 1) +
            relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)
    elif t_typ == 3:
        tf_r = (dt_today -
                datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)
    elif t_typ == 4:
        tf_r = (
            dt_today -
            datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())
                ).isoformat()  # 本周最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
        article_groups = models.Articles.objects.filter(build_date__gte=tf_r,
                                                        build_date__lte=tl_r)

    return (article_groups, tf_r, tl_r)


def tt_compensatory(t_typ, tf_r, tl_r):
    dt_today = datetime.date.today()
    if t_typ == 0:
        pl = models.Compensatories.objects.all().order_by('compensatory_date')
        tf_r = pl.first().compensatory_date.isoformat()  #
        tl_r = pl.last().compensatory_date.isoformat()  #
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year,
                             dt_today.month - (dt_today.month - 1) % 3,
                             1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (
            datetime.date(dt_today.year, dt_today.month -
                          (dt_today.month - 1) % 3 + 2, 1) +
            relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today -
                datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (
            dt_today -
            datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())
                ).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    return (tf_r, tl_r)


def tt_provide(t_typ, tf_r, tl_r):
    dt_today = datetime.date.today()
    if t_typ == 0:
        pl = models.Provides.objects.filter(
            provide_balance__gt=0).order_by('provide_date')
        tf_r = pl.first().provide_date.isoformat()  # 在保第一笔日期
        tl_r = pl.last().provide_date.isoformat()  # 在保最后一笔日期
    elif t_typ == 1:
        tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
        tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    elif t_typ == 2:
        tf_r = datetime.date(dt_today.year,
                             dt_today.month - (dt_today.month - 1) % 3,
                             1).isoformat()  # 本季第一天
        tl_r = quarter_end_day = (
            datetime.date(dt_today.year, dt_today.month -
                          (dt_today.month - 1) % 3 + 2, 1) +
            relativedelta(months=1, days=-1)).isoformat()  # 本季最后一天
    elif t_typ == 3:
        tf_r = (dt_today -
                datetime.timedelta(days=dt_today.day - 1)).isoformat()  # 本月第一天
        tl_r = (dt_today + datetime.timedelta(days=-dt_today.day + 1) +
                relativedelta(months=1, days=-1)).isoformat()  # 本月最后一天
    elif t_typ == 4:
        tf_r = (
            dt_today -
            datetime.timedelta(days=dt_today.weekday())).isoformat()  # 本周第一天
        tl_r = (dt_today + datetime.timedelta(days=6 - dt_today.weekday())
                ).isoformat()  # 本周最后一天
    elif t_typ == 11:
        tf_r = datetime.date(dt_today.year - 1, 1, 1).isoformat()  # 上年第一天
        tl_r = datetime.date(dt_today.year - 1, 12, 31).isoformat()  # 上年最后一天
    elif t_typ == 99:
        if tf_r and tl_r:
            tf_r = tf_r
            tl_r = tl_r
        else:
            tf_r = datetime.date(dt_today.year, 1, 1).isoformat()  # 本年第一天
            tl_r = datetime.date(dt_today.year, 12, 31).isoformat()  # 本年最后一天
    return (tf_r, tl_r)


# ----------------------报表---------------------#
@login_required
@authority
def report(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '报表系统'

    return render(request, 'dbms/report/report.html', locals())


# -----------------------在保列表---------------------#
def report_provide_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保明细'
    '''PROVIDE_TYP_LIST = [(1, '流贷'), (11, '承兑'), (21, '保函'), (31, '委贷'),
                        (41, '过桥贷'), (52, '房抵贷'), (53, '担保贷')]'''
    provide_typ_list = [(0, '全部'), (1, '贷款担保'), (11, '票据承兑担保'), (13, '信用证担保'),
                        (19, '其他担保'), (21, '履约保函'),
                        (22, '投标保函'), (23, '预付款保函'), (31, '委贷'), (41, '过桥贷'),
                        (52, '房抵贷'), (53, '担保贷'), (55, '经营贷'), (57, '票据贷'),
                        (58, '消费贷')]  # 筛选条件
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    p_typ = kwargs['p_typ']
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)

    provide_list = models.Provides.objects.filter(
        provide_balance__gt=0, provide_date__gte=tf_r,
        provide_date__lte=tl_r).select_related('notify').order_by(
            '-provide_date')
    if p_typ:
        provide_list = provide_list.filter(provide_typ=p_typ).select_related(
            'notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'notify__agree__lending__summary__custom__name',
            'notify__agree__lending__summary__custom__short_name',
            'notify__agree__branch__name', 'notify__agree__branch__short_name',
            'notify__agree__agree_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        provide_list = provide_list.filter(q)
    provide_provide = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    old_amount_sum = provide_list.aggregate(
        Sum('old_amount'))['old_amount__sum']  #
    new_amount_sum = provide_list.aggregate(
        Sum('new_amount'))['new_amount__sum']  #
    repayment_sum = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    provide_count = provide_list.count()  #

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------在保分类（按放款）---------------------#
def report_balance_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保放款分类统计表'
    CLASS_LIST = [
        (1, '品种'),
        (11, '授信银行'),
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (71, '放款支行'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    provide_typ_dic = dict(models.Provides.PROVIDE_TYP_LIST)

    fication_dic = dict(FICATION_LIST)

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)
    provide_groups = models.Provides.objects.filter(provide_balance__gt=0,
                                                    provide_date__gte=tf_r,
                                                    provide_date__lte=tl_r)

    provide_old = provide_groups.aggregate(
        Sum('old_amount'))['old_amount__sum']  # 续贷金额
    provide_new = provide_groups.aggregate(
        Sum('new_amount'))['new_amount__sum']  # 新增金额
    provide_balance = provide_groups.aggregate(
        Sum('provide_money'))['provide_money__sum']  # 放款金额
    provide_repayment_tot = provide_groups.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance_tot = provide_groups.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    provide_count = provide_groups.aggregate(
        Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values('provide_typ').annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values('provide_typ', 'con', 'sum_old',
                                               'sum_new', 'sum', 'repayment',
                                               'balance').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__director__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__assistant__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__control__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__idustry__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__custom__idustry__name',
                'con', 'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_fication = provide_groups.values('fication').annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values('fication', 'con', 'sum_old',
                                               'sum_new', 'sum', 'repayment',
                                               'balance').order_by('fication')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__district__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__custom__district__name',
                'con', 'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__branch__cooperator__short_name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__branch__short_name', 'con', 'sum_old',
                'sum_new', 'sum', 'repayment', 'balance').order_by('-sum')
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name'
    ).annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values(
            'notify__agree__lending__summary__director__department__name',
            'con', 'sum_old', 'sum_new', 'sum', 'repayment',
            'balance').order_by('-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__expert__organization', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')

    return render(request, 'dbms/report/balance-class-provide.html', locals())


# ----------------------在保分类统计（按放款）明细---------------------#
def report_provid_w_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款分类明细（在保）'
    CLASS_LIST = [
        (1, '品种'),
        (11, '授信银行'),
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (71, '放款支行'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST
    provide_typ_wen = {}
    for provide_typ in provide_typ_list:
        provide_typ_wen[provide_typ[1]] = provide_typ[0]
    fication_list = FICATION_LIST
    fication_dic = dict(fication_list)
    fication_wen = {}
    for fication in fication_list:
        fication_wen[fication[1]] = fication[0]
    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)
    ss_value = request.GET.get('_cs')
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']

    c_typ_dic_this = c_typ_dic[c_typ]
    t_typ_dic_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)

    provide_list = models.Provides.objects.filter(
        provide_balance__gt=0, provide_date__gte=tf_r,
        provide_date__lte=tl_r).select_related('notify').order_by(
            '-provide_date')

    if c_typ == 1:
        provide_list = provide_list.filter(
            provide_typ=provide_typ_wen[ss_value])
    elif c_typ == 11:
        provide_list = provide_list.filter(
            notify__agree__branch__cooperator__short_name=ss_value)
    elif c_typ == 21:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__custom__district__name=ss_value)
    elif c_typ == 31:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__custom__idustry__name=ss_value)
    elif c_typ == 33:
        provide_list = provide_list.filter(fication=fication_wen[ss_value])
    elif c_typ == 35:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__department__name=ss_value
        )
    elif c_typ == 41:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__name=ss_value)
    elif c_typ == 51:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__assistant__name=ss_value)
    elif c_typ == 61:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__control__name=ss_value)
    elif c_typ == 71:
        provide_list = provide_list.filter(
            notify__agree__branch__short_name=ss_value)
    elif c_typ == 81:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__expert__organization=ss_value)

    old_amount_tot = provide_list.aggregate(
        Sum('old_amount'))['old_amount__sum']  #
    new_amount_tot = provide_list.aggregate(
        Sum('new_amount'))['new_amount__sum']  #
    provide_money_tot = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    provide_repayment_tot = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance_tot = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    article_acount = provide_list.count()

    return render(request, 'dbms/report/list/class-provide-list.html',
                  locals())


# -----------------------在保分类(按项目)---------------------#
def report_article_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '在保分类(按项目)'
    CLASS_LIST = [
        (2, '阶段'),
        (21, '区域'),
        (31, '行业'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (81, '法律顾问'),
    ]

    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 项目阶段
    article_state_dic = dict(article_state_list)

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = 0
    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)

    article_renewal = article_groups.aggregate(
        Sum('renewal'))['renewal__sum']  # 续贷金额
    article_augment = article_groups.aggregate(
        Sum('augment'))['augment__sum']  # 新增金额
    article_amount = article_groups.aggregate(
        Sum('amount'))['amount__sum']  # 金额合计
    article_notify_sum = article_groups.aggregate(
        Sum('article_notify_sum'))['article_notify_sum__sum']  # 通知金额
    article_provide_sum = article_groups.aggregate(
        Sum('article_provide_sum'))['article_provide_sum__sum']  # 放款金额
    article_repayment_sum = article_groups.aggregate(
        Sum('article_repayment_sum'))['article_repayment_sum__sum']  # 还款金额
    article_balance = article_groups.aggregate(
        Sum('article_balance'))['article_balance__sum']  # 在保余额
    article_count = article_groups.aggregate(
        Count('article_balance'))['article_balance__count']  # 项目数

    article_balance_stage = article_groups.values(
        'article_state').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('article_state', 'con', 'sum_renewal', 'sum_augment', 'sum_amount', 'sum_notify',
               'sum_provide', 'sum_repayment', 'sum_balance').order_by('article_state')  # 阶段余额分组
    article_balance_district = article_groups.values(
        'custom__district__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__district__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 区域
    article_balance_idustry = article_groups.values(
        'custom__idustry__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__idustry__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 行业
    article_balance_depart = article_groups.values(
        'director__department__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__department__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 部门
    article_balance_director = article_groups.values(
        'director__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目经理
    article_balance_assistant = article_groups.values(
        'assistant__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('assistant__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目助理
    article_balance_control = article_groups.values(
        'control__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('control__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 风控专员
    article_balance_organization = article_groups.values(
        'expert__organization').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('expert__organization', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 法律顾问

    return render(request, 'dbms/report/balance-class-article.html', locals())


# -----------------------放款列表---------------------#
def report_provide_accrual(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款明细'
    provide_typ_list = [(0, '全部'), (1, '贷款担保'), (11, '票据承兑担保'), (13, '信用证担保'),
                        (19, '其他担保'),
                        (21, '履约保函'), (25, '投标保函'), (26, '预付款保函'),
                        (29, '其他保函'), (38, '委贷'), (41, '过桥贷'),
                        (52, '房抵贷'), (53, '担保贷'), (55, '经营贷'), (57, '票据贷'),
                        (58, '消费贷')]  # 筛选条件
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    p_typ = kwargs['p_typ']
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)
    provide_list = models.Provides.objects.filter(
        provide_date__gte=tf_r, provide_date__lte=tl_r).select_related(
            'notify').order_by('-provide_date')
    if p_typ:
        provide_list = provide_list.filter(provide_typ=p_typ).select_related(
            'notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'notify__agree__lending__summary__custom__name',
            'notify__agree__lending__summary__custom__short_name',
            'notify__agree__branch__name', 'notify__agree__branch__short_name',
            'notify__agree__agree_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        provide_list = provide_list.filter(q)
    provide_provide = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    old_amount_sum = provide_list.aggregate(
        Sum('old_amount'))['old_amount__sum']  #
    new_amount_sum = provide_list.aggregate(
        Sum('new_amount'))['new_amount__sum']  #
    repayment_sum = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    provide_count = provide_list.count()  #

    return render(request, 'dbms/report/provide_list.html', locals())


# -----------------------放款列表（报送报表）---------------------#
def report_provide_report(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款明细(报送)'
    provide_typ_list = [(0, '全部'), (1, '贷款担保'), (11, '票据承兑担保'), (13, '信用证担保'),
                        (19, '其他担保'), (21, '履约保函'), (25, '投标保函'),
                        (26, '预付款保函'), (29, '其他保函')]  # 筛选条件
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    p_typ = kwargs['p_typ']
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)
    provide_list = models.Provides.objects.filter(
        provide_date__gte=tf_r, provide_date__lte=tl_r).select_related(
            'notify').order_by('-provide_date')
    if p_typ:
        provide_list = provide_list.filter(provide_typ=p_typ).select_related(
            'notify').order_by('-provide_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'notify__agree__lending__summary__custom__name',
            'notify__agree__lending__summary__custom__short_name',
            'notify__agree__branch__name', 'notify__agree__branch__short_name',
            'notify__agree__agree_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        provide_list = provide_list.filter(q)
    provide_provide = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    old_amount_sum = provide_list.aggregate(
        Sum('old_amount'))['old_amount__sum']  #
    new_amount_sum = provide_list.aggregate(
        Sum('new_amount'))['new_amount__sum']  #
    repayment_sum = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    provide_count = provide_list.count()  #

    return render(request, 'dbms/report/provide_list_p.html', locals())


# -----------------------还款列表---------------------#
def report_repay_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '还款明细'
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)
    repay_list = models.Repayments.objects.filter(
        repayment_date__gte=tf_r, repayment_date__lte=tl_r).select_related(
            'provide').order_by('-repayment_date')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'provide__notify__agree__lending__summary__custom__name',
            'provide__notify__agree__lending__summary__custom__short_name',
            'provide__notify__agree__branch__name',
            'provide__notify__agree__branch__short_name',
            'provide__notify__agree__agree_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        repay_list = repay_list.filter(q)
    repay_sum = repay_list.aggregate(
        Sum('repayment_money'))['repayment_money__sum']  #
    repay_count = repay_list.count()  #

    return render(request, 'dbms/report/repay_list.html', locals())


# -----------------------放款分类统计---------------------#
def report_accrual_class(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款分类统计表'
    CLASS_LIST = [
        (1, '品种'),
        (11, '授信银行'),
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (71, '放款支行'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    provide_typ_dic = dict(models.Provides.PROVIDE_TYP_LIST)
    fication_dic = dict(FICATION_LIST)

    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_dic_this = c_typ_dic[c_typ]
    t_typ_dic_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)

    provide_groups = models.Provides.objects.filter(provide_date__gte=tf_r,
                                                    provide_date__lte=tl_r)

    provide_old = provide_groups.aggregate(
        Sum('old_amount'))['old_amount__sum']  # 续贷金额
    provide_new = provide_groups.aggregate(
        Sum('new_amount'))['new_amount__sum']  # 新增金额
    provide_balance = provide_groups.aggregate(
        Sum('provide_money'))['provide_money__sum']  # 放款金额
    provide_repayment_tot = provide_groups.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance_tot = provide_groups.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    provide_count = provide_groups.aggregate(
        Count('provide_money'))['provide_money__count']  # 放款项目数

    provide_groups_breed = provide_groups.values('provide_typ').annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values('provide_typ', 'con', 'sum_old',
                                               'sum_new', 'sum', 'repayment',
                                               'balance').order_by('-sum')
    provide_groups_director = provide_groups.values(
        'notify__agree__lending__summary__director__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__director__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_assistant = provide_groups.values(
        'notify__agree__lending__summary__assistant__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__assistant__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_control = provide_groups.values(
        'notify__agree__lending__summary__control__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__control__name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_idustry = provide_groups.values(
        'notify__agree__lending__summary__custom__idustry__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__custom__idustry__name',
                'con', 'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_fication = provide_groups.values('fication').annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values('fication', 'con', 'sum_old',
                                               'sum_new', 'sum', 'repayment',
                                               'balance').order_by('fication')
    provide_groups_district = provide_groups.values(
        'notify__agree__lending__summary__custom__district__name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__custom__district__name',
                'con', 'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_bank = provide_groups.values(
        'notify__agree__branch__cooperator__short_name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__branch__cooperator__short_name', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')
    provide_groups_branch = provide_groups.values(
        'notify__agree__branch__short_name').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__branch__short_name', 'con', 'sum_old',
                'sum_new', 'sum', 'repayment', 'balance').order_by('-sum')
    provide_groups_depart = provide_groups.values(
        'notify__agree__lending__summary__director__department__name'
    ).annotate(
        con=Count('provide_money'),
        sum_old=Sum('old_amount'),
        sum_new=Sum('new_amount'),
        sum=Sum('provide_money'),
        repayment=Sum('provide_repayment_sum'),
        balance=Sum('provide_balance')).values(
            'notify__agree__lending__summary__director__department__name',
            'con', 'sum_old', 'sum_new', 'sum', 'repayment',
            'balance').order_by('-sum')
    provide_groups_organization = provide_groups.values(
        'notify__agree__lending__summary__expert__organization').annotate(
            con=Count('provide_money'),
            sum_old=Sum('old_amount'),
            sum_new=Sum('new_amount'),
            sum=Sum('provide_money'),
            repayment=Sum('provide_repayment_sum'),
            balance=Sum('provide_balance')).values(
                'notify__agree__lending__summary__expert__organization', 'con',
                'sum_old', 'sum_new', 'sum', 'repayment',
                'balance').order_by('-sum')

    return render(request, 'dbms/report/balance-class-accrual.html', locals())


# -----------------------放款分类统计明细---------------------#
def report_provide_class_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '放款分类明细'
    CLASS_LIST = [
        (1, '品种'),
        (11, '授信银行'),
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (71, '放款支行'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]
    provide_typ_list = models.Provides.PROVIDE_TYP_LIST
    provide_typ_dic = dict(provide_typ_list)
    provide_typ_wen = {}
    for provide_typ in provide_typ_list:
        provide_typ_wen[provide_typ[1]] = provide_typ[0]

    fication_list = FICATION_LIST
    fication_dic = dict(fication_list)
    fication_wen = {}
    for fication in fication_list:
        fication_wen[fication[1]] = fication[0]

    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)
    ss_value = request.GET.get('_cs')
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_dic_this = c_typ_dic[c_typ]
    t_typ_dic_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_provide(t_typ, tf_r, tl_r)

    if t_typ == 0:
        provide_list = models.Provides.objects.filter(
            provide_balance__gt=0,
            provide_date__gte=tf_r,
            provide_date__lte=tl_r).select_related('notify').order_by(
                '-provide_date')
    else:
        provide_list = models.Provides.objects.filter(
            provide_date__gte=tf_r, provide_date__lte=tl_r).select_related(
                'notify').order_by('-provide_date')
    if c_typ == 1:
        provide_list = provide_list.filter(
            provide_typ=provide_typ_wen[ss_value])
    elif c_typ == 11:
        provide_list = provide_list.filter(
            notify__agree__branch__cooperator__short_name=ss_value)
    elif c_typ == 21:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__custom__district__name=ss_value)
    elif c_typ == 31:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__custom__idustry__name=ss_value)
    elif c_typ == 33:
        provide_list = provide_list.filter(fication=fication_wen[ss_value])
    elif c_typ == 35:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__department__name=ss_value
        )
    elif c_typ == 41:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__director__name=ss_value)
    elif c_typ == 51:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__assistant__name=ss_value)
    elif c_typ == 61:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__control__name=ss_value)
    elif c_typ == 71:
        provide_list = provide_list.filter(
            notify__agree__branch__short_name=ss_value)
    elif c_typ == 81:
        provide_list = provide_list.filter(
            notify__agree__lending__summary__expert__organization=ss_value)

    old_amount_tot = provide_list.aggregate(
        Sum('old_amount'))['old_amount__sum']  #
    new_amount_tot = provide_list.aggregate(
        Sum('new_amount'))['new_amount__sum']  #
    provide_money_tot = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    provide_repayment_tot = provide_list.aggregate(
        Sum('provide_repayment_sum'))['provide_repayment_sum__sum']  #
    provide_balance_tot = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    article_acount = provide_list.count()

    return render(request, 'dbms/report/list/class-provide-list.html',
                  locals())


# -----------------------项目分类统计---------------------#
def report_article(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '项目分类'
    CLASS_LIST = [
        (2, '阶段'),
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    article_state_dic = dict(models.Articles.ARTICLE_STATE_LIST)  # 项目阶段

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']

    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    article_renewal = article_groups.aggregate(
        Sum('renewal'))['renewal__sum']  # 续贷金额
    article_augment = article_groups.aggregate(
        Sum('augment'))['augment__sum']  # 新增金额
    article_amount = article_groups.aggregate(
        Sum('amount'))['amount__sum']  # 金额合计
    article_notify_sum = article_groups.aggregate(
        Sum('article_notify_sum'))['article_notify_sum__sum']  # 通知金额
    article_provide_sum = article_groups.aggregate(
        Sum('article_provide_sum'))['article_provide_sum__sum']  # 放款金额
    article_repayment_sum = article_groups.aggregate(
        Sum('article_repayment_sum'))['article_repayment_sum__sum']  # 还款金额
    article_balance = article_groups.aggregate(
        Sum('article_balance'))['article_balance__sum']  # 在保余额
    article_count = article_groups.aggregate(
        Count('article_balance'))['article_balance__count']  # 项目数

    article_balance_stage = article_groups.values(
        'article_state').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('article_state', 'con', 'sum_renewal', 'sum_augment', 'sum_amount', 'sum_notify',
               'sum_provide', 'sum_repayment', 'sum_balance').order_by('article_state')  # 阶段余额分组
    article_balance_district = article_groups.values(
        'custom__district__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__district__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 区域
    article_balance_idustry = article_groups.values(
        'custom__idustry__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('custom__idustry__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 行业
    article_balance_depart = article_groups.values(
        'director__department__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__department__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 部门
    article_balance_director = article_groups.values(
        'director__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('director__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目经理
    article_balance_assistant = article_groups.values(
        'assistant__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('assistant__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 项目助理
    article_balance_control = article_groups.values(
        'control__name').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('control__name', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 风控专员
    article_balance_organization = article_groups.values(
        'expert__organization').annotate(
        con=Count('amount'), sum_renewal=Sum('renewal'), sum_augment=Sum('augment'), sum_amount=Sum('amount'),
        sum_notify=Sum('article_notify_sum'), sum_provide=Sum('article_provide_sum'),
        sum_repayment=Sum('article_repayment_sum'), sum_balance=Sum('article_balance')). \
        values('expert__organization', 'con', 'sum_renewal', 'sum_augment', 'sum_amount',
               'sum_notify', 'sum_provide', 'sum_repayment', 'sum_balance').order_by('-sum_renewal')  # 法律顾问

    return render(request, 'dbms/report/balance-class-article.html', locals())


# -----------------------项目分类统计明细---------------------#
def report_article_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '项目分类明细'
    CLASS_LIST = [
        (2, '阶段'),
        (21, '区域'),
        (31, '行业'),
        (35, '部门'),
        (41, '项目经理'),
        (51, '项目助理'),
        (61, '风控专员'),
        (81, '法律顾问'),
    ]
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    article_state_list = models.Articles.ARTICLE_STATE_LIST  # 项目阶段
    article_state_dic = dict(article_state_list)
    article_state_wen = {}
    for article_state in article_state_list:
        article_state_wen[article_state[1]] = article_state[0]
    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)

    t_typ_dic[0] = '在保'

    ss_value = request.GET.get('_cs')
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_dic_this = c_typ_dic[c_typ]
    t_typ_dic_this = t_typ_dic[t_typ]
    article_groups, tf_r, tl_r = tt_article(t_typ, tf_r, tl_r)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if c_typ == 2:
        article_groups = article_groups.filter(
            article_state=article_state_wen[ss_value])
    elif c_typ == 21:
        article_groups = article_groups.filter(custom__district__name=ss_value)
    elif c_typ == 31:
        article_groups = article_groups.filter(custom__idustry__name=ss_value)
    elif c_typ == 35:
        article_groups = article_groups.filter(
            director__department__name=ss_value)
    elif c_typ == 41:
        article_groups = article_groups.filter(director__name=ss_value)
    elif c_typ == 51:
        article_groups = article_groups.filter(assistant__name=ss_value)
    elif c_typ == 61:
        article_groups = article_groups.filter(control__name=ss_value)
    elif c_typ == 81:
        article_groups = article_groups.filter(expert__organization=ss_value)
    article_renewal_tot = article_groups.aggregate(
        Sum('renewal'))['renewal__sum']  #
    article_augment_tot = article_groups.aggregate(
        Sum('augment'))['augment__sum']  #
    article_amount_tot = article_groups.aggregate(
        Sum('amount'))['amount__sum']  #
    article_provide_tot = article_groups.aggregate(
        Sum('article_provide_sum'))['article_provide_sum__sum']  #
    article_repayment_tot = article_groups.aggregate(
        Sum('article_repayment_sum'))['article_repayment_sum__sum']  #
    article_balance_tot = article_groups.aggregate(
        Sum('article_balance'))['article_balance__sum']  #
    article_acount = article_groups.count()

    return render(request, 'dbms/report/list/class-article-list.html',
                  locals())


# -----------------------客户分类统计---------------------#
def report_custom(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类统计表'
    CLASS_LIST = [
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '管户经理'),
        (45, '风控专员'),
    ]
    TERM_LIST = [
        (11, '在保'),
        (21, '授信'),
    ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name

    fication_dic = dict(FICATION_LIST)

    t_typ_dic = dict(TERM_LIST)
    t_typ = kwargs['t_typ']
    t_typ_t = t_typ_dic[t_typ]

    if t_typ == 11:  # 在保
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(amount__gt=0)
    else:
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(Q(credit_amount__gt=0) or Q(amount__gt=0))

    c_credit = custom_groups.aggregate(
        Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    c_g_value = custom_groups.aggregate(
        Sum('g_value'))['g_value__sum']  # 反担保价值
    c_flow = custom_groups.aggregate(
        Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    c_accept = custom_groups.aggregate(
        Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    c_back = custom_groups.aggregate(
        Sum('custom_back'))['custom_back__sum']  # 保函余额
    c_entrusted = custom_groups.aggregate(
        Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    c_petty = custom_groups.aggregate(
        Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    c_amount = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    article_count = custom_groups.aggregate(
        Count('credit_amount'))['credit_amount__count']  # 客户数
    c_credit_w = round(c_credit / 10000, 2)
    c_g_value_w = round(c_g_value / 10000, 2)
    c_flow_w = round(c_credit / 10000, 2)
    c_accept_w = round(c_credit / 10000, 2)
    c_back_w = round(c_back / 10000, 2)
    c_entrusted_w = round(c_entrusted / 10000, 2)
    c_petty_w = round(c_petty / 10000, 2)
    c_amount_w = round(c_amount / 10000, 2)
    if article_count > 0:
        s_credit = round(c_credit_w / article_count, 2)
        s_g_value = round(c_g_value_w / article_count, 2)
        s_flow = round(c_flow_w / article_count, 2)
        s_accept = round(c_accept_w / article_count, 2)
        s_back = round(c_back_w / article_count, 2)
        s_entrusted = round(c_entrusted / article_count, 2)
        s_petty = round(c_petty_w / article_count, 2)
        s_amount = round(c_amount_w / article_count, 2)

    article_balance_district = custom_groups.values(
        'district__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('district__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 区域

    article_balance_idustry = custom_groups.values(
        'idustry__cod_nam').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('idustry__cod_nam', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 行业

    article_balance_fication = custom_groups.values(
        'classification').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('classification', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('classification')  # 行业

    article_balance_depart = custom_groups.values(
        'managementor__department__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('managementor__department__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 部门
    article_balance_director = custom_groups.values(
        'managementor__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('managementor__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 管户经理

    article_balance_control = custom_groups.values(
        'controler__name').annotate(
        con=Count('id'), credit_amount=Sum('credit_amount'), custom_flow=Sum('custom_flow'),
        custom_accept=Sum('custom_accept'),g_value=Sum('g_value'),
        custom_back=Sum('custom_back'), entrusted_loan=Sum('entrusted_loan'),
        petty_loan=Sum('petty_loan'), amount=Sum('amount')). \
        values('controler__name', 'con', 'credit_amount', 'custom_flow', 'custom_accept','g_value',
               'custom_back', 'entrusted_loan', 'petty_loan', 'amount').order_by('-credit_amount')  # 管户经理
    td = datetime.date.today()
    return render(request, 'dbms/report/balance-class-custom.html', locals())


# -----------------------客户分类统计明细---------------------#
def report_custom_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户分类明细'
    CLASS_LIST = [
        (21, '区域'),
        (31, '行业'),
        (33, '分类'),
        (35, '部门'),
        (41, '管户经理'),
        (45, '风控专员'),
    ]
    TERM_LIST = [
        (11, '在保'),
        (21, '授信'),
    ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name
    fication_list = FICATION_LIST
    fication_dic = dict(fication_list)
    fication_wen = {}
    for fication in fication_list:
        fication_wen[fication[1]] = fication[0]

    c_typ_dic = dict(CLASS_LIST)
    t_typ_dic = dict(TERM_LIST)
    ss_value = request.GET.get('_cs')
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_this = c_typ_dic[c_typ]
    t_typ_this = t_typ_dic[t_typ]

    if t_typ == 11:  # 在保
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(amount__gt=0)
    else:
        custom_groups = models.Customes.objects.exclude(
            custom_state=99).filter(Q(credit_amount__gt=0) or Q(amount__gt=0))

    if c_typ == 21:
        custom_groups = custom_groups.filter(district__name=ss_value)
    elif c_typ == 31:
        custom_groups = custom_groups.filter(idustry__cod_nam=ss_value)
    elif c_typ == 33:
        custom_groups = custom_groups.filter(
            classification=fication_wen[ss_value])
    elif c_typ == 35:
        custom_groups = custom_groups.filter(
            managementor__department__name=ss_value)
    elif c_typ == 41:
        custom_groups = custom_groups.filter(managementor__name=ss_value)
    else:
        custom_groups = custom_groups.filter(controler__name=ss_value)
    custom_credit_tot = custom_groups.aggregate(
        Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    custom_g_value_tot = custom_groups.aggregate(
        Sum('g_value'))['g_value__sum']  # 反担保价值
    custom_acount_tot = custom_groups.aggregate(
        Sum('amount'))['amount__sum']  # 在保总额
    custom_acount = custom_groups.count()
    custom_credit_average = 0
    custom_g_value_average = 0
    custom_acount_average = 0
    custom_credit_tot_w = custom_credit_tot / 10000
    custom_g_value_tot_w = custom_g_value_tot / 10000
    custom_acount_tot_w = custom_acount_tot / 10000
    if custom_acount > 0:
        custom_credit_average = round(custom_credit_tot_w / custom_acount, 2)
        custom_g_value_average = round(custom_g_value_tot_w / custom_acount, 2)
        custom_acount_average = round(custom_acount_tot_w / custom_acount, 2)
    td = datetime.date.today()
    return render(request, 'dbms/report/list/class-custom-list.html', locals())


# -----------------------客户分类排名---------------------#
def top_custom(request, *args, **kwargs):  #
    # print(dir(request),request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户统计'
    CLASS_LIST = [(11, '在保'), (21, '授信')]
    TERM_LIST = [(7, '前五大'), (11, '前十大'), (21, '前二十大'), (99, '自定义金额')]
    CLASS_DIC = dict(CLASS_LIST)
    TERM_DIC = dict(TERM_LIST)

    industry_list = models.Industries.objects.all()
    lndustry_dic = {}
    for industry in industry_list:
        lndustry_dic[industry.code] = industry.name

    custom_groups = models.Customes.objects.exclude(custom_state=99)
    custom_groups_t = models.Customes.objects.exclude(custom_state=99)
    c_typ = kwargs['c_typ']
    t_typ = kwargs['t_typ']
    c_typ_c = CLASS_DIC[c_typ]
    t_typ_t = TERM_DIC[t_typ]
    screen_value = request.GET.get('ascreen')

    if c_typ == 11:  # 按在保
        custom_groups_t = custom_groups.filter(amount__gt=0)
        if t_typ == 7:  # (7, '前五大')
            custom_groups = custom_groups_t.order_by('-amount')[:
                                                                5]  # 在保前五名在保余额
            screen_value = custom_groups[4].amount
        elif t_typ == 11:  # (11, '前十大')
            custom_groups = custom_groups_t.order_by(
                '-amount')[:10]  # 在保前十名在保余额
            screen_value = custom_groups[9].amount
        elif t_typ == 21:  # (21, '前二十大')
            custom_groups = custom_groups_t.order_by(
                '-amount')[:20]  # 在保前二十名在保余额
            screen_value = custom_groups[19].amount
        else:  # (99, '自定义金额')
            if screen_value:
                custom_groups = custom_groups_t.filter(
                    amount__gte=screen_value).order_by('-amount')  # 按金额筛选
            else:
                screen_value = 0  #custom_groups_t.order_by('-amount')[:5][4].amount
                custom_groups = custom_groups_t.filter(
                    amount__gte=screen_value).order_by('-amount')  # 按金额筛选
    elif c_typ == 21:  # 按授信
        custom_groups_t = custom_groups.filter(
            Q(credit_amount__gt=0) or Q(amount__gt=0))
        if t_typ == 7:  # (7, '前五大')
            custom_groups = custom_groups_t.order_by(
                '-credit_amount')[:5]  # 在保前十名在保余额
            screen_value = custom_groups[4].credit_amount
        elif t_typ == 11:  # (11, '前十大')
            custom_groups = custom_groups_t.order_by(
                '-credit_amount')[:10]  # 在保前十名在保余额
            screen_value = custom_groups[9].credit_amount
        elif t_typ == 21:  # (21, '前二十大')
            custom_groups = custom_groups_t.order_by(
                '-credit_amount')[:20]  # 在保前二十名在保余额
            screen_value = custom_groups[19].credit_amount
        else:  # (99, '自定义金额')
            if screen_value:
                custom_groups = custom_groups_t.filter(
                    credit_amount__gte=screen_value).order_by(
                        '-credit_amount')  # 按金额筛选
            else:
                screen_value = 0  #custom_groups_t.order_by('-amount')[:5][4].amount
                custom_groups = custom_groups_t.filter(
                    credit_amount__gte=screen_value).order_by(
                        '-credit_amount')  # 按金额筛选
    c_credit = custom_groups.aggregate(
        Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    c_g_value = custom_groups.aggregate(
        Sum('g_value'))['g_value__sum']  # 反担保价值
    c_flow = custom_groups.aggregate(
        Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    c_accept = custom_groups.aggregate(
        Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    c_back = custom_groups.aggregate(
        Sum('custom_back'))['custom_back__sum']  # 保函余额
    c_entrusted = custom_groups.aggregate(
        Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    c_petty = custom_groups.aggregate(
        Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    c_amount = custom_groups.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    c_custom_count = custom_groups.aggregate(
        Count('credit_amount'))['credit_amount__count']  # 客户数

    t_credit = custom_groups_t.aggregate(
        Sum('credit_amount'))['credit_amount__sum']  # 授信总额
    t_g_value = custom_groups_t.aggregate(
        Sum('g_value'))['g_value__sum']  # 反担保价值
    t_flow = custom_groups_t.aggregate(
        Sum('custom_flow'))['custom_flow__sum']  # 流贷余额
    t_accept = custom_groups_t.aggregate(
        Sum('custom_accept'))['custom_accept__sum']  # 承兑余额
    t_back = custom_groups_t.aggregate(
        Sum('custom_back'))['custom_back__sum']  # 保函余额
    t_entrusted = custom_groups_t.aggregate(
        Sum('entrusted_loan'))['entrusted_loan__sum']  # 委贷余额
    t_petty = custom_groups_t.aggregate(
        Sum('petty_loan'))['petty_loan__sum']  # 小贷余额
    t_amount = custom_groups_t.aggregate(Sum('amount'))['amount__sum']  # 在保总额
    t_custom_count = custom_groups_t.aggregate(
        Count('credit_amount'))['credit_amount__count']  # 客户总数

    c_g_radio = 0
    t_g_radio = 0
    if c_credit > 0:
        c_g_radio = round(c_g_value / c_credit * 100, 2)
    if t_credit > 0:
        t_g_radio = round(t_g_value / t_credit * 100, 2)
    c_v_radio = 0
    t_v_radio = 0
    if c_amount > 0:
        c_v_radio = round(c_g_value / c_amount * 100, 2)
    if t_amount > 0:
        t_v_radio = round(t_g_value / t_amount * 100, 2)

    r_credit = 0
    r_g_value = 0
    r_g_radio = 0
    r_flow = 0
    r_accept = 0
    r_back = 0
    r_entrusted = 0
    r_petty = 0
    r_amount = 0
    r_custom_count = 0

    if t_credit > 0:
        r_credit = round(c_credit / t_credit * 100, 2)
    if t_g_value > 0:
        r_g_value = round(c_g_value / t_g_value * 100, 2)
    if t_g_radio > 0:
        r_g_radio = round(c_g_radio / t_g_radio * 100, 2)
    if t_flow > 0:
        r_flow = round(c_flow / t_flow * 100, 2)
    if t_accept > 0:
        r_accept = round(c_accept / t_accept * 100, 2)
    if t_back > 0:
        r_back = round(c_back / t_back * 100, 2)
    if t_entrusted > 0:
        r_entrusted = round(c_entrusted / t_entrusted * 100, 2)
    if t_petty > 0:
        r_petty = round(c_petty / t_petty * 100, 2)
    if t_amount > 0:
        r_amount = round(c_amount / t_amount * 100, 2)
    if t_custom_count > 0:
        r_custom_count = round(c_custom_count / t_custom_count * 100, 2)
    td = datetime.date.today()
    return render(request, 'dbms/report/top-class-custom.html', locals())


# -----------------------追偿分类统计---------------------#
def report_dun(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '追偿统计'
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    t_typ_dic = dict(TERM_LIST)
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_compensatory(t_typ, tf_r, tl_r)
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    compensatory_groups = models.Compensatories.objects.all()  # 代偿项目
    charge_groups = models.Charge.objects.all()  # 追偿费用
    retrieve_groups = models.Retrieve.objects.all()  # 案款回收

    if tf_r and tl_r:
        compensatory_groups = compensatory_groups.filter(
            compensatory_date__gte=tf_r, compensatory_date__lte=tl_r)  # 代偿项目
        charge_groups = charge_groups.filter(charge_date__gte=tf_r,
                                             charge_date__lte=tl_r)  # 追偿费用
        retrieve_groups = retrieve_groups.filter(
            retrieve_date__gte=tf_r, retrieve_date__lte=tl_r)  # 案款回收

    compensatory_amount = compensatory_groups.aggregate(
        Sum('compensatory_amount'))['compensatory_amount__sum']  # 代偿合计
    charge_amount = charge_groups.aggregate(
        Sum('charge_amount'))['charge_amount__sum']  # 追偿费用合计
    retrieve_amount = retrieve_groups.aggregate(
        Sum('retrieve_amount'))['retrieve_amount__sum']  # 案款回收合计

    compensatory_count = compensatory_groups.aggregate(
        Count('compensatory_amount'))['compensatory_amount__count']  # 项目数
    charge_count = charge_groups.aggregate(
        Count('charge_amount'))['charge_amount__count']  # 项目数
    retrieve_count = retrieve_groups.aggregate(
        Count('retrieve_amount'))['retrieve_amount__count']  # 项目数

    # charge_dun = charge_groups.values(
    #     'dun__compensatory__provide__notify__agree__lending__summary__custom__name').annotate(
    #     con=Count('charge_amount'), sum=Sum('charge_amount'), ). \
    #     values('dun__compensatory__provide__notify__agree__lending__summary__custom__name',
    #            'con', 'sum', ).order_by('-charge_amount')  # 追偿费用
    # retrieve_dun = retrieve_groups.values(
    #     'dun__compensatory__provide__notify__agree__lending__summary__custom__name').annotate(
    #     con=Count('retrieve_amount'), sum=Sum('retrieve_amount'), ). \
    #     values('dun__compensatory__provide__notify__agree__lending__summary__custom__name',
    #            'con', 'sum', ).order_by('-retrieve_amount')  # 案款回收

    return render(request, 'dbms/report/balance-class-dun.html', locals())


# -----------------------追偿分类统计明细---------------------#
def report_dun_dc_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '代偿分类明细'
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''
    dun_dc_groups = models.Compensatories.objects.all().order_by(
        '-compensatory_date').select_related('provide')

    t_typ_dic = dict(TERM_LIST)

    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_compensatory(t_typ, tf_r, tl_r)

    dun_dc_groups = models.Compensatories.objects.filter(
        compensatory_date__gte=tf_r, compensatory_date__lte=tl_r).order_by(
            '-compensatory_date').select_related('provide')
    dun_dc_capital_tot = dun_dc_groups.aggregate(
        Sum('compensatory_capital'))['compensatory_capital__sum']  #
    dun_dc_interest_tot = dun_dc_groups.aggregate(
        Sum('compensatory_interest'))['compensatory_interest__sum']  #
    dun_dc_default_tot = dun_dc_groups.aggregate(
        Sum('default_interest'))['default_interest__sum']  #
    dun_dc_amount_tot = dun_dc_groups.aggregate(
        Sum('compensatory_amount'))['compensatory_amount__sum']  #
    dun_dc_count = dun_dc_groups.count()

    return render(request, 'dbms/report/list/dun-dc-list.html', locals())


# -----------------------追偿费用分类统计明细---------------------#
def report_dun_fy_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '追偿费用分类明细'
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''

    t_typ_dic = dict(TERM_LIST)
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_compensatory(t_typ, tf_r, tl_r)

    dun_fy_groups = models.Charge.objects.filter(
        charge_date__gte=tf_r,
        charge_date__lte=tl_r).order_by('dun').select_related('dun')
    dun_charge_amount_tot = dun_fy_groups.aggregate(
        Sum('charge_amount'))['charge_amount__sum']  #
    dun_charge_count = dun_fy_groups.count()

    return render(request, 'dbms/report/list/dun-fy-list.html', locals())


# -----------------------追偿回款分类统计明细---------------------#
def report_dun_hk_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '追偿回款分类明细'
    TERM_LIST = [
        (0, '全部'),
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]
    '''CUSTOM_STATE_LIST = [(11, '担保客户'), (21, '反担保客户'), (99, '注销')]'''

    t_typ_dic = dict(TERM_LIST)
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_compensatory(t_typ, tf_r, tl_r)

    dun_hk_groups = models.Retrieve.objects.filter(
        retrieve_date__gte=tf_r,
        retrieve_date__lte=tl_r).order_by('dun').select_related('dun')
    dun_hk_amount_tot = dun_hk_groups.aggregate(
        Sum('retrieve_amount'))['retrieve_amount__sum']  #
    dun_hk_count = dun_hk_groups.count()

    return render(request, 'dbms/report/list/dun-hk-list.html', locals())


# -----------------------上会情况表---------------------#
def report_meeting_list(request, *args, **kwargs):  #
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '上会情况统计表'
    '''REVIEW_MODEL_LIST = [(1, '内审'), (2, '外审'), (5, '签批'), (21, '小贷-评审'), (25, '小贷-签批'), ]'''
    CLASS_LIST = models.Appraisals.REVIEW_MODEL_LIST
    TERM_LIST = [
        (1, '本年'),
        (2, '本季'),
        (3, '本月'),
        (4, '本周'),
        (11, '上年'),
        (99, '自定义'),
    ]

    t_typ_dic = dict(TERM_LIST)
    tf_r = request.GET.get('tf')
    tl_r = request.GET.get('tl')
    t_typ = kwargs['t_typ']
    t_typ_this = t_typ_dic[t_typ]
    tf_r, tl_r = tt_compensatory(t_typ, tf_r, tl_r)

    article_groups = models.Articles.objects.filter(
        appraisal_article__review_date__gte=tf_r,
        appraisal_article__review_date__lte=tl_r).order_by('review_date')
    article_groups_1 = article_groups.filter(appraisal_article__review_model=1)
    article_groups_2 = article_groups.filter(appraisal_article__review_model=2)
    appraisals_groups_1 = models.Appraisals.objects.filter(
        review_date__gte=tf_r, review_date__lte=tl_r, review_model=1)
    appraisals_groups_2 = models.Appraisals.objects.filter(
        review_date__gte=tf_r, review_date__lte=tl_r, review_model=2)

    ap_g_1_count = appraisals_groups_1.aggregate(
        Count('num'))['num__count']  # 内审会数
    ap_g_2_count = appraisals_groups_2.aggregate(
        Count('num'))['num__count']  # 外审会数

    a_g_1_count = article_groups_1.aggregate(
        Count('article_balance'))['article_balance__count']  # 内审项目数
    a_g_2_count = article_groups_2.aggregate(
        Count('article_balance'))['article_balance__count']  # 外审项目数

    article_renewal = article_groups.aggregate(
        Sum('renewal'))['renewal__sum']  # 续贷金额
    article_augment = article_groups.aggregate(
        Sum('augment'))['augment__sum']  # 新增金额
    article_amount = article_groups.aggregate(
        Sum('amount'))['amount__sum']  # 金额合计
    article_count = article_groups.aggregate(
        Count('article_balance'))['article_balance__count']  # 项目数
    article_amount_str = amount_s(article_amount)  # 元转换为万元并去掉小数点后面的零
    return render(request, 'dbms/report/meeting/meeting-article-meeting.html',
                  locals())


# -----------------------------项目反馈情况表------------------------------#
def article_feedback_list(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '项目反馈情况表'
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    article_list = models.Articles.objects.filter(
        article_state__in=[1, 2]).order_by(
            '-augment',
            'article_state',
        )
    article_list_count = article_list.count()
    td = datetime.date.today()
    augment_tot = article_list.aggregate(Sum('augment'))['augment__sum']  #
    renewal_tot = article_list.aggregate(Sum('renewal'))['renewal__sum']  #
    amount_tot = article_list.aggregate(Sum('amount'))['amount__sum']  #
    return render(request, 'dbms/report/meeting/meeting-article-feedback.html',
                  locals())


# -----------------------------风控落实跟踪表------------------------------#
def provide_follow_list(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '风控落实跟踪表'
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    provide_follow_list = models.Agrees.objects.filter(agree_state=31)  # 未落实
    provide_follow_list_count = provide_follow_list.count()
    td = datetime.date.today()
    agree_amount_sum = provide_follow_list.aggregate(
        Sum('agree_amount'))['agree_amount__sum']  #
    return render(request, 'dbms/report/meeting/meeting-follow-list.html',
                  locals())


# -----------------------------逾期归档情况表------------------------------#
def pig_overdue_list(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '逾期归档情况表'
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    date_20_leter = datetime.date.today() - datetime.timedelta(days=20)  # 15天前
    pigeonhole_overdue_list = models.Provides.objects.filter(
        implement__in=[1, 11, 21],
        provide_date__lt=date_20_leter).order_by('provide_date')  # 逾期归档
    pigeonhole_list_count = pigeonhole_overdue_list.count()
    td = datetime.date.today()
    provide_money_sum = pigeonhole_overdue_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    provide_balance_sum = pigeonhole_overdue_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    return render(request, 'dbms/report/meeting/meeting-pigeonhole-list.html',
                  locals())


# -----------------------------保后情况表------------------------------#
def review_plan_list(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '保后情况表'
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    review_plan_list = models.Customes.objects.filter(
        review_state__in=[1, 2]).order_by('review_plan_date', 'lately_date',
                                          'lately_date').select_related(
                                              'idustry', 'managementor',
                                              'controler')  #
    review_plan_count = review_plan_list.count()
    td = datetime.date.today()
    credit_amount_sum = review_plan_list.aggregate(
        Sum('credit_amount'))['credit_amount__sum']  #
    amount_sum = review_plan_list.aggregate(Sum('amount'))['amount__sum']  #
    return render(request, 'dbms/report/meeting/meeting-review-list.html',
                  locals())


# -----------------------------贷款风险分类汇总表------------------------------#
def fication_list(request, *args, **kwargs):  # 项目列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    PAGE_TITLE = '贷款风险分类汇总表'
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''

    provide_list_all = models.Provides.objects.filter(
        provide_balance__gt=0).order_by('fic_date')
    provide_first_date = provide_list_all.first().fic_date
    provide_list = provide_list_all.filter(
        provide_date__lte=provide_first_date).order_by('fic_date')
    provide_list_count = provide_list.count()
    provide_list = provide_list.order_by('-fication', 'due_date')
    td = datetime.date.today()
    provide_money_sum = provide_list.aggregate(
        Sum('provide_money'))['provide_money__sum']  #
    provide_balance_sum = provide_list.aggregate(
        Sum('provide_balance'))['provide_balance__sum']  #
    return render(request, 'dbms/report/meeting/fication-list.html', locals())
