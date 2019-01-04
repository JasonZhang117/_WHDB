from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction


# -----------------------评审会-------------------------#
@login_required
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    form_meeting_add = forms.MeetingAddForm()
    meeting_state_list = models.Appraisals.MEETING_STATE_LIST
    meeting_list = models.Appraisals.objects.filter(**kwargs).order_by('-review_date', '-review_order')
    return render(request, 'dbms/meeting/meeting.html', locals())


# -----------------------评审会预览-------------------------#
@login_required
def meeting_scan(request, meeting_id):  # 评审会预览
    print(__file__, '---->def meeting_scan')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    expert_list = models.Experts.objects.filter(article_expert__appraisal_article=meeting_obj).distinct()

    for expert_obj in expert_list:
        article_count = models.Articles.objects.filter(expert=expert_obj, appraisal_article=meeting_obj).count()
        print("article_count:", expert_obj.id, article_count)
    expert_ll = models.Experts.objects.filter(article_expert__appraisal_article=meeting_obj).count()
    print('expert_ll:', expert_ll)
    form_meeting_article_add = forms.MeetingArticleAddForm()

    meeting_edit_form_data = {'review_model': meeting_obj.review_model, 'review_date': str(meeting_obj.review_date)}
    form_meeting_edit = forms.MeetingEditForm(meeting_edit_form_data)

    return render(request, 'dbms/meeting/meeting-scan.html', locals())


# -----------------------参评项目预览-------------------------#
@login_required
def meeting_scan_article(request, meeting_id, article_id):
    print(__file__, '---->def meeting_scan_article')
    article_obj = models.Articles.objects.get(id=article_id)
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    expert_list = article_obj.expert.values_list('id')
    if expert_list:
        expert_id_list = list(zip(*expert_list))[0]
        form_date = {'expert': expert_id_list}
        form_allot_expert = forms.MeetingAllotForm(initial=form_date)
    else:
        form_allot_expert = forms.MeetingAllotForm()

    return render(request,
                  'dbms/meeting/meeting-scan-article.html',
                  locals())


