from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction


# 抵质押物信息管理
# -----------------------权证添加-------------------------#
def warrant_add_ajax(request):
    print(__file__, '---->def warrant_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_typ_n = int(post_data['warrant_typ_n'])
    if warrant_typ_n == 0:
        warrant_typ = int(post_data['warrant_typ'])
    else:
        warrant_typ = warrant_typ_n

    print('warrant_typ:', warrant_typ)
    print('type(warrant_typ):', type(warrant_typ))
    form_warrant_add = forms.WarrantAddForm(post_data)
    if form_warrant_add.is_valid():
        warrant_add_clean = form_warrant_add.cleaned_data
        if warrant_typ == 1:
            print('warrant_typ == 1')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ)
                        house_obj = models.Houses.objects.create(
                            warrant=warrant_obj,
                            house_locate=house_add_edit_clean['house_locate'],
                            house_app=house_add_edit_clean['house_app'],
                            house_area=house_add_edit_clean['house_area'])
                    response['message'] = '房产创建成功！！！，请继续创建产权证信息。'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '房产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_house_add_edit.errors

        elif warrant_typ == 2:
            print('warrant_typ == 2')
            form_ground_add_edit = forms.GroundAddEidtForm(post_data)
            if form_ground_add_edit.is_valid():
                ground_add_edit_clean = form_ground_add_edit.cleaned_data
                print('ground_add_edit_clean:', ground_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ)
                        ground_obj = models.Grounds.objects.create(
                            warrant=warrant_obj,
                            ground_locate=ground_add_edit_clean['ground_locate'],
                            ground_app=ground_add_edit_clean['ground_app'],
                            ground_area=ground_add_edit_clean['ground_area'])
                    response['message'] = '土地创建成功！！！，请继续创建产权证信息。'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_ground_add_edit.errors
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_warrant_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------权证删除-------------------------#
def warrant_del_ajax(request):
    print(__file__, '---->def warrant_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, 'return_path': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_id = int(post_data['warrant_id'])
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    if warrant_obj.warrant_typ == 1:
        response['return_path'] = '/dbms/house/'
    elif warrant_obj.warrant_typ == 2:
        response['return_path'] = '/dbms/ground/'

    print('warrant_obj:', warrant_obj)
    try:
        warrant_obj.delete()  # 删除评审会
        msg = '%s，删除成功！' % warrant_obj.warrant_num
        response['message'] = msg
    except Exception as e:
        response['status'] = False
        response['message'] = '删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------权证修改-------------------------#
def warrant_edit_ajax(request):
    print(__file__, '---->def warrant_edit_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_id = int(post_data['warrant_id'])
    print('warrant_id:', warrant_id)
    print('type(warrant_id):', type(warrant_id))
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list[0]
    warrant_typ = warrant_obj.warrant_typ

    if warrant_typ == 1:
        print('warrant_typ == 1')
        form_warrant_add_edit = forms.HouseAddForm(post_data)
        if form_warrant_add_edit.is_valid():
            warrant_add_data = form_warrant_add_edit.cleaned_data
            try:
                with transaction.atomic():
                    warrant_list.update(
                        warrant_num=warrant_add_data['warrant_num'])

                    models.Houses.objects.filter(warrant=warrant_obj).update(
                        house_locate=warrant_add_data['house_locate'],
                        house_app=warrant_add_data['house_app'],
                        house_area=warrant_add_data['house_area'])
                response['message'] = '房产修改成功！！！，请继续创建产权证信息。'
            except Exception as e:
                response['status'] = False
                response['message'] = '房产修改失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_warrant_add_edit.errors

    elif warrant_typ == 2:
        print('warrant_typ == 2')
        form_warrant_add_edit = forms.GroundAddForm(post_data)
        if form_warrant_add_edit.is_valid():
            warrant_add_data = form_warrant_add_edit.cleaned_data
            print('warrant_add_data:', warrant_add_data)
            try:
                with transaction.atomic():
                    warrant_list.update(
                        warrant_num=warrant_add_data['warrant_num'])

                    models.Grounds.objects.filter(warrant=warrant_obj).update(
                        ground_locate=warrant_add_data['ground_locate'],
                        ground_app=warrant_add_data['ground_app'],
                        ground_area=warrant_add_data['ground_area'])
                    response['message'] = '土地创建成功！！！，请继续创建产权证信息。'
            except Exception as e:
                response['status'] = False
                response['message'] = '土地创建失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_warrant_add_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------house房产列表-------------------------#
def house(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')
    print('**kwargs:', kwargs)

    add_warrant = '添加房产'
    warrant_typ_n = 1
    form_warrant_edit = forms.WarrantEditForm()
    form_house_add_edit = forms.HouseAddEidtForm()

    house_app_list = models.Houses.HOUSE_APP_LIST
    house_list = models.Houses.objects.filter(**kwargs)
    print('house_list:', house_list)
    ####分页信息###
    paginator = Paginator(house_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/house.html',
                  locals())


# ---------------------house_scan房产预览------------------------#
def house_scan(request, house_id):  # house_scan房产预览
    print(__file__, '---->def house_scan')
    warrant_obj = models.Houses.objects.get(id=house_id)
    edit_warrant = '修改房产'
    del_warrant = '删除房产'
    warrant_typ_n = warrant_obj.warrant.warrant_typ
    form_date = {
        'warrant_num': warrant_obj.warrant,
        'house_locate': warrant_obj.house_locate,
        'house_app': warrant_obj.house_app,
        'house_area': warrant_obj.house_area}

    form_warrant_edit = forms.WarrantEditForm(form_date)
    form_house_add_edit = forms.HouseAddEidtForm(form_date)

    return render(request,
                  'dbms/warrant/house-scan.html',
                  locals())


# -----------------------房产列表-------------------------#
def ground(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')
    print('**kwargs:', kwargs)

    form_ground_add_edit = forms.GroundAddEidtForm()

    ground_app_list = models.Grounds.GROUND_APP_LIST
    ground_list = models.Grounds.objects.filter(**kwargs)
    print('ground_list:', ground_list)
    ####分页信息###
    paginator = Paginator(ground_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/ground.html',
                  locals())


# -----------------------权证列表-------------------------#
def warrant(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')

    add_warrant = '添加权证'
    warrant_typ_n = 0
    form_warrant_add = forms.WarrantAddForm()
    form_house_add_edit = forms.HouseAddEidtForm()
    form_ground_add_edit = forms.GroundAddEidtForm()

    warrant_typ_list = models.Warrants.WARRANT_TYP_LIST
    warrant_list = models.Warrants.objects.filter(**kwargs)

    ####分页信息###
    paginator = Paginator(warrant_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/warrant/warrant.html',
                  locals())


# ---------------------hwarrant_scan权证预览------------------------#
def warrant_scan(request, warrant_id):  # house_scan房产预览
    print(__file__, '---->def warrant_scan')
    house_obj = models.Warrants.objects.get(id=warrant_id)

    form_date = {
        'house_locate': house_obj.house_locate,
        'house_app': house_obj.house_app,
        'house_area': house_obj.house_area}

    form_house_add_edit = forms.HouseAddForm(form_date)

    return render(request,
                  'dbms/warrant/house-scan.html',
                  locals())
