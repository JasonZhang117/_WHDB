from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F


# -----------------------评审会-------------------------#
@login_required
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    form_meeting_add = forms.MeetingAddForm()

    meeting_list = models.Appraisals.objects.filter(
        **kwargs).order_by('-review_date', '-review_order')

    meeting_state_list = models.Appraisals.MEETING_STATE_LIST

    return render(request,
                  'dbms/meeting/meeting.html',
                  locals())


# -----------------------添加评审会ajax-------------------------#
@login_required
def meeting_add_ajax(request):
    print(__file__, '---->def meeting_add_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    data = {
        'review_model': post_data['review_model'],
        'review_date': post_data['review_date'],
        'article': post_data['article']}

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

        meeting_obj = models.Appraisals.objects.create(
            num=review_num,
            review_year=r_year,
            review_model=review_model,
            review_order=order_max_x,
            review_date=review_date,
            meeting_buildor=request.user)
        article_list_l = cleaned_data['article']
        meeting_obj.article.set(article_list_l)

        models.Articles.objects.filter(
            id__in=article_list_l).update(article_state=3)

        response['obj_num'] = meeting_obj.num
        response['message'] = '成功添加评审会：%s！' % meeting_obj.num

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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
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
            for article_obj in article_add_list:
                meeting_obj.article.add(article_obj)
            '''ARTICLE_STATE_LIST = 
            ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
             (4, '已上会'), (5, '已签批'), (6, '已注销'))
             (5, '已签批')-->才能出合同'''
            models.Articles.objects.filter(
                id__in=article_add_list).update(article_state=3)

            response['obj_num'] = meeting_obj.num
            response['message'] = '成功追加评审项目！'

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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }

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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
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

        article_list.update(article_state=4)  # 更新项目状态
        meeting_list.update(meeting_state=2)  # 更新评审会状态
        msg = '%s,完成上会！' % meeting_obj.num
        response['message'] = msg
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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
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
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
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
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state == 4:
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
        arg = '项目状态为：%s，无法修改！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = arg

    result = json.dumps(response, ensure_ascii=False)

    return HttpResponse(result)


