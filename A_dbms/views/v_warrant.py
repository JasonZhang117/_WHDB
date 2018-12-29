from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.contrib.auth.decorators import login_required
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.views import View


# 抵质押物信息管理
# -----------------------权证添加-------------------------#
@login_required
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
    form_warrant_data = {'warrant_typ': warrant_typ,
                         'warrant_num': post_data['warrant_num']}
    form_warrant_add = forms.WarrantAddForm(form_warrant_data)
    if form_warrant_add.is_valid():
        warrant_add_clean = form_warrant_add.cleaned_data
        print('warrant_add_clean:', warrant_add_clean)
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
        elif warrant_typ == 9:
            print('warrant_typ == 9')
            form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(post_data)
            if form_hypothecs_add_eidt.is_valid():
                hypothecs_add_edit_clean = form_hypothecs_add_eidt.cleaned_data
                print('hypothecs_add_edit_clean:', hypothecs_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ)
                        hypothecs_obj = models.Hypothecs.objects.create(
                            warrant=warrant_obj,
                            agree=hypothecs_add_edit_clean['agree'])
                    response['message'] = '他权创建成功！！！，请继续创建抵押资产信息。'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '他权创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_hypothecs_add_eidt.errors
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_warrant_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------权证删除-------------------------#
@login_required
def warrant_del_ajax(request):
    print(__file__, '---->def warrant_del_ajax')
    response = {'status': True, 'message': None, 'forme': None}
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_id = int(post_data['warrant_id'])
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    lending_warrant_list = warrant_obj.lending_warrant.all()
    if lending_warrant_list:
        response['status'] = False
        response['message'] = '担保物已作为项目反担保，无法删除！'
    else:
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
@login_required
def warrant_edit_ajax(request):
    print(__file__, '---->def warrant_edit_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_id = int(post_data['warrant_id'])
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list[0]
    warrant_typ = warrant_obj.warrant_typ

    form_warrant_edit = forms.WarrantEditForm(post_data)

    if form_warrant_edit.is_valid():
        warrant_edit_clean = form_warrant_edit.cleaned_data
        print('warrant_edit_clean:', warrant_edit_clean)

        if warrant_typ == 1:
            print('warrant_typ == 1')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                print('house_add_edit_clean:', house_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])

                        models.Houses.objects.filter(warrant=warrant_obj).update(
                            house_locate=house_add_edit_clean['house_locate'],
                            house_app=house_add_edit_clean['house_app'],
                            house_area=house_add_edit_clean['house_area'])
                    response['message'] = '房产修改成功！！！，请继续创建产权证信息。'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '房产修改失败：%s' % str(e)
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
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])

                        models.Grounds.objects.filter(warrant=warrant_obj).update(
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
        elif warrant_typ == 9:
            print('warrant_typ == 9')
            form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(post_data)
            if form_hypothecs_add_eidt.is_valid():
                hypothecs_add_edit_clean = form_hypothecs_add_eidt.cleaned_data
                print('hypothecs_add_edit_clean:', hypothecs_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])

                        models.Hypothecs.objects.filter(warrant=warrant_obj).update(
                            agree=hypothecs_add_edit_clean['agree'])
                        response['message'] = '土地创建成功！！！，请继续创建产权证信息。'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_hypothecs_add_eidt.errors

    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_warrant_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------产权证添加ajax-------------------------#
