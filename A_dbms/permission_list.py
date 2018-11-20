from . import permission_hook

perm_dic = {
    # 'crm_table_index': ['table_index', 'GET', [], {'source':'qq'}, ],
    #  可以查看CRM APP里所有数据库表
    'dbms_article_list': ['article', 'GET', [], {}],
    #访问项目列表（/zhangjian/dbms/article/1/）
    'dbms_article_list_all': ['article_all', 'GET', [], {}],
    #访问所有项目列表（/zhangjian/dbms/article/1/）
    'dbms_article_add_view': ['article_add', 'GET', [], {}],
    # 访问项目添加页（/zhangjian/dbms/article/add/）
    'dbms_article_add_change': ['article_add', 'POST', [], {}],
    # 添加项目（/zhangjian/dbms/article/add/）
    'crm_table_list_view': ['table_obj_change', 'GET', [], {}],
    # 可以访问表里每条数据的修改页
    'crm_table_list_change': ['table_obj_change', 'POST', [], {}],
    # 可以对表里的每条数据进行修改
    'crm_table_obj_add_view': ['table_obj_add', 'GET', [], {}],
    # 可以访问数据增加页
    'crm_table_obj_add': ['table_obj_add', 'POST', [], {}],
    # 可以创建表里的数据

}
