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


# -----------------------客户添加-------------------------#
@login_required
@authority
def custom_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    form_custom_add = forms.CustomAddForm(post_data)
    if form_custom_add.is_valid():
        custom_add_data = form_custom_add.cleaned_data
        genre = custom_add_data['genre']
        if genre == 1:
            form_custom_c_add = forms.CustomCAddForm(post_data)
            if form_custom_c_add.is_valid():
                custom_c_data = form_custom_c_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_obj = models.Customes.objects.create(
                            name=custom_add_data['name'], genre=genre,
                            short_name=custom_add_data['short_name'],
                            # counter_only=custom_add_data['counter_only'],
                            contact_addr=custom_add_data['contact_addr'],
                            linkman=custom_add_data['linkman'],
                            contact_num=custom_add_data['contact_num'],
                            custom_buildor=request.user)
                        custom_c_obj = models.CustomesC.objects.create(
                            custome=custom_obj,
                            idustry=custom_c_data['idustry'],
                            district=custom_c_data['district'],
                            decisionor=custom_c_data['decisionor'],
                            capital=custom_c_data['capital'],
                            registered_addr=custom_c_data['registered_addr'],
                            representative=custom_c_data['representative'])
                    response['message'] = '客户：%s，创建成功。请继续添加股权信息！' % custom_add_data['name']
                    response['skip'] = "/dbms/custom/scan/%s/" % custom_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_c_add.errors
        elif genre == 2:
            form_custom_p_add = forms.CustomPAddForm(post_data)
            if form_custom_p_add.is_valid():
                custom_p_data = form_custom_p_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_obj = models.Customes.objects.create(
                            name=custom_add_data['name'], genre=genre,
                            short_name=custom_add_data['short_name'],
                            # counter_only=custom_add_data['counter_only'],
                            contact_addr=custom_add_data['contact_addr'],
                            linkman=custom_add_data['linkman'],
                            contact_num=custom_add_data['contact_num'],
                            custom_buildor=request.user)
                        custom_p_obj = models.CustomesP.objects.create(
                            custome=custom_obj, license_num=custom_p_data['license_num'],
                            license_addr=custom_p_data['license_addr'])
                        response['message'] = '客户：%s，创建成功。请继续添加配偶信息！' % custom_add_data['name']
                        response['skip'] = "/dbms/custom/scan/%s/" % custom_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_p_add.errors
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_custom_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------股权信息添加-------------------------#
@login_required
@authority
def shareholder_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    custom_id = post_data['custom_id']
    custom_obj = models.Customes.objects.get(id=custom_id)

    form_shareholder_add = forms.FormShareholderAdd(post_data)
    if form_shareholder_add.is_valid():
        shareholder_add_data = form_shareholder_add.cleaned_data
        custom_c_obj = custom_obj.company_custome
        shareholder_ratio_amount = custom_c_obj.shareholder_custom_c.all().aggregate(Sum('shareholding_ratio'))
        shareholding_ratio = shareholder_add_data['shareholding_ratio']
        shareholder_ratio_a = shareholder_ratio_amount['shareholding_ratio__sum']
        if shareholder_ratio_a:
            ratio_amount = shareholder_ratio_a + shareholding_ratio
        else:
            ratio_amount = shareholding_ratio
        if ratio_amount > 100:
            response['status'] = False
            response['message'] = '股权比合计操过100%，股权信息创建失败！！！'
        else:
            try:
                shareholder_obj = models.Shareholders.objects.create(
                    custom=custom_c_obj, shareholder_name=shareholder_add_data['shareholder_name'],
                    invested_amount=shareholder_add_data['invested_amount'],
                    shareholding_ratio=shareholding_ratio,
                    shareholderor=request.user)
            except Exception as e:
                response['status'] = False
                response['message'] = '股东信息创建失败：%s' % str(e)
            response['message'] = '股东信息创建成功！！！'
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_shareholder_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除股东信息ajax-------------------------#
@login_required
@authority
def shareholder_del_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    custom_obj = models.Customes.objects.get(id=post_data['custom_id'])
    shareholder_obj = models.Shareholders.objects.get(id=post_data['shareholder_id'])
    '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
    custom_genre = custom_obj.genre
    if custom_genre == 1:
        try:
            with transaction.atomic():
                shareholder_obj.delete()  #
            response['message'] = '股东删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '股东删除失败:%s！' % str(e)
    else:
        response['status'] = False
        response['message'] = '客户类别为%s，无法删除相关股东！' % custom_genre
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------董事信息添加-------------------------#
@login_required
@authority
def trustee_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    custom_obj = models.Customes.objects.get(id=post_data['custom_id'])

    form_trustee_add = forms.FormTrusteeAdd(post_data)

    if form_trustee_add.is_valid():
        truste_data = form_trustee_add.cleaned_data
        custom_c_obj = custom_obj.company_custome
        try:
            trustee_obj = models.Trustee.objects.create(
                custom=custom_c_obj, trustee_name=truste_data['trustee_name'],
                trusteeor=request.user)
        except Exception as e:
            response['status'] = False
            response['message'] = '董事信息创建失败：%s' % str(e)
        response['message'] = '董事信息创建成功！！！'
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_trustee_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除董事信息ajax-------------------------#
@login_required
@authority
def trustee_del_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    custom_obj = models.Customes.objects.get(id=post_data['custom_id'])
    trustee_obj = models.Trustee.objects.get(id=post_data['trustee_id'])
    '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
    custom_genre = custom_obj.genre
    if custom_genre == 1:
        try:
            with transaction.atomic():
                trustee_obj.delete()  #
            response['message'] = '董事删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '董事删除失败:%s！' % str(e)
    else:
        response['status'] = False
        response['message'] = '客户类别为%s，无法删除相关董事！' % custom_genre
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------股权信息添加-------------------------#
@login_required
@authority
def spouse_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    custom_obj = models.Customes.objects.get(id=post_data['custom_id'])
    '''CUSTOM_STATE_LIST = ((1, '正常'), (99, '注销'))'''
    custom_state = custom_obj.custom_state
    if custom_state == 1:
        form_spouse_add = forms.FormCustomSpouseAdd(post_data)
        if form_spouse_add.is_valid():
            spouse_cleaned = form_spouse_add.cleaned_data
            spouse_add_obj = models.Customes.objects.get(id=spouse_cleaned['spouses'])
            try:
                with transaction.atomic():
                    models.CustomesP.objects.filter(custome=custom_obj).update(spouses=spouse_add_obj)
                    models.CustomesP.objects.filter(custome=spouse_add_obj).update(spouses=custom_obj)
                response['message'] = '成功添加配偶！'
            except Exception as e:
                response['status'] = False
                response['message'] = '添加配偶失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_spouse_add.errors
    else:
        response['status'] = False
        response['message'] = '客户类型为：%s，无法添加配偶！！！' % custom_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------客户删除-------------------------#
