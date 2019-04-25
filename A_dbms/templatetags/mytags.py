from django import template
from django.utils.safestring import mark_safe
from .. import models
from django.db.models import Q, F

register = template.Library()


def num_to_cn(lending_or):
    if lending_or == 1:
        lending_orz = '一'
    elif lending_or == 2:
        lending_orz = '二'
    elif lending_or == 3:
        lending_orz = '三'
    elif lending_or == 4:
        lending_orz = '四'
    else:
        lending_orz = lending_or
    return lending_orz


def guarantee_house(lending, sure_typ):
    result = ''
    warrant_h_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)
    result += '<tr><td>' \
              '<table style="width: 100%" border="0" align="center">' \
              '<tr> ' \
              '<td>所有权人</td>' \
              '<td>房产坐落</td>' \
              '<td>用途</td>' \
              '<td>建筑面积(㎡)</td></tr>'
    for warrant_h in warrant_h_list:
        owner_list = warrant_h.ownership_warrant.all()
        owners = ''
        owner_c = owner_list.count()
        owner_c_c = 1
        for owner in owner_list:
            owners += '%s' % owner.owner.name
            if owner_c == owner_c_c:
                pass
            else:
                owners += '、'
            owner_c_c += 1
        HOUSE_APP_LIST = models.Houses.HOUSE_APP_LIST
        # ground_app_dic = {}
        for house_app in HOUSE_APP_LIST:
            # ground_app_dic[ground_app[0]] = ground_app[1]
            if warrant_h.house_warrant.house_app == house_app[0]:
                house_app_str = house_app[1]

        result += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            owners, warrant_h.house_warrant.house_locate, house_app_str,
            warrant_h.house_warrant.house_area)
    result += '</table></td></tr>'
    return result


def guarantee_ground(lending, sure_typ):
    result = ''
    warrant_g_list = models.Warrants.objects.filter(
        lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)
    result += '<tr><td>' \
              '<table style="width: 100%" border="0" align="center">' \
              '<tr> ' \
              '<td>所有权人</td>' \
              '<td>土地座落</td>' \
              '<td>用途</td>' \
              '<td>面积(㎡)</td></tr>'
    for warrant_g in warrant_g_list:
        owner_list = warrant_g.ownership_warrant.all()
        owners = ''
        owner_c = owner_list.count()
        owner_c_c = 1
        for owner in owner_list:
            owners += '%s' % owner.owner.name
            if owner_c == owner_c_c:
                pass
            else:
                owners += '、'
            owner_c_c += 1
        GROUND_APP_LIST = models.Grounds.GROUND_APP_LIST
        # ground_app_dic = {}
        for ground_app in GROUND_APP_LIST:
            # ground_app_dic[ground_app[0]] = ground_app[1]
            if warrant_g.ground_warrant.ground_app == ground_app[0]:
                ground_app_str = ground_app[1]
        result += '<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>' % (
            owners, warrant_g.ground_warrant.ground_locate, ground_app_str,
            warrant_g.ground_warrant.ground_area)
        result += '</table></td></tr>'
    return result


