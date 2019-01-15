from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Sum, Max, Count


# -----------------------客户管理-------------------------#
def custom(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    PAGE_TITLE = '客户管理'
    form_custom_add = forms.CustomAddForm()
    form_custom_c_add = forms.CustomCAddForm()
    form_custom_p_add = forms.CustomPAddForm()

    genre_list = models.Customes.GENRE_LIST
    custom_list = models.Customes.objects.filter(**kwargs).order_by('-credit_amount', 'name')

    ####分页信息###
    paginator = Paginator(custom_list, 20)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/custom/custom.html', locals())


# -----------------------客户添加-------------------------#
def custom_add_ajax(request):
    print(__file__, '---->def custom_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

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
                            name=custom_add_data['name'],
                            genre=custom_add_data['genre'],
                            counter_only=custom_add_data['counter_only'],
                            contact_addr=custom_add_data['contact_addr'],
                            linkman=custom_add_data['linkman'],
                            contact_num=custom_add_data['contact_num'])

                        custom_c_obj = models.CustomesC.objects.create(
                            custome=custom_obj,
                            short_name=custom_c_data['short_name'],
                            idustry=custom_c_data['idustry'],
                            district=custom_c_data['district'],
                            capital=custom_c_data['capital'],
                            registered_addr=custom_c_data['registered_addr'],
                            representative=custom_c_data['representative'])
                    response['message'] = '客户：%s，创建成功！！！' % custom_add_data['name']
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
                            name=custom_add_data['name'],
                            genre=custom_add_data['genre'],
                            counter_only=custom_add_data['counter_only'],
                            contact_addr=custom_add_data['contact_addr'],
                            linkman=custom_add_data['linkman'],
                            contact_num=custom_add_data['contact_num'])
                        custom_p_obj = models.CustomesP.objects.create(
                            custome=custom_obj,
                            license_num=custom_p_data['license_num'],
                            license_addr=custom_p_data['license_addr'])
                        response['message'] = '客户：%s，创建成功！！！' % custom_add_data['name']
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
def shareholder_add_ajax(request):
    print(__file__, '---->def shareholder_add_ajax')
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
        print('shareholder_ratio_amount:', shareholder_ratio_amount)
        shareholding_ratio = shareholder_add_data['shareholding_ratio']
        print('shareholding_ratio:', shareholding_ratio)
        shareholder_ratio_a = shareholder_ratio_amount['shareholding_ratio__sum']
        if shareholder_ratio_a:
            ratio_amount = shareholder_ratio_a + shareholding_ratio
        else:
            ratio_amount = shareholding_ratio
        print('ratio_amount:', ratio_amount)
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


# -----------------------客户删除-------------------------#
def custom_del_ajax(request):
    print(__file__, '---->def custom_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_id = post_data['custom_id']
    custom_obj = models.Customes.objects.get(id=custom_id)
    lending_custom_list = custom_obj.lending_custom.all()
    print('lending_custom_list:', lending_custom_list)
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
def custom_edit_ajax(request):
    print(__file__, '---->def custom_edit_ajax')
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
        print('custom_edit_data:', custom_edit_data)
        genre = custom_obj.genre

        if genre == 1:
            form_custom_c_add = forms.CustomCAddForm(post_data)
            if form_custom_c_add.is_valid():
                custom_c_data = form_custom_c_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_lsit.update(
                            name=custom_edit_data['name'],
                            counter_only=custom_edit_data['counter_only'],
                            contact_addr=custom_edit_data['contact_addr'],
                            linkman=custom_edit_data['linkman'],
                            contact_num=custom_edit_data['contact_num'])

                        models.CustomesC.objects.filter(custome=custom_obj).update(
                            short_name=custom_c_data['short_name'],
                            idustry=custom_c_data['idustry'],
                            district=custom_c_data['district'],
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
                print('custom_p_data:', custom_p_data)
                try:
                    with transaction.atomic():
                        custom_lsit.update(
                            name=custom_edit_data['name'],
                            counter_only=custom_edit_data['counter_only'],
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


# -----------------------------客户预览------------------------------#
def custom_scan(request, custom_id):  # 项目预览
    print(__file__, '---->def custom_scan')
    custom_obj = models.Customes.objects.get(id=custom_id)
    if custom_obj.genre == 1:
        shareholder_list = custom_obj.company_custome.shareholder_custom_c.all()
        print('shareholder_list:', shareholder_list)
    form_date = {
        'name': custom_obj.name,
        'contact_addr': custom_obj.contact_addr,
        'linkman': custom_obj.linkman,
        'contact_num': custom_obj.contact_num}
    form_custom_edit = forms.CustomEditForm(initial=form_date)

    if custom_obj.genre == 1:
        form_date = {
            'short_name': custom_obj.company_custome.short_name,
            'idustry': custom_obj.company_custome.idustry,
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

    return render(request, 'dbms/custom/custom-scan.html', locals())
