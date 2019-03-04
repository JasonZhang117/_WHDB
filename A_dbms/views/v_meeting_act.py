from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time,json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.db import transaction
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.urls import resolve
from _WHDB.views import MenuHelper
from _WHDB.views import authority


# -----------------------添加评审会ajax-------------------------#
@login_required
@authority
def meeting_add_ajax(request):
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
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


# -----------------------取消评审会ajax-------------------------#
@login_required
@authority
def meeting_del_ajax(request):  # 取消评审会
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
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
        try:
            with transaction.atomic():
                article_list.update(article_state=2)  # 更新项目状态
                meeting_obj.delete()  # 删除评审会
                response['message'] = '评审会取消成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '取消评审会失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------添加参评项目ajax-------------------------#
@login_required
@authority
def meeting_article_add_ajax(request):  # 添加参评项目ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_obj = models.Appraisals.objects.get(id=post_data['meeting_id'])
    meeting_state = meeting_obj.meeting_state
    if meeting_state == 1:
        form_meeting_article_add = forms.MeetingArticleAddForm(post_data, request.FILES)
        if form_meeting_article_add.is_valid():
            meeting_article_cleaned = form_meeting_article_add.cleaned_data
            article_add_list = meeting_article_cleaned['article']
            meeting_article_add_list = models.Articles.objects.filter(id__in=article_add_list)
            print('meeting_article_add_list:', meeting_article_add_list)
            try:
                with transaction.atomic():
                    for article_obj in meeting_article_add_list:
                        meeting_obj.article.add(article_obj)
                    '''ARTICLE_STATE_LIST = 
                    ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                     (4, '已上会'), (5, '已签批'), (6, '已注销'))
                     (5, '已签批')-->才能出合同'''
                    meeting_article_add_list.update(article_state=3)
                response['message'] = '成功追加评审项目！'
            except Exception as e:
                response['status'] = False
                response['message'] = '追加评审项目失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_meeting_article_add.errors
    else:
        msg = '评审会状态为：%s，无法追加项目！！！' % meeting_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消项目上会ajax-------------------------#
@login_required
@authority
def meeting_article_del_ajax(request):  # 取消项目上会ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_id = post_data['meeting_id']
    article_id = post_data['article_id']

    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    article_lis = models.Articles.objects.filter(id=article_id)
    article_obj = article_lis.first()
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2, 3]:
        try:
            with transaction.atomic():
                article_obj.expert.clear()  # 清除评审委员
                article_lis.update(article_state=2)  # 更新项目状态
                meeting_obj.article.remove(article_lis[0])  # 取消项目上会
            response['message'] = '%s，上会取消成功！' % article_obj.article_num
        except Exception as e:
            response['status'] = False
            response['message'] = '取消项目上会失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法删除！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------分配评审委员ajax-------------------------#
@login_required
@authority
def meeting_allot_add_ajax(request):  # 分配评审委员
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)

    response = {'status': True, 'message': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    article_id = post_data['article_id']
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同'''
    article_obj = models.Articles.objects.get(id=article_id)
    article_meeting_obj = article_obj.appraisal_article.all().first()
    if article_obj.article_state == 3:
        form_meeting_allot = forms.MeetingAllotForm(post_data, request.FILES)
        if form_meeting_allot.is_valid():
            meeting_allot_cleaned = form_meeting_allot.cleaned_data
            expert_add_list = meeting_allot_cleaned['expert']
            expert_add_obj_list = models.Experts.objects.filter(id__in=expert_add_list)
            print('expert_add_list:', expert_add_list)
            try:
                with transaction.atomic():
                    for expert_obj in expert_add_obj_list:
                        article_obj.expert.add(expert_obj)
                response['message'] = '成功为项目：%s分配评委！' % article_obj.article_num
            except Exception as e:
                response['status'] = False
                response['message'] = '分配评委失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_meeting_allot.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法变更评委！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------撤销评审委员ajax-------------------------#
@login_required
@authority
def meeting_allot_del_ajax(request):  # 取消项目上会ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)

    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    article_id = post_data['article_id']
    expert_id = post_data['expert_id']
    article_obj = models.Articles.objects.get(id=article_id)
    expert_obj = models.Experts.objects.get(id=expert_id)

    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2, 3]:
        try:
            with transaction.atomic():
                article_obj.expert.remove(expert_obj)  # 撤销评委
            response['message'] = '评委：%s撤销成功' % expert_obj.name
        except Exception as e:
            response['status'] = False
            response['message'] = '评委撤销失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法撤销评委！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------编辑评审会ajax-------------------------#
@login_required
@authority
def meeting_edit_ajax(request):  # 编辑评审会ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)

    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    meeting_id = post_data['meeting_id']
    meeting_list = models.Appraisals.objects.filter(id=meeting_id)
    meeting_obj = meeting_list.first()
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        form_meeting_edit = forms.MeetingEditForm(post_data, request.FILES)
        if form_meeting_edit.is_valid():
            meeting_edit_cleaned = form_meeting_edit.cleaned_data
            try:
                with transaction.atomic():
                    meeting_list.update(review_model=meeting_edit_cleaned['review_model'],
                                        review_date=meeting_edit_cleaned['review_date'])
                response['message'] = '成功变更评审会：%s！' % meeting_obj.num
            except Exception as e:
                response['status'] = False
                response['message'] = '分配评委失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_meeting_edit.errors
    else:
        response['status'] = False
        response['message'] = '评审会状态为：%s，无法修改！！！' % meeting_obj.meeting_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------完成上会ajax-------------------------#
@login_required
@authority
def meeting_close_ajax(request):  # 完成上会ajax
    print(request.path, '>', resolve(request.path).url_name, '>', request.user)

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
                    response['status'] = False
                    response['message'] = '项目：%s有%s位评委，评委数量不对！' % (article_obj.article_num, aec)
                    result = json.dumps(response, ensure_ascii=False)
                    return HttpResponse(result)
            else:
                if not aec == 7:
                    response['status'] = False
                    response['message'] = '项目：%s有%s位评委，评委数量不对！' % (article_obj.article_num, aec)
                    result = json.dumps(response, ensure_ascii=False)
                    return HttpResponse(result)
            try:
                with transaction.atomic():
                    article_list.update(article_state=4, review_date=meeting_obj.review_date)  # 更新项目状态
                    meeting_list.update(meeting_state=2)  # 更新评审会状态
                    num = 0
                    for article in article_list:
                        num = num + 1
                        summary_num = '%s-%s号' % (meeting_obj.num, num)
                        models.Articles.objects.filter(id=article.id).update(summary_num=summary_num)
                response['message'] = '%s,完成上会！' % meeting_obj.num
            except Exception as e:
                response['status'] = False
                response['message'] = '评审会创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '本次评审会无参会项目，你玩我？？？'
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
