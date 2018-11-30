from django.shortcuts import render, redirect
from .. import models
from .. import forms
import datetime, time


# -----------------------评审会-------------------------#
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    meeting_list = models.Appraisals.objects.filter(
        **kwargs).order_by('-review_date', '-review_order')
    meeting_state_list = models.Appraisals.MEETING_STATE_LIST

    return render(request,
                  'dbms/meeting/meeting.html',
                  locals())


# -----------------------添加评审会-------------------------#
def meeting_add(request):  # 添加评审会
    print(__file__, '---->def meeting_add')

    if request.method == "GET":
        form = forms.MeetingAddForm()
        return render(request,
                      'dbms/meeting/meeting-add.html',
                      locals())
    else:
        form = forms.MeetingAddForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data

            ###上会类型(mod)
            review_model = cleaned_data['review_model']
            REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
            for i in REVIEW_MODEL_LIST:
                x, y = i
                if x == review_model:
                    mod = y

            ###上会年份(r_year)
            review_date = cleaned_data['review_date']
            t = time.strptime(str(review_date), "%Y-%m-%d")
            r_year = t.tm_year

            ###上会次序(order)
            order_list = models.Appraisals.objects.filter(
                review_model=review_model,
                review_year=r_year).values_list('review_order')
            if order_list:
                order_m = list(zip(*order_list))
                order_max = max(list(zip(*order_list))[0])  #####
            else:
                order_max = 0
            review_order = order_max + 1
            if review_order < 10:
                order = '00%s' % review_order
            elif review_order < 100:
                order = '0%s' % review_order
            else:
                order = '%s' % review_order

            ###时间处理
            review_num = "(%s)[%s]%s" % (mod, r_year, order)

            meeting_obj = models.Appraisals.objects.create(
                num=review_num,
                review_year=r_year,
                review_model=review_model,
                review_order=order,
                review_date=review_date)

            article_obj = meeting_obj.article.set(
                cleaned_data['article'])
            '''((1, '待反馈'), (2, '待上会'),
             (3, '无补调'), (4, '需补调'),
             (5, '已补调'), (6, '已签批'))'''
            for i in cleaned_data['article']:
                models.Articles.objects.filter(
                    id=i).update(article_state=2)

            return redirect('dbms:meeting_all')
        else:
            return render(request,
                          'dbms/meeting/meeting-add.html',
                          locals())


# -----------------------编辑评审会-------------------------#
def meeting_edit(request, meeting_id):  # 编辑评审会
    print(__file__, '---->def meeting_edit')
    meeting_list = models.Appraisals.objects.filter(id=meeting_id)
    meeting_obj = meeting_list.first()
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        meeting_list.update(meeting_state=2)
        return redirect('dbms:meeting_all')
    else:
        print('状态为：%s，无法修改！！！' % meeting_obj.meeting_state)
    return redirect('dbms:meeting_all')


# -----------------------评审会预览-------------------------#
def meeting_del(request, meeting_id):  # 删除项目
    print(__file__, '---->def meeting_del')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)

    article_l = meeting_obj.article.values_list('id')
    if article_l:
        article_list = list(zip(*article_l))[0]  #####
        for article in article_list:
            models.Articles.objects.filter(
                id=article).update(article_state=1)

    ''' MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        meeting_obj.delete()
    else:
        print('状态为：%s，无法删除！！！' % meeting_obj.meeting_state)
    return redirect('dbms:meeting_all')


# -----------------------评审会预览-------------------------#
def meeting_scan(request, meeting_id):  # 评审会预览
    print(__file__, '---->def meeting_scan')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    expert_list = models.Experts.objects.filter(
        article_expert__appraisal_article=meeting_obj).distinct()

    return render(request,
                  'dbms/meeting/meeting-scan.html',
                  locals())


def meeting_scan_article(request, meeting_id, article_id):
    print(__file__, '---->def article_scan_agree')
    article_obj = models.Articles.objects.get(id=article_id)
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
    print(article_obj.expert.all())

    return render(request,
                  'dbms/meeting/meeting-article.html',
                  locals())
