from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.contrib.auth.decorators import login_required
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q, F

from django.views import View


# -----------------------权证添加-------------------------#
@login_required
def warrant_add_ajax(request):
    print(__file__, '---->def warrant_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, }
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
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
        if warrant_typ == 1:  # 房产
            print('warrant_typ == 1')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                try:
                    print('house_add_edit_clean:', house_add_edit_clean)
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_typ=warrant_typ,
                            warrant_buildor=request.user)
                        house_obj = models.Houses.objects.create(
                            warrant=warrant_obj, house_locate=house_add_edit_clean['house_locate'],
                            house_app=house_add_edit_clean['house_app'],
                            house_area=house_add_edit_clean['house_area'], house_buildor=request.user)
                    response['message'] = '房产创建成功！！！，请继续创建产权证信息。'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '房产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_house_add_edit.errors
        elif warrant_typ == 5:  # 土地
            print('warrant_typ == 5')
            form_ground_add_edit = forms.GroundAddEidtForm(post_data)
            if form_ground_add_edit.is_valid():
                ground_add_edit_clean = form_ground_add_edit.cleaned_data
                print('ground_add_edit_clean:', ground_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        ground_obj = models.Grounds.objects.create(
                            warrant=warrant_obj,
                            ground_locate=ground_add_edit_clean['ground_locate'],
                            ground_app=ground_add_edit_clean['ground_app'],
                            ground_area=ground_add_edit_clean['ground_area'], ground_buildor=request.user)
                    response['message'] = '土地创建成功！！！，请继续创建产权证信息。'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_ground_add_edit.errors
        elif warrant_typ == 11:
            print('warrant_typ == 11')
            form_receivable_add_edit = forms.FormReceivable(post_data)
            if form_receivable_add_edit.is_valid():
                receivable_clean = form_receivable_add_edit.cleaned_data
                print('receivable_clean:', receivable_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        receivable_obj = models.Receivable.objects.create(
                            warrant=warrant_obj, receivable_buildor=request.user,
                            receive_owner=receivable_clean['receive_owner'],
                            receivable_detail=receivable_clean['receivable_detail'])
                    response['message'] = '应收账款创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '应收账款创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_receivable_add_edit.errors
        elif warrant_typ == 21:
            print('warrant_typ == 21')
            form_stockes_add_edit = forms.FormStockes(post_data)
            if form_stockes_add_edit.is_valid():
                stocke_clean = form_stockes_add_edit.cleaned_data
                print('stocke_clean:', stocke_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        stock_obj = models.Stockes.objects.create(
                            warrant=warrant_obj, stock_buildor=request.user,
                            stock_typ=stocke_clean['stock_typ'],
                            stock_owner=stocke_clean['stock_owner'],
                            target=stocke_clean['target'],
                            share=stocke_clean['share'])
                    response['message'] = '股权创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '股权创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_stockes_add_edit.errors
        elif warrant_typ == 31:
            print('warrant_typ == 31')
            form_draft_add_eidt = forms.FormDraft(post_data)
            if form_draft_add_eidt.is_valid():
                draft_clean = form_draft_add_eidt.cleaned_data
                print('draft_clean:', draft_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        draft_obj = models.Draft.objects.create(
                            warrant=warrant_obj, draft_buildor=request.user,
                            draft_owner=draft_clean['draft_owner'],
                            draft_typ=draft_clean['draft_typ'],
                            draft_detail=draft_clean['draft_detail'])
                    response['message'] = '票据包创建成功，请添加票据！！！'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '票据创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_draft_add_eidt.errors
        elif warrant_typ == 41:
            print('warrant_typ == 41')
            form_vehicle_add_eidt = forms.FormVehicle(post_data)
            if form_vehicle_add_eidt.is_valid():
                vehicle_clean = form_vehicle_add_eidt.cleaned_data
                print('vehicle_clean:', vehicle_clean)
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        vehicle_obj = models.Vehicle.objects.create(
                            warrant=warrant_obj, vehicle_buildor=request.user,
                            vehicle_owner=vehicle_clean['vehicle_owner'],
                            frame_num=vehicle_clean['frame_num'],
                            plate_num=vehicle_clean['plate_num'])
                    response['message'] = '车辆创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '车辆创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_vehicle_add_eidt.errors
        elif warrant_typ == 51:
            print('warrant_typ == 51')
            form_chattel_add_eidt = forms.FormChattel(post_data)
            if form_chattel_add_eidt.is_valid():
                chattel_clean = form_chattel_add_eidt.cleaned_data
                print('chattel_clean:', chattel_clean)
                try:
                    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
        (31, '解保出库'), (99, '已注销'))'''
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        chattel_obj = models.Chattel.objects.create(
                            warrant=warrant_obj, chattel_buildor=request.user,
                            chattel_owner=chattel_clean['chattel_owner'],
                            chattel_typ=chattel_clean['chattel_typ'],
                            chattel_detail=chattel_clean['chattel_detail'])
                    response['message'] = '动产创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '动产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_chattel_add_eidt.errors
        elif warrant_typ == 99:
            print('warrant_typ == 99')
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
                    response['skip'] = "/dbms/warrant/scan/%s" % warrant_obj.id
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
        '''WARRANT_TYP_LIST = [
                    (1, '房产'), (2, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
                    (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
        if warrant_typ == 1:
            print('warrant_typ == 1')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                print('house_add_edit_clean:', house_add_edit_clean)
                try:
                    with transaction.atomic():
                        warrant_list.update(warrant_num=warrant_edit_clean['warrant_num'])
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
        elif warrant_typ == 5:
            print('warrant_typ == 5')
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
        elif warrant_typ == 99:
            print('warrant_typ == 99')
            try:
                warrant_list.update(warrant_num=warrant_edit_clean['warrant_num'])
                response['message'] = '他权信息修改该成功！！！'
            except Exception as e:
                response['status'] = False
                response['message'] = '他权信息修改失败：%s' % str(e)
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
    form_owership_add = forms.OwerShipAddForm(post_data)
    if form_owership_add.is_valid():
        owership_add_clean = form_owership_add.cleaned_data
        print('warrant_add_clean:', owership_add_clean)
        try:
            owership_obj = models.Ownership.objects.create(
                warrant=warrant_obj, ownership_num=owership_add_clean['ownership_num'],
                owner=owership_add_clean['owner'])
            response['message'] = '产权证信息创建成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '产权证信息创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_owership_add.errors
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
        with transaction.atomic():
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
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (3, '已出库'), (4, '已借出'), (5, '已注销'), (6, '无需入库'))'''
    if warrant_obj.warrant_state == 1:
        try:
            hypothec_obj.warrant_m.remove(guaranty_obj)
            response['message'] = '产权证删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '删除失败:%s！' % str(e)
    else:
        response['status'] = False
        response['message'] = '他权状态为：%s，无法删除抵押权证' % warrant_obj.warrant_state

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

    warrant_id = post_data['warrant_id']
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list.first()
    warrant_state = warrant_obj.warrant_state
    form_storage_add_edit = forms.StoragesAddEidtForm(post_data)
    '''STORAGE_TYP_LIST = ((1, '入库'), (2, '出库'), (3, '借出'), (4, '归还'), (5, '解保'))'''
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
         (99, '已注销'))'''
    '''STORAGE_TYP_LIST = ((1, '入库'), (2, '续抵出库'), (11, '借出'), (12, '归还'), (31, '解保出库'))'''
    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
         (99, '已注销'))'''
    if form_storage_add_edit.is_valid():
        storage_add_clean = form_storage_add_edit.cleaned_data
        print('storage_add_clean:', storage_add_clean)
        storage_typ = storage_add_clean['storage_typ']
        print('warrant_state:', warrant_state)

        if warrant_state == 2:  # (2, '已入库'),
            if storage_typ in [2, 11, 31]:  # (2, '出库'), (3, '借出'), (5, '解保')
                '''WARRANT_TYP_LIST = [
                    (1, '房产'), (2, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
                    (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
                if warrant_obj.warrant_typ == 99:  # 他权解保
                    ypothec_obj = warrant_obj.ypothec_warrant  # 他权
                    agree_list = models.Agrees.objects.filter(ypothec_agree=ypothec_obj)
                    agree_obj = agree_list.first()
                    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '已落实，未放款'), (41, '已落实，
                    放款'),(42, '未落实，放款'), (51, '待变更'), (61, '已解保'), (99, '已作废'))'''
                    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
                    if agree_obj.agree_state in [61, 99]:
                        # ypothec_obj.agree  # 他权对应委托合同
                        # 判断合同项下有无余额******
                        try:
                            with transaction.atomic():
                                storage_obj = models.Storages.objects.create(
                                    warrant=warrant_obj, storage_typ=storage_typ,
                                    storage_date=storage_add_clean['storage_date'],
                                    transfer=storage_add_clean['transfer'], conservator=request.user)
                                warrant_list.update(warrant_state=99)
                            response['message'] = '他权解保出库并注销！！！'
                        except Exception as e:
                            response['status'] = False
                            response['message'] = '他权解保失败：%s' % str(e)
                    else:
                        response['status'] = False
                        response['message'] = '%s合同状态为：%s，无法办理他权出库' % (agree_obj.agree_num,
                                                                       agree_obj.agree_state)
                else:
                    try:
                        with transaction.atomic():
                            storage_obj = models.Storages.objects.create(
                                warrant=warrant_obj, storage_typ=storage_typ,
                                storage_date=storage_add_clean['storage_date'],
                                transfer=storage_add_clean['transfer'], conservator=request.user)
                            '''STORAGE_TYP_LIST = ((1, '入库'), (2, '续抵出库'), (11, '借出'), (12, '归还'), (31, '解保出库'))'''
                            '''WARRANT_STATE_LIST = (
                                (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
                                 (99, '已注销'))'''
                            if storage_typ == 2:
                                warrant_list.update(warrant_state=11)
                            elif storage_typ == 11:
                                warrant_list.update(warrant_state=21)
                            else:
                                warrant_list.update(warrant_state=31)
                        response['message'] = '权证出库成功！！！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '权证出库失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '该权证不在库中，无法办理出库操作！！！'
        else:  # (1, '未入库'), (3, '已出库'), (4, '已借出'), (5, '已注销'), (6, '无需入库')
            if storage_typ in [1, 12]:  # (1, '入库'), (4, '归还')
                print("storage_typ in [1, 4]")
                try:
                    with transaction.atomic():
                        storage_obj = models.Storages.objects.create(
                            warrant=warrant_obj, storage_typ=storage_typ,
                            storage_date=storage_add_clean['storage_date'],
                            transfer=storage_add_clean['transfer'], conservator=request.user)
                        print('storage_obj:', storage_obj)
                        warrant_list.update(warrant_state=2)
                    response['message'] = '权证入库成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '权证入库失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '该权证已在库中，无法办理入库操作！！！'
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

    PAGE_TITAL = '权证-房产'
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

    PAGE_TITAL = '权证-土地'
    add_warrant = '添加土地'
    warrant_typ_n = 5

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
    print('request.GET:', request.GET)
    PAGE_TITAL = '权证-所有'
    add_warrant = '添加权证'
    warrant_typ_n = 0
    '''WARRANT_STATE_LIST = (
           (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
           (31, '解保出库'), (99, '已注销'))'''
    ''' WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    '''模态框'''
    form_warrant_add = forms.WarrantAddForm()  # 权证添加
    form_house_add_edit = forms.HouseAddEidtForm()  # 房产添加
    form_ground_add_edit = forms.GroundAddEidtForm()  # 土地添加
    form_receivable_add_edit = forms.FormReceivable()  # 应收添加
    form_stockes_add_edit = forms.FormStockes()  # 21股权添加
    form_draft_add_eidt = forms.FormDraft()  # 31票据添加
    form_vehicle_add_eidt = forms.FormVehicle()  # 41车辆添加
    form_chattel_add_eidt = forms.FormChattel()  # 51动产添加
    form_hypothecs_add_eidt = forms.HypothecsAddEidtForm()  # 99他权添加
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    warrant_typ_list = models.Warrants.WARRANT_TYP_LIST  # 筛选条件
    '''筛选'''
    warrant_list = models.Warrants.objects.filter(**kwargs).order_by('warrant_num')
    '''搜索'''
    search_key = request.GET.get('_s')
    if search_key:
        search_fields = ['warrant_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        warrant_list = warrant_list.filter(q)
    '''分页'''
    paginator = Paginator(warrant_list, 18)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/warrant/warrant.html', locals())


# -----------------------按合同入库---------------------#
@login_required
def warrant_agree(request, *args, **kwargs):  # 按合同入库
    print(__file__, '---->def warrant_agree')
    PAGE_TITAL = '权证-按合同'
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    AGREE_STATE_LIST = models.Agrees.AGREE_STATE_LIST  # 筛选条件
    '''筛选'''
    agree_list = models.Agrees.objects.filter(**kwargs).filter(agree_state__in=[21, 31]).select_related(
        'lending', 'branch').order_by('-agree_num')
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

    return render(request, 'dbms/warrant/warrant-agree.html', locals())


# ---------------------warrant_scan权证预览------------------------#
@login_required
def warrant_scan(request, warrant_id):  # house_scan房产预览
    print(__file__, '---->def warrant_scan')
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    warrant_typ_n = warrant_obj.warrant_typ
    house_ground_list = [1, 5]

    '''WARRANT_TYP_LIST = [
                    (1, '房产'), (2, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
                    (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    if warrant_typ_n == 99:
        agree_lending_obj = warrant_obj.ypothec_warrant.agree.lending
        warrants_lending_list = models.Warrants.objects.filter(
            lending_warrant__sure__lending=agree_lending_obj).values_list('id', 'warrant_num')

    form_warrant_edit_date = {'warrant_num': warrant_obj.warrant_num}
    form_warrant_edit = forms.WarrantEditForm(initial=form_warrant_edit_date)  # 权证编辑form
    warrant_typ = warrant_obj.warrant_typ
    if warrant_typ == 1:
        form_date = {
            'house_locate': warrant_obj.house_warrant.house_locate,
            'house_app': warrant_obj.house_warrant.house_app,
            'house_area': warrant_obj.house_warrant.house_area}
        form_house_add_edit = forms.HouseAddEidtForm(form_date)  # 房产form
    elif warrant_typ == 5:
        form_date = {
            'ground_locate': warrant_obj.ground_warrant.ground_locate,
            'ground_app': warrant_obj.ground_warrant.ground_app,
            'ground_area': warrant_obj.ground_warrant.ground_area}
        form_ground_add_edit = forms.GroundAddEidtForm(form_date)  # 土地form
    elif warrant_typ == 11:
        form_date = {
            'receive_owner': warrant_obj.receive_warrant.receive_owner,
            'receivable_detail': warrant_obj.receive_warrant.receivable_detail}
        form_receivable_add_edit = forms.FormReceivable(form_date)  # 土地form

    elif warrant_typ == 99:
        form_date = {
            'agree': warrant_obj.ypothec_warrant.agree}
        form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(initial=form_date)  # 他权form
    form_storage_add_edit = forms.StoragesAddEidtForm()  # 出入库form
    form_owership_add_edit = forms.OwerShipAddForm()  # 所有权证form
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


# --------------------------按合同入库-按合同查看--------------------------#
@login_required
def warrant_agree_scan(request, agree_id):  # 查看合同
    print(__file__, '---->def warrant_agree_scan')
    PAGE_TITAL = '权证管理'
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
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending

    '''WARRANT_TYP_LIST = [
        (1, '房产'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    SURE_LIST = [1, 2]
    HOUSE_LIST = [11, 21, 42, 52]
    GROUND_LIST = [12, 22, 43, 53]
    RECEIVABLE_LIST = [31]
    STOCK_LIST = [32]
    CHATTEL_LIST = [13]

    form_storage_add_edit = forms.StoragesAddEidtForm()

    return render(request, 'dbms/warrant/warrant-agree-scan.html', locals())


# --------------------------按合同入库-按合同查看--------------------------#
@login_required
def warrant_agree_warrant(request, agree_id, warrant_id):  # 查看合同
    print(__file__, '---->def warrant_agree_scan')
    page_title = '权证管理'
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
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    warrant_obj = models.Warrants.objects.get(id=warrant_id)

    print('agree_obj.ypothec_agree.all():', agree_obj.ypothec_agree.all())
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    sure_list = [1, 2]  # 保证反担保类型
    house_list = [11, 21, 42, 52]
    ground_list = [12, 22, 43, 53]
    receivable_list = [31]
    stock_list = [32]

    form_storage_add_edit = forms.StoragesAddEidtForm()

    return render(request, 'dbms/warrant/warrant-agree-warrant.html', locals())
