from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
from django.contrib.auth.decorators import login_required
import json


# -----------------------------评审意见ajax------------------------------#
@login_required
def comment_edit_ajax(request):  # 修改项目ajax
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
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'), (4, '需补调'),
                          (5, '已补调'), (6, '已签批'))'''
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


@login_required
# -----------------------评审管理-------------------------#
def appraisal(request, *args, **kwargs):  # 评审管理
    print(__file__, '---->def appraisal')
    appraisal_list = models.Appraisals.objects.filter(**kwargs)
    print('appraisal_list:', appraisal_list)
    return render(request,
                  'dbms/appraisal/appraisal.html',
                  locals())


# -----------------------------评审意见ajax------------------------------#
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
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'), (4, '需补调'),
                          (5, '已补调'), (6, '已签批'))'''
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


# -----------------------评审会-------------------------#
def appraisal_edit(request, id):  # 评审会
    print(' -----------------------评审会------------------------')
    article_obj = models.Articles.objects.get(id=id)
    forma_date = {'article_num': article_obj.article_num,
                  'custom_id': article_obj.custom.id,
                  'renewal': article_obj.renewal,
                  'augment': article_obj.augment,
                  'credit_term': article_obj.credit_term,
                  'director_id': article_obj.director.id,
                  'assistant_id': article_obj.assistant.id,
                  'control_id': article_obj.control.id,
                  'article_date': str(article_obj.article_date)}
    forma = forms.ArticlesAdForm(forma_date)
    if request.method == "GET":
        ARTICLE_STATE_LIST = models.Articles.ARTICLE_STATE_LIST
        article_obj = models.Articles.objects.get(id=id)
        if article_obj.article_state == 1:
            form = forms.AppraisalForm()
        elif article_obj.article_state in ARTICLE_STATE_LIST:
            expert_obj = article_obj.expert.values_list('id')
            print('expert_obj:', expert_obj)
            expert_list = list(zip(*expert_obj))[0]  #####
            print('expert_list:', expert_list)
            form_date = {'expert': expert_list,  #####
                         'review_model': article_obj.review_model,
                         'review_order': article_obj.review_order,
                         'review_date': article_obj.review_date}
            form = forms.AppraisalForm(form_date)
        else:
            print('无法修改!')
            return redirect('/dbms/appraisal/')
        return render(request,
                      'dbms/appraisal/appraisal-edit.html',
                      locals())
    else:
        # form验证
        form = forms.AppraisalForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            article_obj = models.Articles.objects.filter(id=id)
            review_model = cleaned_data['review_model'],
            print('cleaned_data:', cleaned_data)
            print('review_model:', cleaned_data['review_model'])

            article_update = article_obj.update(
                article_state=2,
                review_model=cleaned_data['review_model'],
                review_order=cleaned_data['review_order'],
                review_date=cleaned_data['review_date'])
            # 绑定多对多关系
            article_obj[0].expert.set(cleaned_data['expert'])

            return redirect('/dbms/appraisal/')
        else:
            return render(request,
                          'dbms/appraisal/appraisal-edit.html',
                          locals())


# -----------------------撤销上会------------------------#
def appraisal_del(request, id):  # 撤销上会
    print(' -----------------------撤销上会------------------------')
    article_obj = models.Articles.objects.filter(id=id)
    ARTICLE_STATE_LIST = (2,)
    if article_obj[0].article_state in ARTICLE_STATE_LIST:
        # print('article_state:', article_obj[0].expert.all())

        article_obj[0].expert.clear()

        article_obj.update(
            article_state=1)
    else:
        print('无法撤销！！！')
    return redirect('/dbms/appraisal/')


# -----------------------签批------------------------#
def appraisal_sign(request, id):  # 签批
    print(' -----------------------签批------------------------')
    ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'), (4, '需补调'),
                          (5, '已补调'),)
    if request.method == "GET":
        article_obj = models.Articles.objects.get(id=id)
        print('article_obj.article_state:', article_obj.article_state)
        if article_obj.article_state in ARTICLE_STATE_LIST:
            initial_data = {'flow_credit': article_obj.amount}
            form = forms.ArticlesSignForm(initial=initial_data)
        else:
            form_date = {
                'summary_num': article_obj.summary_num,
                'flow_credit': article_obj.flow_credit,  #####
                'flow_rate': article_obj.flow_rate,
                'honour_credit': article_obj.honour_credit,
                'honour_rate': article_obj.honour_rate,
                'accept_credit': article_obj.accept_credit,
                'accept_rate': article_obj.accept_rate,
                'sign_date': article_obj.sign_date}
            form = forms.ArticlesSignForm(form_date)
        return render(request,
                      'dbms/appraisal/appraisal-sign.html',
                      locals())
    else:
        # form验证
        form = forms.ArticlesSignForm(request.POST, request.FILES)
        print('form:', form)
        print('sign_date:', form['sign_date'])
        if form.is_valid():
            cleaned_data = form.cleaned_data
            article_obj = models.Articles.objects.filter(id=id)
            print('sign_date:', cleaned_data['sign_date'])
            article_update = article_obj.update(
                article_state=6,
                summary_num=cleaned_data['summary_num'],
                flow_credit=cleaned_data['flow_credit'],
                flow_rate=cleaned_data['flow_rate'],
                honour_credit=cleaned_data['honour_credit'],
                honour_rate=cleaned_data['honour_rate'],
                accept_credit=cleaned_data['accept_credit'],
                accept_rate=cleaned_data['accept_rate'],
                sign_date=cleaned_data['sign_date'])
            return redirect('/dbms/appraisal/')
        else:
            return render(request,
                          'dbms/appraisal/appraisal-sign.html',
                          locals())
