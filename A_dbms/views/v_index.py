from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import datetime, time
from .. import models
from .. import forms


# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
@login_required
def index(request):
    '''初始化本人权限、菜单，显示本人待处理信息，显示本人业务统计信息'''
    print(__file__, '-->index')
    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    no_feedback_count = models.Articles.objects.filter(article_state=1).count()  # 待反馈
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''
    no_pigeonhole_count = models.Provides.objects.filter(implement__in=[1, 11]).count()  # 未归档
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    no_ascertain_count = models.Agrees.objects.filter(agree_state=31).count()  # 未落实

    today_str = time.strftime("%Y-%m-%d", time.gmtime())  # 元祖>>>字符窜
    print('time.strftime("%Y-%m-%d", time.gmtime()):', today_str)
    today_str = datetime.datetime.now().strftime('%Y-%m-%d')
    print("datetime.datetime.now().strftime('%Y-%m-%d'):", today_str)
    today_str = datetime.date.today()
    print('datetime.date.today():', today_str)

    date_th_later = datetime.datetime.now() - datetime.timedelta(days=-30)  # 30天前的日期
    print("date_th_later.strftime('%Y-%m-%d'):", date_th_later.strftime('%Y-%m-%d'))
    date_th_later = datetime.date.today() - datetime.timedelta(days=-30)  # 30天前的日期
    print('date_th_later:', date_th_later)
    print("date_th_later.strftime('%Y-%m-%d'):", date_th_later.strftime('%Y-%m-%d'))
    '''PROVIDE_STATUS_LIST = [(1, '在保'), (11, '解保'), (21, '代偿')]'''
    overdue_count = models.Provides.objects.filter(provide_status=1, due_date__lt=datetime.date.today()).count()  # 逾期
    soondue_count = models.Provides.objects.filter(provide_status=1, due_date__gte=datetime.date.today(),
                                                   due_date__lt=date_th_later).count()  # 30天内到期
    soondue_draft_count = models.DraftExtend.objects.filter(draft_state__in=[1, 2], due_date__gte=datetime.date.today(),
                                                            due_date__lt=date_th_later).count()  # 30天内到期
    overdue_draft_count = models.DraftExtend.objects.filter(
        draft_state__in=[1, 2], due_date__lt=datetime.date.today()).count()  # 逾期票据
    return render(request, 'dbms/index_dbms.html', locals())
