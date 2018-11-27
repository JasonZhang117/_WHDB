from django.shortcuts import render, redirect
from .. import models
from .. import forms


# 客户、行业、区域信息管理
# -----------------------客户管理-------------------------#
# -----------------------客户列表-------------------------#
def custome(request):  # 客户列表
    print('-------------------custome----------------------------')
    custome_list = models.Customes.objects.all()
    return render(request,
                  'dbms/custome/custome.html',
                  locals())


# -----------------------客户添加-------------------------#
def custome_add(request):  # 客户添加
    print('-------------------custome_add-------------------------')
    if request.method == "GET":
        form = forms.CustomeForm()
        return render(request,
                      'dbms/custome/custome-add.html',
                      locals())
    else:
        # form验证
        form = forms.CustomeForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            idustry_id = cleaned_form_data['idustry_id']
            print('idustry_id:', idustry_id)
            print('idustry_id:', type(idustry_id))
            print('cleaned_form_data:', cleaned_form_data)

            models.Customes.objects.create(**cleaned_form_data)  # 添加数据库

            return redirect('dbms:custome')
        else:
            return render(request,
                          'dbms/custome/custome-add.html',
                          locals())


# -----------------------客户编辑-------------------------#
def custome_edit(request, custome_id,
                 *args, **kwargs):  # 客户编辑
    print('-------------------custome_edit----------------------------')
    print(' **kwargs:', kwargs)
    print(' *args:', args)
    if request.method == "GET":
        form_data = models.Customes.objects.get(id=custome_id)
        print('form_data:', form_data)
        # print('form_data.idustry:', form_data.idustry.id)
        # print('form_data.idustry:', type(form_data.idustry.id))
        # form初始化，适合做修改该
        data = {'name': form_data.name,
                'short_name': form_data.genre,
                'contact_addr': form_data.contact_addr,
                'linkman': form_data.linkman,
                'contact_numb': form_data.contact_numb,
                }
        form = forms.CustomeForm(data)
        return render(request,
                      'dbms/custome/custome-edit.html',
                      locals())
    else:
        # form验证
        form = forms.CustomeForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            # 修改数据库

            models.Customes.objects.filter(
                id=custome_id).update(**cleaned_form_data)

            return redirect('/dbms/custome/')
        else:
            return render(request,
                          'dbms/custome/custome-edit.html',
                          locals())


# -----------------------客户删除-------------------------#
def custome_del(request, custome_id):  # 客户删除
    print('-------------------custome_del----------------------------')
    models.Customes.objects.get(id=custome_id).delete()
    return redirect('/dbms/custome/')


# -----------------------行业管理-------------------------#
# -----------------------行业列表-------------------------#
def industry(request):  # 行业列表
    industry_list = models.Industries.objects.all()
    return render(request,
                  'dbms/custome/industry.html',
                  locals())


# -----------------------添加行业-------------------------#
def industry_add(request):  # 添加行业
    if request.method == 'GET':
        # 空的form，适合昨添加
        # initial参数可以覆盖field中的initial参数
        # industry_add_form = forms.IndustryForm(initial={'code': 'C',
        #                                                 'name': '其他行业'})
        form = forms.IndustryForm()
        return render(request,
                      'dbms/custome/industry-add.html',
                      locals())
    else:
        # form验证
        print(request.POST)
        form = forms.IndustryForm(request.POST)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data
            # form字段与modle字段名不一致时需要一个一个对应创建：
            # models.Industries.objects.create(
            #     code=industry_add_form.cleaned_data['code'],
            #     name=industry_add_form.cleaned_data['name']
            # )
            # form字段与modle字段名一致时：

            models.Industries.objects.create(**cleaned_form_data)

            return redirect('/dbms/industry/')
        else:
            return render(request,
                          'dbms/custome/industry-add.html',
                          locals())


# -----------------------编辑行业-------------------------#
def industry_edit(request, industry_id):  # 编辑行业
    if request.method == "GET":
        # nid = request.GET.get('nid')
        form_data = models.Industries.objects.filter(
            pk=industry_id).first()
        # industry_edit_form =forms.IndustryForm({'code':'D','name':'制造业'})
        # form初始化，适合做修改该
        form = forms.IndustryForm({'code': form_data.code,
                                   'name': form_data.name})
        return render(request,
                      'dbms/custome/industry-edit.html',
                      locals())
    else:
        # form验证
        form = forms.IndustryForm(request.POST, request.FILES)
        if form.is_valid():
            cleaned_form_data = form.cleaned_data

            models.Industries.objects.filter(
                pk=industry_id).update(**cleaned_form_data)

            return redirect('/dbms/industry/')
        else:
            return render(request,
                          'dbms/custome/industry-edit.html',
                          locals())


# -----------------------区域管理-------------------------#
# -----------------------区域列表-------------------------#
def district(request):  # 区域列表

    return render(request, 'dbms/custome/district.html')
