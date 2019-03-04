from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority

# -----------------------客户管理-------------------------#
@login_required
def custom(request, *args, **kwargs):  # 委托合同列表
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
    custom_list = models.Customes.objects.filter(**kwargs).order_by('-credit_amount', '-name')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['name', 'contact_addr', 'linkman', 'contact_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
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


# -----------------------------客户预览------------------------------#
@login_required
def custom_scan(request, custom_id):  # 项目预览
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    PAGE_TITLE = '客户预览'

    custom_obj = models.Customes.objects.get(id=custom_id)

    form_date = {
        'name': custom_obj.name,
        'short_name': custom_obj.short_name,
        'contact_addr': custom_obj.contact_addr,
        'linkman': custom_obj.linkman,
        'contact_num': custom_obj.contact_num}
    form_custom_edit = forms.CustomEditForm(initial=form_date)
    idustry_id = custom_obj.company_custome.idustry.id
    if custom_obj.genre == 1:
        form_date = {
            'idustry': idustry_id,
            'district': custom_obj.company_custome.district,
            'capital': custom_obj.company_custome.capital,
            'registered_addr': custom_obj.company_custome.registered_addr,
            'representative': custom_obj.company_custome.representative}
        form_custom_c_add = forms.CustomCAddForm(initial=form_date)
    else:
        form_date = {
            'license_num': custom_obj.person_custome.license_num,
            'license_addr': custom_obj.person_custome.license_addr}
        form_custom_p_add = forms.CustomPAddForm(initial=form_date)
    form_shareholder_add = forms.FormShareholderAdd()
    form_article_add = forms.ArticlesAddForm()
    form_spouse_add = forms.FormCustomSpouseAdd()

    review_custom_list = custom_obj.review_custom.all().filter().order_by('-review_date', '-review_plan_date')
    article_custom_list = custom_obj.article_custom.all().order_by('-build_date')

    return render(request, 'dbms/custom/custom-scan.html', locals())
