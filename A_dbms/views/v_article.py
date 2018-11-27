from django.shortcuts import render, redirect
from .. import permissions
from .. import models
from .. import forms
import datetime, time
from django.contrib.auth.decorators import login_required
from django.urls import resolve
from django.db.models import Q, F


# 项目信息管理
# --------------------------------70---------------------------------#
# -----------------------------项目管理-------------------------------#
@login_required
def article(request, *args, **kwargs):  # 项目列表
    print(__file__, '---->def article')
    print('article-->**kwargs:', kwargs)
    print('article_add-->request.path:', request.path)
    print('article_add-->request.get_host:', request.get_host())
    print('article_add-->resolve(request.path):',
          resolve(request.path))
    print('type(request.user):', type(request.user))

    condition = {
        # 'article_state' : 0, #查询字段及值的字典，空字典查询所有
    }  # 建立空的查询字典
    for k, v in kwargs.items():
        # temp = int(v)
        temp = v
        kwargs[k] = temp
        if temp:
            condition[k] = temp  # 将参数放入查询字典
    print('condition:', condition)
    article_state_list = models.Articles.ARTICLE_STATE_LIST
    article_state_list_dic = list(map(
        lambda x: {'id': x[0], 'name': x[1]},
        article_state_list))
    print('article-->article_state_list:', article_state_list)
    # 列表或元组转换为字典并添加key
    article_list = models.Articles.objects.filter(
        **kwargs).select_related(
        'custom',
        'director',
        'assistant',
        'control')
    print('article-->article_list:', article_list)
    return render(request,
                  'dbms/article/article.html',
                  locals())


# -----------------------------添加项目------------------------------#
@login_required
def article_add(request):  # 添加项目
    print(__file__, '---->def article_add')
    if request.method == "GET":
        form = forms.ArticlesAddForm()
        return render(request,
                      'dbms/article/article-add.html',
                      locals())
    else:
        form = forms.ArticlesAddForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            custom_id = cleaned_data['custom_id']
            custom = models.Customes.objects.get(id=custom_id)
            if custom.genre == 1:
                short_name = models.CustomesC.objects. \
                    get(custome__id=custom_id).short_name
            else:
                short_name = custom.name
            ###时间处理
            article_date = cleaned_data['article_date']
            date_array = time.strptime(str(article_date),
                                       "%Y-%m-%d")
            year = str(date_array.tm_year)
            if date_array.tm_mon < 10:
                mon = '0' + str(date_array.tm_mon)
            else:
                mon = str(date_array.tm_mon)
            ###时间处理
            renewal = cleaned_data['renewal']
            augment = cleaned_data['augment']
            amount = renewal + augment
            article_num = short_name + '_' + \
                          year + mon + '_' + \
                          str(int(amount / 10000)) + \
                          '万'

            article_obj = models.Articles.objects.create(
                article_num=article_num,
                custom_id=custom_id,
                renewal=renewal,
                augment=augment,
                amount=amount,
                director_id=cleaned_data['director_id'],
                assistant_id=cleaned_data['assistant_id'],
                control_id=cleaned_data['control_id'],
                article_date=article_date)

            return redirect('dbms:article_all')
        else:
            return render(request,
                          'dbms/article/article-add.html',
                          locals())


# -----------------------------编辑项目------------------------------#
@login_required
def article_edit(request, article_id):  # 编辑项目
    print(__file__, '---->def article_edit')
    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'), (4, '需补调'),
                          (5, '已补调'), (6, '已签批'))'''
    if article_obj.article_state == 1:
        if request.method == "GET":
            # form初始化，适合做修改该
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
                          'dbms/article/article-edit.html',
                          locals())
        else:
            # form验证
            form = forms.ArticlesAddForm(request.POST, request.FILES)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                custom_id = cleaned_data['custom_id']
                custom = models.Customes.objects.get(id=custom_id)
                if custom.genre == 1:
                    short_name = models.CustomesC.objects. \
                        get(custome__id=custom_id).short_name
                else:
                    short_name = custom.name
                ###时间处理
                article_date = cleaned_data['article_date']
                date_array = time.strptime(str(article_date),
                                           "%Y-%m-%d")
                year = str(date_array.tm_year)
                if date_array.tm_mon < 10:
                    mon = '0' + str(date_array.tm_mon)
                else:
                    mon = str(date_array.tm_mon)
                ###时间处理
                renewal = cleaned_data['renewal']
                augment = cleaned_data['augment']
                amount = renewal + augment
                article_num = short_name + '_' + \
                              year + mon + '_' + \
                              str(int(amount / 10000)) + \
                              '万'
                # 修改数据库
                print('cleaned_data:', cleaned_data)
                article_obj = models.Articles.objects.filter(
                    id=article_id)

                article_obj.update(
                    article_num=article_num,
                    custom_id=custom_id,
                    renewal=renewal,
                    augment=augment,
                    amount=amount,
                    credit_term=cleaned_data['credit_term'],
                    director_id=cleaned_data['director_id'],
                    assistant_id=cleaned_data['assistant_id'],
                    control_id=cleaned_data['control_id'],
                    article_date=article_date)

                return redirect('dbms:article_all')
            else:
                return render(request,
                              'dbms/article/article-edit.html',
                              locals())
    else:
        print('状态为：%s，无法修改！！！' % article_obj.article_state)
        return redirect('dbms:article_all')


# -----------------------------删除项目------------------------------#
@login_required
def article_del(request, article_id):  # 删除项目
    print(__file__, '---->def article_del')
    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'), (4, '需补调'),
                          (5, '已补调'), (6, '已签批'))'''
    if article_obj.article_state == 1:
        article_obj.delete()
    else:
        print('状态为：%s，无法删除！！！' % article_obj.article_state)
    return redirect('dbms:article_all')


# -----------------------------项目预览------------------------------#
@login_required
def article_scan(request, article_id):  # 项目预览
    print(__file__, '---->def article_scan')
    article_obj = models.Articles.objects.get(id=article_id)
    return render(request,
                  'dbms/article/article-scan.html',
                  locals())


@login_required
def article_scan_agree(request, article_id, agree_id):  # 项目预览
    print(__file__, '---->def article_scan_agree')
    print('article_id:', article_id)
    print('agree_id:', agree_id)
    article_obj = models.Articles.objects.get(id=article_id)
    agree_obj = models.Agrees.objects.get(id=agree_id)
    return render(request,
                  'dbms/article/article-agree.html',
                  locals())
