from django.shortcuts import render, redirect, HttpResponse
from .. import models, forms
import datetime, time, json
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.utils import IntegrityError
from django.db import transaction
from django.contrib.auth.decorators import login_required
from django.db.models import Q, F
from django.urls import resolve, reverse
from _WHDB.views import MenuHelper
from _WHDB.views import authority, UND, UNX
from .v_agree import convert, convert_num, credit_term_c, convert


# ---------------------------合同签批ajax----------------------------#
@login_required
@authority
def agree_sign_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    agree_id = post_data['agree_id']
    agree_list = models.Agrees.objects.filter(id=agree_id)
    agree_obj = agree_list.first()
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (25, '已签订'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    if agree_obj.agree_state in [11, 21]:
        form_agree_sign = forms.FormAgreeSign(post_data, request.FILES)
        if form_agree_sign.is_valid():
            agree_sign_cleaned = form_agree_sign.cleaned_data
            try:
                agree_list.update(agree_state=21, agree_sign_date=agree_sign_cleaned['agree_sign_date'])
                response['message'] = '合同签批成功：%s！' % agree_obj.agree_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同签批失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agree_sign.errors
    else:
        response['status'] = False
        response['message'] = '合同状态为：%s，签批失败！！！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


def agree_limit_test(agree_typ, order_amount, cooperator_up_scale, agree_amount, amount_limit, response):
    '''合同限额检测函数'''
    '''AGREE_TYP_LIST = [(1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
                      (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
                      (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
                      (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
    if agree_typ in [2, 42, 52]:  # (2, '最高额'), (42, 'D-最高额(公证)'),  (52, 'X-小贷最高额'),
        order_amount_up = round(order_amount * (1 + cooperator_up_scale), 2)  # 最高允许的合同金额
    else:
        order_amount_up = order_amount
    ###判断合同金额情况：
    if agree_amount > order_amount_up:
        response['status'] = False
        response['message'] = '合同金额（%s）超过审批额度（%s）！' % (agree_amount, order_amount)
        result = json.dumps(response, ensure_ascii=False)
        return HttpResponse(result)
    elif amount_limit > order_amount:
        response['status'] = False
        response['message'] = '放款限额（%s）超过审批额度（%s）！' % (amount_limit, order_amount,)
        result = json.dumps(response, ensure_ascii=False)
        return HttpResponse(result)


def agree_num_f(agree_typ_list, pre, agree_t, guarantee_typ, agree_copies):
    '''合同编号生成函数'''
    ###合同年份(agree_year)
    t = time.gmtime(time.time())  # 时间戳--》元组
    agree_year = t.tm_year
    ###合同序号(order)
    order_max_x = models.Agrees.objects.filter(
        agree_date__year=agree_year, agree_typ__in=agree_typ_list).count() + 1
    if order_max_x < 10:
        agree_order = '00%s' % order_max_x
    elif order_max_x < 100:
        agree_order = '0%s' % order_max_x
    else:
        agree_order = '%s' % order_max_x
    ###合同编号拼接
    '''成武担[2016]018④W6-1,成武贷[2016]018④J6-1'''
    agree_num_prefix = "%s[%s]%s%s" % (pre, agree_year, agree_order, guarantee_typ)
    agree_num = "%s%s%s-1" % (agree_num_prefix, agree_t, agree_copies)

    return (agree_num_prefix, agree_num)


def agree_name_f(agree_typ):
    '''合同名称生成函数'''
    '''AGREE_TYP_LIST = [(1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
                      (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
                      (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
                      (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
    '''AGREE_NAME_LIST = [(1, '委托保证合同'), (11, '最高额委托保证合同'),
                       (21, '委托出具分离式保函合同'), (22, '开立保函合同'),
                       (31, '借款合同'), (32, '最高额借款合同'), (41, '委托贷款合同'), ]'''
    agree_name = ''
    if agree_typ in [1, 41]:  # (1, 'D-单笔'), (41, 'D-单笔(公证)'),
        agree_name = 1  # (1, '委托保证合同')
    elif agree_typ in [2, 42]:  # (2, 'D-最高额'),(42, 'D-最高额(公证)'),
        agree_name = 11  # (11, '最高额委托保证合同'),
    elif agree_typ in [4, ]:  # (4, 'D-委贷'),
        agree_name = 41  # (41, '委托贷款合同'),
    elif agree_typ in [51, ]:  # (51, 'X-小贷单笔'),
        agree_name = 31  # (31, '借款合同'),
    elif agree_typ in [52, ]:  # (51, 'X-小贷最高额'),
        agree_name = 32  # (32, '最高额借款合同'),
    elif agree_typ in [21, ]:  # (21, 'D-分离式保函'),
        agree_name = 21  # (21, '委托出具分离式保函合同'),
    elif agree_typ in [22, ]:  # (22, 'D-公司保函'),
        agree_name = 22  # (22, '开立保函合同'),
    return agree_name


# ---------------------------添加合同ajax----------------------------#
@login_required
@authority
def agree_add_ajax(request):  # 添加合同
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    lending_obj = models.LendingOrder.objects.get(id=post_data['lending'])
    article_state_lending = lending_obj.summary.article_state
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    if article_state_lending in [4, 5, 51, 61]:
        # form_agree_add = forms.AgreeAddForm(post_data, request.FILES)
        form_agree_add = forms.ArticleAgreeAddForm(post_data, request.FILES)
        from_agree_jk_add = forms.AgreeJkAddForm(post_data)
        if form_agree_add.is_valid() and from_agree_jk_add.is_valid():
            agree_add_cleaned = form_agree_add.cleaned_data
            jk_add_cleaned = from_agree_jk_add.cleaned_data
            # lending_obj = agree_add_cleaned['lending']
            agree_amount = round(agree_add_cleaned['agree_amount'], 2)  # 合同金额
            guarantee_typ = agree_add_cleaned['guarantee_typ']
            agree_copies = agree_add_cleaned['agree_copies']
            branch_id = agree_add_cleaned['branch']
            agree_typ = agree_add_cleaned['agree_typ']  # 合同类型
            amount_limit = agree_add_cleaned['amount_limit']  # 合同放款限额
            branche_obj = models.Branches.objects.get(id=branch_id)
            cooperator_up_scale = branche_obj.cooperator.up_scale  # 最高额上浮比例
            order_amount = round(lending_obj.order_amount, 2)  # 放款次序金额
            '''合同限额检测'''
            agree_limit_test(agree_typ, order_amount, cooperator_up_scale, agree_amount, amount_limit, response)

            if agree_typ in [2, 42, 52]:  # (2, '最高额')
                order_amount_up = round(order_amount * (1 + cooperator_up_scale), 2)  # 最高允许的合同金额
            else:
                order_amount_up = order_amount
            ###判断合同金额情况：
            if agree_amount > order_amount_up:
                response['status'] = False
                response['message'] = '合同金额（%s）超过审批额度（%s）！' % (agree_amount, order_amount)
                result = json.dumps(response, ensure_ascii=False)
                return HttpResponse(result)
            elif amount_limit > order_amount:
                response['status'] = False
                response['message'] = '放款限额（%s）超过审批额度（%s）！' % (amount_limit, order_amount,)
                result = json.dumps(response, ensure_ascii=False)
                return HttpResponse(result)
            '''AGREE_TYP_LIST = [(1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
                      (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
                      (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
                      (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
            AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保类合同
            AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷类合同
            if agree_typ in AGREE_TYP_D:  # 属于担保类合同
                agree_num_prefix, agree_num = agree_num_f(AGREE_TYP_D, '成武担', 'W', guarantee_typ, agree_copies)
            elif agree_typ in AGREE_TYP_X:  # 属于小贷类合同
                agree_num_prefix, agree_num = agree_num_f(AGREE_TYP_X, '成武贷', 'J', guarantee_typ, agree_copies)
            agree_name = agree_name_f(agree_typ)

            repay_method=jk_add_cleaned['repay_method']
            agree_rate=float(agree_add_cleaned['agree_rate'])
            agree_term=int(agree_add_cleaned['agree_term'])
            repay_ex=jk_add_cleaned['repay_ex']
            if repay_method == 21: #等额本息
                agree_rate_q = agree_rate / 1000
                fz = agree_amount * agree_rate_q * (1 + agree_rate_q) ** agree_term
                fm = (1 + agree_rate_q) ** agree_term - 1
                if fm:
                    repay_ex = convert(round(fz/fm,2))
            try:
                with transaction.atomic():
                    agree_obj = models.Agrees.objects.create(
                        agree_num=agree_num, agree_name=agree_name, num_prefix=agree_num_prefix,
                        lending=lending_obj, branch_id=branch_id, agree_typ=agree_typ,
                        agree_term=agree_term,
                        amount_limit=amount_limit, agree_rate=agree_rate,
                        investigation_fee=agree_add_cleaned['investigation_fee'],
                        agree_amount=agree_amount, guarantee_typ=guarantee_typ,
                        agree_copies=agree_copies, other=agree_add_cleaned['other'],
                        agree_start_date=jk_add_cleaned['agree_start_date'],
                        agree_due_date=jk_add_cleaned['agree_due_date'], acc_name=jk_add_cleaned['acc_name'],
                        acc_num=jk_add_cleaned['acc_num'], acc_bank=jk_add_cleaned['acc_bank'],
                        repay_method=repay_method, repay_ex=repay_ex,
                        agree_buildor=request.user)
                    '''AGREE_TYP_LIST = [
                        (1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
                        (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
                        (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
                        (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
                    if agree_typ == 22:
                        form_letter_add = forms.LetterGuaranteeAddForm(post_data, request.FILES)
                        if form_letter_add.is_valid():
                            letter_add_cleaned = form_letter_add.cleaned_data
                            letter_typ = letter_add_cleaned['letter_typ']
                            '''LETTER_TYP_LIST = [(1, '履约保函'), (11, '投标保函'), (21, '预付款保函'), ]'''
                            guarantee_num_f = ''
                            if letter_typ == 1:
                                guarantee_num_f = '-LY'
                            elif letter_typ == 11:
                                guarantee_num_f = '-TB'
                            elif letter_typ == 21:
                                guarantee_num_f = '-YF'

                            guarantee_num = agree_num + guarantee_num_f + '1'
                            letter_obj = models.LetterGuarantee.objects.create(
                                agree=agree_obj, letter_typ=letter_typ, beneficiary=letter_add_cleaned['beneficiary'],
                                basic_contract=letter_add_cleaned['basic_contract'],
                                basic_contract_num=letter_add_cleaned['basic_contract_num'],
                                starting_date=letter_add_cleaned['starting_date'],
                                due_date=letter_add_cleaned['due_date'],
                                guarantee_number=guarantee_num,
                                creator=request.user, create_date=datetime.date.today())
                response['skip'] = "/dbms/agree/scan/%s" % agree_obj.id
                response['message'] = '成功创建合同：%s！' % agree_obj.agree_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同创建失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agree_add.errors
    else:
        response['status'] = False
        response['message'] = '项目状态为：%s，合同创建失败！！！' % article_state_lending
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


def counter_name_f(agree_typ, counter_typ):
    '''反/担保合同名称函数'''
    '''AGREE_TYP_LIST = [
        (1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
        (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
        (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
        (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
    '''COUNTER_TYP_LIST = [
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')]'''
    '''COUNTER_NAME_LIST = [
        (1, '保证反担保合同'), (2, '不可撤销的反担保函'),
        (3, '抵押反担保合同'), (4, '应收账款质押反担保合同'),
        (5, '股权质押反担保合同'), (6, '质押反担保合同'), (9, '预售合同'),
        (21, '最高额保证反担保合同'),
        (23, '最高额抵押反担保合同'), (24, '最高额应收账款质押反担保合同'),
        (25, '最高额股权质押反担保合同'), (26, '最高额质押反担保合同'),
        (41, '保证合同'),
        (43, '抵押合同'), (44, '应收账款质押合同'),
        (45, '股权质押合同'), (46, '质押合同'),
        (59, '举办者权益转让协议'), ]'''
    if agree_typ in [1, 22, 41, ]:  # (1, 'D-单笔'), (22, 'D-公司保函'), 41, 'D-单笔(公证)'),
        if counter_typ in [1, ]:  # (1, '企业担保'),
            counter_name = 1  # (1, '保证反担保合同'),
        elif counter_typ in [2, ]:  # (2, '个人保证'),
            if agree_typ in [41, ]:
                counter_name = 1  # (1, '保证反担保合同'),
            else:
                counter_name = 2  # (2, '不可撤销的反担保函'),
            ''' (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),'''
        elif counter_typ in [11, 12, 13, 14, 15]:
            counter_name = 3  # (3, '抵押反担保合同'),
        elif counter_typ in [31, ]:  # 31, '应收质押'),
            counter_name = 4  # (4, '应收账款质押反担保合同'),
        elif counter_typ in [32, ]:  # (32, '股权质押'),
            counter_name = 5  # (5, '股权质押反担保合同'),
        elif counter_typ in [33, 34, 41]:  # (33, '票据质押'), (34, '动产质押'), (41, '其他权利质押'),
            counter_name = 6  # (6, '质押反担保合同'),
        elif counter_typ in [51, 52, 53]:  # (51, '股权预售'), (52, '房产预售'), (53, '土地预售'),
            counter_name = 9  # (9, '预售合同'),
        elif counter_typ in [59, ]:  # (59, '其他预售')
            counter_name = 59  # (59, '举办者权益转让协议'),
    elif agree_typ in [2, 21, 42]:  # (2, 'D-最高额'), (21, 'D-分离式保函'), (42, 'D-最高额(公证)'),
        if counter_typ in [1, ]:  # (1, '企业担保'),
            counter_name = 21  # (21, '最高额保证反担保合同'),
        elif counter_typ in [2, ]:  # (2, '个人保证'),
            if agree_typ in [42, ]:
                counter_name = 1  # (1, '保证反担保合同'),
            else:
                counter_name = 2  # (2, '不可撤销的反担保函'),
            ''' (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),'''
        elif counter_typ in [11, 12, 13, 14, 15]:
            counter_name = 23  # (23, '最高额抵押反担保合同'),
        elif counter_typ in [31, ]:  # 31, '应收质押'),
            counter_name = 24  # (24, '最高额应收账款质押反担保合同'),
        elif counter_typ in [32, ]:  # (32, '股权质押'),
            counter_name = 25  # (25, '最高额股权质押反担保合同'),
        elif counter_typ in [33, 34, 39, 41]:  # (33, '票据质押'), (34, '动产质押'), (41, '其他权利质押'),
            counter_name = 26  # (26, '最高额质押反担保合同'),
        elif counter_typ in [51, 52, 53]:  # (51, '股权预售'), (52, '房产预售'), (53, '土地预售'),
            counter_name = 9  # (9, '预售合同'),
        elif counter_typ in [59, ]:  # (59, '其他预售')
            counter_name = 59  # (59, '举办者权益转让协议'),
    elif agree_typ in [4, 51]:  # (4, 'D-委贷'), 51, 'X-小贷单笔'),
        if counter_typ in [1, 2]:  # (1, '企业担保'), (2, '个人保证'),
            counter_name = 41  # (41, '保证合同'),
            ''' (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),'''
        elif counter_typ in [11, 12, 13, 14, 15]:
            counter_name = 43  # (43, '抵押合同'),
        elif counter_typ in [31, ]:  # 31, '应收质押'),
            counter_name = 44  # (44, '应收账款质押合同'),
        elif counter_typ in [32, ]:  # (32, '股权质押'),
            counter_name = 45  # (45, '股权质押合同'),
        elif counter_typ in [33, 34, 39, 41]:  # (33, '票据质押'), (34, '动产质押'), (41, '其他权利质押'),
            counter_name = 46  # (46, '质押合同'),
        elif counter_typ in [51, 52, 53]:  # (51, '股权预售'), (52, '房产预售'), (53, '土地预售'),
            counter_name = 9  # (9, '预售合同'),
        elif counter_typ in [59, ]:  # (59, '其他预售')
            counter_name = 59  # (59, '举办者权益转让协议'),
    elif agree_typ in [52, ]:  # (52, 'X-小贷最高额'),
        if counter_typ in [1, 2]:  # (1, '企业担保'), (2, '个人保证'),
            counter_name = 61  # (61, '最高额保证合同'),
            ''' (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),'''
        elif counter_typ in [11, 12, 13, 14, 15]:
            counter_name = 63  # (63, '最高额抵押合同'), 
        elif counter_typ in [31, 32, 33, 34, 39, 41 ]:  # 
            counter_name = 66  # (66, '最高额质押合同'),
        elif counter_typ in [51, 52, 53]:  # (51, '股权预售'), (52, '房产预售'), (53, '土地预售'),
            counter_name = 9  # (9, '预售合同'),
        elif counter_typ in [59, ]:  # (59, '其他预售')
            counter_name = 59  # (59, '举办者权益转让协议'),
    return counter_name


# ---------------------------修改合同ajax----------------------------#
@login_required
@authority
def agree_edit_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_list = models.Agrees.objects.filter(id=post_data['agree_id'])
    agree_obj = agree_list.first()
    agree_state = agree_obj.agree_state
    lending_obj = agree_obj.lending
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    if agree_state in [11, 51]:
        # form_agree_add = forms.AgreeAddForm(post_data, request.FILES)
        form_agree_add = forms.ArticleAgreeAddForm(post_data, request.FILES)
        from_agree_jk_add = forms.AgreeJkAddForm(post_data)
        if form_agree_add.is_valid() and from_agree_jk_add.is_valid():
            agree_add_cleaned = form_agree_add.cleaned_data
            jk_add_cleaned = from_agree_jk_add.cleaned_data
            # lending_obj = agree_add_cleaned['lending']
            agree_amount = round(agree_add_cleaned['agree_amount'], 2)
            guarantee_typ = agree_add_cleaned['guarantee_typ']
            agree_copies = agree_add_cleaned['agree_copies']
            branch_id = agree_add_cleaned['branch']
            agree_typ = agree_add_cleaned['agree_typ']
            amount_limit = agree_add_cleaned['amount_limit']
            branche_obj = models.Branches.objects.get(id=branch_id)
            cooperator_up_scale = branche_obj.cooperator.up_scale
            order_amount = round(lending_obj.order_amount, 2)  # 放款次序金额
            '''合同限额检测'''
            agree_limit_test(agree_typ, order_amount, cooperator_up_scale, agree_amount, amount_limit, response)
            agree_name = agree_name_f(agree_typ)  # 生成合同名称

            repay_method=jk_add_cleaned['repay_method']
            agree_rate=float(agree_add_cleaned['agree_rate'])
            agree_term=int(agree_add_cleaned['agree_term'])
            repay_ex=jk_add_cleaned['repay_ex']
            if repay_method == 21: #等额本息
                agree_rate_q = agree_rate / 1000
                fz = agree_amount * agree_rate_q * (1 + agree_rate_q) ** agree_term
                fm = (1 + agree_rate_q) ** agree_term - 1
                if fm:
                    repay_ex = convert(round(fz/fm,2))
            try:
                with transaction.atomic():
                    agree_list.update(
                        agree_name=agree_name, branch_id=branch_id, agree_typ=agree_typ,
                        agree_term=agree_term,
                        amount_limit=amount_limit, agree_rate=agree_rate,
                        investigation_fee=agree_add_cleaned['investigation_fee'],
                        agree_amount=agree_amount, guarantee_typ=guarantee_typ,
                        agree_copies=agree_copies, other=agree_add_cleaned['other'],
                        agree_start_date=jk_add_cleaned['agree_start_date'],
                        agree_due_date=jk_add_cleaned['agree_due_date'], acc_name=jk_add_cleaned['acc_name'],
                        acc_num=jk_add_cleaned['acc_num'], acc_bank=jk_add_cleaned['acc_bank'],
                        repay_method=repay_method, repay_ex=repay_ex,
                        agree_buildor=request.user)
                    if agree_obj.agree_typ == 22:  # (22, 'D-公司保函')
                        form_letter_add = forms.LetterGuaranteeAddForm(post_data)
                        if form_letter_add.is_valid():
                            letter_add_cleaned = form_letter_add.cleaned_data
                            letter_typ = letter_add_cleaned['letter_typ']
                            '''LETTER_TYP_LIST = [(1, '履约保函'), (11, '投标保函'), (21, '预付款保函'), ]'''
                            guarantee_num_f = ''
                            if letter_typ == 1:
                                guarantee_num_f = '-LY'
                            elif letter_typ == 11:
                                guarantee_num_f = '-TB'
                            elif letter_typ == 21:
                                guarantee_num_f = '-YF'
                            guarantee_num = agree_obj.agree_num + guarantee_num_f + '1'

                            letter_clean = form_letter_add.cleaned_data
                            default = {
                                'agree_id': agree_obj.id, 'letter_typ': letter_typ,
                                'beneficiary': letter_add_cleaned['beneficiary'],
                                'basic_contract': letter_add_cleaned['basic_contract'],
                                'basic_contract_num': letter_add_cleaned['basic_contract_num'],
                                'starting_date': letter_add_cleaned['starting_date'],
                                'due_date': letter_add_cleaned['due_date'],
                                'guarantee_number': guarantee_num,
                                'creator': request.user}
                            letter, created = models.LetterGuarantee.objects.update_or_create(
                                agree=agree_obj, defaults=default)
                        else:
                            response['status'] = False
                            response['message'] = '表单信息有误！！！'
                            response['forme'] = form_agree_add.errors
                    for counter in agree_obj.counter_agree.all():
                        counter_typ = counter.counter_typ
                        counter_name = counter_name_f(agree_typ, counter_typ)
                        models.Counters.objects.filter(id=counter.id).update(counter_name=counter_name)
                response['skip'] = "/dbms/agree/scan/%s" % agree_obj.id
                response['message'] = '成功修改合同：%s！' % agree_obj.agree_num
            except Exception as e:
                response['status'] = False
                response['message'] = '委托合同修改失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '表单信息有误！！！'
            response['forme'] = form_agree_add.errors
    else:
        response['status'] = False
        response['message'] = '合同状态为：%s，合同修改失败！！！' % agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------删除合同ajax------------------------------#
@login_required
@authority
def agree_del_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_obj = models.Agrees.objects.get(id=post_data['agree_id'])
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    agree_last = models.Agrees.objects.last().id
    if agree_obj.agree_state in [11, 99]:
        if agree_obj.id == agree_last:
            try:
                with transaction.atomic():
                    agree_obj.delete()
                response['message'] = '委托保证合同删除成功！'
                response['skip'] = '/dbms/agree/'
            except Exception as e:
                response['status'] = False
                response['message'] = '委托保证合同删除失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '删除失败，只能删除最后一份委托保证合同！'
    else:
        response['status'] = False
        response['message'] = '合同状态为%s，无法删除！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ---------------------------委托担保合同保存ajax----------------------------#
@login_required
def agree_save_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_content = post_data['content']
    agree_obj = models.Agrees.objects.filter(id=post_data['agree_id'])
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    try:
        agree_obj.update(agree_view=agree_content)
        response['message'] = '合同保存成功，正式签订合同须经公司领导签批！合同签批后，合同内容将固定！'
    except Exception as e:
        response['status'] = False
        response['message'] = '合同保存失败：%s' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ---------------------------补充协议保存ajax----------------------------#
@login_required
def supple_save_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_content = post_data['content']
    agree_obj = models.Agrees.objects.filter(id=post_data['agree_id'])
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    try:
        agree_obj.update(supplementary=agree_content)
        response['message'] = '合同保存成功，正式签订合同须经公司领导签批！合同签批后，合同内容将固定！'
    except Exception as e:
        response['status'] = False
        response['message'] = '合同保存失败：%s' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)

def counter_num_f(counter_prefix, agree_typ, counter_typ, agree_obj):
    '''担保合同编号函数'''
    '''AGREE_TYP_LIST = [
            (1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
            (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
            (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
            (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
    '''COUNTER_TYP_LIST = [
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')]'''
    if counter_typ in [1, 2]:  # (1, '企业担保')
        counter_typ_n = 'X'
        counter_copies = 3
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[1, 2]).count() + 1
    elif counter_typ in [2, ]:  # 个人反担保函类型
        counter_typ_n = 'G'
        counter_copies = 2
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ=counter_typ).count() + 1
        ''' (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),'''
    elif counter_typ in [11, 12, 13, 14, 15]:  # 抵押类
        counter_typ_n = 'D'
        counter_copies = 4
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[11, 12, 13, 14, 15]).count() + 1
        '''(31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (41, '其他权利质押'),'''
    elif counter_typ in [31, 32, 33, 34, 41]:  # 质押类
        counter_typ_n = 'Z'
        counter_copies = 4
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33, 34, 41]).count() + 1
        '''(51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')'''
    elif counter_typ in [51, 52, 53, 59]:  # 预售类
        counter_typ_n = 'Y'
        counter_copies = 3
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[51, 52, 53, 59]).count() + 1
    else:
        counter_typ_n = ''
        counter_copies = 2
        counter_max = models.Counters.objects.filter(
            agree=agree_obj, counter_typ__in=[31, 32, 33]).count() + 1
    '''AGREE_TYP_LIST = [(1, '单笔'), (2, '最高额'), (3, '保函'), (7, '小贷'),
                      (41, '单笔(公证)'), (42, '最高额(公证)'), (47, '小贷(公证)')]'''
    if agree_typ in [41, 42, 51, 52]:
        counter_copies += 1
    '''成武担[2016]018④W6-1'''
    counter_num = '%s%s%s-%s' % (counter_prefix, counter_typ_n, counter_copies, counter_max)
    return (counter_num, counter_copies)


# -------------------------添加反担保合同ajax-------------------------#
@login_required
@authority
def counter_add_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_id = post_data['agree_id']
    counter_typ = int(post_data['counter_typ'])
    agree_obj = models.Agrees.objects.get(id=agree_id)
    agree_typ = agree_obj.agree_typ
    from_counter_add = forms.AddCounterForm(post_data)
    counter_prefix = agree_obj.num_prefix  # 合同前缀
    counter_name = counter_name_f(agree_typ, counter_typ)  # 生成合同名称
    '''生成（反）担保合同编号及合同份数'''
    counter_num, counter_copies = counter_num_f(counter_prefix, agree_typ, counter_typ, agree_obj)
    agree_state_counter = agree_obj.agree_state  # 主合同状态
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''

    if from_counter_add.is_valid():
        counter_clean = from_counter_add.cleaned_data
        if agree_state_counter in [11, 51]:
            if counter_typ in [1, 2]:  # 保证反担保
                if counter_typ in [1, ]:
                    custom_list = post_data['custom_c']  #
                else:
                    custom_list = post_data['custom_p']
                try:
                    with transaction.atomic():
                        '''创建反担保合同'''
                        counter_obj = models.Counters.objects.create(
                            counter_num=counter_num, counter_name=counter_name, agree=agree_obj,
                            counter_typ=counter_typ, counter_other=counter_clean['counter_other'],
                            counter_copies=counter_copies, counter_buildor=request.user)
                        '''创建保证反担保合同'''
                        counter_assure_obj = models.CountersAssure.objects.create(
                            counter=counter_obj, counter_assure_buildor=request.user)
                        '''添加反担保人'''
                        for custom in custom_list:
                            counter_assure_obj.custome.add(custom)
                    response['message'] = '成功创建反担保合同：%s！' % counter_obj.counter_num
                except Exception as e:
                    response['status'] = False
                    response['message'] = '委托合同创建失败：%s' % str(e)
            else:
                '''COUNTER_TYP_LIST = [
            (1, '企业担保'), (2, '个人保证'),
            (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
            (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
            (41, '其他权利质押'),
            (51, '股权预售'), (52, '房产预售'), (53, '土地预售'), (59, '其他预售')]'''
                if counter_typ in [11, 52]:  # (11, '房产抵押'),(52, '房产预售'),
                    warrant_list = post_data['house']
                elif counter_typ in [12, 53]:  # (12, '土地抵押'),(53, '土地预售')
                    warrant_list = post_data['ground']
                elif counter_typ in [14, ]:  # (14, '在建工程抵押')
                    warrant_list = post_data['coustruct']
                elif counter_typ in [31, ]:  # (31, '应收质押')
                    warrant_list = post_data['receivable']
                elif counter_typ in [32, 51]:  # (32, '股权质押'), (51, '股权预售')
                    warrant_list = post_data['stock']
                elif counter_typ in [33, ]:  # (33, '票据质押')
                    warrant_list = post_data['draft']
                elif counter_typ in [15, ]:  # (15, '车辆抵押')
                    warrant_list = post_data['vehicle']
                elif counter_typ in [13, 34]:  # (13, '动产抵押'), (34, '动产质押')
                    warrant_list = post_data['chattel']
                elif counter_typ in [41, 59]:  # (41, '其他权利质押')
                    warrant_list = post_data['other']
                try:
                    with transaction.atomic():
                        '''创建反担保合同'''
                        counter_obj = models.Counters.objects.create(
                            counter_num=counter_num, counter_name=counter_name, agree=agree_obj,
                            counter_typ=counter_typ, counter_other=counter_clean['counter_other'],
                            counter_copies=counter_copies, counter_buildor=request.user)
                        '''创建抵质押反担保合同'''
                        counter_warrant_obj = models.CountersWarrants.objects.create(
                            counter=counter_obj, counter_warrant_buildor=request.user)
                        '''添加抵质押权证'''
                        for warrant in warrant_list:
                            counter_warrant_obj.warrant.add(warrant)
                    response['message'] = '成功创建反担保合同：%s！' % counter_obj.counter_num
                except Exception as e:
                    response['status'] = False
                    response['message'] = '委托合同创建失败：%s' % str(e)
        else:
            response['status'] = False
            response['message'] = '委托合同状态为：%s，反担保合同创建失败！！！' % agree_state_counter
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = from_counter_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------删除反担保合同ajax-------------------------#
@login_required
@authority
def counter_del_ajax(request):  # 删除反担保合同ajax
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)

    agree_id = post_data['agree_id']
    counter_id = post_data['counter_id']

    agree_obj = models.Agrees.objects.get(id=agree_id)
    counter_obj = models.Counters.objects.get(id=counter_id)
    '''COUNTER_TYP_LIST = (
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
    if counter_obj.counter_typ in [1, 2]:
        counter_counter_obj = counter_obj.assure_counter
    else:
        counter_counter_obj = counter_obj.warrant_counter
    '''AGREE_STATE_LIST = ((11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '作废'))'''
    counter_last_id = models.Counters.objects.filter(agree=agree_obj).last().id
    if agree_obj.agree_state in [11, 51]:
        if counter_obj.id == counter_last_id:
            try:
                with transaction.atomic():
                    counter_counter_obj.delete()  # 删除保证/抵质押反担保合同
                    counter_obj.delete()  # 删除反担保合同
                response['message'] = '反担保合同删除成功！'
            except Exception as e:
                response['status'] = False
                response['message'] = '反担保合同删除失败:%s！' % str(e)
        else:
            response['status'] = False
            response['message'] = '删除失败，只能删除最后一份反担保合同！'
    else:
        response['status'] = False
        response['message'] = '委托担保合同状态为%s，无法删除反担保合同！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# ---------------------------反担保合同保存ajax----------------------------#
@login_required
def counter_save_ajax(request):  # 添加合同
    response = {'status': True, 'message': None, 'forme': None, 'skip': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    counter_content = post_data['content']
    counter_obj = models.Counters.objects.filter(id=post_data['counter_id'])
    '''ARTICLE_STATE_LIST = [(1, '待反馈'), (2, '已反馈'), (3, '待上会'), (4, '已上会'), (5, '已签批'),
                          (51, '已放款'), (52, '已放完'), (55, '已解保'), (61, '待变更'), (99, '已注销')]'''
    try:
        counter_obj.update(counter_view=counter_content)
        response['message'] = '合同保存成功，正式签订合同须经公司领导签批！合同签批后，合同内容将固定'
    except Exception as e:
        response['status'] = False
        response['message'] = '合同保存失败：%s' % str(e)

    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -----------------------------决议声明合同ajax------------------------------#
@login_required
@authority
def result_state_ajax(request):  #
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_obj = models.Agrees.objects.get(id=post_data['agree_id'])
    LITRER_TYT_DIC = dict(models.LetterGuarantee.LETTER_TYP_LIST)
    '''AGREE_TYP_LIST = [
        (1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
        (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
        (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
        (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
    '''SURE_TYP_LIST = [
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
        (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''
    '''COUNTER_TYP_LIST = [
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'),
        (41, '其他权利质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售')]'''
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    if agree_obj.agree_state in [21, 31, 41, 61, 99]:
        response['status'] = False
        response['message'] = '合同状态为%s，无法生成决议及声明！' % agree_obj.agree_state
        result = json.dumps(response, ensure_ascii=False)
        return HttpResponse(result)
    agree_custom_obj = agree_obj.lending.summary.custom
    counter_agree_list = agree_obj.counter_agree.all()
    search_fields = ['counter_custome__counter',
                     'owner_custome__warrant__counter_warrant__counter',
                     'receive_custome__warrant__counter_warrant__counter',
                     'stock_owner_custome__warrant__counter_warrant__counter',
                     'draft_custome__warrant__counter_warrant__counter',
                     'vehicle_custome__warrant__counter_warrant__counter',
                     'chattel_custome__warrant__counter_warrant__counter',
                     'other_custome__warrant__counter_warrant__counter']
    q = Q()
    q.connector = 'OR'
    for field in search_fields:
        q.children.append(("%s__in" % field, counter_agree_list,))

    counter_custom_list = models.Customes.objects.filter(q).distinct()
    agree_custom_list = models.Customes.objects.filter(
        article_custom__lending_summary__agree_lending=agree_obj).distinct()
    custom_list = []  # 所有合同相关人列表
    for counter_custom in counter_custom_list:
        custom_list.append(counter_custom)
    for agree_custom in agree_custom_list:
        if not agree_custom in custom_list:
            custom_list.append(agree_custom)
    agree_amount_cn = convert(agree_obj.agree_amount)  # 合同金额大写
    agree_term = round(agree_obj.agree_term, 0)
    agree_term_str = credit_term_c(agree_term)  # 合同期限转换
    '''AGREE_TYP_LIST = [(1, '单笔'), (2, '最高额'), (3, '保函'), (7, '小贷'),
                      (41, '单笔(公证)'), (42, '最高额(公证)'), (47, '小贷(公证)')]'''
    agr_typ = agree_obj.agree_typ
    AGREE_TYP_D = models.Agrees.AGREE_TYP_D  # 担保公司合同类型
    AGREE_TYP_X = models.Agrees.AGREE_TYP_X  # 小贷公司合同类型
    AGREE_TYP_S = models.Agrees.AGREE_TYP_S  # 单笔合同类型
    AGREE_TYP_H = models.Agrees.AGREE_TYP_H  # 最高额合同类型
    if agr_typ in AGREE_TYP_H:
        hhh = '最高额'
    else:
        hhh = ''
    UN = '？？？？？？？？？？？'
    if agr_typ in AGREE_TYP_D:
        UN = UND
        DF = '反'
    elif agr_typ in AGREE_TYP_X:
        UN = UNX
        DF = ''
    try:
        with transaction.atomic():
            for counter_custom in custom_list:
                result = ''
                order = 0
                counter_warrant_count = models.Warrants.objects.filter(
                    counter_warrant__counter__in=counter_agree_list, warrant_typ__in=[1, 2, 5],
                    ownership_warrant__owner=counter_custom).exists()
                counter_receive_count = models.Receivable.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, receive_owner=counter_custom).exists()
                counter_target_count = models.Stockes.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, target=counter_custom.name).exists()
                counter_draft_count = models.Draft.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, draft_owner=counter_custom).exists()
                counter_vehicle_count = models.Vehicle.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, vehicle_owner=counter_custom).exists()
                counter_chattel_count = models.Chattel.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, chattel_owner=counter_custom).exists()
                counter_other_count = models.Others.objects.filter(
                    warrant__counter_warrant__counter__in=counter_agree_list, other_owner=counter_custom).exists()
                counter_asure_count = models.CountersAssure.objects.filter(
                    counter__in=counter_agree_list, custome=counter_custom).exists()
                counter_count = (counter_warrant_count + counter_receive_count + counter_target_count +
                                 counter_draft_count + counter_vehicle_count + counter_chattel_count +
                                 counter_other_count + counter_asure_count)  # 客户项下反担保总类数量
                if counter_count > 0:
                    oo = '1、'
                else:
                    oo = ''
                if counter_custom.genre == 1:  # 企业
                    '''WARRANT_TYP_LIST = [
                       (1, '房产'), (2, '房产包'), (5, '土地'), (6, '在建工程'), (11, '应收账款'),
                       (21, '股权'), (31, '票据'), (41, '车辆'), (51, '动产'), (55, '其他'), (99, '他权')]'''

                    '''DECISIONOR_LIST = [(11, '股东会'), (13, '合伙人会议'), (15, '举办者会议'), (21, '董事会'), 
                        (23, '管理委员会')]'''
                    '''RESULT_TYP_LIST = [(11, '股东会决议'), (13, '合伙人会议决议'), (15, '举办者会议决议'),
                        (21, '董事会决议'), (23, '管委会决议'),
                       (31, '声明书'), (41, '单身申明')]'''
                    decision = counter_custom.company_custome.decisionor
                    if decision == 11:  # (11, '股东会')
                        result_tp = 11  # (11, '股东会决议')
                        result = '<div class="split"><div class="tt" align="center"><strong>%s</strong></div>' % counter_custom.name
                        result += '<div class="split"><div class="ff" align="center"><strong>股东会决议</strong></div>'
                        result += '<p>会议时间：&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                        result += '<p>会议地点:  公司会议室</p>'
                        result += '<p>本次股东会会议已按《中华人民共和国公司法》及公司章程的有关规定' \
                                  '通知全体股东到会参加会议。本公司共有股东<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，' \
                                  '与会股东<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会股东所持股份占公司股份' \
                                  '的<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>，符合《公司法》和本公司章程规定的' \
                                  '程序和要求。经代表<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>表决权的股东表决通过，' \
                                  '做出如下决议：</p>'
                    elif decision == 13:  # (13, '合伙人会议')
                        result_tp = 13  # (13, '合伙人会议决议')
                        result = '<div class="split"><div class="tt" align="center"><strong>%s</strong></div>' % counter_custom.name
                        result += '<div class="split"><div class="ff" align="center"><strong>合伙人决议</strong></div>'
                        result += '<p>会议时间：&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                        result += '<p>会议地点:  公司会议室</p>'
                        result += '<p>本次合伙人会议已按《中华人民共和国合伙企业法》及合伙人协议的有关规定' \
                                  '通知全体合伙人到会参加会议。本公司共有合伙人<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>' \
                                  '名，与会合伙人<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会合伙人占企业合伙' \
                                  '人的<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>，符合《中华人民共和国合伙企业法》和本' \
                                  '合伙企业合伙人协议规定的程序和要求。经<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名' \
                                  '合伙人表决通过，做出如下决议：</p>'
                    elif decision == 15:  # (15, '举办者会议')
                        result_tp = 15  # (15, '举办者会议决议')
                        result = '<div class="split"><div class="tt" align="center"><strong>%s</strong></div>' % counter_custom.name
                        result += '<div class="split"><div class="ff" align="center"><strong>举办者会议决议</strong></div>'
                        result += '<p>会议时间：&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                        result += '<p>会议地点:  公司会议室</p>'
                        result += '<p>本次举办者会议已按本医院章程及相关文件规定通知全体举办者到会参加会议。' \
                                  '本医院共有举办者<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会举办者' \
                                  '<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会举办者所持举办者权益占医院举办' \
                                  '者权益的<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>，符合本医院章程规定的程序和要求。' \
                                  '经代表<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>表决权的举办者表决通过，做出如下决议：</p>'
                    elif decision == 21:  # (21, '董事会')
                        result_tp = 21  # (21, '董事会决议')
                        result = '<div class="split"><div class="tt" align="center"><strong>%s</strong></div>' % counter_custom.name
                        result += '<div class="split"><div class="ff" align="center"><strong>董事会决议</strong></div>'
                        result += '<p>会议时间：&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                        result += '<p>会议地点:  公司会议室</p>'
                        result += '<p>本次董事会会议已按《中华人民共和国公司法》及公司章程的有关规定通知全体董事到会参' \
                                  '加会议。本公司共有董事<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会董' \
                                  '事<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，占公司董事的' \
                                  '<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>，符合《公司法》和本公司章程规定' \
                                  '的程序和要求。经<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名董事表决通过，做出如下决议：</p>'
                    elif decision == 23:  # (23, '管理委员会')
                        result_tp = 23  # (23, '管委会决议')
                        result = '<div class="split"><div class="tt" align="center"><strong>%s</strong></div>' % counter_custom.name
                        result += '<div class="split"><div class="ff" align="center"><strong>管委会决议</strong></div>'
                        result += '<p>会议时间：&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                        result += '<p>会议地点:  公司会议室</p>'
                        result += '<p>本次管委会会议已按《民办非企业单位登记管理暂行条例》及本企业《章程》的有关规定' \
                                  '通知全体管委会委员到会参加会议。本公司共有管委会委员' \
                                  '<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会委员' \
                                  '<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名，与会委员占全体委员的' \
                                  '<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>，符合《民办非企业单位登记管理暂行条例》和本' \
                                  '企业《章程》规定的程序和要求。经<u>&nbsp&nbsp&nbsp&nbsp&nbsp&nbsp</u>名' \
                                  '委员表决通过，做出如下决议：</p>'
                    if counter_custom == agree_custom_obj:  # （反）担保人与委托人相同
                        '''AGREE_TYP_LIST = [
                            (1, 'D-单笔'), (2, 'D-最高额'), (4, 'D-委贷'),
                            (21, 'D-分离式保函'), (22, 'D-公司保函'), (23, 'D-银行保函'),
                            (41, 'D-单笔(公证)'), (42, 'D-最高额(公证)'),
                            (51, 'X-小贷单笔'), (52, 'X-小贷最高额'), ]'''
                        if agr_typ in AGREE_TYP_D:
                            if agr_typ in [1, 41]:  # (1, 'D-单笔'), (41, 'D-单笔(公证)'),
                                result += '<p>  1、同意向%s申请人民币%s%s期贷款，用以补充流动资金。</p>' % (
                                    agree_obj.branch.name, agree_amount_cn, agree_term_str)
                                result += '<p>  2、同意委托%s为该贷款向贷款方提供担保。</p>' % UN
                                order = 2
                            elif agr_typ in [2, 42]:  # (2, 'D-最高额'),  (42, 'D-最高额(公证)'),
                                result += '<p>  1、同意向%s申请最高限额为人民币%s%s期的银行授信（包括借款或银行' \
                                          '承兑汇票、保函等），用以补充流动资金。</p>' % (
                                              agree_obj.branch.name, agree_amount_cn, agree_term_str)
                                result += '<p>  2、同意委托%s为该授信向贷款方提供担保。</p>' % UN
                                order = 2
                            elif agr_typ in [21, ]:  # (21, 'D-分离式保函'),
                                result += '<p>  %s同意委托%s向%s申请开立最高限额为人民币%s的保函。</p>' % (
                                    oo, UN, agree_obj.branch.name, agree_amount_cn)
                                order = 1
                            elif agr_typ in [22, ]:  # (22, 'D-公司保函'),
                                result += '<p>  %s同意向%s申请开立人民币%s%s期的%s。</p>' % (
                                    oo, UN, agree_amount_cn, agree_term_str,
                                    LITRER_TYT_DIC[agree_obj.guarantee_agree.letter_typ])
                                order = 1
                        elif agr_typ in AGREE_TYP_X:
                            if agr_typ in [51, ]:  # 单笔
                                result += '<p>  1、同意向%s申请人民币%s%s期的贷款。</p>' % (
                                    UN, agree_amount_cn, agree_term_str)
                                order = 1
                            elif agr_typ in [52, ]:  # 最高额
                                result += '<p>  1、同意向%s申请人民币%s%s期的最高额授信。</p>' % (
                                    UN, agree_amount_cn, agree_term_str)
                                order = 1
                    else:
                        order = 0
                    if counter_count + order > 1:  # 判断决议条目是否是一条以上
                        order += 1
                        crder_str = '%s、' % order
                    elif agr_typ in [41, 42, 51, 52]:  # 公证版本
                        order += 1
                        crder_str = '%s、' % order
                    else:
                        crder_str = ''  # 如只有一个决议条目，则无编号
                    qqq = ''
                    if crder_str == '' or crder_str == '1、':
                        if agr_typ in AGREE_TYP_D:  # 担保公司类合同
                            if agr_typ in [1, 41]:  # 单笔
                                qqq = '为%s在%s申请的人民币%s%s期贷款' % (
                                    agree_custom_obj.name, agree_obj.branch.name, agree_amount_cn, agree_term_str)
                            elif agr_typ in [2, 42]:  # 最高额
                                qqq = '为%s在%s申请的最高限额为人民币%s%s期银行授信' % (
                                    agree_custom_obj.name, agree_obj.branch.name, agree_amount_cn, agree_term_str)
                            elif agr_typ in [22, ]:  # 公司保函
                                qqq = '为%s在%s申请开立的人民币%s%s期%s业务' % (
                                    agree_custom_obj.name, agree_obj.branch.name, agree_amount_cn, agree_term_str,
                                    LITRER_TYT_DIC[agree_obj.guarantee_agree.letter_typ])
                        if agr_typ in AGREE_TYP_X:  # 小贷公司类合同
                            if agr_typ in [51, ]:  # 单笔
                                qqq += '为%s在%s申请的人民币%s%s期的贷款' % (
                                    agree_custom_obj.name, agree_obj.branch.name, agree_amount_cn, agree_term_str,)
                                order = 1
                            elif agr_typ in [52, ]:  # 最高额
                                qqq += '为%s在%s申请的人民币%s%s期的最高额授信' % (
                                    agree_custom_obj.name, agree_obj.branch.name, agree_amount_cn, agree_term_str,)
                                order = 1

                    # 保证反担保
                    counter_asure_list = models.CountersAssure.objects.filter(
                        counter__in=counter_agree_list, custome=counter_custom)
                    if counter_asure_list:
                        result += '<p>%s同意%s，向%s提供连带责任保证%s担保。</p>' % (crder_str, qqq, UN, DF)
                        order += 1
                        crder_str = '%s、' % order
                    # (1, '房产'), (2, '房产包')
                    counter_house_list = models.Warrants.objects.filter(
                        counter_warrant__counter__in=counter_agree_list, warrant_typ__in=[1, 2],
                        ownership_warrant__owner=counter_custom)
                    if counter_house_list:
                        result += '<p>%s同意%s以企业名下房产向%s提供%s抵押%s担保，签订%s抵押%s担保合同，并办理%s抵押登' \
                                  '记。房产的详细信息如下：</p>' % (crder_str, qqq, UN, hhh, DF, hhh, DF, hhh)
                        result += '<table>' \
                                  '<tr>' \
                                  '<td align="center">所有权人</td> ' \
                                  '<td align="center">处所</td> ' \
                                  '<td align="center">面积(㎡)</td> ' \
                                  '<td align="center">产权证编号</td> ' \
                                  '</tr>'
                        for warrant_house in counter_house_list:
                            owership_list = warrant_house.ownership_warrant.all()
                            owership_list_count = owership_list.count()
                            owership_name = ''
                            owership_num = ''
                            owership_list_order = 0
                            for owership in owership_list:
                                owership_name += '%s' % owership.owner.name
                                owership_num += '%s' % owership.ownership_num
                                owership_list_order += 1
                                if owership_list_order < owership_list_count:
                                    owership_name += '、'
                                    owership_num += '、'
                            if warrant_house.warrant_typ == 1:
                                house = warrant_house.house_warrant
                                house_locate = house.house_locate
                                house_app = house.house_app
                                house_area = house.house_area
                                result += '<tr>' \
                                          '<td>%s</td> ' \
                                          '<td>%s</td> ' \
                                          '<td align="right">%s</td> ' \
                                          '<td>%s</td> ' \
                                          '</tr>' % (
                                              owership_name, house_locate, house_area, owership_num)
                            else:
                                housebag_list = warrant_house.housebag_warrant.all()
                                housebag_count = housebag_list.count()
                                housebag_num = 1
                                for housebag in housebag_list:
                                    housebag_locate = housebag.housebag_locate
                                    housebag_app = housebag.housebag_app
                                    housebag_area = housebag.housebag_area
                                    if housebag_num == 1:
                                        result += '<tr>' \
                                                  '<td rowspan="%s">%s</td> ' \
                                                  '<td>%s</td> ' \
                                                  '<td align="right">%s</td> ' \
                                                  '<td rowspan="%s">%s</td> ' \
                                                  '</tr>' % (
                                                      housebag_count, owership_name, housebag_locate,
                                                      housebag_area, housebag_count, owership_num)
                                        housebag_num += 1
                                    else:
                                        result += '<tr>' \
                                                  '<td>%s</td> ' \
                                                  '<td align="right">%s</td> ' \
                                                  '</tr>' % (
                                                      housebag_locate, housebag_area)
                        result += '</table>'
                        order += 1
                        crder_str = '%s、' % order
                    # (5, '土地')
                    counter_ground_list = models.Warrants.objects.filter(
                        counter_warrant__counter__in=counter_agree_list, warrant_typ=5,
                        ownership_warrant__owner=counter_custom)
                    if counter_ground_list:
                        result += '<p>%s同意%s以企业名下国有土地使用权及地上建筑物向%s提供%s抵押%s担保，' \
                                  '签订%s抵押%s担保合同，并办理%s抵押登记。国有土地使用权' \
                                  '的详细信息如下：</p>' % (crder_str, qqq, UN, hhh, DF, hhh, DF, hhh)
                        result += '<table>' \
                                  '<tr>' \
                                  '<td align="center">所有权人</td> ' \
                                  '<td align="center">座落</td> ' \
                                  '<td align="center">面积(㎡)</td> ' \
                                  '<td align="center">产权证编号</td> ' \
                                  '</tr>'
                        for warrant_ground in counter_ground_list:
                            owership_list = warrant_ground.ownership_warrant.all()
                            owership_list_count = owership_list.count()
                            owership_name = ''
                            owership_num = ''
                            owership_list_order = 0
                            for owership in owership_list:
                                owership_name += '%s' % owership.owner.name
                                owership_num += '%s' % owership.ownership_num
                                owership_list_order += 1
                                if owership_list_order < owership_list_count:
                                    owership_name += '、'
                                    owership_num += '、'
                            ground = warrant_ground.ground_warrant
                            ground_locate = ground.ground_locate
                            ground_app = ground.ground_app
                            ground_area = ground.ground_area

                            result += '<tr>' \
                                      '<td>%s</td> ' \
                                      '<td>%s</td> ' \
                                      '<td align="right">%s</td> ' \
                                      '<td>%s</td> ' \
                                      '</tr>' % (
                                          owership_name, ground_locate, ground_area, owership_num)
                        result += '</table>'
                        order += 1
                        crder_str = '%s、' % order
                    #  (11, '应收账款')
                    counter_receive_list = models.Receivable.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, receive_owner=counter_custom)
                    if counter_receive_list:
                        result += '<p>%s同意以' % crder_str
                        receive_count = counter_receive_list.count()
                        receive_num = 0
                        for receive in counter_receive_list:
                            receive_detail = receive.receivable_detail
                            result += '%s' % (receive_detail)
                            receive_num += 1
                            if receive_num < receive_count:
                                result += '、'
                        result += '%s向%s提供%s质押%s担保，签订%s质押%s担保合同，并办理%s质押' \
                                  '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    # (21, '股权')
                    counter_target_list = models.Stockes.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, target=counter_custom.name)
                    if counter_target_list:
                        result += '<p>%s同意企业股东' % crder_str
                        target_count = counter_target_list.count()
                        target_num = 0
                        for target in counter_target_list:
                            target_owner = target.stock_owner
                            target_ratio = target.ratio
                            result += '%s以其持有本企业的%s' % (target_owner, target_ratio)
                            result += '%股权'
                            target_num += 1
                            if target_num < target_count:
                                result += '、'
                        result += '%s向%s提供%s质押%s担保，签订%s质押%s担保合同，并办理%s质押' \
                                  '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    # 持有(21, '股权')
                    counter_stock_list = models.Stockes.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, stock_owner=counter_custom)
                    if counter_stock_list:
                        result += '<p>%s同意以本企业所持有的' % crder_str
                        stock_count = counter_target_list.count()
                        stock_num = 0
                        for stock in counter_stock_list:
                            target = stock.target
                            ratio = stock.ratio
                            result += '%s%s' % (target, ratio)
                            result += '%股权'
                            stock_num += 1
                            if stock_num < stock_count:
                                result += '、'
                        result += '%s向%s提供%s质押%s担保，签订%s质押%s担保合同，并办理%s质押' \
                                  '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    # (31, '票据')
                    counter_draft_list = models.Draft.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, draft_owner=counter_custom)
                    if counter_draft_list:
                        result += '<p>%s同意以本企业所有的' % crder_str
                        draft_count = counter_draft_list.count()
                        draft_num = 0
                        for draft in counter_draft_list:
                            if draft_num == 0:
                                draft_detail = draft.draft_detail
                                result += '%s' % draft_detail
                                draft_num += 1
                                if draft_num < draft_count:
                                    result += '、'
                        result += '%s向%s提供%s质押%s担保，签订%s质押%s担保合同，并办理%s质押' \
                                  '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    # (41, '车辆')
                    counter_vehicle_list = models.Vehicle.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, vehicle_owner=counter_custom)
                    if counter_vehicle_list:
                        result += '<p>%s同意%s以企业名下车辆向%s提供%s抵押%s担保，签订%s抵押%s担保合同，' \
                                  '并办理%s抵押登记。车辆的详细信息' \
                                  '如下：</p>' % (crder_str, qqq, UN, hhh, DF, hhh, DF, hhh)
                        result += '<table>' \
                                  '<tr>' \
                                  '<td align="center">所有权人</td> ' \
                                  '<td align="center">车架号</td> ' \
                                  '<td align="center">车牌号</td> ' \
                                  '<td align="center">品牌及型号</td> ' \
                                  '<td align="center">备注</td> ' \
                                  '</tr>'
                        vehicle_count = counter_vehicle_list.count()
                        vehicle_num = 0
                        for vehicle in counter_vehicle_list:
                            vehicle_owner = vehicle.vehicle_owner
                            frame_num = vehicle.frame_num
                            plate_num = vehicle.plate_num
                            vehicle_brand = vehicle.vehicle_brand
                            vehicle_remark = vehicle.vehicle_remark
                            result += '<tr>' \
                                      '<td>%s</td> ' \
                                      '<td>%s</td> ' \
                                      '<td>%s</td> ' \
                                      '<td>%s</td> ' \
                                      '<td>%s</td> ' \
                                      '</tr>' % (vehicle_owner, frame_num, plate_num, vehicle_brand, vehicle_remark)
                        result += '</table>'
                        order += 1
                        crder_str = '%s、' % order
                    # (51, '动产')
                    counter_chattel_list = models.Chattel.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, chattel_owner=counter_custom)
                    if counter_chattel_list:
                        result += '<p>%s同意以本企业所有的' % crder_str
                        chattel_count = counter_chattel_list.count()
                        chattel_num = 0
                        for chattel in counter_chattel_list:
                            if chattel_num == 0:
                                chattel_detail = chattel.chattel_detail
                                result += '%s' % chattel_detail
                                chattel_num += 1
                                if chattel_num < chattel_count:
                                    result += '、'
                        result += '%s向成都%s提供%s抵押%s担保，签订%s抵押%s担保合同，并办理%s抵押' \
                                  '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    # (55, '其他')
                    counter_other_list = models.Others.objects.filter(
                        warrant__counter_warrant__counter__in=counter_agree_list, other_owner=counter_custom)
                    if counter_other_list:
                        result += '<p>%s同意以本公司所有的' % crder_str
                        other_count = counter_other_list.count()
                        other_num = 0
                        for other in counter_other_list:
                            if other_num == 0:
                                other_detail = other.other_detail
                                result += '%s' % other_detail
                                other_num += 1
                                if other_num < other_count:
                                    result += '、'
                        if counter_other_list.first().other_typ == 21:
                            result += '提供%s质押%s担保，签订%s质押%s担保合同，将车辆合格证存放在%s，并' \
                                      '按照质押%s担保合同及其他相关约定进行更换。</p >' % (
                                          hhh, DF, hhh, DF, UN, DF,)
                        else:
                            result += '%s向%s提供%s质押%s担保，签订%s质押%s担保合同，并办理%s质押' \
                                      '登记。</p>' % (qqq, UN, hhh, DF, hhh, DF, hhh)
                        order += 1
                        crder_str = '%s、' % order
                    if agr_typ in [41, 42, 51, 52]:
                        result += '<p>%s同意对上述事项所涉及的相关合同及协议进行强制执行公证。' % crder_str
                    if decision in [11, ]:
                        result += '<p><strong>本公司及参会股东对本次股东会决议的程序的合法性以及股东签名的真实性负责。</strong></p>'
                        result += '<p>参会股东（或代表）签字：</p>'
                    elif decision in [13, ]:
                        result += '<p><strong>本合伙企业及参会合伙人对本次合伙人会议决议的程序的合法性以及合伙人签名的真实性负责。</strong></p>'
                        result += '<p>参会合伙人（或代表）签字：</p>'
                    elif decision in [15, ]:
                        result += '<p><strong>本企业及参会举办者对本次举办者会议决议的程序的合法性以及举办者签名的真实性负责。</strong></p>'
                        result += '<p>参会举办者（或代表）签字：</p>'
                    elif decision in [21, ]:
                        result += '<p><strong>本公司及参会董事对本次董事会决议的程序的合法性以及董事签名的真实性负责。</strong></p>'
                        result += '<p>参会董事（或代表）签字：</p>'
                    elif decision in [23, ]:
                        result += '<p><strong>本企业及参会管委会委员对本次管委会决议的程序的合法性以及委员签名的真实性负责。</strong></p>'
                        result += '<p>参会委员（或代表）签字：</p>'

                    if decision in [11, 13, 15]:
                        shareholder_list = counter_custom.company_custome.shareholder_custom_c.all()
                        shareholder_count = shareholder_list.count()
                        shareholder_num = 0
                        result += '<p>'
                        if decision == 11:
                            signature = '<table><tr><th width="200pt">股东姓名（名称）</th><th>签字（盖章）</th><th>联系方式</th></tr>'
                        elif decision == 13:
                            signature = '<table><tr><th width="200pt">合伙人姓名（名称）</th><th>签字（盖章）</th><th>联系方式</th></tr>'
                        elif decision == 15:
                            signature = '<table><tr><th width="200pt">举办者姓名（名称）</th><th>签字（盖章）</th><th>联系方式</th></tr>'
                        for shareholder in shareholder_list:
                            result += '%s' % shareholder.shareholder_name
                            signature += '<tr class="trs"><td align="center">%s</td><td></td><td></td></tr>' % shareholder.shareholder_name
                            shareholder_num += 1
                            if shareholder_num < shareholder_count:
                                result += '、'
                        signature += '</table>'
                        result += '</p></div>'
                        if decision == 11:
                            result += '<div class="tt" align="center">%s股东</div>' \
                                      '<div class="ts" align="center">签字样本</div>' % counter_custom.name
                        elif decision == 13:
                            result += '<div class="tt" align="center">%s合伙人</div>' \
                                      '<div class="ts" align="center">签字样本</div>' % counter_custom.name
                        elif decision == 15:
                            result += '<div class="tt" align="center">%s举办者</div>' \
                                      '<div class="ts" align="center">签字样本</div>' % counter_custom.name
                        result += signature
                    elif decision in [21, 23]:  #
                        trustee_list = counter_custom.company_custome.trustee_custom_c.all()
                        trustee_count = trustee_list.count()
                        trustee_num = 0
                        result += '<p>'
                        if decision == 21:
                            signature = '<table><tr><th width="200pt">董事姓名</th><th>签字</th><th>联系方式</th></tr>'
                        elif decision == 23:
                            signature = '<table><tr><th width="200pt">委员姓名</th><th>签字</th><th>联系方式</th></tr>'
                        for trustee in trustee_list:
                            result += '%s' % trustee.trustee_name
                            signature += '<tr class="trs"><td align="center">%s</td><td></td><td></td></tr>' % trustee.trustee_name
                            trustee_num += 1
                            if trustee_num < trustee_count:
                                result += '、'
                        signature += '</table>'
                        result += '</p></div>'
                        if decision == 21:
                            result += '<div class="tt" align="center">%s董事</div>' \
                                      '<div class="ts" align="center">签字样本</div>' % counter_custom.name
                        elif decision == 23:
                            result += '<div class="tt" align="center">%s管委会委员</div>' \
                                      '<div class="ts" align="center">签字样本</div>' % counter_custom.name
                        result += signature
                    default = {'agree': agree_obj, 'custom': counter_custom, 'result_typ': result_tp,
                               'result_detail': result, 'resultor': request.user}
                    result_obj, created = models.ResultState.objects.update_or_create(
                        agree=agree_obj, custom=counter_custom, result_typ=result_tp, defaults=default)
                else:
                    spouse = counter_custom.person_custome.spouses
                    if not spouse:
                        marital_s_list = models.CustomesP.MARITAL_STATUS  # 婚姻状况
                        marital_s_dic = {}
                        for marital_s in marital_s_list:
                            marital_s_dic[marital_s[0]] = marital_s[1]
                        '''MARITAL_STATUS = ((1, '未婚'), (11, '已婚'), (21, '离婚'), (31, '离婚'), (41, '丧偶'),)'''
                        marital_status = counter_custom.person_custome.marital_status
                        if not marital_status == 11:
                            result += '<div class="tt" align="center"><strong>个人婚姻状况及财产申明</strong></div>'
                            result += '<p>姓名：%s</p>' % counter_custom.name
                            result += '<p>居民身份证编号： %s</p>' % counter_custom.person_custome.license_num
                            result += '<p>家庭详细住址：%s</p>' % counter_custom.contact_addr
                            result += '<p>现本人申明：</p><p>1、截止到<u>&nbsp&nbsp&nbsp</u>年<u>&nbsp&nbsp</u>月' \
                                      '<u>&nbsp&nbsp</u>日，本人婚姻状况为：<u>%s</u>。' \
                                      '</p>' % marital_s_dic[marital_status]
                            result += '<p>2、本人名下所有房屋、银行存款等资产均系本人单独所有，无其他共有人。</p>'
                            result += '<p><strong>特此申明！</strong></p><br>'
                            result += '<p class="sm">申明人：</p><br>'
                            result += '<p class="sm">&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                            default = {'agree': agree_obj, 'custom': counter_custom, 'result_typ': 41,
                                       'result_detail': result, 'resultor': request.user}
                            result_obj, created = models.ResultState.objects.update_or_create(
                                agree=agree_obj, custom=counter_custom, result_typ=41, defaults=default)
                    else:
                        ''''''
                        counter_house_list = models.Warrants.objects.filter(
                            counter_warrant__counter__in=counter_agree_list, warrant_typ__in=[1, 2],
                            ownership_warrant__owner=counter_custom)
                        single_house_list = counter_house_list.exclude(ownership_warrant__owner=spouse)
                        owership_name = ''
                        owership_w = ''
                        if single_house_list:
                            owership_list = single_house_list.first().ownership_warrant.all()
                            owership_list_count = owership_list.count()
                            owership_list_order = 0
                            for owership in owership_list:
                                owership_name += '%s' % owership.owner.name
                                owership_list_order += 1
                                if owership_list_order < owership_list_count:
                                    owership_name += '、'
                            if owership_list_count < 2:
                                owership_w += '单独所有'
                            else:
                                owership_w += '所有'
                        ''''''
                        result += '<div class="tt" align="center"><strong>声明书</strong></div>'
                        result += '<p>声明人：%s，公民身份号码：%s</p>' % (
                            spouse.name, spouse.person_custome.license_num)
                        result += '<p>我声明人<strong><u>%s</u></strong>与<strong><u>%s</u></strong>是夫妻关系，' \
                                  '下表所列房屋系<strong><u>%s</u></strong>%s，无其他共有人，' \
                                  '现<strong><u>%s</u></strong>以下列房' \
                                  '屋作抵押，我无异议。若到期债务人不能清偿债务须处分下列房屋时，我' \
                                  '无条件放弃对该物业的任何权益主张。</p>' % (
                                      spouse.name, counter_custom.name,
                                      owership_name, owership_w, counter_custom.name)

                        # (1, '房产'), (2, '房产包')
                        counter_house_list = models.Warrants.objects.filter(
                            counter_warrant__counter__in=counter_agree_list, warrant_typ__in=[1, 2],
                            ownership_warrant__owner=counter_custom)
                        single_house_list = counter_house_list.exclude(ownership_warrant__owner=spouse)
                        if single_house_list:
                            result += '<table>' \
                                      '<tr>' \
                                      '<td align="center">所有权人</td> ' \
                                      '<td align="center">处所</td> ' \
                                      '<td align="center">面积(平方米)</td> ' \
                                      '<td align="center">产权证编号</td> ' \
                                      '</tr>'
                            for warrant_house in single_house_list:
                                owership_list = warrant_house.ownership_warrant.all()
                                owership_list_count = owership_list.count()
                                owership_name = ''
                                owership_num = ''
                                owership_list_order = 0
                                for owership in owership_list:
                                    owership_name += '%s' % owership.owner.name
                                    owership_num += '%s' % owership.ownership_num
                                    owership_list_order += 1
                                    if owership_list_order < owership_list_count:
                                        owership_name += '、'
                                        owership_num += '、'
                                if warrant_house.warrant_typ == 1:
                                    house = warrant_house.house_warrant
                                    house_locate = house.house_locate
                                    house_app = house.house_app
                                    house_area = house.house_area
                                    result += '<tr>' \
                                              '<td>%s</td> ' \
                                              '<td>%s</td> ' \
                                              '<td align="right">%s</td> ' \
                                              '<td>%s</td> ' \
                                              '</tr>' % (
                                                  owership_name, house_locate, house_area, owership_num)
                                else:
                                    housebag_list = warrant_house.housebag_warrant.all()
                                    housebag_count = housebag_list.count()
                                    housebag_num = 1
                                    for housebag in housebag_list:
                                        housebag_locate = housebag.housebag_locate
                                        housebag_app = housebag.housebag_app
                                        housebag_area = housebag.housebag_area
                                        if housebag_num == 1:
                                            result += '<tr>' \
                                                      '<td rowspan="%s">%s</td> ' \
                                                      '<td>%s</td> ' \
                                                      '<td align="right">%s</td> ' \
                                                      '<td rowspan="%s">%s</td> ' \
                                                      '</tr>' % (
                                                          housebag_count, counter_custom.name, housebag_locate,
                                                          housebag_area, housebag_count, owership_num)
                                            housebag_num += 1
                                        else:
                                            result += '<tr>' \
                                                      '<td>%s</td> ' \
                                                      '<td align="right">%s</td> ' \
                                                      '</tr>' % (
                                                          housebag_locate, housebag_area)
                            result += '</table>'
                            result += '<p><strong>我保证我的上述声明真实有效，如有虚假，所产生的法律责任' \
                                      '均由我本人承担。</strong></p><br>'
                            result += '<p class="sm">声明人：</p><br>'
                            result += '<p class="sm">&nbsp&nbsp&nbsp年&nbsp&nbsp月&nbsp&nbsp日</p>'
                            default = {'agree': agree_obj, 'custom': spouse, 'result_typ': 31,
                                       'result_detail': result, 'resultor': request.user}
                            result_obj, created = models.ResultState.objects.update_or_create(
                                agree=agree_obj, custom=spouse, result_typ=31, defaults=default)
        response['message'] = '决议及声明生成成功！'
    except Exception as e:
        response['status'] = False
        response['message'] = '决议及声明生成失败：%s' % str(e)
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -------------------------手动添加声明ajax-------------------------#
@login_required
@authority
def promise_add_ajax(request):
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_obj = models.Agrees.objects.get(id=post_data['agree_id'])

    form_promise_add = forms.PromiseAddForm(post_data)

    if form_promise_add.is_valid():
        counter_clean = form_promise_add.cleaned_data
        custom = counter_clean['custom']
        result_typ = counter_clean['result_typ']
        try:
            with transaction.atomic():
                default = {'agree': agree_obj, 'custom': custom,
                           'result_typ': result_typ,
                           'result_detail': counter_clean['result_typ'],
                           'resultor': request.user}
                result_obj, created = models.ResultState.objects.update_or_create(
                    agree=agree_obj, custom=custom, result_typ=result_typ, defaults=default)
            response['message'] = '成功创建声明/承诺！'
        except Exception as e:
            response['status'] = False
            response['message'] = '声明/承诺创建失败：%s' % str(e)
    else:
        response['status'] = False
        response['message'] = '表单信息有误！！！'
        response['forme'] = form_promise_add.errors
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)


# -------------------------删除决议ajax-------------------------#
@login_required
@authority
def result_del_ajax(request):  # 删除反担保合同ajax
    response = {'status': True, 'message': None, 'forme': None, }
    post_data_str = request.POST.get('postDataStr')
    post_data = json.loads(post_data_str)
    agree_obj = models.Agrees.objects.get(id=post_data['agree_id'])
    result_obj = models.ResultState.objects.get(id=post_data['result_id'])
    '''AGREE_STATE_LIST = [(11, '待签批'), (21, '已签批'), (31, '未落实'),
                        (41, '已落实'), (51, '待变更'), (61, '已解保'), (99, '已注销')]'''
    # if True:
    if agree_obj.agree_state in [11, 51]:
        try:
            with transaction.atomic():
                result_obj.delete()  # 删除保证反担保合同
            response['message'] = '决议及声明删除成功！'
        except Exception as e:
            response['status'] = False
            response['message'] = '决议及声明删除失败:%s！' % str(e)
    else:
        response['status'] = False
        response['message'] = '委托担保合同状态为%s，无法删除相关决议及声明！' % agree_obj.agree_state
    result = json.dumps(response, ensure_ascii=False)
    return HttpResponse(result)
