# ----------------------v_article项目模型--------------------#
# 项目
from .m_article import Articles
from .m_appraisal import Appraisals, SummaryNum
# -----------------------v_agree合同模型---------------------#
# 委托合同、反担保合同
from .m_agree import Agrees, Counters
# 保证反担保合同、房产抵押合同
from .m_agree import CountersAssure, CountersHouse
# -------------------v_warrant担保物模型---------------------#
#  担保物、产权证、他权
from .m_warrant import Warrants, Ownership, Hypothecs
#  房产、土地
from .m_warrant import Houses, Grounds
# 出入库、评估
from .m_warrant import Evaluate, Storages
# -----------------------v_provide放款模型-------------------#
# 放款、还款、归档
from .m_provide import Provides, Repayments, Pigeonholes
# 代偿、追偿
from .m_dun import Compensatories

# ---------------------v_interior内部信息----------------------#
# 部门、岗位、员工
from .m_interior import Departments
from .m_emploee import Jobs, Employees, Menus
# ---------------------v_external外部信息----------------------#
# 授信银行、放款机构、评审
from .m_external import Cooperators, Branches, Experts
# ---------------------v_custome客户信息-----------------------#
# 区域、行业
from .m_custome import Districtes, Industries
# 客户、企业客户、个人客户
from .m_custome import Customes, CustomesC, CustomesP
