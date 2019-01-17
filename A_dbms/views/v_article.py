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


# -----------------------------项目管理-------------------------------#
def creat_article_num(custom_id):
    custom = models.Customes.objects.get(id=custom_id)
    if custom.genre == 1:
        short_name = models.CustomesC.objects.get(custome__id=custom_id).short_name
    else:
        short_name = custom.name
        ###时间处理
    article_date = time.gmtime()
    n_year = article_date.tm_year
    if article_date.tm_mon < 10:
        n_mon = '0' + str(article_date.tm_mon)
    else:
        n_mon = str(article_date.tm_mon)
    r_order = models.Articles.objects.filter(
        custom=custom_id, article_date__year=n_year).count() + 1
    article_num = '%s-%s%s-%s' % (short_name, str(n_year), n_mon, r_order)
    return article_num


@login_required
def article(request, *args, **kwargs):  # 项目列表
    print(__file__, '---->def article')
    print('**kwargs:', kwargs)
    # print('request.path:', request.path)
    # print('request.get_host:', request.get_host())
    # print('resolve(request.path):', resolve(request.path))
    # print('type(request.user):', type(request.user))
    # print('request.user:', request.user)
    # print('request.GET.items():', request.GET.items())
    # request.GET.items()获取get传递的参数对
    print('request.GET:', request.GET)

    form_article_add_edit = forms.ArticlesAddForm()

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
    article_state_list_dic = list(map(lambda x: {'id': x[0], 'name': x[1]}, article_state_list))
    print('article_state_list_dic:', article_state_list_dic)
    # 列表或元组转换为字典并添加key

    article_list = models.Articles.objects.filter(**kwargs).select_related(
        'custom', 'director', 'assistant', 'control').order_by('-article_date')
    search_key = request.GET.get('_s')
    print('search_key:', search_key)
    if search_key:
        search_fields = ['custom__name', 'director__name', 'assistant__name', 'control__name']
        q = Q()
        q.connector = 'OR'

        for field in search_fields:
            q.children.append(("%s__contains" % field, search_key))
        print('q:', q)
        article_list = article_list.filter(q)

    # 分页
    paginator = Paginator(article_list, 18)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request, 'dbms/article/article.html', locals())


# -----------------------------项目预览------------------------------#
@login_required
def article_scan(request, article_id):  # 项目预览
    print(__file__, '---->def article_scan')
    PAGE_TITLE = '查看项目'

    article_obj = models.Articles.objects.get(id=article_id)

    form_date = {
        'custom_id': article_obj.custom.id, 'renewal': article_obj.renewal,
        'augment': article_obj.augment, 'credit_term': article_obj.credit_term,
        'director_id': article_obj.director.id,
        'assistant_id': article_obj.assistant.id, 'control_id': article_obj.control.id,
        'article_date': str(article_obj.article_date)}
    form_article_add_edit = forms.ArticlesAddForm(form_date)
    expert_list = article_obj.expert.values_list('id')
    feedbac_list = article_obj.feedback_article.all()
    if feedbac_list:
        form_date = {
            'propose': feedbac_list[0].propose, 'analysis': feedbac_list[0].analysis,
            'suggestion': feedbac_list[0].suggestion}
        form_feedback = forms.FeedbackAddForm(initial=form_date)
    else:
        form_feedback = forms.FeedbackAddForm()

    return render(request, 'dbms/article/article-scan.html', locals())


# -----------------------------项目预览------------------------------#

@login_required
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    print(__file__, '---->def article_scan_agree')
    PAGE_TITLE = '查看项目'

    sure_list = [1, 2]  # 保证反担保类型
    house_list = [11, 21, 42, 52]
    ground_list = [12, 22, 43, 53]
    receivable_list = [31]
    stock_list = [32]

    article_obj = models.Articles.objects.get(id=article_id)
    agree_obj = models.Agrees.objects.get(id=agree_id)
    lending_obj = agree_obj.lending
    return render(request, 'dbms/article/article-scan-agree.html', locals())


