insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (0,'ddl','switch_check_ddl','检测DDL语法及权限','true','{0}','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (1,'ddl','switch_tab_not_exists_pk','检查表必须为主键','true','表:\'{0}\'无主键!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (2,'ddl','switch_tab_pk_id','强制主键名为ID','true','表:\'{0}\'主键列名必须为\"id\"!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (3,'ddl','switch_tab_pk_auto_incr','强制主键为自增列','true','表:\'{0}\'主键列名必须为自增列!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (4,'ddl','switch_tab_pk_autoincrement_1','强制自增列初始值为1','true','表:\'{0}\'主键列自增初始值必须为1!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (5,'ddl','switch_pk_not_int_bigint','允许主键类型非int/bigint','false','表:\'{0}\'主键类型非int/bigint','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (6,'ddl','switch_tab_comment','检查表注释','true','表:\'{0}\'没有注释!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (7,'ddl','switch_col_comment','检查列注释','true','表:\'{0}\'列\'{1}\'没有注释!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (8,'ddl','switch_col_not_null','检查列是否为not null','true','表:\'{0}\'列\'{1}\'不能为空!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (9,'ddl','switch_col_default_value','检查列默认值','false','表:\'{0}\'非空列\'{1}\'上没有默认值!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (10,'ddl','switch_tcol_default_value','检查时间字段默认值','true','表:\'{0}\'时间列\'{1}\'默认值必须为\'{2}\'!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (11,'ddl','switch_char_max_len','字符字段最大长度','2000','表:\'{0}\'字符列\'{1}\'长度不能超过{2}!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (12,'ddl','switch_tab_has_time_fields','表必须拥有字段','create_time,update_time','表:\'{0}\'无\'{1}\'列!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (13,'ddl','switch_tab_tcol_datetime','时间字段类型为datetime','true','表:\'{0}\'列\'{1}\'必须为datetime类型!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (14,'ddl','switch_tab_char_total_len','字符列总长度','8000','表:\'{0}\'字符列总长度不能超过{1}个字符!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (15,'ddl','switch_tab_ddl_max_rows','DDL最大影响行数','2000','表:\'{0}\'DDL操作影响行数不能超过{1}行!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (20,'ddl','switch_tab_name_check','开启表名称规范','true','','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (21,'ddl','switch_tab_max_len','表名最大长度','60','表:\'{0}\'名称长度不能超过{1}个字符!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (22,'ddl','switch_tab_not_digit_first','表名不能以数字开头','true','表:\'{0}\'不允许以数字开头!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (23,'ddl','switch_tab_two_digit_end','禁止连续2位数字为后缀','true','表:\'{0}\'不允许连续2位及以上数字结尾!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (24,'ddl','switch_tab_disable_prefix','禁止表名前后缀','temp,tmp,bak,backup','表:\'{0}\'禁止{1}为前后缀!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (25,'ddl','switch_ddl_batch','是否开启批量DDL','true','不允许执行多个DDL语句!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (26,'ddl','switch_ddl_timeout','DDL超时时间','120','表:\'{0}\'执行DDL已超时!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (27,'ddl','switch_disable_trigger','禁止使用触发器','true','禁止使用触发器!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (28,'ddl','switch_disable_func','禁止使用函数','true','禁止使用函数!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (29,'ddl','switch_disable_proc','禁止使用过程','true','禁止使用过程!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (30,'ddl','switch_disable_event','禁止使用过程','true','禁止使用事件!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (31,'ddl','switch_drop_database','允许删除库','false','禁止删除数据库！','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (32,'ddl','switch_drop_table','允许删除表','false','禁止删除表！','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (33,'ddl','switch_virtual_col','允许便用虚拟列','false','表:\'{0}\'不允许使用虚拟列!','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (34,'ddl','switch_tab_migrate','是否允许跨库表迁移','false','表:\'{0}\'不允许跨库迁移操作!','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (35,'ddl','switch_col_order_rule','允许设置列排序规则','false','表:\'{0}\'不允许设置列排序规则!','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (36,'ddl','switch_col_charset','允许设置列字符集','false','表:\'{0}\'不允许设置列字符集！','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (37,'ddl','switch_tab_charset','允许设置表字符集','true','表:\'{0}\'不允许设置列排序规则!','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (38,'ddl','switch_tab_charset_range','允许表字符集范围','utf8mb4,utf8','表:\'{0}\'只允许表字符集范围为({1})!','0');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (40,'ddl','switch_idx_name_check','开启索引规范','true','','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (41,'ddl','switch_idx_name_null','允许索引名为空','true','表:\'{0}\'不允许索引名为空!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (42,'ddl','switch_idx_name_rule','启用索引名规则','false','表:\'{0}\'索引名\'{1}\'唯反规则!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (43,'ddl','switch_idx_numbers','单表索引数上限\r\n','2','表:\'{0}\'索引个数超限!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (44,'ddl','switch_idx_col_numbers','单个索引字段上限\r\n','3','表:\'{0}\'的索引\'{1}\'列个数超限!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (45,'ddl','switch_idx_name_col','允许索引名与列名相同','true','表:\'{0}\'索引名与列名不能相同!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (61,'dml','switch_dml_batch','是否开启批量DML','false','不允许执行批量DML语句!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (62,'dml','switch_dml_where','检测DML语句条件','true','DML语句必须存在where条件!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (63,'dml','switch_dml_order','DML语句禁用order','true','DML语句禁止使用order by!\'','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (64,'dml','switch_dml_select','DML语句禁用select','true','DML语句禁用SELECT!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (65,'dml','switch_dml_max_rows','DML最大影响行数\r\n','3','DML最大影响行数\r\n不能超过{0}行!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (66,'dml','switch_dml_ins_exists_col','检查插入语句必须存在列名','true','Insert语句必须指定列名!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (67,'dml','switch_dml_ins_cols','INSERT语句字段上限','8','Insert语句字段数不能超过{0}列!','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (68,'dml','switch_check_dml','验证DML语句语法','true','','1');
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (80,'query','switch_query_rows','限制查询条数','1000','查询超出{0}最大行限制！',NULL);
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (81,'query','switch_timeout','查询超时时间','3','查询超过{0}秒，停止查询!',NULL);
insert  into `t_sql_audit_rule`(`id`,`rule_type`,`rule_code`,`rule_name`,`rule_value`,`error`,`status`) values (82,'query','switch_sensitive_columns','查询敏感列设置','user_mobile,user_email,user_name','***敏感列***',NULL);
