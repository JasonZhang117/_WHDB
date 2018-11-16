from django.shortcuts import render, redirect
from .. import models
from .. import forms


# 放款、还款、归档事务管理
# -----------------------风控落实-------------------------#
# -----------------------风控落实-------------------------#
# -----------------------风控落实-------------------------#
# -----------------------风控落实-------------------------#
def provide(request, usernum):  # 项目列表
    print('-------------------article----------------------------')
    provide_list = models.Agrees.objects.filter(implement=0). \
        select_related('article_id', 'branch_id')
    add_link = 'dbms:provide'
    return render(request,
                  'dbms/provide/provide.html',
                  locals())


# def provide_add(request): pass


def provide_edit(request, usernum, agree_id):
    print('-------------------provide_edit----------------------------')
    provide_list1 = models.CountersAssure.objects.filter(agree_id=agree_id)
    provide_list2 = models.CountersHouse.objects.filter(agree_id=agree_id)
    print('provide_list:', provide_list2)
    add_link = 'dbms:provide'
    return render(request,
                  'dbms/provide/provide-edit.html',
                  locals())

# def provide_del(request): pass