# -----------------------------添加项目ajax------------------------------#
@login_required
def article_add_ajax(request):  # 添加项目
    print(__file__, '---->def article_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    form = forms.ArticlesAddForm(post_data, request.FILES)  #####
    if form.is_valid():
        cleaned_data = form.cleaned_data
        custom_id = cleaned_data['custom_id']
        renewal = cleaned_data['renewal']
        augment = cleaned_data['augment']
        article_num = creat_article_num(custom_id)
        print('article_num:', article_num)
        amount = renewal + augment
        try:
            article_obj = models.Articles.objects.create(
                article_num=article_num, custom_id=custom_id, renewal=renewal,
                augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                director_id=cleaned_data['director_id'], assistant_id=cleaned_data['assistant_id'],
                control_id=cleaned_data['control_id'], article_buildor=request.user)
            response['message'] = '成功创建项目：%s！' % article_obj.article_num
        except Exception as e:
            response['status'] = False
            response['message'] = '项目未创建成功：%s' % str(e)
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
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))
        (5, '已签批')-->才能出合同'''
    if article_obj.article_state == 1:
        form = forms.ArticlesAddForm(post_data, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print('cleaned_data:', cleaned_data)
            renewal = cleaned_data['renewal']
            augment = cleaned_data['augment']
            amount = renewal + augment
            try:
                article_list = models.Articles.objects.filter(id=article_id)
                article_list.update(
                    custom_id=cleaned_data['custom_id'], renewal=renewal,
                    augment=augment, amount=amount, credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'], assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'], article_buildor=request.user)
                response['message'] = '成功修改项目：%s！' % article_obj.article_num
            except Exception as e:
                response['status'] = False
                response['message'] = '项目未修改成功:%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法修改！！！' % article_obj.article_state

    result = json.dumps(response, ensure_ascii=False)

    return HttpResponse(result)


# -----------------------------删除项目ajax------------------------------#
@login_required
def article_del_ajax(request):
    print(__file__, '---->def article_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))
        (5, '已签批')-->才能出合同'''
    if article_obj.article_state == 1:
        article_obj.delete()  # 删除评审会
        response['message'] = '%s，删除成功！' % article_obj.article_num
    else:
        response['status'] = False
        response['message'] = '状态为：%s，删除失败！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------反馈项目ajax------------------------------#
@login_required
def article_feedback_ajax(request):
    print(__file__, '---->def article_feedback_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list[0]
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2]:
        form = forms.FeedbackAddForm(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print('cleaned_data:', cleaned_data)
            try:
                today_str = time.strftime("%Y-%m-%d", time.gmtime())
                default = {
                    'article_id': article_id, 'propose': cleaned_data['propose'],
                    'analysis': cleaned_data['analysis'], 'suggestion': cleaned_data['suggestion'],
                    'feedback_date': today_str, 'feedback_buildor': request.user}
                article, created = models.Feedback.objects.update_or_create(
                    article_id=article_id, defaults=default)
                article_list.update(article_state=2)  # 更新项目状态
                if created:
                    response['message'] = '成功成功反馈项目%s！' % article_obj.article_num
                else:
                    response['message'] = '成功更新反馈信息！'
            except Exception as e:
                response['status'] = False
                response['message'] = "项目未反馈成功：%s" % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法反馈！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)

#
# @login_required
# def article_scan_lending(request, article_id, lending_id):  # 项目预览
#     print(__file__, '---->def article_scan_lending')
#     print('request.path:', request.path)
#
#     sure_list = [1, 2]
#     house_list = [11, 21, 42, 52]
#     ground_list = [12, 22, 43, 53]
#     receivable_list = [31]
#     stock_list = [32, 51]
#     lending_operate = False
#
#     article_obj = models.Articles.objects.get(id=article_id)
#     lending_obj = models.LendingOrder.objects.get(id=lending_id)
#     print(article_obj, lending_obj)
#     return render(request, 'dbms/article/article-scan-lending.html', locals())