@register.simple_tag
def article_summary(article_id):
    article_obj = models.Articles.objects.get(id=article_id)
    lending_list = article_obj.lending_summary.all()  # 放款次序列表
    result = '<tr><td>'
    lending_or = 1
    for lending in lending_list:
        lending_orz = num_to_cn(lending_or)
        lending_list_count = lending_list.count()
        if lending_list_count > 1:
            result += '<tr><td>（%s）第%s次发放%s万元，并落实以下反担保措施</td></tr>' % (
                lending_orz, lending_orz, str(lending.order_amount / 10000).rstrip('0').rstrip('.'))
        lending_or += 1
        sure_list = lending.sure_lending.all()
        sure_or = 1
        sure_count = sure_list.count()
        for sure in sure_list:
            sure_typ = sure.sure_typ
            ''' SURE_TYP_LIST = (
                    (1, '企业保证'), (2, '个人保证'),
                    (11, '房产抵押'), (12, '土地抵押'), (13, '动产抵押'), (14, '在建工程抵押'), (15, '车辆抵押'),
                    (21, '房产顺位'), (22, '土地顺位'), (23, '在建工程顺位'), (24, '动产顺位'),
                    (31, '应收质押'), (32, '股权质押'), (33, '票据质押'), (34, '动产质押'), (39, '其他权利质押'),
                    (42, '房产监管'), (43, '土地监管'), (44, '票据监管'), (47, '动产监管'), (49, '其他监管'),
                    (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))'''
            if sure_typ == 1:  # 企业保证
                custom_c_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=1)  # 企业
                if sure_count > 1:
                    result += '<tr><td>（%s）企业保证：' % sure_or
                else:
                    result += '<tr><td>企业保证：'
                custom_c_count = custom_c_list.count()
                custom_c_c = 1
                for custom_c in custom_c_list:
                    result += '%s' % custom_c.name
                    if custom_c_count == custom_c_c:
                        pass
                    else:
                        result += '、'
                    custom_c_c += 1
                result += '提供企业连带责任保证反担保。</td></tr>'
                sure_or += 1
            elif sure_typ == 2:  # 个人保证
                custom_p_list = models.Customes.objects.filter(lending_custom__sure__lending=lending, genre=2)  # 个人
                if sure_count > 1:
                    result += '<tr><td>（%s）个人保证：' % sure_or
                else:
                    result += '<tr><td>个人保证：'
                custom_p_count = custom_p_list.count()
                custom_p_c = 1
                for custom_p in custom_p_list:
                    result += '%s' % custom_p.name
                    if custom_p.person_custome.spouses:
                        result += '、%s夫妇' % custom_p.person_custome.spouses
                    if custom_p_count == custom_p_c:
                        pass
                    else:
                        result += '，'
                    custom_p_c += 1
                result += '提供个人连带责任保证反担保。</td></tr>'
                sure_or += 1
            elif sure_typ == 11:  # 房产抵押
                if sure_count > 1:
                    result += '<tr><td>（%s）房产抵押：' \
                              '以下房产抵押给我公司，签订抵押反担保合同并办理抵押登记</td></tr>' % sure_or
                else:
                    result += '<tr><td>房产抵押：' \
                              '以下房产抵押给我公司，签订抵押反担保合同并办理抵押登记</td></tr>'
                result += guarantee_house(lending, sure_typ)
                sure_or += 1
            elif sure_typ == 12:  # 土地抵押
                warrant_g_12_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 抵押土地
                result += '<tr><td>' \
                          '（%s）土地抵押：以下国有土地使用权抵押给我公司，签订抵押反担保合同并办理抵押登记' \
                          '</td></tr>' % sure_or
                result += guarantee_ground(lending, sure_typ)
                sure_or += 1
            elif sure_typ == 13:  # 动产抵押
                warrant_c_13_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 抵押动产
                result += '<tr><td>（%s）动产抵押：' % sure_or
                for warrant_c in warrant_c_13_list:
                    result += '%s将其%s' % (warrant_c.chattel_warrant.chattel_owner,
                                          warrant_c.chattel_warrant.chattel_detail)
                result += '抵押给我公司，签订抵押反担保合同并办理抵押登记。</td></tr>'
                sure_or += 1
            elif sure_typ == 14:  # 在建工程动产
                warrant_c_13_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 抵押动产
                result += '<tr><td>（%s）在建工程抵押：</td></tr>' % sure_or
                sure_or += 1
            elif sure_typ == 15:  # 车辆抵押
                warrant_c_13_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 抵押动产
                result += '<tr><td>（%s）车辆抵押：</td></tr>' % sure_or
                sure_or += 1
            elif sure_typ == 21:  # 顺位房产
                result += '<tr><td>' \
                          '（%s）房产顺位：以下房产抵押给我公司，签订抵押反担保合同并办理顺位抵押登记' \
                          '</td></tr>' % sure_or
                result += guarantee_house(lending, sure_typ)
                sure_or += 1
            elif sure_typ == 22:
                result += '<tr><td>' \
                          '（%s）土地顺位：以下国有土地使用权抵押给我公司，签订抵押反担保合同并办理顺位抵押登记' \
                          '</td></tr>' % sure_or
                result += guarantee_ground(lending, sure_typ)
                sure_or += 1
            elif sure_typ == 23:  # 在建工程顺位
                result += '<tr><td>' \
                          '（%s）在建工程顺位：以下在建工程抵押给我公司，签订抵押反担保合同并办理顺位抵押登记' \
                          '</td></tr>' % sure_or
                result += guarantee_ground(lending, sure_typ)
                sure_or += 1
            elif sure_typ == 24:
                warrant_c_24_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 抵押动产
                result += '<tr><td>（%s）动产顺位：' % sure_or
                for warrant_c in warrant_c_24_list:
                    result += '%s将其%s' % (warrant_c.chattel_warrant.chattel_owner,
                                          warrant_c.chattel_warrant.chattel_detail)
                result += '抵押给我公司，签订抵押反担保合同并办理顺位抵押登记。</td></tr>'
                sure_or += 1
            elif sure_typ == 39:
                warrant_o_39_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 其他权利质押
                result += '<tr><td>（%s）其他：</td></tr>' % sure_or
                sure_or += 1
            elif sure_typ == 49:
                warrant_o_49_list = models.Warrants.objects.filter(
                    lending_warrant__sure__lending=lending, lending_warrant__sure__sure_typ=sure_typ)  # 其他监管
                result += '<tr><td>（%s）监管措施：' % sure_or
                for warrant_o in warrant_o_49_list:
                    result += '%s提供%s' % (warrant_o.other_warrant.other_owner,
                                          warrant_o.other_warrant.other_detail)
                result += '存放于我公司进行保管。</td></tr>'
                sure_or += 1
    return mark_safe(result)


@register.simple_tag
def decision(agree_id):
    agree_obj = models.Agrees.objects.get(id=agree_id)
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
        q.children.append(("%s__in" % field, counter_agree_list))
    counter_custom_list = models.Customes.objects.filter(q)
    print('counter_custom_list:', counter_custom_list)
    if agree_custom_obj.genre == 1:
        result = '<p>%s股东会决议</p>'
