from django.shortcuts import render, redirect, HttpResponse
from .. import permissions
from .. import models
from .. import forms
import datetime, time
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from django.db.utils import IntegrityError


# 项目信息管理
# --------------------------------70---------------------------------#
# -----------------------------项目管理-------------------------------#
def creat_article_num(custom_id, renewal, augment):
    custom = models.Customes.objects.get(id=custom_id)
    if custom.genre == 1:
        short_name = models.CustomesC.objects. \
            get(custome__id=custom_id).short_name
    else:
        short_name = custom.name

        ###时间处理
    article_date = time.gmtime()
    n_year = str(article_date.tm_year)
    if article_date.tm_mon < 10:
        n_mon = '0' + str(article_date.tm_mon)
    else:
        n_mon = str(article_date.tm_mon)

    amount = renewal + augment
    amount_w = str(int(amount / 10000))

    article_num = '%s_%s%s_%s万' % (short_name, n_year, n_mon, amount_w)

    return article_num


@login_required
def article(request, *args, **kwargs):  # 项目列表
    print(__file__, '---->def article')
    # print('**kwargs:', kwargs)
    # print('request.path:', request.path)
    # print('request.get_host:', request.get_host())
    # print('resolve(request.path):', resolve(request.path))
    # print('type(request.user):', type(request.user))
    # print('request.user:', request.user)
    # print('request.GET.items():', request.GET.items())
    # request.GET.items()获取get传递的参数对
    form = forms.ArticlesAddForm()
    for k, v in request.GET.items():
        print(k, ' ', v)

    condition = {
        # 'article_state' : 0, #查询字段及值的字典，空字典查询所有
    }  # 建立空的查询字典
    for k, v in kwargs.items():
        # temp = int(v)
        temp = v
        kwargs[k] = temp
        if temp:
            condition[k] = temp  # 将参数放入查询字典

    article_state_list = models.Articles.ARTICLE_STATE_LIST
    article_state_list_dic = list(map(
        lambda x: {'id': x[0], 'name': x[1]},
        article_state_list))
    # 列表或元组转换为字典并添加key

    article_list = models.Articles.objects.filter(
        **kwargs).select_related(
        'custom',
        'director',
        'assistant',
        'control', ).order_by('-article_date')

    # 分页
    paginator = Paginator(article_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/article/article.html',
                  locals())


# -----------------------------添加项目ajax------------------------------#
@login_required
def article_add_ajax(request):  # 添加项目
    print(__file__, '---->def article_add_ajax')

    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    custom_id = post_data['custom_id']
    renewal = post_data['renewal']
    augment = post_data['augment']
    credit_term = post_data['credit_term']
    director_id = post_data['director_id']
    assistant_id = post_data['assistant_id']
    control_id = post_data['control_id']

    data = {
        'custom_id': custom_id,
        'renewal': renewal,
        'augment': augment,
        'credit_term': credit_term,
        'director_id': director_id,
        'assistant_id': assistant_id,
        'control_id': control_id}

    form = forms.ArticlesAddForm(data, request.FILES)

    if form.is_valid():
        cleaned_data = form.cleaned_data

        custom_id = cleaned_data['custom_id']
        renewal = cleaned_data['renewal']
        augment = cleaned_data['augment']
        article_num = creat_article_num(custom_id, renewal, augment)

        amount = renewal + augment

        try:
            article_obj = models.Articles.objects.create(
                article_num=article_num,
                custom_id=custom_id,
                renewal=renewal,
                augment=augment,
                amount=amount,
                credit_term=cleaned_data['credit_term'],
                director_id=cleaned_data['director_id'],
                assistant_id=cleaned_data['assistant_id'],
                control_id=cleaned_data['control_id'],
                buildor=request.user)
            response['obj_num'] = article_obj.article_num
            response['message'] = '成功创建项目：%s！' % article_obj.article_num

        except IntegrityError as e:
            response['status'] = False
            response['message'] = '请不要重复创建项目！'

    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form.errors

    result = json.dumps(response, ensure_ascii=False)

    return HttpResponse(result)


# -----------------------------修改项目ajax------------------------------#
@login_required
def article_edit_ajax(request):  # 修改项目ajax
    print(__file__, '---->def article_edit_ajax')

    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    custom_id = post_data['custom_id']
    renewal = post_data['renewal']
    augment = post_data['augment']
    credit_term = post_data['credit_term']
    director_id = post_data['director_id']
    assistant_id = post_data['assistant_id']
    control_id = post_data['control_id']

    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同'''
    if article_obj.article_state == 1:
        data = {
            'custom_id': custom_id,
            'renewal': renewal,
            'augment': augment,
            'credit_term': credit_term,
            'director_id': director_id,
            'assistant_id': assistant_id,
            'control_id': control_id}

        form = forms.ArticlesAddForm(data, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            custom_id = cleaned_data['custom_id']
            renewal = cleaned_data['renewal']
            augment = cleaned_data['augment']
            article_num = creat_article_num(custom_id, renewal, augment)

            amount = renewal + augment

            try:
                article_list = models.Articles.objects.filter(
                    id=article_id)
                article_list.update(
                    article_num=article_num,
                    custom_id=custom_id,
                    renewal=renewal,
                    augment=augment,
                    amount=amount,
                    credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'],
                    assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'])

                response['obj_num'] = article_obj.article_num
                response['message'] = '成功修改项目：%s！' % article_obj.article_num

            except IntegrityError as e:
                response['status'] = False
                response['message'] = '项目未修改成功！'

        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        arg = '状态为：%s，无法修改！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = arg

    result = json.dumps(response, ensure_ascii=False)

    return HttpResponse(result)


# -----------------------------删除项目ajax------------------------------#
@login_required
def article_del_ajax(request):
    print(__file__, '---->def article_del_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']

    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同'''
    if article_obj.article_state == 1:
        article_obj.delete()  # 删除评审会
        msg = '%s，删除成功！' % article_obj.article_num
        response['message'] = msg
        response['data'] = article_obj.id

    else:
        msg = '状态为：%s，删除失败！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    # return redirect('dbms:article_all')
    return HttpResponse(result)


# -----------------------------项目预览------------------------------#
@login_required
def article_scan(request, article_id):  # 项目预览
    print(__file__, '---->def article_scan')
    article_obj = models.Articles.objects.get(id=article_id)
    form_date = {
        'custom_id': article_obj.custom.id,
        'renewal': article_obj.renewal,
        'augment': article_obj.augment,
        'credit_term': article_obj.credit_term,
        'director_id': article_obj.director.id,
        'assistant_id': article_obj.assistant.id,
        'control_id': article_obj.control.id,
        'article_date': str(article_obj.article_date)}
    form = forms.ArticlesAddForm(form_date)
    return render(request,
                  'dbms/article/article-scan.html',
                  locals())


@login_required
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    print(__file__, '---->def article_scan_agree')
    article_obj = models.Articles.objects.get(id=article_id)
    agree_obj = models.Agrees.objects.get(id=agree_id)
    return render(request,
                  'dbms/article/article-agree.html',
                  locals())
