from django.shortcuts import render, redirect
from .. import models
from .. import forms
import datetime, time


# -----------------------评审会-------------------------#
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    meeting_list = models.Appraisals.objects.filter(
        **kwargs).order_by('-review_date')
    # print('appraisal_list:', appraisal_list)
    meeting_state_list = models.Appraisals.MEETING_STATE_LIST
    # print('review_mode_list:', review_mode_list)

    return render(request,
                  'dbms/meeting/meeting.html',
                  locals())


# -----------------------添加评审会-------------------------#
def meeting_add(request):  # 添加评审会
    print(__file__, '---->def meeting_add')

    order_list = models.Appraisals.objects.filter(
        review_year=2017).values_list('review_order')
    print('order_list:', order_list)
    # date_array = time.strptime(str(datetime.date.today), "%Y-%m-%d").tm_year
    date_array = time.time()
    print('time.time():', date_array)
    date_array = time.ctime().strip()
    print('time.ctime():', date_array)

    date_array = datetime.date.today().year
    print('datetime.date:', type(date_array))

    if request.method == "GET":
        form = forms.MeetingAddForm()
        # print('article-->form:', form)
        return render(request,
                      'dbms/meeting/meeting-add.html',
                      locals())
    else:
        form = forms.MeetingAddForm(request.POST, request.FILES)
        # print('form:', form)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            print('cleaned_data:', cleaned_data)

            review_date = cleaned_data['review_date']
            print('review_date:', review_date)
            print('type(review_date):', type(review_date))
            review_model = cleaned_data['review_model']
            REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
            print('REVIEW_MODEL_LIST:', REVIEW_MODEL_LIST)
            for i in REVIEW_MODEL_LIST:
                x, y = i
                if x == review_model:
                    mod = y
            review_order = cleaned_data['review_order']
            if review_order < 10:
                order = '00%s' % review_order
            elif review_order < 100:
                order = '0%s' % review_order
            else:
                order = '%s' % review_order
            ###时间处理
            year = 2018,
            print('year:', type(year))

            ###时间处理
            review_num = "(%s)[%s]%s" % (mod, year, order)
            print(type(review_order))
            print('review_num:', review_num)

            meeting_obj = models.Appraisals.objects.create(
                num=review_num,
                review_year=year,
                review_model=review_model,
                review_order=review_order,
                review_date=review_date)
            print('meeting_obj:', meeting_obj)
            expert_obj = meeting_obj.expert.set(
                cleaned_data['expert'])
            print("cleaned_data['expert']:", cleaned_data['expert'])

            article_obj = meeting_obj.article.set(
                cleaned_data['article'])
            print("cleaned_data['article']:", cleaned_data['article'])
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
    print('meeting_obj:', meeting_obj, meeting_obj.id)
    '''MEETING_STATE_LIST = ((1, '待上会'), (2, '已上会'))'''
    if meeting_obj.meeting_state == 1:
        if request.method == "GET":
            # form初始化，适合做修改该
            article_l = meeting_obj.article.values_list('id')
            print('article_l:', article_l)
            article_list = list(zip(*article_l))[0]  #####

            for article in article_list:
                models.Articles.objects.filter(
                    id=article).update(article_state=1)

            expert_l = meeting_obj.expert.values_list('id')
            print('expert_l:', expert_l)
            expert_list = list(zip(*expert_l))[0]  #####

            form_date = {
                'review_model': meeting_obj.review_model,
                'review_order': meeting_obj.review_order,
                'review_date': str(meeting_obj.review_date),
                'expert': expert_list,
                'article': article_list}
            form = forms.MeetingAddForm(form_date)
            print('form:', form)

            return render(request,
                          'dbms/meeting/meeting-edit.html',
                          locals())
        else:
            # form验证
            form = forms.MeetingAddForm(request.POST, request.FILES)
            # print('form:', form)
            if form.is_valid():
                cleaned_data = form.cleaned_data

                review_date = cleaned_data['review_date']
                review_model = cleaned_data['review_model']
                REVIEW_MODEL_LIST = models.Appraisals.REVIEW_MODEL_LIST
                for i in REVIEW_MODEL_LIST:
                    x, y = i
                    if x == review_model:
                        modl = y
                review_order = cleaned_data['review_order']
                if review_order < 10:
                    order = '00%s' % review_order
                elif review_order < 100:
                    order = '0%s' % review_order
                else:
                    order = '%s' % review_order
                ###时间处理
                date_array = time.strptime(str(review_date),
                                           "%Y-%m-%d")
                year = str(date_array.tm_year)
                order_list = models.Appraisals.objects.filter().values_list(
                    'review_order')

                ###时间处理
                review_num = "(%s)[%s]%s" % (modl, year, order)

                meeting_list.update(
                    num=review_num,
                    review_model=review_model,
                    review_order=review_order,
                    review_date=review_date)

                expert_obj = meeting_obj.expert.set(
                    cleaned_data['expert'])

                article_obj = meeting_obj.article.set(
                    cleaned_data['article'])

                for i in cleaned_data['article']:
                    models.Articles.objects.filter(
                        id=i).update(article_state=2)
                # 修改数据库
                return redirect('dbms:meeting_all')
            else:
                return render(request,
                              'dbms/meeting/meeting-edit.html',
                              locals())
    else:
        print('状态为：%s，无法修改！！！' % meeting_obj.meeting_state)
        return redirect('dbms:meeting_all')


# -----------------------评审会预览-------------------------#
def meeting_del(request, meeting_id):  # 删除项目
    print(__file__, '---->def meeting_del')
    meeting_obj = models.Appraisals.objects.get(id=meeting_id)
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
    return render(request,
                  'dbms/meeting/meeting-scan.html',
                  locals())
