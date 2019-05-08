from django.shortcuts import HttpResponse, render, redirect
from .. import models, forms
from django.contrib.auth.decorators import login_required
import time, json
from django.db import transaction
from django.db.models import Q, F
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------权证添加-------------------------#
@login_required
@authority
def warrant_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_typ_n = int(post_data['warrant_typ_n'])
    if warrant_typ_n == 0:
        warrant_typ = int(post_data['warrant_typ'])
    else:
        warrant_typ = warrant_typ_n
    form_warrant_add = forms.WarrantAddForm(post_data)
    if form_warrant_add.is_valid():
        warrant_add_clean = form_warrant_add.cleaned_data
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地使用权'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        if warrant_typ == 1:  # 房产
            print('warrant_typ == 1')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_typ=warrant_typ,
                            warrant_buildor=request.user)
                        house_obj = models.Houses.objects.create(
                            warrant=warrant_obj, house_locate=house_add_edit_clean['house_locate'],
                            house_app=house_add_edit_clean['house_app'],
                            house_area=house_add_edit_clean['house_area'],
                            house_name=house_add_edit_clean['house_name'],
                            house_buildor=request.user)
                    response['message'] = '房产创建成功！！！，请继续创建产权证信息。'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '房产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_house_add_edit.errors
        elif warrant_typ == 2:  # 房产包
            print('warrant_typ == 2')
            try:
                warrant_obj = models.Warrants.objects.create(
                    warrant_num=warrant_add_clean['warrant_num'],
                    warrant_typ=warrant_typ, warrant_buildor=request.user)
                response['message'] = '房产包创建成功，请继续添加房产信息！！！'
                response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
            except Exception as e:
                response['status'] = False
                response['message'] = '土地创建失败：%s' % str(e)
        elif warrant_typ == 5:  # 土地
            print('warrant_typ == 5')
            form_ground_add_edit = forms.GroundAddEidtForm(post_data)
            if form_ground_add_edit.is_valid():
                ground_add_edit_clean = form_ground_add_edit.cleaned_data
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
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_ground_add_edit.errors
        elif warrant_typ == 6:  # 在建工程
            print('warrant_typ == 6')
            form_construct_add_edit = forms.ConstructionAddForm(post_data)  # 在建工程
            if form_construct_add_edit.is_valid():
                construct_clean = form_construct_add_edit.cleaned_data
                '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销'))'''
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6, evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        construct_obj = models.Construction.objects.create(
                            warrant=warrant_obj,
                            coustruct_locate=construct_clean['coustruct_locate'],
                            coustruct_app=construct_clean['coustruct_app'],
                            coustruct_area=construct_clean['coustruct_area'], coustructor=request.user)
                    response['message'] = '在建工程创建成功！！！，请继续创建产权证信息。'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_construct_add_edit.errors
        elif warrant_typ == 11:  # 应收
            print('warrant_typ == 11')
            form_receivable_add_edit = forms.FormReceivable(post_data)
            if form_receivable_add_edit.is_valid():
                receivable_clean = form_receivable_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6, evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        receivable_obj = models.Receivable.objects.create(
                            warrant=warrant_obj, receivable_buildor=request.user,
                            receive_owner_id=receivable_clean['receive_owner'],
                            receivable_detail=receivable_clean['receivable_detail'])
                    response['message'] = '应收账款创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '应收账款创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_receivable_add_edit.errors
        elif warrant_typ == 21:  # 股权
            print('warrant_typ == 21')
            form_stockes_add_edit = forms.FormStockes(post_data)
            if form_stockes_add_edit.is_valid():
                stocke_clean = form_stockes_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6, evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        stock_obj = models.Stockes.objects.create(
                            warrant=warrant_obj, stock_buildor=request.user,
                            stock_typ=stocke_clean['stock_typ'],
                            stock_owner_id=stocke_clean['stock_owner'],
                            target=stocke_clean['target'], registe=round(stocke_clean['registe'], 2),
                            share=round(stocke_clean['share'], 2),
                            ratio=round(stocke_clean['ratio'], 2))
                    response['message'] = '股权创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '股权创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_stockes_add_edit.errors
        elif warrant_typ == 31:  # 票据
            print('warrant_typ == 31')
            form_draft_add_eidt = forms.FormDraft(post_data)
            if form_draft_add_eidt.is_valid():
                draft_clean = form_draft_add_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        draft_obj = models.Draft.objects.create(
                            warrant=warrant_obj, draft_buildor=request.user,
                            draft_owner_id=draft_clean['draft_owner'],
                            typ=draft_clean['typ'],
                            denomination=draft_clean['denomination'],
                            draft_detail=draft_clean['draft_detail'])
                    response['message'] = '票据包创建成功，请添加票据！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '票据创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_draft_add_eidt.errors
        elif warrant_typ == 41:  # 车辆
            print('warrant_typ == 41')
            form_vehicle_add_eidt = forms.FormVehicle(post_data)
            if form_vehicle_add_eidt.is_valid():
                vehicle_clean = form_vehicle_add_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        vehicle_obj = models.Vehicle.objects.create(
                            warrant=warrant_obj, vehicle_buildor=request.user,
                            vehicle_owner_id=vehicle_clean['vehicle_owner'],
                            frame_num=vehicle_clean['frame_num'],
                            plate_num=vehicle_clean['plate_num'],
                            vehicle_brand=vehicle_clean['vehicle_brand'],
                            vehicle_remark=vehicle_clean['vehicle_remark'])
                    response['message'] = '车辆创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '车辆创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_vehicle_add_eidt.errors
        elif warrant_typ == 51:  # 动产
            print('warrant_typ == 51')
            form_chattel_add_eidt = forms.FormChattel(post_data)
            if form_chattel_add_eidt.is_valid():
                chattel_clean = form_chattel_add_eidt.cleaned_data
                try:
                    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), 
        (31, '解保出库'), (99, '已注销'))'''
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6, evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        chattel_obj = models.Chattel.objects.create(
                            warrant=warrant_obj, chattel_buildor=request.user,
                            chattel_owner_id=chattel_clean['chattel_owner'],
                            chattel_typ=chattel_clean['chattel_typ'],
                            chattel_detail=chattel_clean['chattel_detail'])
                    response['message'] = '动产创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '动产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_chattel_add_eidt.errors
        elif warrant_typ == 55:  # 其他
            print('warrant_typ == 55')
            form_other_add_eidt = forms.FormOthers(post_data)  # 55其他添加
            if form_other_add_eidt.is_valid():
                other_clean = form_other_add_eidt.cleaned_data
                try:
                    '''WARRANT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销'))'''
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'], warrant_state=6, evaluate_state=99,
                            warrant_typ=warrant_typ, warrant_buildor=request.user)
                        other_obj = models.Others.objects.create(
                            warrant=warrant_obj, otheror=request.user,
                            other_owner_id=other_clean['other_owner'],
                            other_typ=other_clean['other_typ'],
                            other_detail=other_clean['other_detail'])
                    response['message'] = '资产创建成功！！！'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
                except Exception as e:
                    response['status'] = False
                    response['message'] = '资产创建失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_other_add_eidt.errors
        elif warrant_typ == 99:  # 他权
            print('warrant_typ == 99')
            form_hypothecs_add_eidt = forms.HypothecsAddEidtForm(post_data)
            if form_hypothecs_add_eidt.is_valid():
                hypothecs_add_edit_clean = form_hypothecs_add_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_obj = models.Warrants.objects.create(
                            warrant_num=warrant_add_clean['warrant_num'],
                            warrant_typ=warrant_typ)
                        hypothecs_obj = models.Hypothecs.objects.create(
                            warrant=warrant_obj,
                            agree=hypothecs_add_edit_clean['agree'])
                    response['message'] = '他权创建成功！！！，请继续创建抵押资产信息。'
                    response['skip'] = "/dbms/warrant/scan/%s/" % warrant_obj.id
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
@authority
def warrant_del_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def warrant_edit_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = int(post_data['warrant_id'])
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list.first()
    warrant_typ = warrant_obj.warrant_typ
    form_warrant_edit = forms.WarrantEditForm(post_data)
    if form_warrant_edit.is_valid():
        warrant_edit_clean = form_warrant_edit.cleaned_data
        '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
        (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''
        if warrant_typ == 1:  # (1, '房产')
            form_house_add_edit = forms.HouseAddEidtForm(post_data)
            if form_house_add_edit.is_valid():
                house_add_edit_clean = form_house_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(warrant_num=warrant_edit_clean['warrant_num'])
                        models.Houses.objects.filter(warrant=warrant_obj).update(
                            house_locate=house_add_edit_clean['house_locate'],
                            house_app=house_add_edit_clean['house_app'],
                            house_name=house_add_edit_clean['house_name'],
                            house_area=house_add_edit_clean['house_area'])
                    response['message'] = '房产修改成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '房产修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_house_add_edit.errors
        elif warrant_typ == 5:  # (5, '土地')
            form_ground_add_edit = forms.GroundAddEidtForm(post_data)
            if form_ground_add_edit.is_valid():
                ground_add_edit_clean = form_ground_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Grounds.objects.filter(warrant=warrant_obj).update(
                            ground_locate=ground_add_edit_clean['ground_locate'],
                            ground_app=ground_add_edit_clean['ground_app'],
                            ground_area=ground_add_edit_clean['ground_area'])
                        response['message'] = '土地信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '土地修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_ground_add_edit.errors
        elif warrant_typ == 6:  # (6, '在建工程')
            form_construct_add_edit = forms.ConstructionAddForm(post_data)
            if form_construct_add_edit.is_valid():
                construct_add_edit_clean = form_construct_add_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Construction.objects.filter(warrant=warrant_obj).update(
                            coustruct_locate=construct_add_edit_clean['coustruct_locate'],
                            coustruct_app=construct_add_edit_clean['coustruct_app'],
                            coustruct_area=construct_add_edit_clean['coustruct_area'])
                        response['message'] = '在建工程信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '在建工程修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_construct_add_edit.errors
        elif warrant_typ == 11:  # (11, '应收账款')
            form_receivable_edit = forms.FormReceivableEdit(post_data)
            if form_receivable_edit.is_valid():
                receivable_edit_clean = form_receivable_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Receivable.objects.filter(warrant=warrant_obj).update(
                            receivable_detail=receivable_edit_clean['receivable_detail'])
                        response['message'] = '应收账款信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '应收账款信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_receivable_edit.errors
        elif warrant_typ == 21:  # (21, '股权')
            form_stockes_edit = forms.FormStockesEdit(post_data)
            if form_stockes_edit.is_valid():
                stockes_edit_clean = form_stockes_edit.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Stockes.objects.filter(warrant=warrant_obj).update(
                            target=stockes_edit_clean['target'], registe=round(stockes_edit_clean['registe'], 2),
                            share=stockes_edit_clean['share'], ratio=stockes_edit_clean['ratio'],
                            stock_typ=stockes_edit_clean['stock_typ'])
                        response['message'] = '股权信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '股权信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_stockes_edit.errors
        elif warrant_typ == 31:  # (31, '票据')
            form_draft_eidt = forms.FormDraftEdit(post_data)
            if form_draft_eidt.is_valid():
                draft_edit_clean = form_draft_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Draft.objects.filter(warrant=warrant_obj).update(
                            draft_detail=draft_edit_clean['draft_detail'],
                            typ=draft_edit_clean['typ'],
                            denomination=draft_edit_clean['denomination'])
                        response['message'] = '票据信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '票据信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_draft_eidt.errors
        elif warrant_typ == 41:  # (41, '车辆')
            form_vehicle_eidt = forms.FormVehicleEdit(post_data)  # 41车辆添加
            if form_vehicle_eidt.is_valid():
                vehicle_edit_clean = form_vehicle_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Vehicle.objects.filter(warrant=warrant_obj).update(
                            frame_num=vehicle_edit_clean['frame_num'],
                            plate_num=vehicle_edit_clean['plate_num'],
                            vehicle_brand=vehicle_edit_clean['vehicle_brand'],
                            vehicle_remark=vehicle_edit_clean['vehicle_remark'], )
                        response['message'] = '车辆信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '车辆信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_vehicle_eidt.errors
        elif warrant_typ == 51:  # (51, '动产')
            form_chattel_eidt = forms.FormChattelEdit(post_data)  # 51动产添加
            if form_chattel_eidt.is_valid():
                chattel_edit_clean = form_chattel_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Chattel.objects.filter(warrant=warrant_obj).update(
                            chattel_typ=chattel_edit_clean['chattel_typ'],
                            chattel_detail=chattel_edit_clean['chattel_detail'])
                        response['message'] = '动产信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '动产信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_chattel_eidt.errors
        elif warrant_typ == 55:  # (55, '其他')
            form_other_eidt = forms.FormOthersEdit(post_data)  # 55其他添加
            if form_other_eidt.is_valid():
                other_edit_clean = form_other_eidt.cleaned_data
                try:
                    with transaction.atomic():
                        warrant_list.update(
                            warrant_num=warrant_edit_clean['warrant_num'])
                        models.Others.objects.filter(warrant=warrant_obj).update(
                            other_typ=other_edit_clean['other_typ'],
                            other_detail=other_edit_clean['other_detail'])
                        response['message'] = '其他权证信息修改该成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '其他权证信息修改失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_other_eidt.errors
        elif warrant_typ == 99:  # (99, '他权')
            try:
                warrant_list.update(warrant_num=warrant_edit_clean['warrant_num'])
                response['message'] = '他权信息修改该成功！！！'
            except Exception as e:
                response['status'] = False
                response['message'] = '他权信息修改失败：%s' % str(e)
        else:
            response['message'] = '无该类型权证，请联系管理员！！！'
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_warrant_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------产权证添加ajax-------------------------#
@login_required
@authority
def owership_add_ajax(request):  # 产权证添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def owership_del_ajax(request):  # 产权证删除ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    warrant_id = post_data['warrant_id']
    owership_id = post_data['owership_id']

    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    owership_obj = models.Ownership.objects.get(id=owership_id)

    lending_warrant_list = ''  # warrant_obj.lending_warrant.all()

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


# -----------------------产权证添加ajax-------------------------#
@login_required
@authority
def housebag_add_ajax(request):  # 产权证添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = post_data['warrant_id']
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    form_housebag_add_edit = forms.HouseBagAddEidtForm(post_data)
    if form_housebag_add_edit.is_valid():
        housebag_clean = form_housebag_add_edit.cleaned_data
        print('housebag_clean:', housebag_clean)
        try:
            housebag_obj = models.HouseBag.objects.create(
                warrant=warrant_obj, housebag_locate=housebag_clean['housebag_locate'],
                housebag_app=housebag_clean['housebag_app'], housebag_area=housebag_clean['housebag_area'],
                housebag_buildor=request.user)
            response['message'] = '资产包创建成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '资产包创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_housebag_add_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------产权证删除ajax-------------------------#
@login_required
@authority
def housebag_del_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    housebag_obj = models.HouseBag.objects.get(id=post_data['housebag_id'])

    lending_warrant_list = ''  # warrant_obj.lending_warrant.all()
    if lending_warrant_list:
        response['status'] = False
        response['message'] = '担保物已作为项目反担保，无法删除！'
    else:
        try:
            housebag_obj.delete()  # 删除评审会
            msg = '房产项目删除成功！'
            response['message'] = msg
        except Exception as e:
            response['status'] = False
            response['message'] = '房产项目删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ----------------------付款人添加ajax-------------------------#
@login_required
@authority
def receivextend_add_ajax(request):  # 产权证添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    receive_obj = models.Receivable.objects.get(id=post_data['receivable_id'])

    form_receivbag_add = forms.FormReceivExtend(post_data)
    if form_receivbag_add.is_valid():
        receivbag_clean = form_receivbag_add.cleaned_data
        try:
            receivbag_obj = models.ReceiveExtend.objects.create(
                receivable=receive_obj, receive_unit=receivbag_clean['receive_unit'],
                receiv_e_buildor=request.user)
            response['message'] = '应收单位创建成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '应收单位创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_receivbag_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------付款人删除ajax-------------------------#
@login_required
@authority
def receivextend_del_ajax(request):  # 产权证删除ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    receivbag_obj = models.ReceiveExtend.objects.get(id=post_data['receivbag_id'])

    lending_warrant_list = ''  # warrant_obj.lending_warrant.all()
    if lending_warrant_list:
        response['status'] = False
        response['message'] = '担保物已作为项目反担保，无法删除！'
    else:
        try:
            receivbag_obj.delete()  # 删除评审会
            msg = '付款人删除成功！'
            response['message'] = msg
        except Exception as e:
            response['status'] = False
            response['message'] = '付款人删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ----------------------票据添加ajax-------------------------#
@login_required
@authority
def draftextend_add_ajax(request):  # 产权证添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = post_data['warrant_id']
    warrant_obj = models.Warrants.objects.get(id=warrant_id)
    draft_obj = warrant_obj.draft_warrant
    form_draftbag_add_edit = forms.FormDraftExtend(post_data)
    if form_draftbag_add_edit.is_valid():
        draftbag_clean = form_draftbag_add_edit.cleaned_data
        print('draftbag_clean:', draftbag_clean)
        try:
            draftbag_obj = models.DraftExtend.objects.create(
                draft=draft_obj, draft_typ=draftbag_clean['draft_typ'],
                draft_num=draftbag_clean['draft_num'], draft_acceptor=draftbag_clean['draft_acceptor'],
                draft_amount=draftbag_clean['draft_amount'],
                issue_date=draftbag_clean['issue_date'], due_date=draftbag_clean['due_date'],
                draft_e_buildor=request.user)
            response['message'] = '票据创建成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '票据创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_draftbag_add_edit.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------票据删除ajax-------------------------#
@login_required
@authority
def draftbag_del_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    draftbag_obj = models.DraftExtend.objects.get(id=post_data['draftbag_id'])

    lending_warrant_list = ''  # warrant_obj.lending_warrant.all()
    if lending_warrant_list:
        response['status'] = False
        response['message'] = '担保物已作为项目反担保，无法删除！'
    else:
        try:
            draftbag_obj.delete()  # 删除评审会
            msg = '票据项删除成功！'
            response['message'] = msg
        except Exception as e:
            response['status'] = False
            response['message'] = '票据项删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------抵押物添加ajax-------------------------#
@login_required
@authority
def guaranty_add_ajax(request):  # 抵押物添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def guaranty_del_ajax(request):  # 抵押物
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
@authority
def storages_add_ajax(request):  # 出入库添加ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_id = post_data['warrant_id']
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list.first()
    warrant_state = warrant_obj.warrant_state
    form_storage_add_edit = forms.StoragesAddEidtForm(post_data)
    '''STORAGE_TYP_LIST = [(1, '入库'), (2, '续抵出库'), (6, '无需入库'), (11, '借出'), (12, '归还'), 
    (31, '解保出库')]'''
    '''WARRANT_STATE_LIST = [
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销')]'''
    if form_storage_add_edit.is_valid():
        storage_add_clean = form_storage_add_edit.cleaned_data
        storage_typ = storage_add_clean['storage_typ']
        if warrant_state == 99:  # (99, '已注销'))
            response['status'] = False
            response['message'] = '权证状态为：%s，无法办理出入库操作！' % warrant_state
        elif warrant_state == 2:  # (2, '已入库')----在库状态
            if storage_typ in [2, 11, 31]:  # (2, '出库'), (3, '借出'), (5, '解保')----出库
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
                                storage_explain = storage_add_clean['storage_explain']
                                storage_obj = models.Storages.objects.create(
                                    warrant=warrant_obj, storage_typ=storage_typ,
                                    storage_date=storage_add_clean['storage_date'],
                                    transfer=storage_add_clean['transfer'],
                                    storage_explain=storage_explain,
                                    conservator=request.user)
                                warrant_list.update(warrant_state=99, storage_explain=storage_explain)
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
                            storage_explain = storage_add_clean['storage_explain']
                            storage_obj = models.Storages.objects.create(
                                warrant=warrant_obj, storage_typ=storage_typ,
                                storage_date=storage_add_clean['storage_date'],
                                transfer=storage_add_clean['transfer'],
                                storage_explain=storage_explain,
                                conservator=request.user)
                            '''STORAGE_TYP_LIST = ((1, '入库'), (2, '续抵出库'), (11, '借出'), (12, '归还'), (31, '解保出库'))'''
                            '''WARRANT_STATE_LIST = (
                                (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
                                 (99, '已注销'))'''
                            if storage_typ == 2:
                                warrant_list.update(warrant_state=11, storage_explain=storage_explain)
                            elif storage_typ == 11:
                                warrant_list.update(warrant_state=21, storage_explain=storage_explain)
                            else:
                                warrant_list.update(warrant_state=31, storage_explain=storage_explain)
                        response['message'] = '权证出库成功！！！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '权证出库失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '该权证不在库中，无法办理出库操作！！！'
        else:  # (1, '未入库'), (3, '已出库'), (4, '已借出'), (6, '无需入库')----不在库状态
            if storage_typ in [1, 12]:  # (1, '入库'), (4, '归还')----入库
                try:
                    with transaction.atomic():
                        storage_explain = storage_add_clean['storage_explain']
                        storage_obj = models.Storages.objects.create(
                            warrant=warrant_obj, storage_typ=storage_typ,
                            storage_date=storage_add_clean['storage_date'],
                            transfer=storage_add_clean['transfer'],
                            storage_explain=storage_explain,
                            conservator=request.user)
                        warrant_list.update(warrant_state=2, storage_explain=storage_explain)
                    response['message'] = '权证入库成功！！！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '权证入库失败：%s' % str(e)
            elif storage_typ == 6:  # (6, '无需入库')
                try:
                    with transaction.atomic():
                        storage_explain = storage_add_clean['storage_explain']
                        storage_obj = models.Storages.objects.create(
                            warrant=warrant_obj, storage_typ=storage_typ,
                            storage_date=storage_add_clean['storage_date'],
                            transfer=storage_add_clean['transfer'],
                            storage_explain=storage_explain,
                            conservator=request.user)
                        warrant_list.update(warrant_state=6, storage_explain=storage_explain)
                    response['message'] = '权证设置为“无需入库”！！！'
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


# -----------------------出入库删除ajax-------------------------#
@login_required
@authority
def storage_del_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    warrant_list = models.Warrants.objects.filter(id=post_data['warrant_id'])
    warrant_obj = warrant_list.first()
    warrant_state = warrant_obj.warrant_state

    storage_list = models.Storages.objects.filter(id=post_data['storage_id'])
    storage_obj = storage_list.first()
    storage_typ = storage_obj.storage_typ

    '''STORAGE_TYP_LIST = [(1, '入库'), (2, '续抵出库'), (6, '无需入库'), (11, '借出'), (12, '归还'), 
    (31, '解保出库')]'''
    '''WARRANT_STATE_LIST = [
        (1, '未入库'), (2, '已入库'), (6, '无需入库'), (11, '续抵出库'), (21, '已借出'), (31, '解保出库'),
        (99, '已注销')]'''
    if storage_typ in [1, 6]:  # (1, '入库'), (6, '无需入库')
        try:
            with transaction.atomic():
                storage_list.delete()
                warrant_list.update(warrant_state=1)
            response['message'] = '出入库信息删除成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '出入库信息散出失败：%s' % str(e)
    elif storage_typ in [2, 11, 31]:  # (2, '续抵出库'),(11, '借出'), (31, '解保出库')
        try:
            with transaction.atomic():
                storage_list.delete()
                warrant_list.update(warrant_state=2)
            response['message'] = '出入库信息删除成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '出入库信息散出失败：%s' % str(e)
    elif storage_typ == 12:  # (12, '归还')
        try:
            with transaction.atomic():
                storage_list.delete()
                warrant_list.update(warrant_state=21)
            response['message'] = '出入库信息删除成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '出入库信息散出失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------评估添加ajax-------------------------#
@login_required
@authority
def evaluate_add_ajax(request):  #
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    warrant_id = post_data['warrant_id']
    warrant_list = models.Warrants.objects.filter(id=warrant_id)
    warrant_obj = warrant_list.first()
    form_evaluate_add_edit = forms.EvaluateAddEidtForm(post_data)
    if form_evaluate_add_edit.is_valid():
        evaluate_clean = form_evaluate_add_edit.cleaned_data
        try:
            with transaction.atomic():
                evaluate_state = evaluate_clean['evaluate_state']
                evaluate_value = evaluate_clean['evaluate_value']
                evaluate_date = evaluate_clean['evaluate_date']
                evaluate_explain = evaluate_clean['evaluate_explain']
                ''' EVALUATE_STATE_LIST = [(1, '机构评估'), (11, '机构预估'), (21, '综合询价'), (31, '购买成本'),
                                           (41, '拍卖评估'), (99, '无需评估')]'''
                evaluate_default = {
                    'warrant': warrant_obj, 'evaluate_state': evaluate_state, 'evaluate_value': evaluate_value,
                    'evaluate_date': evaluate_date, 'evaluate_explain': evaluate_explain,
                    'evaluator': request.user}
                evaluate_obj, created = models.Evaluate.objects.update_or_create(
                    warrant=warrant_obj, evaluate_date=evaluate_date, defaults=evaluate_default)

                '''EVALUATE_STATE_LIST = [(0, '待评估'), (1, '机构评估'), (11, '机构预估'), 
                (21, '综合询价'), (31, '购买成本'),
                           (41, '拍卖评估'), (99, '无需评估')]'''
                warrant_list.update(evaluate_state=evaluate_state, evaluate_value=evaluate_value,
                                    evaluate_date=evaluate_date, evaluate_explain=evaluate_explain)
            response['message'] = '评估成功！！！'
        except Exception as e:
            response['status'] = False
            response['message'] = '评估失败：%s' % str(e)
            print(response['message'])
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_evaluate_add_edit.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
