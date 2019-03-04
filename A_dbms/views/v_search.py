from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
from django.contrib.auth.decorators import login_required
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction
from django.db.models import Q, F

from django.views import View
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority

# -----------------------搜索客户-------------------------#
# @login_required
def search_custom_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, 'custom_list': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    '''搜索'''
    search_key = post_data['search_custom']
    print('search_key:', search_key)
    if search_key:
        search_fields = ['name', 'short_name']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
    custom_list = models.Customes.objects.filter(q).order_by('name').values_list('id', 'name')

    custom_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, custom_list))

    print('custom_list:', custom_list)
    print('custom_list_dic:', custom_list_dic)

    response['custom_list'] = custom_list_dic
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------搜索权证-------------------------#
# @login_required
def search_warrant_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, 'warrant_list': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    '''搜索'''
    search_key = post_data['search_warrant']
    print('search_key:', search_key)
    if search_key:
        search_fields = ['warrant_num']
        q = Q()
        q.connector = 'OR'
        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
    warrant_list = models.Warrants.objects.filter(q).order_by('warrant_num').values_list('id', 'warrant_num')
    warrant_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, warrant_list))

    response['warrant_list'] = warrant_list_dic
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------搜索权证-------------------------#
# @login_required
def guarantee_warrant_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, ' skip': None, 'warrant_list': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    '''搜索'''
    sure_typ = int(post_data['sure_typ'])
    '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if sure_typ == 1:  # 企业
        search_typ = 1
    elif sure_typ == 2:  # 个人
        search_typ = 2
    elif sure_typ in [11, 21, 42, 52]:  # 房产
        search_typ = [1, 2]
    elif sure_typ in [12, 22, 43, 53]:  # 土地
        search_typ = 5
    elif sure_typ == 13:  # 动产
        search_typ = 51
    elif sure_typ == 15:  # 车辆
        search_typ = 41
    elif sure_typ == 31:  # 应收
        search_typ = 11
    elif sure_typ in [32, 51]:  # 股权
        search_typ = 21
    elif sure_typ == 33:  # 票据
        search_typ = 31
    elif sure_typ == 41:  # 合格证
        search_typ = ''
    else:
        search_typ = ''
    '''WARRANT_TYP_LIST = [
        (1, '房产'), (2, '房产包'), (5, '土地'), (11, '应收'), (21, '股权'),
        (31, '票据'), (41, '车辆'), (51, '动产'), (99, '他权')]'''
    search_key = post_data['search_guarantee']
    print('search_key:', search_key, 'sure_typ:', sure_typ)
    if sure_typ in [1, 2]:
        '''GENRE_LIST = ((1, '企业'), (2, '个人'))'''
        search_list = models.Customes.objects.filter(genre=search_typ).order_by('name')
        if search_key:
            search_fields = ['name', 'short_name']
            q = Q()
            q.connector = 'OR'
            for field in search_fields:
                q.children.append(("%s__contains" % field, search_key))
            search_list = search_list.filter(q).values_list('id', 'name')
    else:
        if sure_typ in [11, 21, 42, 52]:
            search_list = models.Warrants.objects.filter(warrant_typ__in=search_typ).order_by('warrant_num')
        else:
            search_list = models.Warrants.objects.filter(warrant_typ=search_typ).order_by('warrant_num')
        if search_key:
            search_fields = ['warrant_num']
            q = Q()
            q.connector = 'OR'
            for field in search_fields:
                q.children.append(("%s__contains" % field, search_key))
        search_list = search_list.filter(q).values_list('id', 'warrant_num')
    print('search_list:', search_list)
    search_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, search_list))
    response['search_list'] = search_list_dic
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