# -----------------------添加评审会ajax-------------------------#
@login_required
def meeting_add_ajax(request):
    print(__file__, '---->def meeting_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    form = forms.MeetingAddForm(post_data, request.FILES)

    if form.is_valid():
        cleaned_data = form.cleaned_data

        REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
        review_model = cleaned_data['review_model']
        review_date = cleaned_data['review_date']

        ###上会类型(r_mod)
        r_mod = "内审"
        for i in REVIEW_MODEL_LIST:
            x, y = i
            if x == review_model:
                r_mod = y

        ###上会年份(r_year)
        today_str = time.strptime(str(review_date), "%Y-%m-%d")
        r_year = today_str.tm_year

        ###上会次序(r_order)
        order_max = models.Appraisals.objects.filter(
            review_model=review_model,
            review_year=r_year).aggregate(Count('review_order'))

        order_max_x = order_max['review_order__count'] + 1

        if order_max_x < 10:
            r_order = '00%s' % order_max_x
        elif order_max_x < 100:
            r_order = '0%s' % order_max_x
        else:
            r_order = '%s' % order_max_x
        ###评审会编号拼接
        review_num = "(%s)[%s]%s" % (r_mod, r_year, r_order)

        article_list_l = cleaned_data['article']
        try:
            with transaction.atomic():
                meeting_obj = models.Appraisals.objects.create(
                    num=review_num, review_year=r_year, review_model=review_model, review_order=order_max_x,
                    review_date=review_date, meeting_buildor=request.user)
                meeting_obj.article.set(article_list_l)
                models.Articles.objects.filter(id__in=article_list_l).update(article_state=3)
            response['message'] = '成功添加评审会：%s！' % meeting_obj.num
        except Exception as e:
            response['status'] = False
            response['message'] = '添加评审会失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------添加参评项目ajax-------------------------#
@login_required
def meeting_article_add_ajax(request):  # 添加参评项目ajax
    print(__file__, '---->def meeting_article_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_list = post_data['article']
    meeting_obj = models.Appraisals.objects.get(id=post_data['meeting_id'])
    meeting_state = meeting_obj.meeting_state
    if meeting_state == 1:
        form_data = {'article': article_list}
        form = forms.MeetingArticleAddForm(form_data, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            article_add_list = models.Articles.objects.filter(
                id__in=cleaned_data['article'])
            print('article_add_list:', article_add_list)
            try:
                with transaction.atomic():
                    for article_obj in article_add_list:
                        meeting_obj.article.add(article_obj)
                    '''ARTICLE_STATE_LIST = 
                    ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                     (4, '已上会'), (5, '已签批'), (6, '已注销'))
                     (5, '已签批')-->才能出合同'''
                    models.Articles.objects.filter(id__in=article_add_list).update(article_state=3)
                response['message'] = '成功追加评审项目！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追加评审项目失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        msg = '评审会状态为：%s，无法追加项目！！！' % meeting_state
        response['status'] = False
        response['message'] = msg

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------分配评审委员ajax-------------------------#
@login_required
def meeting_allot_ajax(request):  # 分配评审委员
    print(__file__, '---->def meeting_allot_ajax')
    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同'''
    article_obj = models.Articles.objects.get(id=article_id)
    if article_obj.article_state == 3:
        expert = post_data['expert']
        data = {
            'article_id': article_id,
            'expert': expert}

        form = forms.MeetingAllotForm(data, request.FILES)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            article_obj.expert.set(cleaned_data['expert'])

            response['obj_num'] = article_obj.article_num
            response['message'] = '成功为项目：%s分配评委！' % article_obj.article_num

        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        msg = '项目状态为：%s，无法变更评委！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------编辑评审会ajax-------------------------#
@login_required
def meeting_edit_ajax(request):  # 编辑评审会ajax
    print(__file__, '---->def meeting_edit_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    meeting_id = post_data['meeting_id']

    meeting_list = models.Appraisals.objects.filter(id=meeting_id)
    meeting_obj = meeting_list[0]
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        review_model = post_data['review_model']
        review_date = post_data['review_date']
        data = {
            'review_model': review_model,
            'review_date': review_date}
        form = forms.MeetingEditForm(data, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            meeting_list.update(
                review_model=review_model,
                review_date=review_date)
            response['obj_num'] = meeting_obj.num
            response['message'] = '成功变更评审会：%s！' % meeting_obj.num

        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        msg = '评审会状态为：%s，无法修改！！！' % meeting_obj.meeting_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------完成上会ajax-------------------------#
@login_required
def meeting_close_ajax(request):  # 完成上会ajax
    print(__file__, '---->def meeting_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    meeting_id = post_data['meeting_id']
    meeting_list = models.Appraisals.objects.filter(id=meeting_id)
    meeting_obj = meeting_list.first()
    article_list = meeting_obj.article.all()
    if article_list.exists():
        ''' ARTICLE_STATE_LIST = 
                ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                (4, '已上会'), (5, '已签批'), (6, '已注销'))
                (5, '已签批')-->才能出合同'''
        for article_obj in article_list:
            aec = article_obj.expert.count()
            rm = meeting_obj.review_model
            if rm == 1:
                if not aec == 5:
                    msg = '项目：%s有%s位评委，评委数量不对！' % (article_obj.article_num, aec)
                    response['status'] = False
                    response['message'] = msg
                    result = json.dumps(response, ensure_ascii=False)
                    return HttpResponse(result)
            else:
                if not aec == 7:
                    msg = '项目：%s有%s位评委，评委数量不对！' % (article_obj.article_num, aec)
                    response['status'] = False
                    response['message'] = msg
                    result = json.dumps(response, ensure_ascii=False)
                    return HttpResponse(result)
            try:
                with transaction.atomic():
                    article_list.update(article_state=4, review_date=meeting_obj.review_date)  # 更新项目状态
                    meeting_list.update(meeting_state=2)  # 更新评审会状态
                    num = 0
                    for article in article_list:
                        num = num + 1
                        summary_num = '%s-%s' % (meeting_obj.num, num)
                        models.Articles.objects.filter(id=article.id).update(summary_num=summary_num)
                msg = '%s,完成上会！' % meeting_obj.num
                response['message'] = msg
            except Exception as e:
                response['status'] = False
                response['message'] = '评审会创建失败：%s' % str(e)
    else:
        msg = '本次评审会无参会项目，你玩我？？？'
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消评审会ajax-------------------------#
@login_required
def meeting_del_ajax(request):  # 取消评审会
    print(__file__, '---->def meeting_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_id = post_data['meeting_id']
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    article_list = meeting_obj.article.all()
    if article_list.exists():
        msg = '请删除所有参会项目后再取消评审会！！！'
        response['status'] = False
        response['message'] = msg
    else:
        '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
        article_list.update(article_state=2)  # 更新项目状态
        meeting_obj.delete()  # 删除评审会
        msg = '评审会取消成功！'
        response['message'] = msg

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消项目上会ajax-------------------------#
@login_required
def meeting_article_del_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def meeting_article_del')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_id = post_data['meeting_id']
    article_id = post_data['article_id']

    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    article_lis = models.Articles.objects.filter(id=article_id)

    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_lis[0].article_state in [1, 2, 3]:

        article_lis[0].expert.clear()  # 清除评审委员
        article_lis.update(article_state=2)  # 更新项目状态
        meeting_obj.article.remove(article_lis[0])  # 取消项目上会

        msg = '%s，取消成功！' % article_lis[0].article_num
        response['message'] = msg
        response['data'] = meeting_obj.id

    else:
        msg = '项目状态为：%s，无法删除！！！' % article_lis[0].article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------评审会通知-------------------------#
@login_required
def meeting_notice(request, meeting_id):  # 评审会通知
    print(__file__, '---->def meeting_scan')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    return render(request,
                  'dbms/meeting/meeting-notice.html',
                  locals())
