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
            compensatory_capital = comp_cleaned['compensatory_capital']
            compensatory_interest = comp_cleaned['compensatory_interest']
            default_interest = comp_cleaned['default_interest']
            compensatory_amount = compensatory_capital + compensatory_interest + default_interest
            provide_money = provide_obj.provide_money  # 放款金额
            provide_repayment_sum = provide_obj.provide_repayment_sum  # 还款总额
            residual_amount = provide_money - provide_repayment_sum
            if compensatory_capital > residual_amount:
                response['status'] = False
                response['message'] = '代偿本金(%s)超过剩余未偿还本金(%s)，代偿失败：%s' % (compensatory_capital, residual_amount)
            else:
                try:
                    with transaction.atomic():
                        compensatorye_obj = models.Compensatories.objects.create(
                            provide=provide_obj, compensatory_date=comp_cleaned['compensatory_date'],
                            compensatory_capital=compensatory_capital, compensatory_interest=compensatory_interest,
                            default_interest=default_interest,
                            compensatory_amount=compensatory_amount, dun_state=1, compensator=request.user)
                        provide_list.update(provide_status=21)
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
