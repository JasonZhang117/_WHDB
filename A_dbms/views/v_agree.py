from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import datetime


# 项目信息管理
# -----------------------委托管理-------------------------#
# -----------------------委托管理-------------------------#
# -----------------------委托合同列表---------------------#
def agree(request, usernum):  # 委托合同列表
    print(__file__)
    agree_typ_list = models.Agrees.AGREE_TYP_LIST
    agree_list = models.Agrees.objects.all(). \
        select_related('article', 'branch')
    return render(request,
                  'dbms/agree/agree.html',
                  locals())


def agree_add(request, usernum):  # 添加合同
    print('----------------agree_add------------------------')
    if request.method == "GET":
        form = forms.AgreeAddForm()
        return render(request,
                      'dbms/agree/agree-add.html',
                      locals())
    else:
        form = forms.AgreeAddForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_data = form.cleaned_data
            article_obj = models.Agrees.objects.create(
                agree_num=cleaned_data['agree_num'],
                article_id=cleaned_data['article_id'],
                branch_id=cleaned_data['branch_id'],
                agree_typ=cleaned_data['agree_typ'],
                agree_amount=cleaned_data['agree_amount'],
                agree_state=1)
            return redirect('dbms:agree')
        else:
            return render(request,
                          'dbms/article/article-add.html',
                          locals())


def agree_edit(request, usernum, id):  # 修改合同
    print('----------------agree_edit---------------------')
    agree_obj = models.Agrees.objects.get(id=id)
    if agree_obj.agree_state == 1:
        if request.method == "GET":
            # form初始化，适合做修改该
            form_date = {'agree_num': agree_obj.agree_num,
                         'article_id': agree_obj.article.id,
                         'branch_id': agree_obj.branch.id,
                         'agree_typ': agree_obj.agree_typ,
                         'agree_amount': agree_obj.agree_amount}
            form = forms.AgreeAddForm(form_date)
            return render(request,
                          'dbms/agree/agree-edit.html',
                          locals())
        else:
            # form验证
            form = forms.AgreeAddForm(request.POST,
                                      request.FILES)
            if form.is_valid():
                cleaned_data = form.cleaned_data
                agree_obj = models.Agrees.objects.filter(id=id)
                agree_obj.update(
                    agree_num=cleaned_data['agree_num'],
                    article_id=cleaned_data['article_id'],
                    branch_id=cleaned_data['branch_id'],
                    agree_typ=cleaned_data['agree_typ'],
                    agree_amount=cleaned_data['agree_amount'],
                    agree_state=1)
                return redirect('/dbms/agree/')
            else:
                return render(request,
                              'dbms/agree/agree-edit.html',
                              locals())
    else:
        print('无法修改！！！')
        return redirect('/dbms/article/')


def agree_scan(request, usernum, id):  # 查看合同
    print('---------------agree_scan------------------------')
    if request.method == "GET":
        agree_obj = models.Agrees.objects.get(id=id)

        return render(request,
                      'dbms/agree/agree-scan.html',
                      locals())
