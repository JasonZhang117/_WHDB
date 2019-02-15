from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .. import models
from .. import forms


# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
# -----------------------首页-------------------------#
@login_required
def index(request):
    '''
    初始化本人权限、菜单，显示本人待处理信息，显示本人业务统计信息
    '''
    print(__file__, '-->index')
    #
    # user = request.user
    # print('user:', user)
    # print('type(user):', type(user))
    # print('user.job:', user.job)
    # if user:
    #     menu_list = models.Menus.objects.filter(jobs__employees=user).distinct()
    #     # job_list = models.Jobs.objects.filter(employee_job=user)
    # print('menu_list:', menu_list)
    # print('job_list:', job_list)
    # session_menus = request.session.menus
    # print('session_menus:', session_menus)

    '''ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放完'), (61, '待变更'), (99, '已注销'))'''
    no_feedback_count = models.Articles.objects.filter(article_state=1).count()
    '''IMPLEMENT_LIST = [(1, '未归档'), (11, '退回'), (21, '暂存风控'), (31, '移交行政'), (41, '已归档')]'''

    no_pigeonhole_count = models.Provides.objects.filter(implement__in=[1, 11]).count()
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    no_ascertain_count = models.Agrees.objects.filter(agree_state=31).count()

    return render(request, 'dbms/index_dbms.html', locals())
