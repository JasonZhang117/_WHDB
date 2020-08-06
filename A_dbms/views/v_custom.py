from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import (authority, custom_list_screen, custom_right)


# -----------------------客户管理-------------------------#
@login_required
@authority
def custom(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户管理'
    '''模态框'''
    form_custom_add = forms.CustomAddForm()  # 客户添加
    form_custom_c_add = forms.CustomCAddForm()  # 企业客户添加
    form_custom_p_add = forms.CustomPAddForm()  # 个人客户添加
    '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
    genre_list = models.Customes.GENRE_LIST  # 筛选条件
    '''筛选'''
    custom_list = models.Customes.objects.filter(**kwargs).order_by(
        '-credit_amount', '-name')
    custom_list = custom_list_screen(custom_list, request)
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'name', 'short_name', 'managementor__name', 'idustry__name',
            'district__name', 'contact_addr', 'linkman', 'contact_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        custom_list = custom_list.filter(q)
    '''分页'''
    paginator = Paginator(custom_list, 19)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    return render(request, 'dbms/custom/custom.html', locals())


# -----------------------企业客户列表-------------------------#
@login_required
@authority
def custom_c(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '企业客户'
    '''筛选'''
    custom_list = models.Customes.objects.filter(**kwargs).order_by(
        '-credit_amount', '-name')
    custom_list = custom_list.filter(genre=1,
                                     credit_amount__gt=0).select_related(
                                         'managementor', 'idustry')
    custom_list = custom_list_screen(custom_list, request)
    for custom_obj in custom_list:
        credit_code = custom_obj.company_custome.credit_code
        if credit_code:
            try:
                if int(credit_code) > 0:
                    credit_code_str = "%s%s" % ("'", credit_code)
                    models.CustomesC.objects.filter(custome=custom_obj).update(
                        credit_code=credit_code_str)
            except Exception as e:
                pass
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'name', 'short_name', 'managementor__name', 'idustry__name',
            'district__name', 'contact_addr', 'linkman', 'contact_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        custom_list = custom_list.filter(q)
    '''分页'''
    paginator = Paginator(custom_list, 200)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    return render(request, 'dbms/custom/custom-c.html', locals())


# -----------------------个人客户列表-------------------------#
@login_required
@authority
def custom_p(request, *args, **kwargs):  # 委托合同列表
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '企业客户'
    '''筛选'''
    custom_list = models.Customes.objects.filter(**kwargs).order_by(
        '-credit_amount', '-name')
    custom_list = custom_list.filter(genre=2,
                                     credit_amount__gt=0).select_related(
                                         'managementor', 'idustry')
    custom_list = custom_list_screen(custom_list, request)
    for custom_obj in custom_list:
        credit_code = custom_obj.person_custome.license_num
        if credit_code:
            print(credit_code)
            try:
                if int(credit_code) > 0:
                    credit_code_str = "%s%s" % ("'", credit_code)
                    print(credit_code_str)
                    models.CustomesC.objects.filter(custome=custom_obj).update(
                        license_num=credit_code_str)
            except Exception as e:
                pass
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = [
            'name', 'short_name', 'managementor__name', 'idustry__name',
            'district__name', 'contact_addr', 'linkman', 'contact_num'
        ]
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key.strip()))
        custom_list = custom_list.filter(q)
    '''分页'''
    paginator = Paginator(custom_list, 50)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)
    return render(request, 'dbms/custom/custom-p.html', locals())


# -----------------------------客户预览------------------------------#
@login_required
@authority
@custom_right
def custom_scan(request, custom_id):  # 项目预览
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户预览'

    custom_obj = models.Customes.objects.get(id=custom_id)

    custom_edit_data = {
        'name': custom_obj.name,
        'short_name': custom_obj.short_name,
        'contact_addr': custom_obj.contact_addr,
        'linkman': custom_obj.linkman,
        'contact_num': custom_obj.contact_num,
        'idustry': custom_obj.idustry,
        'district': custom_obj.district,
    }
    form_custom_edit = forms.CustomEditForm(initial=custom_edit_data)
    custom_change_data = {
        'custom_typ': custom_obj.custom_typ,
        'credit_amount': custom_obj.credit_amount,
        'custom_state': custom_obj.custom_state,
        'managementor': custom_obj.managementor,
        'controler': custom_obj.controler,
    }
    form_custom_change = forms.CustomChangeForm(initial=custom_change_data)
    custom_controler_data = {
        'controler': custom_obj.controler,
    }
    form_controler_change = forms.CustomControlerForm(
        initial=custom_controler_data)
    if custom_obj.genre == 1:
        form_date = {
            'decisionor': custom_obj.company_custome.decisionor,
            'credit_code': custom_obj.company_custome.credit_code,
            'custom_nature': custom_obj.company_custome.custom_nature,
            'typing': custom_obj.company_custome.typing,
            'capital': custom_obj.company_custome.capital,
            'registered_addr': custom_obj.company_custome.registered_addr,
            'representative': custom_obj.company_custome.representative
        }
        form_custom_c_add = forms.CustomCAddForm(initial=form_date)
    else:
        form_date = {
            'license_num': custom_obj.person_custome.license_num,
            'license_addr': custom_obj.person_custome.license_addr,
            'marital_status': custom_obj.person_custome.marital_status
        }
        form_custom_p_add = forms.CustomPAddForm(initial=form_date)
    form_shareholder_add = forms.FormShareholderAdd()
    form_trustee_add = forms.FormTrusteeAdd()
    form_article_add = forms.ArticlesAddForm()
    form_spouse_add = forms.FormCustomSpouseAdd()
    review_custom_list = custom_obj.review_custom.all().filter().order_by(
        '-review_date', '-review_plan_date')
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销'))'''
    article_custom_list = custom_obj.article_custom.all().order_by(
        '-build_date')[0:12]
    return render(request, 'dbms/custom/custom-scan.html', locals())
