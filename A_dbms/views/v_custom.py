from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms
import time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db import transaction


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
                  'dbms/custom/custom.html',
                  locals())


# -----------------------客户添加-------------------------#
def custom_add_ajax(request):
    print(__file__, '---->def custom_add_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    form_custom_add = forms.CustomAddForm(post_data)
    if form_custom_add.is_valid():
        custom_add_data = form_custom_add.cleaned_data
        genre = custom_add_data['genre']
        if genre == 1:
            form_custom_c_add = forms.CustomCAddForm(post_data)
            if form_custom_c_add.is_valid():
                custom_c_data = form_custom_c_add.cleaned_data
                try:
                    custom_obj = models.Customes.objects.create(
                        name=custom_add_data['name'],
                        idustry=custom_add_data['idustry'],
                        district=custom_add_data['district'],
                        genre=custom_add_data['genre'],
                        contact_addr=custom_add_data['contact_addr'],
                        linkman=custom_add_data['linkman'],
                        contact_num=custom_add_data['contact_num'])

                    custom_c_obj = models.CustomesC.objects.create(
                        custome=custom_obj,
                        short_name=custom_c_data['short_name'],
                        capital=custom_c_data['capital'],
                        registered_addr=custom_c_data['registered_addr'],
                        representative=custom_c_data['representative'])
                    response['message'] = '客户%s创建成功！！！' % custom_add_data['name']
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户创建失败：%s' % str(e)

            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_c_add.errors

        elif genre == 2:
            form_custom_p_add = forms.CustomPAddForm(post_data)
            if form_custom_p_add.is_valid():
                custom_p_data = form_custom_p_add.cleaned_data
                try:
                    with transaction.atomic():
                        custom_obj = models.Customes.objects.create(
                            name=custom_add_data['name'],
                            idustry=custom_add_data['idustry'],
                            district=custom_add_data['district'],
                            genre=custom_add_data['genre'],
                            contact_addr=custom_add_data['contact_addr'],
                            linkman=custom_add_data['linkman'],
                            contact_num=custom_add_data['contact_num'])

                        custom_p_obj = models.CustomesP.objects.create(
                            custome=custom_obj,
                            license_num=custom_p_data['license_num'],
                            license_addr=custom_p_data['license_addr'])
                        response['message'] = '客户%s创建成功！！！' % custom_add_data['name']
                except Exception as e:
                    response['status'] = False
                    response['message'] = '客户创建失败：%s' % str(e)


            else:
                response['status'] = False
                response['message'] = '表单信息有误！！！'
                response['forme'] = form_custom_p_add.errors
                result = json.dumps(response, ensure_ascii=False)
                return HttpResponse(result)

    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_custom_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------客户删除-------------------------#
def custom_del_ajax(request):
    print(__file__, '---->def custom_del_ajax')
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    print('post_data:', post_data)

    custom_id = post_data['custom_id']
    custom_obj = models.Customes.objects.get(id=custom_id)
    
    try:
        custom_obj.delete()  # 删除评审会
        msg = '%s，删除成功！' % custom_obj.name
        response['message'] = msg
    except Exception as e:
        response['status'] = False
        response['message'] = '客户删除失败:%s！' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------客户预览------------------------------#
def custom_scan(request, custom_id):  # 项目预览
    print(__file__, '---->def custom_scan')
    custom_obj = models.Customes.objects.get(id=custom_id)

    if custom_obj.genre == 1:
        form_date = {
            'name': custom_obj.name,
            'idustry': custom_obj.idustry,
            'district': custom_obj.district,
            'genre': custom_obj.genre,
            'contact_addr': custom_obj.contact_addr,
            'linkman': custom_obj.linkman,
            'contact_num': custom_obj.contact_num}

        form_article_add_edit = forms.ArticlesAddForm(form_date)

    return render(request,
                  'dbms/custom/custom-scan.html',
                  locals())
