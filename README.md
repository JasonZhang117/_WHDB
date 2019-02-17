菜单：
我的主页
项目管理
--项目列表
评审管理
--评审会
--项目评审
合同管理
--合同列表
权证管理
--权证列表
--按合同
放款管理
--风控落实
--放款通知
--放款列表
--逾期列表
--1月到期
归档管理
--未归档列表
--逾期归档
--移交行政
保后管理
--待保后列表
--逾期保后
追偿管理
--代偿
--追偿列表
客户管理
机构管理
--授信机构
--放款银行
报表管理
--项目
--合同

在保余额--上年同期
本年发生额--上年同期
每月放款额，每月还款额，每月净增加额--上年同期
carte_list：
[{
	'parrent': None,
	'child': [
		{'parrent': 1, 'child': [], 'id': 2, 'url': 'dbms:article_all', 'name': '查看项目列表'}],
	'id': 1,
	'ordery': 1,
	'name': '项目管理'
},
{
	'parrent': None,
	'child': [
		{'parrent': 2, 'child': [], 'id': 3, 'url': 'dbms:meeting_all', 'name': '查看评审会'},
		{'parrent': 2, 'child': [], 'id': 4, 'url': 'dbms:appraisal_all', 'name': '查看项目评审'}],
	'id': 2,
	'ordery': 2,
	'name': '评审管理'}]
result：
[{
	'parrent': None,
	'child': [
		{'parrent': 1, 'child': [],'id': 2, 'url': 'dbms:article_all', 'name': '查看项目列表'}],
	'id': 1,
	'ordery': 1,
	'name': '项目管理'
},
{
	'parrent': None,
	'child': [
		{'parrent': 2, 'child': [], 'id': 3, 'url': 'dbms:meeting_all', 'name': '查看评审会'},
		{'parrent': 2, 'child': [], 'id': 4, 'url': 'dbms:appraisal_all', 'name': '查看项目评审'}],
	'id': 2,
	'ordery': 2,
	'name': '评审管理'}]


申保会纪要变更---变更情况（tab,modle)
客户联系方式变更，财产线索（tab,modle)

客户-->项目-->放款次序-->合同-->放款通知-->放款-->还款
------>项目经理、助理、风控专员
------------------------>银行

WARRANT_TYP_LIST = [ 权证类型
        (1, '房产'), (2, '土地'), (3, '应收'), (4, '股权'),
        (5, '票据'), (6, '车辆'), (7, '其他'), (9, '他权')]
SURE_TYP_LIST = ( 反担保措施
        (1, '企业保证'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (21, '房产顺位'), (22, '土地顺位'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (41, '合格证监管'), (42, '房产监管'), (43, '土地监管'),(44, '票据监管'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))
COUNTER_TYP_LIST = ( #反担保合同类型
        (1, '企业担保'), (2, '个人保证'),
        (11, '房产抵押'), (12, '土地抵押'), (13, '设备抵押'), (14, '存货抵押'), (15, '车辆抵押'),
        (31, '应收质押'), (32, '股权质押'), (33, '票据质押'),
        (51, '股权预售'), (52, '房产预售'), (53, '土地预售'))

模态对话框

Ajax

模板中的跨表查询

动态表单集

window.location.reload() #js主动刷新页面

ARTICLE_STATE_LIST = ((1, '待反馈'), (2, '已反馈'), (3, '待上会'),
                          (4, '已上会'), (5, '已签批'), (6, '已注销'))
                          (5, '已签批')-->才能出合同

AGREE_STATE_LIST = ((1, '待签批'), (2, '已签批'),
                        (3, '已落实'), (4, '已注销'))
                            (3, '已落实')-->才能出放款通知

www.processon.com
需求分析

思维导图

业务场景分析（用户场景分析）

原型图
    Axure

开发工具选型
    Python
    Django
    mysql
    jquery
    bootstrap
    linux
    nginx
    pyharm

创建项目
    设计表结构
    写代码

…or create a new repository on the command line

echo "# Q3-Day82" >> README.md
git init
git add README.md
git commit -m "first commit"
git remote add origin git@github.com:JasonZhang117/Q3-Day82.git
git push -u origin master

…or push an existing repository from the command line

git remote add origin git@github.com:JasonZhang117/Q3-Day82.git
git push -u origin master

…or import code from another repository

You can initialize this repository with code from a Subversion, Mercurial, or TFS project.