@login_required
@authority
def custom_del_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_id = post_data['custom_id']
    custom_obj = models.Customes.objects.get(id=custom_id)
    lending_custom_list = custom_obj.lending_custom.all()
    if lending_custom_list:
        response['status'] = False
        response['message'] = '客户已作为项目反担保人，无法删除！'
    else:
        try:
            custom_obj.delete()
            msg = '%s，删除成功！' % custom_obj.name
            response['message'] = msg
        except Exception as e:
            response['status'] = False
            response['message'] = '客户删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------客户修改-------------------------#
@login_required
@authority
def custom_edit_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    custom_id = post_data['custom_id']
    custom_lsit = models.Customes.objects.filter(id=custom_id)
    custom_obj = custom_lsit[0]
    form_custom_edit = forms.CustomEditForm(post_data)
    if form_custom_edit.is_valid():
        custom_edit_data = form_custom_edit.cleaned_data
        genre = custom_obj.genre
        if genre == 1:
            form_custom_c_add = forms.CustomCAddForm(post_data)
            if form_custom_c_add.is_valid():
                custom_c_data = form_custom_c_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_lsit.update(
                            name=custom_edit_data['name'],
                            short_name=custom_edit_data['short_name'],
                            # counter_only=custom_edit_data['counter_only'],
                            contact_addr=custom_edit_data['contact_addr'],
                            linkman=custom_edit_data['linkman'],
                            contact_num=custom_edit_data['contact_num'])
                        models.CustomesC.objects.filter(custome=custom_obj).update(
                            idustry=custom_c_data['idustry'],
                            district=custom_c_data['district'],
                            decisionor=custom_c_data['decisionor'],
                            capital=custom_c_data['capital'],
                            registered_addr=custom_c_data['registered_addr'],
                            representative=custom_c_data['representative'])
                    response['message'] = '客户：%s，修改成功！！！' % custom_edit_data['name']
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户修改失败：%s' % str(e)

            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_c_add.errors

        elif genre == 2:
            form_custom_p_add = forms.CustomPAddForm(post_data)
            if form_custom_p_add.is_valid():
                custom_p_data = form_custom_p_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_lsit.update(
                            name=custom_edit_data['name'],
                            short_name=custom_edit_data['short_name'],
                            # counter_only=custom_edit_data['counter_only'],
                            contact_addr=custom_edit_data['contact_addr'],
                            linkman=custom_edit_data['linkman'],
                            contact_num=custom_edit_data['contact_num'])
                        models.CustomesP.objects.filter(custome=custom_obj).update(
                            license_num=custom_p_data['license_num'],
                            license_addr=custom_p_data['license_addr'])
                        response['message'] = '客户：%s，修改成功！！！' % custom_edit_data['name']
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_p_add.errors
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_custom_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
