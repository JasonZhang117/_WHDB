from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required


# -----------------------委托合同列表---------------------#
@login_required
def agree(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    form_agree_add = forms.AgreeAddForm()

    agree_state_list = models.Agrees.AGREE_STATE_LIST
    agree_list = models.Agrees.objects.filter(**kwargs).select_related(
        'lending', 'branch').order_by('-agree_num')

    ####分页信息###
    paginator = Paginator(agree_list, 10)
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
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    counter_typ_custom = [1, 2]
    counter_typ_h_g = [11, 12, 52, 53]

    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_lending_obj = agree_obj.lending

    custom_c_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=1).values_list('id', 'name')
    custom_p_lending_list = models.Customes.objects.filter(
        lending_custom__sure__lending=agree_lending_obj, genre=2).values_list('id', 'name')
    warrants_h_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=1).values_list('id', 'warrant_num')
    warrants_g_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=2).values_list('id', 'warrant_num')
    warrants_r_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=3).values_list('id', 'warrant_num')
    warrants_s_lending_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=agree_lending_obj, warrant_typ=4).values_list('id', 'warrant_num')
    from_counter = forms.AddCounterForm()

    return render(request, 'dbms/agree/agree-scan.html', locals())


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
            print('lending_obj:', lending_obj)
            print('type(lending_obj):', type(lending_obj))
            agree_amount = agree_add_cleaned['agree_amount']
            guarantee_typ = agree_add_cleaned['guarantee_typ']
            agree_copies = agree_add_cleaned['agree_copies']

            ###判断合同情况：
            if agree_amount > lending_obj.order_amount:
                response['status'] = False
                msg = '该项目本次发放额度最高为%s,合同金额超过审批额度！！！' % lending_obj.amount
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
    if agree_state_counter in [1, 7]:
        if counter_typ in [1, 2]:  # 保证反担保
            if counter_typ == 1:
                custom_list = post_data['custom_c']
            else:
                custom_list = post_data['custom_p']
            try:
                with transaction.atomic():
                    counter_obj = models.Counters.objects.create(
                        counter_num=counter_num, agree=agree_obj, counter_typ=counter_typ,
                        counter_copies=counter_copies, counter_state=1, counter_buildor=request.user)
                    counter_assure_obj = models.CountersAssure.objects.create(counter=counter_obj)
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
                        counter_copies=counter_copies, counter_state=1, counter_buildor=request.user)
                    counter_warrant_obj = models.CountersWarrants.objects.create(counter=counter_obj)
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


# -------------------------合同预览-------------------------#
@login_required
def agree_preview(request, agree_id):
    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request,
                  'dbms/agree/agree-preview.html', locals())
