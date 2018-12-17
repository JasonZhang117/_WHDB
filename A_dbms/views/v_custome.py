from django.shortcuts import render, redirect
from .. import models
from .. import forms
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage


# 客户、行业、区域信息管理
# -----------------------客户管理-------------------------#
def custom(request, *args, **kwargs):  # 委托合同列表
    print(__file__, '---->def agree')
    form_custom_add = forms.CustomAddForm()
    form_custom_c_add = forms.CustomCAddForm()
    form_custom_p_add = forms.CustomPAddForm()

    genre_list = models.Customes.GENRE_LIST
    custom_list = models.Customes.objects.filter(**kwargs)

    ####分页信息###
    paginator = Paginator(custom_list, 10)
    page = request.GET.get('page')
    try:
        p_list = paginator.page(page)
    except PageNotAnInteger:
        p_list = paginator.page(1)
    except EmptyPage:
        p_list = paginator.page(paginator.num_pages)

    return render(request,
                  'dbms/custome/custom.html',
                  locals())
