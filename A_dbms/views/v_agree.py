from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
import datetime


# -----------------------委托合同列表---------------------#
@login_required
def agree(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    PAGE_TITAL = '合同管理'
    operate_agree_add = True
    '''模态框'''
    form_agree_add = forms.AgreeAddForm()  # 合同添加
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
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
    '''分页'''
    paginator = Paginator(agree_list, 18)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/agree/agree.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
def agree_scan(request, agree_id):  # 查看合同
    print(__file__, '---->def agree_scan')
    APPLICATION = 'agree_scan'
    PAGE_TITLE = '合同详情'
    COUNTER_TYP_CUSTOM = [1, 2]

    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
    print('warrant_agree_list:', warrant_agree_list)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=1).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=5).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num')
    print(custom_c_lending_list, custom_p_lending_list, warrants_h_lending_list, warrants_g_lending_list,
          warrants_r_lending_list, warrants_s_lending_list)
    from_counter = forms.AddCounterForm()

    today_str = time.strftime("%Y-%m-%d", time.gmtime())
    form_agree_sign_data = {'agree_sign_date': str(today_str)}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


# -----------------------------查看合同------------------------------#
@login_required
def agree_scan_counter(request, agree_id, counter_id):  # 查看合同
    print(__file__, '---->def agree_scan_counter')
    APPLICATION = 'agree_scan_counter'
    PAGE_TITLE = '担保合同'
    COUNTER_TYP_CUSTOM = [1, 2]

    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    warrant_agree_list = models.Warrants.objects.filter(counter_warrant__counter__agree=agree_obj)
    print('warrant_agree_list:', warrant_agree_list)
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).exclude(
        counter_custome__counter__agree=agree_obj).values_list('id', 'name').order_by('name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=1).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=2).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=11).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=21).exclude(
        counter_warrant__counter__agree=agree_obj).values_list('id', 'warrant_num').order_by('warrant_num')
    print(custom_c_lending_list, custom_p_lending_list, warrants_h_lending_list, warrants_g_lending_list,
          warrants_r_lending_list, warrants_s_lending_list)
    from_counter = forms.AddCounterForm()

    today_str = time.strftime("%Y-%m-%d", time.gmtime())
    form_agree_sign_data = {'agree_sign_date': str(today_str)}
    form_agree_sign = forms.FormAgreeSign(initial=form_agree_sign_data)
    return render(request, 'dbms/agree/agree-scan.html', locals())


# ---------------------------合同签批ajax----------------------------#
@login_required
def agree_sign_ajax(request):  # 添加合同
    print(__file__, '---->def agree_add_ajax')
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
    print(__file__, '---->def agree_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    lending_id = post_data['lending']
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    article_state_lending = lending_obj.summary.article_state
    print('article_state_lending:', article_state_lending)
    if article_state_lending == 5:
        form_agree_add = forms.AgreeAddForm(post_data, request.FILES)
        if form_agree_add.is_valid():
            agree_add_cleaned = form_agree_add.cleaned_data
            lending_obj = agree_add_cleaned['lending']
            agree_amount = agree_add_cleaned['agree_amount']
            guarantee_typ = agree_add_cleaned['guarantee_typ']
            agree_copies = agree_add_cleaned['agree_copies']

            ###判断合同情况：
            if agree_amount > lending_obj.order_amount:
                response['status'] = False
                msg = '该项目本次发放额度最高为%s,合同金额超过审批额度！！！' % lending_obj.order_amount
                response['message'] = msg
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
            print('agree_num_prefix', agree_num_prefix)
            agree_num = "%sW%s-1" % (agree_num_prefix, agree_copies)
            print('agree_num', agree_num)
            try:
                agree_obj = models.Agrees.objects.create(
                    agree_num=agree_num, num_prefix=agree_num_prefix, lending=lending_obj,
                    branch=agree_add_cleaned['branch'], agree_typ=agree_add_cleaned['agree_typ'],
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
    print(__file__, '---->def counter_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    agree_id = post_data['agree_id']
    counter_typ = int(post_data['counter_typ'])
    agree_obj = models.Agrees.objects.get(id=agree_id)
    print('agree_obj:', agree_obj)
    from_counter_add = forms.AddCounterForm(post_data)

    counter_prefix = agree_obj.num_prefix
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
    elif counter_typ in [31, 32, 33]:
        counter_typ_n = 'Z'
        counter_copies = 4
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33]).count() + 1
    else:
        counter_typ_n = ''
        counter_copies = 2
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33]).count() + 1
    '''成武担[2016]018④W6-1'''
    counter_num = '%s%s%s-%s' % (counter_prefix, counter_typ_n, counter_copies, counter_max)

    agree_state_counter = agree_obj.agree_state
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '已落实，未放款'), (41, '已落实，放款'),
                        (42, '未落实，放款'), (51, '待变更'), (61, '已解保'), (99, '已作废'))'''
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
            if counter_typ in [11, 52]:
                warrant_list = post_data['house']
            elif counter_typ in [12, 53]:
                warrant_list = post_data['ground']
            elif counter_typ == 31:
                warrant_list = post_data['receivable']
            elif counter_typ == 32:
                warrant_list = post_data['stock']
            else:
                warrant_list = post_data['ground']
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
    print(__file__, '---->def counter_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    agree_id = post_data['agree_id']
    counter_id = post_data['counter_id']

    agree_obj = models.Agrees.objects.get(id=agree_id)
    counter_obj = models.Counters.objects.get(id=counter_id)
    assure_counter_obj = counter_obj.assure_counter
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '已落实，未放款'), (41, '已落实，放款'),
                        (42, '未落实，放款'), (51, '待变更'), (61, '已解保'), (99, '已作废'))'''
    if agree_obj.agree_state in [11, 51]:
        try:
            with transaction.atomic():
                assure_counter_obj.delete()  # 删除保证反担保合同
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


# -------------------------合同预览-------------------------#
@login_required
def agree_preview(request, agree_id):
    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request,
                  'dbms/agree/agree-preview.html', locals())
