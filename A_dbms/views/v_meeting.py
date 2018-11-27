from django.shortcuts import render, redirect
from .. import models
from .. import forms
import datetime, time


# -----------------------评审会-------------------------#
def meeting(request, *args, **kwargs):  # 评审会
    print(__file__, '---->def meeting')
    # print('kwargs:', kwargs)
    appraisal_list = models.Appraisals.objects.filter(**kwargs)
    # print('appraisal_list:', appraisal_list)
    review_mode_list = models.Appraisals.REVIEW_MODEL_LIST
    # print('review_mode_list:', review_mode_list)

    return render(request,
                  'dbms/appraisal/meeting.html',
                  locals())


# -----------------------添加评审会-------------------------#
def meeting_add(request):  # 添加评审会
    print(__file__, '---->def meeting_add')
    if request.method == "GET":
        form = forms.MeetingAddForm()
        # print('article-->form:', form)
        return render(request,
                      'dbms/appraisal/appraisal-add.html',
                      locals())
    else:
        form = forms.MeetingAddForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            review_date = cleaned_data['review_date']
            review_model = cleaned_data['review_model']
            review_order = cleaned_data['review_order']
            if review_order < 10:
                order = '00%s' % review_order
            elif review_order < 100:
                order = '0%s' % review_order
            else:
                order = '%s' % review_order
            ###时间处理
            article_date = cleaned_data['article_date']
            date_array = time.strptime(str(article_date),
                                       "%Y-%m-%d")
            year = str(date_array.tm_year)
            ###时间处理
            review_num = "（%s）%s%s" % (review_model, year, order)
            print('review_num:', review_num)
            meeting_obj = models.Appraisals.objects.create(
                num=review_num,
                review_model=review_model,
                review_order=review_order,
                review_date=review_date,
                expert=augment,
                article_id=amount)
            return redirect('dbms:meeting_all')
        else:
            return render(request,
                          'dbms/appraisal/appraisal-add.html',
                          locals())