# -----------------------单项额度ajax-------------------------#
@login_required
def single_quota_ajax(request):  # 单项额度ajax
    print(__file__, '---->def single_quota_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_id = post_data['article_id']
    credit_model = post_data['credit_model']
    credit_amount = post_data['credit_amount']
    flow_rate = post_data['flow_rate']

    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state == 4:

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
        msg = '项目状态为：%s，无法设置单项额度！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------单项额度删除ajax-------------------------#
@login_required
def single_del_ajax(request):  # 单项额度删除ajax
    print(__file__, '---->def single_del_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    single_id = post_data['single_id']
    article_id = post_data['article_id']

    single_obj = models.SingleQuota.objects.get(id=single_id)
    article_obj = models.Articles.objects.get(id=article_id)
    print('single_obj:', single_obj)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4]:
        single_obj.delete()  # 删除单项额度
        response['obj_id'] = single_obj.id
        msg = '单项额度删除成功！'
        response['message'] = msg

    else:
        msg = '项目状态为：%s，无法删除单项额度！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------签批ajax-------------------------#
@login_required
def article_sign_ajax(request):
    print(__file__, '---->def article_sign_ajax')
    response = {'status': True, 'message': None,
                'obj_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    '''((1, '同意'), (2, '不同意'))'''
    sign_type = post_data['sign_type']
    article_id = post_data['article_id']
    aritcle_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if aritcle_obj.article_state == 4:
        if int(sign_type) == 2:
            models.Articles.objects.filter(id=article_id).update(
                sign_type=sign_type,
                sign_date=post_data['sign_date'],
                article_state=6)
            response['obj_num'] = aritcle_obj.article_num
            response['message'] = '%s项目被否决，更新为注销状态！' % aritcle_obj.article_num
        else:
            data = {
                'summary_num': post_data['summary_num'],
                'sign_type': sign_type,
                'renewal': post_data['renewal'],
                'augment': post_data['augment'],
                'sign_detail': post_data['sign_detail'],
                'sign_date': post_data['sign_date']}

            form = forms.ArticlesSignForm(data)
            if form.is_valid():
                cleaned_data = form.cleaned_data

                article_expert_amount = aritcle_obj.expert.all().count()
                article_comment_amount = aritcle_obj.comment_summary.all().count()
                if article_expert_amount == article_comment_amount:
                    renewal = cleaned_data['renewal']
                    augment = cleaned_data['augment']
                    article_amount = renewal + augment
                    single_quota_amount = models.SingleQuota.objects.filter(
                        summary__id=article_id).aggregate(Sum('credit_amount'))
                    single_quota_amount = single_quota_amount['credit_amount__sum']

                    if single_quota_amount == article_amount:

                        models.Articles.objects.filter(id=article_id).update(
                            summary_num=cleaned_data['summary_num'],
                            sign_type=sign_type,
                            renewal=renewal,
                            augment=augment,
                            amount=article_amount,
                            sign_detail=cleaned_data['sign_detail'],
                            sign_date=cleaned_data['sign_date'],
                            article_state=5)
                        # 更新客户授信总额
                        custom_id = aritcle_obj.custom.id
                        models.Customes.objects.filter(id=custom_id).update(
                            credit_amount=F('credit_amount') + augment)

                        response['obj_num'] = aritcle_obj.article_num
                        response['message'] = '成功签批项目：%s！' % aritcle_obj.article_num
                    else:
                        msg = '单项额度合计与签批总额不相等，项目签批不成功！！！'
                        response['status'] = False
                        response['message'] = msg
                else:
                    msg = '还有评审委员没有发表评审意见，项目签批不成功！！！'
                    response['status'] = False
                    response['message'] = msg
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form.errors
    else:
        msg = '项目状态为：%s，本次签批失败！！！' % aritcle_obj.article_state
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


# -----------------------评审会预览-------------------------#
@login_required
def meeting_scan(request, meeting_id):  # 评审会预览
    print(__file__, '---->def meeting_scan')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    expert_list = models.Experts.objects.filter(
        article_expert__appraisal_article=meeting_obj).distinct()

    form_meeting_article_add = forms.MeetingArticleAddForm()

    meeting_edit_form_data = {
        'review_model': meeting_obj.review_model,
        'review_date': str(meeting_obj.review_date)}

    form_meeting_edit = forms.MeetingEditForm(meeting_edit_form_data)

    return render(request,
                  'dbms/meeting/meeting-scan.html',
                  locals())


# -----------------------参评项目预览-------------------------#
@login_required
def meeting_scan_article(request, meeting_id, article_id):
    print(__file__, '---->def meeting_scan_article')
    article_obj = models.Articles.objects.get(id=article_id)
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    expert_list = article_obj.expert.values_list('id')
    if expert_list:
        expert_id_list = list(zip(*expert_list))[0]
        form_date = {
            'expert': expert_id_list}
        form_allot_expert = forms.MeetingAllotForm(initial=form_date)
    else:
        form_allot_expert = forms.MeetingAllotForm()
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state:
        form_date = {
            'summary_num': article_obj.summary_num,
            'sign_type': article_obj.sign_type,
            'renewal': article_obj.renewal,
            'augment': article_obj.augment,
            'sign_detail': article_obj.sign_detail,
            'sign_date': str(article_obj.sign_date)}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)
    else:
        today_str = time.strftime("%Y-%m-%d", time.gmtime())
        form_date = {
            'renewal': article_obj.renewal,
            'augment': article_obj.augment,
            'sign_date': today_str}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)

    form_comment = forms.CommentsAddForm()

    form_single = forms.SingleQuotaForm()

    return render(request,
                  'dbms/meeting/meeting-article.html',
                  locals())
