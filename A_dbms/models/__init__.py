# ----------------------v_article项目模型--------------------#
# 项目
from .m_article import (Articles, Feedback)
from .m_appraisal import (
    Appraisals, SingleQuota, Comments, LendingOrder, LendingSures,
    SureExtends, MortgageExtends, )
# -----------------------v_agree合同模型---------------------#
# 委托合同、反担保合同
from .m_agree import (
    Agrees, AgreeesExtend, Counters, CountersAssure, CountersHouse)
# -------------------v_warrant担保物模型---------------------#
from .m_warrant import (
    Warrants, Ownership, Houses, Grounds, Stockes, Receivable,
    Hypothecs, Evaluate, Storages)
# -----------------------v_provide放款模型-------------------#
# 放款、还款、归档
from .m_provide import (Provides, Repayments, Pigeonholes, Charges)
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
# 客户、企业客户、个人客户
from .m_custom import Customes, CustomesC, CustomesP

# 区域、行业
from .m_custom import Districtes, Industries
