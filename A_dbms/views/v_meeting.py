from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required


# -----------------------评审会-------------------------#
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    form = forms.MeetingAddForm()
    meeting_list = models.Appraisals.objects.filter(
        **kwargs).order_by('-review_date', '-review_order')
    meeting_state_list = models.Appraisals.MEETING_STATE_LIST

    return render(request,
                  'dbms/meeting/meeting.html',
                  locals())


# -----------------------添加评审会ajax-------------------------#
def meeting_add_ajax(request):
    print(__file__, '---->def meeting_add_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    review_model = post_data['review_model']
    review_date = post_data['review_date']
    article = post_data['article']

    data = {
        'review_model': review_model,
        'review_date': review_date,
        'article': article}

    form = forms.MeetingAddForm(data, request.FILES)

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
        order_list = models.Appraisals.objects.filter(
            review_model=review_model,
            review_year=r_year).values_list('review_order')
        if order_list:
            order_m = list(zip(*order_list))
            order_max = max(list(zip(*order_list))[0])  #####
        else:
            order_max = 0
        order_max_x = order_max + 1
        if order_max_x < 10:
            r_order = '00%s' % order_max_x
        elif order_max_x < 100:
            r_order = '0%s' % order_max_x
        else:
            r_order = '%s' % order_max_x
        ###评审会编号拼接
        review_num = "(%s)[%s]%s" % (r_mod, r_year, r_order)
        print('review_num:', review_num)

        meeting_obj = models.Appraisals.objects.create(
            num=review_num,
            review_year=r_year,
            review_model=review_model,
            review_order=order_max_x,
            review_date=review_date,
            meeting_buildor=request.user)
        article_list_l = cleaned_data['article']
        meeting_obj.article.set(article_list_l)
        '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '无补调'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))'''
        models.Articles.objects.filter(
            id__in=article_list_l).update(article_state=2)

        response['obj_num'] = meeting_obj.num
        response['message'] = '成功添加评审会：%s！' % meeting_obj.num

    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------分配评审委员ajax-------------------------#
def meeting_allot_ajax(request):  # 分配评审委员
    print(__file__, '---->def meeting_allot_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    article_id = post_data['article_id']
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '已上会'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))'''
    article_obj = models.Articles.objects.get(id=article_id)
    if article_obj.article_state in [1, 2]:
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
def meeting_edit_ajax(request):  # 编辑评审会ajax
    print(__file__, '---->def meeting_edit_ajax')
    meeting_list = models.Appraisals.objects.filter(id=meeting_id)
    meeting_obj = meeting_list.first()
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        meeting_list.update(meeting_state=2)
        return redirect('dbms:meeting_all')
    else:
        print('状态为：%s，无法修改！！！' % meeting_obj.meeting_state)
    return redirect('dbms:meeting_all')


# -----------------------取消评审会ajax-------------------------#
def meeting_del_ajax(request):  # 取消评审会
    print(__file__, '---->def meeting_del_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_id = post_data['meeting_id']
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    ''' MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        article_list = meeting_obj.article.all()

        article_list.update(article_state=1)  # 更新项目状态
        for article in article_list:
            article.expert.clear()  # 清除评审委员
        meeting_obj.delete()  # 删除评审会

        msg = '%s，删除成功！' % meeting_obj.num
        response['message'] = msg
        response['data'] = meeting_obj.id
    else:
        msg = '状态为：%s，无法删除！！！' % meeting_obj.meeting_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------取消项目上会ajax-------------------------#
def meeting_article_del_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def meeting_article_del')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    meeting_id = post_data['meeting_id']
    article_id = post_data['article_id']

    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    article_lis = models.Articles.objects.filter(id=article_id)

    ''' ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '已上会'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))'''
    if article_lis[0].article_state in [1, 2]:

        article_lis[0].expert.clear()  # 清除评审委员
        article_lis.update(article_state=1)  # 更新项目状态
        meeting_obj.article.remove(article_lis[0])

        msg = '%s，取消成功！' % article_lis[0].article_num
        response['message'] = msg
        response['data'] = meeting_obj.id

    else:
        msg = '状态为：%s，无法删除！！！' % article_lis[0].article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------评审意见ajax------------------------#
