from django.shortcuts import render, redirect
from .. import models
from .. import forms
import datetime, time


# 项目信息管理
# --------------------------------70---------------------------------#
# -----------------------------项目管理------------------------------#
def article(request, usernum, *args, **kwargs):  # 项目列表
    print(__file__, '---->def article')
    print('article-->usernum:', usernum)
    print('article-->**kwargs:', kwargs)
    ''' 
    condition = {
        # 'article_state' : 0, #查询字段及值的字典，空字典查询所有
    } #建立空的查询字典
    for k, v in kwargs.items():
        temp = int(v)
        kwargs[k] = temp
        if temp:
            condition[k] = temp #将参数放入查询字典
    '''
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
def article_add(request, usernum):  # 添加项目
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
            return redirect('dbms:article_all', user=request.user)
        else:
            return render(request,
                          'dbms/article/article-add.html',
                          locals())


# -----------------------------编辑项目------------------------------#
def article_edit(request, usernum, id):  # 编辑项目
    print(__file__, '---->def article_edit')
    article_obj = models.Articles.objects.get(id=id)
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
                article_obj = models.Articles.objects.filter(id=id)
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
                return redirect('dbms:article_all', user=request.user)
            else:
                return render(request,
                              'dbms/article/article-edit.html',
                              locals())
    else:
        print('无法修改！！！')
        return redirect('dbms:article_all', user=request.user)


# -----------------------------删除项目------------------------------#
def article_del(request, usernum, id):  # 删除项目
    print(__file__, '---->def article_del')
    article_obj = models.Articles.objects.get(id=id)
    if article_obj.article_state == 1:
        article_obj.delete()
    else:
        print('无法删除！！！')
    return redirect('dbms:article_all', user=request.user)
