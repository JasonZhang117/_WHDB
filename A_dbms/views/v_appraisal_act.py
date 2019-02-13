from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime, time
import json
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Max, Count
from django.db.models import Q, F
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction


# -----------------------------反担保措施添加ajax------------------------#
@login_required
def guarantee_add_ajax(request):  # 反担保措施添加ajax
    print(__file__, '---->def guarantee_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    lending_id = int(post_data['lending_id'])
    lending_obj = models.LendingOrder.objects.get(id=lending_id)

    form_lendingsures = forms.LendingSuresForm(post_data)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    article_state = lending_obj.summary.article_state
    ''' SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'),  (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if article_state in [1, 2, 3, 4, 61]:
        if form_lendingsures.is_valid():
            lendingsures_clean = form_lendingsures.cleaned_data
            sure_typ = lendingsures_clean['sure_typ']
            default_sure = {'lending': lending_obj, 'sure_typ': sure_typ, 'sure_buildor': request.user}
            if sure_typ == 1:  # 企业保证
                form_lendingcustoms_c_add = forms.LendingCustomsCForm(post_data)
                if form_lendingcustoms_c_add.is_valid():
                    lendingcustoms_c_clean = form_lendingcustoms_c_add.cleaned_data
                    print('lendingcustoms_c_clean:', lendingcustoms_c_clean)
                    try:
                        with transaction.atomic():
                            lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                                lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                            default = {'sure': lendingsure_obj, 'lending_c_buildor': request.user}
                            lendingcustom_obj, created = models.LendingCustoms.objects.update_or_create(
                                sure=lendingsure_obj, defaults=default)
                            for custom in lendingcustoms_c_clean['sure_c']:
                                lendingcustom_obj.custome.add(custom)
                        response['message'] = '反担保设置成功！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ == 2:  # 个人保证
                form_lendingcustoms_p_add = forms.LendingCustomsPForm(post_data)
                if form_lendingcustoms_p_add.is_valid():
                    lendingcustoms_p_clean = form_lendingcustoms_p_add.cleaned_data
                    try:
                        with transaction.atomic():
                            lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                                lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                            default = {'sure': lendingsure_obj, 'lending_c_buildor': request.user}
                            lendingcustom_obj, created = models.LendingCustoms.objects.update_or_create(
                                sure=lendingsure_obj, defaults=default)
                            for custom in lendingcustoms_p_clean['sure_p']:
                                lendingcustom_obj.custome.add(custom)
                        response['message'] = '反担保设置成功！'
                    except Exception as e:
                        response['status'] = False
                        response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ in [11, 21, 42, 52]:  # 房产
                form_lendinghouse_add = forms.LendingHouseForm(post_data)
                if form_lendinghouse_add.is_valid():
                    lendingwarrant_clean = form_lendinghouse_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendingwarrant_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_house']:
                            lendingwarrant_obj.warrant.add(warrant)
                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ in [12, 22, 43, 53]:  # 土地
                form_lendingground_add = forms.LendingGroundForm(post_data)
                if form_lendingground_add.is_valid():
                    lendingwarrant_clean = form_lendingground_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendingwarrant_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_ground']:
                            lendingwarrant_obj.warrant.add(warrant)

                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ == 31:  # 应收质押
                form_lendinggreceivable_add = forms.LendinReceivableForm(post_data)
                if form_lendinggreceivable_add.is_valid():
                    lendingwarrant_clean = form_lendinggreceivable_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendinreceivable_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_receivable']:
                            lendinreceivable_obj.warrant.add(warrant)
                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ in [32, 51]:  # 股权质押
                form_lendingstock_add = forms.LendinStockForm(post_data)
                if form_lendingstock_add.is_valid():
                    lendingwarrant_clean = form_lendingstock_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendinstock_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_stock']:
                            lendinstock_obj.warrant.add(warrant)
                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ == 13:  # 动产抵押
                form_lendingchattel_add = forms.LendinChattelForm(post_data)
                if form_lendingchattel_add.is_valid():
                    lendingwarrant_clean = form_lendingchattel_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendingchattel_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_chattel']:
                            lendingchattel_obj.warrant.add(warrant)
                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            elif sure_typ == 33:  # 票据质押
                form_lendingdraft_add = forms.LendinDraftForm(post_data)
                if form_lendingdraft_add.is_valid():
                    lendingwarrant_clean = form_lendingdraft_add.cleaned_data
                try:
                    with transaction.atomic():
                        lendingsure_obj, created = models.LendingSures.objects.update_or_create(
                            lending=lending_obj, sure_typ=sure_typ, defaults=default_sure)
                        default = {'sure': lendingsure_obj, 'lending_w_buildor': request.user}
                        lendingdraft_obj, created = models.LendingWarrants.objects.update_or_create(
                            sure=lendingsure_obj, defaults=default)
                        for warrant in lendingwarrant_clean['sure_draft']:
                            lendingdraft_obj.warrant.add(warrant)
                    response['message'] = '反担保设置成功！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '反担保设置失败：%s' % str(e)
            else:
                response['status'] = False
                response['message'] = '本反担保类型尚不能设置，请联系开发人员！！！'
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_lendingsures.errors
    else:
        arg = '项目状态为：%s，无法设置反担保措施！！！' % article_state
        response['status'] = False
        response['message'] = arg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------反担保措施删除ajax-------------------------#
@login_required
def guarantee_del_ajax(request):  # 反担保人删除ajax
    print(__file__, '---->def guarantee_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)
    lending_id = post_data['lending_id']
    sure_typ = int(post_data['sure_typ'])

    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    article_state = lending_obj.summary.article_state
    if article_state in [1, 2, 3, 4, 61]:
        lendingsure_obj = lending_obj.sure_lending.get(sure_typ=sure_typ)
        '''SURE_TYP_LIST = (
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
        if sure_typ in [1, 2]:
            custom_id = post_data['del_guarantee_id']
            custom_obj = models.Customes.objects.get(id=custom_id)
            print('custom_obj:', custom_obj)
            try:
                with transaction.atomic():
                    lendingsure_obj.custom_sure.custome.remove(custom_obj)
                    lendingcustom_list = lendingsure_obj.custom_sure.custome.all()
                    if not lendingcustom_list:
                        lendingsure_obj.custom_sure.delete()
                        lendingsure_obj.delete()
                    msg = '反担保人删除成功！'
                    response['message'] = msg
            except Exception as e:
                response['status'] = False
                response['message'] = '反担保人删除失败：%s' % str(e)
        else:
            warrant_id = post_data['del_guarantee_id']
            warrant_obj = models.Warrants.objects.get(id=warrant_id)
            try:
                with transaction.atomic():
                    lendingsure_obj.warrant_sure.warrant.remove(warrant_obj)

                    lendingwarrant_list = lendingsure_obj.warrant_sure.warrant.all()
                    if not lendingwarrant_list:
                        lendingsure_obj.warrant_sure.delete()
                        lendingsure_obj.delete()
                    msg = '放担保物删除成功！'
                    response['message'] = msg
            except Exception as e:
                response['status'] = False
                response['message'] = '放担保物删除失败：%s' % str(e)
    else:
        msg = '项目状态为：%s，无法删除放款次序！！！' % article_state
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
                    'summary_id': article_id, 'expert_id': expert_id, 'comment_type': cleaned_data['comment_type'],
                    'concrete': cleaned_data['concrete'], 'comment_buildor': request.user}
                comment, created = models.Comments.objects.update_or_create(
                    summary_id=article_id, expert_id=expert_id, defaults=default)
                response['obj_id'] = comment.id
                if created:
                    response['message'] = '成功创建评审意见！'
                else:
                    response['message'] = '成功更新评审意见！'
            except Exception as e:
                response['status'] = False
                response['message'] = '评审意见修改失败：%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法修改！！！' % article_obj.article_state

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
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if article_obj.article_state in [4, 61]:

        form = forms.SingleQuotaForm(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
        default = {
            'summary_id': article_id, 'credit_model': credit_model, 'credit_amount': credit_amount,
            'flow_rate': flow_rate, 'single_buildor': request.user}
        single, created = models.SingleQuota.objects.update_or_create(
            summary_id=article_id, credit_model=credit_model, defaults=default)
        response['message'] = '单项额度设置成功！'

    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法设置单项额度！！！' % article_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------放款次序ajax-------------------------#
@login_required
def lending_order_ajax(request):  # 放款次序ajax
    print(__file__, '---->def single_quota_ajax')
    response = {'status': True, 'message': None, 'forme': None}
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    article_id = post_data['article_id']
    article_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if article_obj.article_state in [4, 61]:
        form = forms.FormLendingOrder(post_data)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            try:
                models.LendingOrder.objects.create(
                    summary_id=article_id, order=cleaned_data['order'],
                    order_amount=cleaned_data['order_amount'], lending_buildor=request.user)
                response['message'] = '放款次序设置成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '放款次序设置失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form.errors

    else:
        msg = '项目状态为：%s，无法设置放款次序！！！' % article_obj.article_state
        response['status'] = False
        response['message'] = msg
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------放款次序删除ajax-------------------------#
@login_required
def lending_del_ajax(request):  # 放款次序删除ajax
    print(__file__, '---->def single_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    lending_id = post_data['lending_id']
    article_id = post_data['article_id']

    lending_obj = models.LendingOrder.objects.get(id=lending_id)
    article_obj = models.Articles.objects.get(id=article_id)
    print('lending_obj:', lending_obj)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4, 61]:
        try:
            lending_obj.delete()  # 删除单项额度
            response['message'] = '放款次序删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '放款次序删除失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，无法删除放款次序！！！' % article_obj.article_state
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
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if article_obj.article_state in [1, 2, 3, 4, 61]:
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
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    '''((1, '同意'), (2, '不同意'))'''
    sign_type = int(post_data['sign_type'])
    article_id = post_data['article_id']
    aritcle_obj = models.Articles.objects.get(id=article_id)
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    if aritcle_obj.article_state == 4:
        if sign_type == 2:
            models.Articles.objects.filter(id=article_id).update(
                sign_type=sign_type, sign_date=post_data['sign_date'], article_state=6)
            response['message'] = '%s项目被否决，更新为注销状态！' % aritcle_obj.article_num
        else:
            form = forms.ArticlesSignForm(post_data)
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
                        try:
                            with transaction.atomic():
                                models.Articles.objects.filter(id=article_id).update(
                                    sign_type=sign_type, renewal=renewal, augment=augment, amount=article_amount,
                                    sign_detail=cleaned_data['sign_detail'],
                                    rcd_opinion=cleaned_data['rcd_opinion'],
                                    convenor_opinion=cleaned_data['convenor_opinion'],
                                    sign_date=cleaned_data['sign_date'],
                                    article_state=5)
                                # 更新客户授信总额
                                custom_id = aritcle_obj.custom.id
                                models.Customes.objects.filter(id=custom_id).update(
                                    credit_amount=F('credit_amount') + augment)
                            response['message'] = '成功签批项目：%s！' % aritcle_obj.article_num
                        except Exception as e:
                            response['status'] = False
                            response['message'] = '项目签批失败失败：%s' % str(e)
                    else:
                        msg = '单项额度或放款次序金额合计与签批总额不相等，项目签批不成功！！！'
                        response['status'] = False
                        response['message'] = msg
                else:
                    response['status'] = False
                    response['message'] = '还有评审委员没有发表评审意见，项目签批不成功！！！'
            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，本次签批失败！！！' % aritcle_obj.article_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------项目变更ajax-------------------------#
@login_required
def article_change_ajax(request):
    print(__file__, '---->def 项目变更ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    '''((1, '同意'), (2, '不同意'))'''
    article_id = post_data['article_id']
    article_list = models.Articles.objects.filter(id=article_id)
    article_obj = article_list.first()
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    form_article_change = forms.ArticleChangeForm(post_data)
    if form_article_change.is_valid():
        change_cleaned = form_article_change.cleaned_data
        change_view = change_cleaned['change_view']
        '''CHANGE_VIEW_LIST = ((1, '变更申请'), (11, '同意变更'), (21, '否决变更'))'''
        article_state = article_obj.article_state
        if article_state in [5, 61]:
            if change_view == 11:
                try:
                    with transaction.atomic():
                        article_list.update(article_state=61)
                        models.ArticleChange.objects.create(
                            article=article_obj, change_view=change_view, change_detail=change_cleaned['change_detail'],
                            change_date=change_cleaned['change_date'], change_buildor=request.user)
                    response['message'] = '项目变更成功，请重新设置方案！'
                except Exception as e:
                    response['status'] = False
                    response['message'] = '项目变更失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '项目状态为：%s，本次变更失败！！！' % article_obj.article_state
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_article_change.errors

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)