@login_required
def owership_add_ajax(request):  # 产权证添加ajax
    print(__file__, '---->def owership_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = post_data['warrant_id']
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    form_owership_add_edit = forms.OwerShipEditForm(post_data)
    if form_owership_add_edit.is_valid():
        owership_add_clean = form_owership_add_edit.cleaned_data
        print('warrant_add_clean:', owership_add_clean)
        try:
            owership_obj = models.Ownership.objects.create(
                warrant=warrant_obj,
                ownership_num=owership_add_clean['ownership_num'],
                owner=owership_add_clean['owner'])
            response['message'] = '产权证信息创建成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '产权证信息创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_owership_add_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------产权证删除ajax-------------------------#
@login_required
def owership_del_ajax(request):  # 产权证删除ajax
    print(__file__, '---->def owership_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    warrant_id = post_data['warrant_id']
    owership_id = post_data['owership_id']

    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    owership_obj = models.Ownership.objects.get(id=owership_id)

    lending_warrant_list = warrant_obj.lending_warrant.all()

    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if lending_warrant_list:
        response['status'] = False
        response['message'] = '担保物已作为项目反担保，无法删除！'
    else:
        try:
            owership_obj.delete()  # 删除评审会
            msg = '产权证删除成功！'
            response['message'] = msg
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------抵押物添加ajax-------------------------#
@login_required
def guaranty_add_ajax(request):  # 抵押物添加ajax
    print(__file__, '---->def guaranty_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = post_data['warrant_id']
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    try:
        warrant_hypothec_obj = models.Hypothecs.objects.get(warrant=warrant_obj)
        for warrant in post_data['warrant']:
            warrant_hypothec_obj.warrant_m.add(warrant)
        response['message'] = '抵押物添加成功！！！'
    except Exception as e:
        response['status'] = False
        response['message'] = '抵押物添加失败：%s' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------抵押物删除ajax-------------------------#
@login_required
def guaranty_del_ajax(request):  # 抵押物
    print(__file__, '---->def guaranty_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    warrant_id = post_data['warrant_id']
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    guaranty_id = post_data['guaranty_id']
    guaranty_obj = models.Warrants.objects.get(id=guaranty_id)
    hypothec_obj = models.Hypothecs.objects.get(warrant=warrant_obj)

    try:
        hypothec_obj.warrant_m.remove(guaranty_obj)
        msg = '产权证删除成功！'
        response['message'] = msg
    except Exception as e:
        response['status'] = False
        response['message'] = '删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------出入库添加ajax-------------------------#
@login_required
def storages_add_ajax(request):  # 出入库添加ajax
    print(__file__, '---->def storages_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    print('request.user:', request.user.id)
    print('request.user:', type(request.user.id))
    bbbb = models.Employees.objects.get(id=request.user.id)
    print('bbbb:', bbbb)
    print(post_data['transfer'])
    print(type(post_data['transfer']))
    warrant_id = post_data['warrant_id']
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list[0]
    warrant_state = warrant_obj.warrant_state
    form_storage_add_edit = forms.StoragesAddEidtForm(post_data)
    '''STORAGE_TYP_LIST = ((1, '入库'), (2, '出库'), (3, '借出'), 
    (4, '归还'), (5, '解保'))'''
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (3, '已出库'),
        (4, '已借出'), (5, '已注销'))'''
    if form_storage_add_edit.is_valid():
        storage_add_clean = form_storage_add_edit.cleaned_data
        print('storage_add_clean:', storage_add_clean)
        storage_typ = storage_add_clean['storage_typ']
        print('warrant_state:', warrant_state)
        if warrant_state == 2:
            if storage_typ in [2, 3, 5]:
                print('storage_typ in [2, 3, 5]')
                print("storage_add_clean['transfer_builder']:",
                      type(storage_add_clean['transfer']))
                '''WARRANT_TYP_LIST = [
                    (1, '房产'), (2, '土地'), (3, '应收'), (4, '股权'),
                    (5, '票据'), (6, '车辆'), (7, '其他'), (9, '他权')]'''
                if warrant_obj.warrant_typ == 9 and storage_typ == 5:  # 他权解保
                    ypothec_obj = warrant_obj.ypothec_warrant  # 他权
                    agree_list = models.Agrees.objects.filter(ypothec_agree=ypothec_obj)
                    agree_obj = agree_list[0]
                    if agree_obj.agree_state == 5:
                        # ypothec_obj.agree  # 他权对应委托合同
                        # 判断合同项下有无余额******
                        try:
                            with transaction.atomic():
                                storage_obj = models.Storages.objects.create(
                                    warrant=warrant_obj, storage_typ=storage_typ,
                                    storage_date=storage_add_clean['storage_date'],
                                    transfer=storage_add_clean['transfer'],
                                    conservator=request.user)
                                warrant_list.update(warrant_state=5)
                            response['message'] = '他权解保出库并注销！！！'
                        except Exception as e:
                            response['status'] = False
                            response['message'] = '他权解保失败：%s' % str(e)
                    else:
                        response['status'] = False
                        response['message'] = '%s合同状态为：%s，无法解保他权' % (agree_obj.agree_num,
                                                                     agree_obj.agree_state)
                else:
                    try:
                        with transaction.atomic():
                            storage_obj = models.Storages.objects.create(
                                warrant=warrant_obj, storage_typ=storage_typ,
                                storage_date=storage_add_clean['storage_date'],
                                transfer=storage_add_clean['transfer'],
                                conservator=request.user)
                            if storage_typ == 3:
                                warrant_list.update(warrant_state=4)
                            else:
                                warrant_list.update(warrant_state=3)
                        response['message'] = '权证出库信息创建成功！！！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '权证出库信息创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '该权证已在库中，无法办理入库操作！！！'
        else:
            if storage_typ in [1, 4]:
                print("storage_typ in [1, 4]")
                print("storage_add_clean['transfer_builder']:",
                      type(storage_add_clean['transfer']))
                try:
                    with transaction.atomic():
                        storage_obj = models.Storages.objects.create(
                            warrant=warrant_obj, storage_typ=storage_typ,
                            storage_date=storage_add_clean['storage_date'],
                            transfer=storage_add_clean['transfer'],
                            conservator=request.user)
                        print('storage_obj:', storage_obj)
                        warrant_list.update(warrant_state=2)
                    response['message'] = '权证入库信息创建成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '权证入库信息创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '该权证不在库中，无法办理出库操作！！！'
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_storage_add_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------house房产列表-------------------------#
@login_required
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

    return render(request, 'dbms/warrant/house.html', locals())


# -----------------------房产列表-------------------------#
@login_required
def ground(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')
    print('**kwargs:', kwargs)

    add_warrant = '添加土地'
    warrant_typ_n = 2

    form_warrant_edit = forms.WarrantEditForm()
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

    return render(request, 'dbms/warrant/ground.html', locals())


# -----------------------权证列表-------------------------#
@login_required
def warrant(request, *args, **kwargs):  # 房产列表
    print(__file__, '---->def warrant')

    add_warrant = '添加权证'
    warrant_typ_n = 0
    form_warrant_add = forms.WarrantAddForm()

    form_house_add_edit = forms.HouseAddEidtForm()
    form_ground_add_edit = forms.GroundAddEidtForm()
    form_hypothecs_add_eidt = forms.HypothecsAddEidtForm()

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

    return render(request, 'dbms/warrant/warrant.html', locals())


# ---------------------warrant_scan权证预览------------------------#
@login_required
def warrant_scan(request, warrant_id):  # house_scan房产预览
    print(__file__, '---->def warrant_scan')
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    warrant_typ_n = warrant_obj.warrant_typ
    if warrant_typ_n == 9:
        agree_lending_obj = warrant_obj.ypothec_warrant.agree.lending

        warrants_lending_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=agree_lending_obj).values_list(
            'id', 'warrant_num')

        print('agree_lending_obj:', agree_lending_obj)
        print('warrants_lending_list:', warrants_lending_list)

    form_warrant_edit_date = {'warrant_num': warrant_obj.warrant_num}
    form_warrant_edit = forms.WarrantEditForm(initial=form_warrant_edit_date)

    house_ground_list = [1, 2]

    warrant_typ = warrant_obj.warrant_typ
    if warrant_typ == 1:
        form_date = {
            'house_locate': warrant_obj.house_warrant.house_locate,
            'house_app': warrant_obj.house_warrant.house_app,
            'house_area': warrant_obj.house_warrant.house_area}
        form_house_add_edit = forms.HouseAddEidtForm(form_date)
    elif warrant_typ == 2:
        form_date = {
            'ground_locate': warrant_obj.ground_warrant.ground_locate,
            'ground_app': warrant_obj.ground_warrant.ground_app,
            'ground_area': warrant_obj.ground_warrant.ground_area}
        form_ground_add_edit = forms.GroundAddEidtForm(form_date)
    elif warrant_typ == 9:
        form_date = {
            'agree': warrant_obj.ypothec_warrant.agree}
        form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(initial=form_date)
        form_guaranty_add_edit = forms.HypothecGuarantyAddEidtForm()

    form_storage_add_edit = forms.StoragesAddEidtForm()
    form_owership_add_edit = forms.OwerShipAddForm()

    ####分页信息###
    storages_list = warrant_obj.storage_warrant.all().order_by('-id')
    paginator = Paginator(storages_list, 5)
    page = request.GET.get('page')
    try:
        storages_p_list = paginator.page(page)
    except PageNotAnInteger:
        storages_p_list = paginator.page(1)
    except EmptyPage:
        storages_p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/warrant-scan.html', locals())
