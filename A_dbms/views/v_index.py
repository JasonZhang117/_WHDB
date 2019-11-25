from django.shortcuts import render, HttpResponse, redirect
from django.contrib.auth.decorators import login_required
import datetime, time, json
from .. import models
from .. import forms
from django.db.models import Q, F
from django.urls import resolve
from _WHDB.views import MenuHelper, authority, article_right, sub_article_right


# -----------------------首页-------------------------#
@login_required
def index(request):
    '''初始化本人权限、菜单，显示本人待处理信息，显示本人业务统计信息'''
    current_url_name = resolve(request.path).url_name  # 获取当前URL_NAME
    authority_list = request.session.get('authority_list')  # 获取当前用户的所有权限
    menu_result = MenuHelper(request).menu_data_list()
    job_list = request.session.get('job_list')  # 获取当前用户的所有角色
    # 待反馈
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    no_feedback_list = models.Articles.objects.filter(article_state=1)
    if '项目经理' in job_list:
        no_feedback_list = no_feedback_list.filter(Q(director=request.user) | Q(assistant=request.user))
    no_feedback_count = no_feedback_list.count()  # 待反馈
    # 未落实风控条件
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    no_ascertain_list = models.Agrees.objects.filter(agree_state=31)
    if '项目经理' in job_list:
        no_ascertain_list = no_ascertain_list.filter(
            Q(lending__summary__director=request.user) | Q(lending__summary__assistant=request.user))
    no_ascertain_count = no_ascertain_list.count()  # 未落实
    '''
    today_str = time.strftime("%Y-%m-%d", time.gmtime())  # 元祖>>>字符窜
    print('time.strftime("%Y-%m-%d", time.gmtime()):', today_str)
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    print("datetime.datetime.now().strftime('%Y-%m-%d'):", today_str)
    today_str = datetime.date.today()
    print('datetime.date.today():', today_str)
    date_th_later = datetime.datetime.now() - datetime.timedelta(days=-30)  # 30天前的日期
    print("date_th_later.strftime('%Y-%m-%d'):", date_th_later.strftime('%Y-%m-%d'))
    '''
    date_90_later = datetime.date.today() + datetime.timedelta(days=90)  # 90天后的日期
    date_30_later = datetime.date.today() + datetime.timedelta(days=30)  # 30天后的日期
    date_7_later = datetime.date.today() + datetime.timedelta(days=7)  # 7天后的日期
    date_30_befor = datetime.date.today() - datetime.timedelta(days=30)  # 30天前的日期
    date_20_leter = datetime.date.today() - datetime.timedelta(days=20)  # 20天前
    # 逾期放款（到期日小于今天的日期）
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    overdue_list = models.Provides.objects.filter(
        provide_status=1, due_date__lt=datetime.date.today())
    if '项目经理' in job_list:
        overdue_list = overdue_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    overdue_count = overdue_list.count()
    # 30天内到期放款
    soondue_list = models.Provides.objects.filter(
        provide_status=1, due_date__gte=datetime.date.today(),
        due_date__lt=date_30_later)  # 到期日大于今天的日期，小于30天后的日期
    if '项目经理' in job_list:
        soondue_list = soondue_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    soondue_count = soondue_list.count()
    # 30天内到期票据
    '''DRAFT_STATE_LIST = (
        (1, '未入库'), (2, '已入库'), (21, '置换出库'), (31, '解保出库'), (41, '托收出库'), (99, '已注销'))'''
    soondue_draft_count = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__gte=datetime.date.today(), due_date__lt=date_30_later).count()
    # 逾期票据
    overdue_draft_count = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__lt=datetime.date.today()).count()
    # 90天内到期协议
    '''COOPERATOR_STATE_LIST = ((1, '正常'), (11, '注销'))'''
    soondue_cooperator_count = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__gte=datetime.date.today(), due_date__lt=date_90_later).count()
    # 逾期协议
    overdue_cooperator_count = models.Cooperators.objects.filter(
        cooperator_state=1, due_date__lt=datetime.date.today()).count()
    # 30天内到期查封
    '''SEAL_STATE_LIST = [(1, '查询跟踪'), (3, '诉前保全'), (5, '首次首封'), (11, '首次轮封'), (21, '续查封'),
                       (51, '解除查封'), (99, '注销')]'''
    soondue_seal_count = models.Seal.objects.filter(
        seal_state__in=[3, 5, 11, 21], due_date__gte=datetime.date.today(),
        due_date__lt=date_30_later).count()
    # 逾期查封
    overdue_seal_count = models.Seal.objects.filter(
        seal_state__in=[3, 5, 11, 21], due_date__lt=datetime.date.today()).count()
    # 超过30天未查询
    overdue_search_count = models.Seal.objects.filter(
        seal_state__in=[1, 5, 11, 21], inquiry_date__lt=date_30_befor).count()
    # 未归档
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
    no_pigeonhole_list = models.Provides.objects.filter(implement=21)
    if '项目经理' in job_list:
        no_pigeonhole_list = no_pigeonhole_list.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    no_pigeonhole_count = no_pigeonhole_list.count()  # 未归档
    # 逾期归档
    pigeonhole_overdue = models.Provides.objects.filter(implement__in=[1, 11], provide_date__lt=date_20_leter)
    if '项目经理' in job_list:
        pigeonhole_overdue = pigeonhole_overdue.filter(
            Q(notify__agree__lending__summary__director=request.user) | Q(
                notify__agree__lending__summary__director=request.user))
    pigeonhole_overdue = pigeonhole_overdue.count()  # 逾期归档
    # 逾期保后
    '''REVIEW_STATE_LIST = [(1, '待保后'), (11, '待报告'), (21, '已完成'), (81, '自主保后')]'''
    review_overdue = models.Customes.objects.filter(
        review_state=1, review_plan_date__lt=datetime.date.today())  # 逾期保后
    if '项目经理' in job_list:
        review_overdue = review_overdue.filter(managementor=request.user)
    review_overdue = review_overdue.count()
    '''TRACK_STATE_LIST = [(11, '待跟踪'), (21, '已跟踪'), ]'''
    # 7日内的跟踪计划
    track_soondue = models.Track.objects.filter(
        track_state=11, plan_date__gte=datetime.date.today(), plan_date__lt=date_7_later)
    if '项目经理' in job_list:
        track_soondue = track_soondue.filter(
            Q(provide__notify__agree__lending__summary__director=request.user) |
            Q(provide__notify__agree__lending__summary__assistant=request.user))
    track_soondue_count = track_soondue.count()
    # 逾期跟踪
    track_overdue = models.Track.objects.filter(track_state=11, plan_date__lt=datetime.date.today())
    if '项目经理' in job_list:
        track_overdue = track_overdue.filter(
            Q(provide__notify__agree__lending__summary__director=request.user) |
            Q(provide__notify__agree__lending__summary__assistant=request.user))
    track_overdue_count = track_overdue.count()
    return render(request, 'dbms/index_dbms.html', locals())


