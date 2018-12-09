from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
import json
from django.db.utils import IntegrityError


# 项目信息管理
# -----------------------委托管理-------------------------#
# -----------------------委托管理-------------------------#
# -----------------------委托合同列表---------------------#
def agree(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    form = forms.AgreeAddForm()

    agree_state_list = models.Agrees.AGREE_STATE_LIST
    agree_list = models.Agrees.objects.filter(
        **kwargs).select_related('article', 'branch')

    ####分页信息###
    paginator = Paginator(agree_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/agree/agree.html',

                  locals())


# -----------------------------查看合同------------------------------#
def agree_scan(request, agree_id):  # 查看合同
    print(__file__, '---->def agree_scan')
    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request,
                  'dbms/agree/agree-scan.html',
                  locals())



# -----------------------------添加合同ajax------------------------------#
def agree_add_ajax(request):  # 添加合同
    print(__file__, '---->def agree_add_ajax')
    response = {'status': True, 'message': None,
                'agree_num': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    data = {
        'article_id': post_data['article_id'],
        'branch_id': post_data['branch_id'],
        'agree_typ': post_data['agree_typ'],
        'agree_amount': post_data['agree_amount'],
        'guarantee_typ': post_data['guarantee_typ'],
        'agree_copies': post_data['agree_copies']}
    form = forms.AgreeAddForm(data, request.FILES)
    if form.is_valid():
        cleaned_data = form.cleaned_data
        print('cleaned_data:', cleaned_data)
        article_id = cleaned_data['article_id']
        agree_amount = cleaned_data['agree_amount']
        guarantee_typ = cleaned_data['guarantee_typ']
        agree_copies = cleaned_data['agree_copies']

        ###判断合同情况：
        article_obj = models.Articles.objects.get(id=article_id)
        if agree_amount > article_obj.amount:
            response['status'] = False
            msg = '该项目审批额度为%s,合同金额超过审批额度！！！' % article_obj.amount
            response['message'] = msg
            result = json.dumps(response, ensure_ascii=False)
            return HttpResponse(result)

        ###合同年份(agree_year)
        t = time.gmtime(time.time())  # 时间戳--》元组
        agree_year = t.tm_year
        ###合同序号(order)
        order_max_x = models.Agrees.objects.filter(
            agree_date__year=agree_year).count() + 1

        if order_max_x < 10:
            agree_order = '00%s' % order_max_x
        elif order_max_x < 100:
            agree_order = '0%s' % order_max_x
        else:
            agree_order = '%s' % order_max_x

        ###评审会编号拼接
        '''成武担[2016]018④W6-1'''
        agree_num = "成武担[%s]%s%sW%s-1" % (
            agree_year, agree_order, guarantee_typ, agree_copies)
        print('agree_num', agree_num)
        try:
            agree_obj = models.Agrees.objects.create(
                agree_num=agree_num,
                article_id=article_id,
                branch_id=cleaned_data['branch_id'],
                agree_typ=cleaned_data['agree_typ'],
                agree_amount=agree_amount,
                guarantee_typ=guarantee_typ,
                agree_copies=agree_copies,
                agree_buildor=request.user)

            response['agree_num'] = agree_obj.agree_num
            response['message'] = '成功创建合同：%s！' % agree_obj.agree_num

        except Exception as e:
            response['status'] = False
            response['message'] = str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


def agree_preview(request, agree_id):
    agree_obj = models.Agrees.objects.get(id=agree_id)

    return render(request,
                  'dbms/agree/agree-preview.html',
                  locals())


def agree_edit(request, id):  # 修改合同
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
            form = forms.AgreeAddForm(request.POST, request.FILES)
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
                return redirect('dbms:agree')
            else:
                return render(request,
                              'dbms/agree/agree-edit.html',
                              locals())
    else:
        print('无法修改！！！')
        return redirect('/dbms/article/')
