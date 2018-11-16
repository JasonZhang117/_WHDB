from django.shortcuts import render, redirect, HttpResponse
from .. import models
from .. import forms


# 抵质押物信息管理
# -----------------------房产管理-------------------------#
# -----------------------房产管理-------------------------#
# -----------------------房产管理-------------------------#
# -----------------------房产列表-------------------------#
def warrant(request, usernum):  # 房产列表
    warrant_list = models.Warrants.objects.all()
    # print(house_list)
    for warrant in warrant_list:
        print(warrant.warrant_num)
    return render(request,
                  'dbms/warrant/warrant.html',
                  locals())
