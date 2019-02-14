from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count


# -----------------------代偿列表-------------------------#
@login_required
def compensatory(request, *args, **kwargs):  # 代偿列表
    print(__file__, '---->def compensatory')
    PAGE_TITLE = '代偿列表'

    dun_state_list = models.Compensatories.DUN_STATE_LIST
    compensatory_list = models.Compensatories.objects.filter(**kwargs).select_related('provide')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['provide__notify__agree__agree_num',  # 合同编号
                         'provide__notify__agree__branch__name',  # 放款银行
                         'provide__notify__agree__lending__summary__summary_num',  # 纪要编号
                         'provide__notify__agree__lending__summary__custom__name']  # 客户名称
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        compensatory_list = compensatory_list.filter(q)
    compensatory_amount = compensatory_list.count()  # 信息数目
    '''分页'''
    paginator = Paginator(compensatory_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/dun/compensatory.html', locals())


# -----------------------代偿查看-------------------------#
@login_required
def compensatory_scan(request, compensatory_id):
    pass


# -----------------------代偿添加ajax-------------------------#
@login_required
def compensatory_add_ajax(request):  # 代偿添加ajax
    print(__file__, '---->def compensatory_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    provide_list = models.Provides.objects.filter(id=post_data['provide_id'])
    provide_obj = provide_list.first()
    print('provide_obj:', provide_obj)

    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    form_compensatory_add = forms.FormCompensatoryAdd(post_data)
    if form_compensatory_add.is_valid():
        provide_status = provide_obj.provide_status
        if provide_status in [1, 21]:
            comp_cleaned = form_compensatory_add.cleaned_data
            compensatory_capital = comp_cleaned['compensatory_capital']  # 代偿本金金额
            compensatory_interest = comp_cleaned['compensatory_interest']
            default_interest = comp_cleaned['default_interest']
            compensatory_amount = compensatory_capital + compensatory_interest + default_interest
            provide_money = provide_obj.provide_money  # 放款金额
            provide_repayment_sum = provide_obj.provide_repayment_sum  # 还款总额
            provide_repayment_amount = provide_repayment_sum + compensatory_capital  # 累计还款额+代偿本金金额
            residual_amount = provide_money - provide_repayment_sum
            if compensatory_capital > residual_amount:
                response['status'] = False
                response['message'] = '代偿本金(%s)超过剩余未偿还本金(%s)，代偿失败!' % (compensatory_capital, residual_amount)
            else:
                try:
                    compensatory_date = comp_cleaned['compensatory_date']
                    with transaction.atomic():
                        compensatorye_obj = models.Compensatories.objects.create(
                            provide=provide_obj, compensatory_date=compensatory_date,
                            compensatory_capital=compensatory_capital, compensatory_interest=compensatory_interest,
                            default_interest=default_interest,
                            compensatory_amount=compensatory_amount, dun_state=1, compensator=request.user)
                        provide_list.update(provide_status=21)

                        repayment_obj = models.Repayments.objects.create(
                            provide=provide_obj, repayment_money=compensatory_capital, repaymentor=request.user,
                            repayment_date=compensatory_date)  # 创建还款记录

                        '''provide_repayment_sum，更新放款还款情况'''
                        provide_list.update(provide_repayment_sum=provide_repayment_amount)  # 放款，更新还款总额
                        '''notify_repayment_sum，更新放款通知还款情况'''
                        notify_list = models.Notify.objects.filter(provide_notify=provide_obj)  # 放款通知
                        notify_obj = notify_list.first()
                        notify_repayment_amount = \
                            models.Repayments.objects.filter(provide__notify=notify_obj).aggregate(
                                Sum('repayment_money'))['repayment_money__sum']  # 通知项下还款合计
                        notify_list.update(notify_repayment_sum=round(notify_repayment_amount, 2))  # 放款通知，更新还款总额
                        '''agree_repayment_sum，更新合同还款信息'''
                        agree_list = models.Agrees.objects.filter(notify_agree=notify_obj)  # 合同
                        agree_obj = agree_list.first()
                        agree_repayment_amount = models.Repayments.objects.filter(
                            provide__notify__agree=agree_obj).aggregate(
                            Sum('repayment_money'))['repayment_money__sum']  # 合同项下还款合计
                        agree_list.update(agree_repayment_sum=round(agree_repayment_amount, 2))  # 合同，更新还款总额
                        '''lending_repayment_sum，更新放款次序还款信息'''
                        lending_list = models.LendingOrder.objects.filter(agree_lending=agree_obj)  # 放款次序
                        lending_obj = lending_list.first()
                        lending_repayment_amount = models.Repayments.objects.filter(
                            provide__notify__agree__lending=lending_obj).aggregate(
                            Sum('repayment_money'))['repayment_money__sum']
                        lending_list.update(lending_repayment_sum=round(lending_repayment_amount, 2))  # 放款次序，更新还款总额
                        '''article_repayment_sum，更新项目还款信息'''
                        article_list = models.Articles.objects.filter(lending_summary=lending_obj)  # 项目
                        article_obj = article_list.first()
                        article_repayment_amount = models.Repayments.objects.filter(
                            provide__notify__agree__lending__summary=article_obj).aggregate(
                            Sum('repayment_money'))['repayment_money__sum']
                        article_list.update(article_repayment_sum=round(article_repayment_amount, 2))  # 项目，更新还款总额
                        '''更新客户余额信息,custom_flow,custom_accept,custom_back'''
                        '''更新银行余额信息,branch_flow,branch_accept,branch_back'''
                        custom_list = models.Customes.objects.filter(article_custom=article_obj)
                        branch_list = models.Branches.objects.filter(agree_branch=agree_obj)
                        provide_typ = provide_obj.provide_typ
                        if provide_typ == 1:
                            custom_list.update(custom_flow=F('custom_flow') - compensatory_capital)  # 客户，更新流贷余额
                            branch_list.update(branch_flow=F('branch_flow') - compensatory_capital)  # 放款银行，更新流贷余额
                        elif provide_typ == 11:
                            custom_list.update(custom_accept=F('custom_accept') - compensatory_capital)  # 客户，更新承兑余额
                            branch_list.update(branch_accept=F('branch_accept') - compensatory_capital)  # 放款银行，更新承兑余额
                        else:
                            custom_list.update(custom_back=F('custom_back') - compensatory_capital)  # 客户，更新保函余额
                            branch_list.update(branch_back=F('branch_back') - compensatory_capital)  # 放款银行，更新保函余额

                    response['message'] = '代偿添加成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '代偿添加失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '状态为：%s，代偿添加失败' % provide_status
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_compensatory_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
