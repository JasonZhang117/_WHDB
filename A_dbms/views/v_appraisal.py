from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# -----------------------appraisal评审情况-------------------------#
@login_required
def appraisal(request):  # 评审情况
    print(__file__, '---->def appraisal')
    # print('kwargs:', kwargs)
    form_meeting_add = forms.MeetingAddForm()

    appraisal_list = models.Articles.objects.filter(
        article_state__in=[4, 5]).order_by('-review_date')
    print('appraisal_list:', appraisal_list)

    paginator = Paginator(appraisal_list, 10)

    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/appraisal/appraisal.html',
                  locals())


# -----------------------appraisal_scan评审项目预览-------------------------#
@login_required
def appraisal_scan(request, article_id):  # 评审项目预览
    print(__file__, '---->def appraisal_scam')
    article_obj = models.Articles.objects.get(id=article_id)
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
            'sign_date': str(today_str)}
        form_article_sign = forms.ArticlesSignForm(initial=form_date)

    form_comment = forms.CommentsAddForm()
    form_single = forms.SingleQuotaForm()
    form_lending = forms.LendingOrder()

    return render(request,
                  'dbms/appraisal/appraisal-scan.html',
                  locals())


# -----------------------appraisal_scan_lending评审项目预览-------------------------#
@login_required
def appraisal_scan_lending(request, article_id, lending_id):  # 评审项目预览
    print(__file__, '---->def appraisal_scan_lending')
    article_obj = models.Articles.objects.get(id=article_id)
    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    '''(0, '--------'),
        (1, '个人保证'), (2, '企业保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'),
        (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''

    sure_list = [1, 2]
    house_list = [11, 21, 42]
    ground_list = [12, 22, 43]

    lending_sure = lending_obj.sure_lending.all()
    # lending_warrant = lending_obj.
    print('lending_sure:', lending_sure)
    for sure in lending_sure:
        # print(type(i))
        print('sure.sure_typ:', sure.sure_typ)
        if sure.sure_typ in sure_list:
            print('sure.sure_typ:', sure.sure_typ)
            for custome in sure.custome_sure.custome.all():
                print(custome)

    return render(request,
                  'dbms/appraisal/appraisal-scan-lending.html',
                  locals())


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


# -----------------------放款次序ajax-------------------------#
@login_required
def lending_order_ajax(request):  # 放款次序ajax
    print(__file__, '---->def single_quota_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_id = post_data['article_id']
    order = post_data['order']
    order_amount = post_data['order_amount']

    article_obj = models.Articles.objects.get(id=article_id)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
        (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state == 4:
        data = {
            'order': order,
            'order_amount': order_amount}

        form = forms.LendingOrder(data)

        if form.is_valid():
            cleaned_data = form.cleaned_data

            models.LendingOrder.objects.create(
                summary_id=article_id,
                order=cleaned_data['order'],
                order_amount=cleaned_data['order_amount'])
            msg = '放款次序设置成功！'
            response['message'] = msg

    else:
        msg = '项目状态为：%s，无法设置放款次序！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------放款次序删除ajax-------------------------#
@login_required
def lending_del_ajax(request):  # 单项额度删除ajax
    print(__file__, '---->def single_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    lending_id = post_data['lending_id']
    article_id = post_data['article_id']

    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    article_obj = models.Articles.objects.get(id=article_id)
    print('lending_obj:', lending_obj)
    '''((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
       (4, '已上会'), (5, '已签批'), (6, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4]:
        lending_obj.delete()  # 删除单项额度
        msg = '放款次序删除成功！'
        response['message'] = msg

    else:
        msg = '项目状态为：%s，无法删除放款次序！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------单项额度删除ajax-------------------------#
@login_required
def single_del_ajax(request):  # 单项额度删除ajax
    print(__file__, '---->def single_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
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

                    lending_amount = models.LendingOrder.objects.filter(
                        summary__id=article_id).aggregate(Sum('order_amount'))
                    lending_amount = lending_amount['order_amount__sum']

                    print('lending_amount:', lending_amount)

                    if single_quota_amount == article_amount and lending_amount == article_amount:

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
                        msg = '单项额度或放款次序金额合计与签批总额不相等，项目签批不成功！！！'
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
