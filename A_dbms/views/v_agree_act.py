from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.urls import resolve, reverse
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# ---------------------------合同签批ajax----------------------------#
@login_required
def agree_sign_ajax(request):  # 添加合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    agree_id = post_data['agree_id']
    agree_list = models.Agrees.objects.filter(id=agree_id)
    agree_obj = agree_list.first()
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '已落实，未放款'), (41, '已落实，放款'),
                        (42, '未落实，放款'), (51, '待变更'), (61, '已解保'), (99, '已作废'))'''
    if agree_obj.agree_state == 11:
        form_agree_sign = forms.FormAgreeSign(post_data, request.FILES)
        if form_agree_sign.is_valid():
            agree_sign_cleaned = form_agree_sign.cleaned_data
            try:
                agree_list.update(agree_state=21, agree_sign_date=agree_sign_cleaned['agree_sign_date'])
                response['message'] = '合同签批成功：%s！' % agree_obj.agree_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同签批失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agree_sign.errors
    else:
        response['status'] = False
        response['message'] = '合同状态为：%s，签批失败！！！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ---------------------------添加合同ajax----------------------------#
@login_required
def agree_add_ajax(request):  # 添加合同
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    lending_obj = models.LendingOrder.objects.get(id=post_data['lending'])
    article_state_lending = lending_obj.summary.article_state
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    if article_state_lending in [4, 5, 51, 61]:
        # form_agree_add = forms.AgreeAddForm(post_data, request.FILES)
        form_agree_add = forms.ArticleAgreeAddForm(post_data, request.FILES)
        if form_agree_add.is_valid():
            agree_add_cleaned = form_agree_add.cleaned_data
            # lending_obj = agree_add_cleaned['lending']
            agree_amount = agree_add_cleaned['agree_amount']
            guarantee_typ = agree_add_cleaned['guarantee_typ']
            agree_copies = agree_add_cleaned['agree_copies']
            branch_id = agree_add_cleaned['branch']
            agree_typ = agree_add_cleaned['agree_typ']
            branche_obj = models.Branches.objects.get(id=branch_id)
            cooperator_up_scale = branche_obj.cooperator.up_scale
            '''AGREE_TYP_LIST = ((1, '单笔'), (2, '最高额'), (3, '保函'))'''
            order_amount = lending_obj.order_amount  # 放款次序金额
            if agree_typ == 2:  # (2, '最高额')
                order_amount_up = order_amount * (1 + cooperator_up_scale)  # 最高允许的合同金额
            else:
                order_amount_up = order_amount
            amount_limit = agree_add_cleaned['amount_limit']
            ###判断合同金额情况：
            if agree_amount > order_amount_up:
                response['status'] = False
                response['message'] = '合同金额（%s）超过审批额度（%s）！' % (agree_amount, order_amount)
                result = json.dumps(response, ensure_ascii=False)
                return HttpResponse(result)
            elif amount_limit > order_amount:
                response['status'] = False
                response['message'] = '放款限额（%s）超过审批额度（%s）！' % (amount_limit, order_amount,)
                result = json.dumps(response, ensure_ascii=False)
                return HttpResponse(result)

            ###合同年份(agree_year)
            t = time.gmtime(time.time())  # 时间戳--》元组
            agree_year = t.tm_year
            ###合同序号(order)
            order_max_x = models.Agrees.objects.filter(
                agree_date__year=agree_year).count() + 1

            if order_max_x < 10:
                agree_order = '00%s' % order_max_x
            elif order_max_x < 100:
                agree_order = '0%s' % order_max_x
            else:
                agree_order = '%s' % order_max_x

            ###评审会编号拼接
            '''成武担[2016]018④W6-1'''
            agree_num_prefix = "成武担[%s]%s%s" % (agree_year, agree_order, guarantee_typ)
            agree_num = "%sW%s-1" % (agree_num_prefix, agree_copies)
            try:
                agree_obj = models.Agrees.objects.create(
                    agree_num=agree_num, num_prefix=agree_num_prefix, lending=lending_obj,
                    branch_id=branch_id, agree_typ=agree_typ,
                    agree_term=agree_add_cleaned['agree_term'],
                    amount_limit=amount_limit,
                    agree_amount=agree_amount, guarantee_typ=guarantee_typ, agree_copies=agree_copies,
                    agree_buildor=request.user)
                response['skip'] = "/dbms/agree/scan/%s" % agree_obj.id
                response['message'] = '成功创建合同：%s！' % agree_obj.agree_num

            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同创建失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agree_add.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，合同创建失败！！！' % article_state_lending
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -------------------------添加反担保合同ajax-------------------------#
@login_required
def counter_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    agree_id = post_data['agree_id']
    counter_typ = int(post_data['counter_typ'])
    agree_obj = models.Agrees.objects.get(id=agree_id)
    from_counter_add = forms.AddCounterForm(post_data)

    counter_prefix = agree_obj.num_prefix
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if counter_typ == 1:
        counter_typ_n = 'X'
        counter_copies = 3
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ=counter_typ).count() + 1
    elif counter_typ == 2:
        counter_typ_n = 'G'
        counter_copies = 2
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ=counter_typ).count() + 1
    elif counter_typ in [11, 12, 13, 14, 15]:
        counter_typ_n = 'D'
        counter_copies = 4
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[11, 12, 13, 14, 15]).count() + 1
    elif counter_typ in [31, 32, 33, 34, 41]:
        counter_typ_n = 'Z'
        counter_copies = 4
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33, 34, 41]).count() + 1
    elif counter_typ in [51, 52, 53]:
        counter_typ_n = 'Y'
        counter_copies = 3
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[51, 52, 53]).count() + 1
    else:
        counter_typ_n = ''
        counter_copies = 2
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33]).count() + 1
    '''成武担[2016]018④W6-1'''
    counter_num = '%s%s%s-%s' % (counter_prefix, counter_typ_n, counter_copies, counter_max)

    agree_state_counter = agree_obj.agree_state
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销'))'''
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if agree_state_counter in [11, 51]:
        if counter_typ in [1, 2]:  # 保证反担保
            if counter_typ == 1:
                custom_list = post_data['custom_c']
            else:
                custom_list = post_data['custom_p']
            try:
                with transaction.atomic():
                    counter_obj = models.Counters.objects.create(
                        counter_num=counter_num, agree=agree_obj, counter_typ=counter_typ,
                        counter_copies=counter_copies, counter_buildor=request.user)
                    counter_assure_obj = models.CountersAssure.objects.create(
                        counter=counter_obj, counter_assure_buildor=request.user)
                    for custom in custom_list:
                        counter_assure_obj.custome.add(custom)
                response['message'] = '成功创建反担保合同：%s！' % counter_obj.counter_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同创建失败：%s' % str(e)
        else:
            if counter_typ in [11, 52]:  # (11, '房产抵押'),(52, '房产预售'),
                warrant_list = post_data['house']
            elif counter_typ in [12, 53]:  # (12, '土地抵押'),(53, '土地预售')
                warrant_list = post_data['ground']
            elif counter_typ == 14:  # (14, '在建工程抵押')
                warrant_list = post_data['coustruct']
            elif counter_typ == 31:  # (31, '应收质押')
                warrant_list = post_data['receivable']
            elif counter_typ in [32, 51]:  # (32, '股权质押'), (51, '股权预售')
                warrant_list = post_data['stock']
            elif counter_typ == 33:  # (33, '票据质押')
                warrant_list = post_data['draft']
            elif counter_typ == 15:  # (15, '车辆抵押')
                warrant_list = post_data['vehicle']
            elif counter_typ in [13, 34]:  # (13, '动产抵押'), (34, '动产质押')
                warrant_list = post_data['chattel']
            elif counter_typ == 41:  # (41, '其他权利质押')
                warrant_list = post_data['other']
            try:
                with transaction.atomic():
                    counter_obj = models.Counters.objects.create(
                        counter_num=counter_num, agree=agree_obj, counter_typ=counter_typ,
                        counter_copies=counter_copies, counter_buildor=request.user)
                    counter_warrant_obj = models.CountersWarrants.objects.create(
                        counter=counter_obj, counter_warrant_buildor=request.user)
                    for warrant in warrant_list:
                        counter_warrant_obj.warrant.add(warrant)
                response['message'] = '成功创建反担保合同：%s！' % counter_obj.counter_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '委托合同状态为：%s，反担保合同创建失败！！！' % agree_state_counter
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除反担保合同ajax-------------------------#
@login_required
def counter_del_ajax(request):  # 删除反担保合同ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    agree_id = post_data['agree_id']
    counter_id = post_data['counter_id']

    agree_obj = models.Agrees.objects.get(id=agree_id)
    counter_obj = models.Counters.objects.get(id=counter_id)
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if counter_obj.counter_typ in [1, 2]:
        counter_counter_obj = counter_obj.assure_counter
    else:
        counter_counter_obj = counter_obj.warrant_counter
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    if agree_obj.agree_state in [11, 51]:
        try:
            with transaction.atomic():
                counter_counter_obj.delete()  # 删除保证反担保合同
                counter_obj.delete()  # 删除反担保合同
            response['message'] = '反担保合同删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '反担保合同删除失败:%s！' % str(e)
    else:
        response['status'] = False
        response['message'] = '委托担保合同状态为%s，无法删除反担保合同！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