@login_required
def comment_edit_ajax(request):  # 修改项目ajax
    print(__file__, '---->def article_edit_ajax')

    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }

    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_id = post_data['article_id']

    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '已上会'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))'''
    if article_obj.article_state in [3, 4, 5, 6]:
        comment_type = post_data['comment_type']
        concrete = post_data['concrete']

        data = {
            'comment_type': comment_type,
            'concrete': concrete}

        form = forms.CommentsAddForm(data)

        if form.is_valid():
            cleaned_data = form.cleaned_data
            expert_id = post_data['expert_id']
            try:
                default = {
                    'summary_id': article_id,
                    'expert_id': expert_id,
                    'comment_type': cleaned_data['comment_type'],
                    'concrete': cleaned_data['concrete'],
                    'comment_buildor': request.user}

                comment, created = models.Comments.objects.update_or_create(
                    summary_id=article_id,
                    expert_id=expert_id,
                    defaults=default)
                print('comment:', comment)
                response['obj_id'] = comment.id
                if created:
                    response['message'] = '成功创建评审意见！'
                else:
                    response['message'] = '成功更新评审意见！'
            except:
                response['status'] = False
                response['message'] = '评审意见未修改成功！'

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


# -----------------------单项额度ajax-------------------------#
def single_quota_ajax(request):  # 取消项目上会ajax
    print(__file__, '---->def meeting_article_del')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_id = post_data['article_id']
    credit_model = post_data['credit_model']
    credit_amount = post_data['credit_amount']
    flow_rate = post_data['flow_rate']

    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '待上会'),
                          (3, '已上会'),
                          (4, '无补调'), (5, '需补调'),
                          (6, '已补调'), (7, '已签批'))'''
    if article_obj.article_state in [3, 4, 5, 6]:

        data = {
            'credit_model': credit_model,
            'credit_amount': credit_amount,
            'flow_rate': flow_rate}

        form = forms.SingleQuotaForm(data)

        if form.is_valid():
            cleaned_data = form.cleaned_data

        default = {
            'summary_id': article_id,
            'credit_model': credit_model,
            'credit_amount': credit_amount,
            'flow_rate': flow_rate,
            'single_buildor': request.user}

        single, created = models.SingleQuota.objects.update_or_create(
            summary_id=article_id, credit_model=credit_model,
            defaults=default)
        print('single:', single)
        response['obj_id'] = single.id

        msg = '单项额度设置成功！'
        response['message'] = msg

    else:
        msg = '状态为：%s，无法设置单项额度！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------评审会预览-------------------------#
def meeting_scan(request, meeting_id):  # 评审会预览
    print(__file__, '---->def meeting_scan')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    expert_list = models.Experts.objects.filter(
        article_expert__appraisal_article=meeting_obj).distinct()

    form = forms.MeetingAddForm()

    return render(request,
                  'dbms/meeting/meeting-scan.html',
                  locals())


# -----------------------参评项目预览-------------------------#
def meeting_scan_article(request, meeting_id, article_id):
    print(__file__, '---->def article_scan_agree')
    article_obj = models.Articles.objects.get(id=article_id)
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    expert_list = article_obj.expert.values_list('id')
    if expert_list:
        expert_id_list = list(zip(*expert_list))[0]

        form_date = {
            'expert': expert_id_list}

        form = forms.MeetingAllotForm(initial=form_date)
    else:
        form = forms.MeetingAllotForm()

    form_comment = forms.CommentsAddForm()

    form_single = forms.SingleQuotaForm()

    return render(request,
                  'dbms/meeting/meeting-article.html',
                  locals())
