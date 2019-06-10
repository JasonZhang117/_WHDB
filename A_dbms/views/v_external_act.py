from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.db.models import Avg, Min, Sum, Max, Count
from django.db import transaction
from django.db.models import Sum, Max, Count
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------添加合作协议ajax-------------------------#
@login_required
@authority
def agreement_add_ajax(request):  # 合作协议ajax
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    cooperator_list = models.Cooperators.objects.filter(id=post_data['cooperator_id'])
    cooperator_obj = cooperator_list.first()
    cooperator_state = cooperator_obj.cooperator_state
    '''COOPERATOR_STATE_LIST = ((1, '正常'), (11, '注销'))'''
    form_agreement_add = forms.FormAgreementAdd(post_data)
    if form_agreement_add.is_valid():
        if cooperator_state == 1:
            agreement_cleaned = form_agreement_add.cleaned_data
            flow_credit = round(agreement_cleaned['flow_credit'], 2)
            flow_limit = round(agreement_cleaned['flow_limit'], 2)
            back_credit = round(agreement_cleaned['back_credit'], 2)
            back_limit = round(agreement_cleaned['back_limit'], 2)
            credit_date = agreement_cleaned['credit_date']
            due_date = agreement_cleaned['due_date']
            try:
                with transaction.atomic():
                    agreement_obj = models.Agreements.objects.create(
                        cooperator=cooperator_obj,
                        flow_credit=flow_credit, flow_limit=flow_limit,
                        back_credit=back_credit, back_limit=back_limit,
                        credit_date=credit_date, due_date=due_date,
                        agreementor=request.user)
                    cooperator_list.update(
                        flow_credit=flow_credit, flow_limit=flow_limit,
                        back_credit=back_credit, back_limit=back_limit,
                        credit_date=credit_date, due_date=due_date)
                response['message'] = '合作协议添加成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '合作协议添加失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '状态为：%s，合作协议添加失败' % cooperator_state
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_agreement_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
