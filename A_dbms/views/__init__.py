# ----------------------v_index首页管理视图--------------------#
from .v_index import index
# ----------------------v_article合项目管理视图--------------------#
from .v_article import (article, article_add, article_scan,
                        article_scan_agree,
                        article_edit, article_del)
# ----------------------v_appraisal评审视图--------------------#
from .v_meeting import (meeting, meeting_add, meeting_scan,meeting_allot,
                        meeting_edit, meeting_del, meeting_scan_article,
                        meeting_add_ajax)
from .v_appraisal import appraisal
from .v_appraisal import appraisal_sign, appraisal_del, appraisal_edit
# ----------------------v_agree合同管理视图--------------------#
from .v_agree import agree, agree_add, agree_edit, agree_scan
# ----------------------v_warrant权证管理视图--------------------#
from .v_warrant import warrant
# ----------------------v_provide放款管理视图--------------------#
from .v_provide import provide, provide_edit

# 客户、行业、区域
from .v_custome import custome, custome_add, custome_edit, custome_del
from .v_custome import industry, industry_add, industry_edit
from .v_custome import district
# 部门、员工
from .v_interior import department, department_add, department_edit
from .v_interior import department_del
from .v_interior import employee, employee_add, employee_edit, employee_del
from .v_interior import employee_del_ajax
