#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/7/10 13:18
# @Author  : 马飞
# @File    : t_sql.py
# @Software: PyCharm

import sqlparse
import traceback,re
import logging
import datetime
import json
from web.utils.common           import current_time
from web.model.t_user           import get_user_by_loginame
from web.model.t_ds             import get_ds_by_dsid,get_ds_by_dsid_sync
from web.model.t_dmmx           import get_dmmc_from_dm,get_dmmc_from_dm_sync
from web.model.t_sql_check      import check_mysql_ddl
from web.utils.common           import send_mail,send_mail_param,get_sys_settings,get_sys_settings_sync
from web.utils.common           import format_sql as fmt_sql
from web.model.t_user           import get_user_by_userid,get_user_by_loginame_sync
from web.utils.mysql_async      import async_processer
from web.utils.mysql_sync       import sync_processer
from web.utils.mysql_rollback   import write_rollback,delete_rollback
from web.model.t_sql_check      import reReplace,check_statement_count

async def get_sqlid():
    sql="select ifnull(max(id),0)+1 from t_sql_release"
    rs = await async_processer.query_one(sql)
    return rs[0]

async def get_sql_release(p_id):
    sql="select * from t_sql_release where id={}".format(p_id)
    return await async_processer.query_dict_one(sql)

def get_sql_release_sync(p_id):
    sql="select * from t_sql_release where id={}".format(p_id)
    return sync_processer.query_dict_one(sql)

async def get_sql_by_sqlid(p_sql_id):
    sql="select sqltext from t_sql_release where id={0}".format(p_sql_id)
    rs = await async_processer.query_one(sql)
    return rs[0]

def get_sql_by_sqlid_sync(p_sql_id):
    sql="select sqltext from t_sql_release where id={0}".format(p_sql_id)
    rs = sync_processer.query_one(sql)
    return rs[0]

async def query_audit(p_name,p_dsid,p_creator,p_userid,p_username):
    print('p_creator=',p_creator,'p_userid',p_username)
    v_where = ''
    if p_name != '':
       v_where = v_where + " and a.sqltext like '%{0}%'\n".format(p_name)

    if p_dsid != '':
        v_where = v_where + " and a.dbid='{0}'\n".format(p_dsid)
    else:
        v_where = v_where + """ and exists(select 1 from t_user_proj_privs x 
                                           where x.proj_id=b.id and x.user_id='{0}' and priv_id='3')""".format(p_userid)
    if p_creator != '':
        v_where = v_where + " and a.creator='{0}'\n".format(p_creator)

    if p_username != 'admin':
        v_where = v_where + " and a.creator='{0}'\n".format(p_username)

    sql = """SELECT  a.id, 
                     a.message,
                      CASE a.status 
                           WHEN '0' THEN '已发布'
                           WHEN '1' THEN '已审核'
                           WHEN '2' THEN '审核失败'
                           WHEN '3' THEN '执行中'
                           WHEN '4' THEN '执行成功'
                           WHEN '5' THEN '执行失败'
                           WHEN '6' THEN '已驳回'
                           WHEN '7' THEN '准备执行'
                     END  STATUS,
                     CASE  WHEN a.run_time IS NOT NULL and a.run_time !='' THEN
                        CONCAT(c.dmmc,'(<span style="color:red">定时</span>)')
                     ELSE
                        c.dmmc 
                     END AS 'type',
                     b.db_desc,
                     a.db,
                     (SELECT NAME FROM t_user d WHERE d.login_name=a.creator) creator,
                     DATE_FORMAT(a.creation_date,'%Y-%m-%d %h:%i:%s')  creation_date,
                     (SELECT NAME FROM t_user e WHERE e.login_name=a.auditor) auditor,
                     DATE_FORMAT(a.audit_date,'%y-%m-%d %h:%i:%s')   audit_date   
            FROM t_sql_release a,t_db_source b,t_dmmx c
            WHERE a.dbid=b.id
              AND c.dm='13'
              AND a.type=c.dmm
              {0}
            order by a.creation_date desc
          """.format(v_where)
    print(sql)
    return await async_processer.query_list(sql)

async def query_run(p_name,p_dsid,p_creator,p_userid,p_username):
    v_where = ''
    if p_name != '':
       v_where = v_where + " and a.sqltext like '%{0}%'\n".format(p_name)
    if p_dsid != '':
        v_where = v_where + " and a.dbid='{0}'\n".format(p_dsid)
    else:
        v_where = v_where + """ and exists(select 1 from t_user_proj_privs x 
                                   where x.proj_id=b.id and x.user_id='{0}' and priv_id='4')""".format(p_userid)
    if p_creator != '':
        v_where = v_where + " and a.creator='{0}'\n".format(p_creator)

    if p_username != 'admin':
        v_where = v_where + " and a.creator='{0}'\n".format(p_username)

    sql = """SELECT  a.id, 
                     a.message,
                     CASE a.status 
                           WHEN '0' THEN '已发布'
                           WHEN '1' THEN '已审核'
                           WHEN '2' THEN '审核失败'
                           WHEN '3' THEN '执行中'
                           WHEN '4' THEN '执行成功'
                           WHEN '5' THEN '执行失败'
                           WHEN '6' THEN '已驳回'
                           WHEN '7' THEN '准备执行'
                     END  STATUS,
                     CASE  WHEN a.run_time IS NOT NULL and a.run_time !='' THEN
                        CONCAT(c.dmmc,'(<span style="color:red">定时</span>)')
                     ELSE
                        c.dmmc 
                     END AS 'type',
                     b.db_desc,
                     a.db,
                     (SELECT NAME FROM t_user e WHERE e.login_name=a.creator) creator,
                     DATE_FORMAT(a.creation_date,'%Y-%m-%d %h:%i:%s')  creation_date,
                     (SELECT NAME FROM t_user e WHERE e.login_name=a.auditor) auditor,
                     DATE_FORMAT(a.audit_date,'%y-%m-%d %h:%i:%s')   audit_date,
                     IFNULL(error,'')  as error   
            FROM t_sql_release a,t_db_source b,t_dmmx c
            WHERE a.dbid=b.id
              AND c.dm='13'
              AND a.type=c.dmm
              {0} order by a.creation_date desc
          """.format(v_where)
    return await async_processer.query_list(sql)

async def query_order(p_name,p_dsid,p_creator,p_username):
    v_where=''

    if p_creator != '':
        v_where = v_where + " and a.creator='{0}'\n".format(p_creator)

    if p_username != 'admin':
       v_where = "  and  a.creator='{0}'".format(p_username)

    if p_name != '':
       v_where = v_where + " and a.sqltext like '%{0}%'\n".format(p_name)

    if p_dsid != '':
        v_where = v_where + " and a.dbid='{0}'\n".format(p_dsid)

    sql = """SELECT  a.id, 
                     a.message,
                      CASE a.status 
                           WHEN '0' THEN '已发布'
                           WHEN '1' THEN '已审核'
                           WHEN '2' THEN '审核失败'
                           WHEN '3' THEN '执行中'
                           WHEN '4' THEN '执行成功'
                           WHEN '5' THEN '执行失败'
                           WHEN '6' THEN '已驳回'
                           WHEN '7' THEN '准备执行'
                     END  STATUS,                     
                     CASE  WHEN a.run_time IS NOT NULL and a.run_time !='' THEN
                        CONCAT(c.dmmc,'(<span style="color:red">定时</span>)')
                     ELSE
                        c.dmmc 
                     END AS 'type',
                     b.db_desc,
                     (SELECT NAME FROM t_user e WHERE e.login_name=a.creator) creator,
                     DATE_FORMAT(a.creation_date,'%Y-%m-%d %h:%i:%s')  creation_date,
                     (SELECT NAME FROM t_user e WHERE e.login_name=a.auditor) auditor,
                     DATE_FORMAT(a.audit_date,'%y-%m-%d %h:%i:%s')   audit_date,
                     error
            FROM t_sql_release a,t_db_source b,t_dmmx c
            WHERE a.dbid=b.id
              AND c.dm='13'
              AND a.type=c.dmm
              {0} order by a.creation_date desc
          """.format(v_where)
    print(sql)
    return await async_processer.query_list(sql)

async def query_wtd(p_userid):
    sql = """SELECT 
                 order_no,
                 (SELECT db_desc FROM t_db_source WHERE  id=a.order_env) AS order_env,
                 (SELECT dmmc FROM t_dmmx WHERE dm='17' AND dmm=a.order_type) AS order_type,
                 (SELECT dmmc FROM t_dmmx WHERE dm='19' AND dmm=a.order_status) AS order_status,                
                 (SELECT NAME FROM t_user WHERE id=a.creator) AS creator,
                 date_format(a.create_date,'%Y-%m-%d') as  create_date,
                 (SELECT NAME FROM t_user WHERE id=a.order_handler) AS order_handler,
                 date_format(a.handler_date,'%Y-%m-%d') as  handler_date                
           FROM t_wtd a
           where a.creator='{0}' or a.order_handler='{1}'
          """.format(p_userid,p_userid)
    return await async_processer.query_list(sql)

async def get_order_attachment_number(p_wtd_no):
    sql = """SELECT  attachment_path FROM t_wtd a where order_no='{0}'""".format(p_wtd_no)
    rs = await async_processer.query_one(sql)
    if rs is None or rs == (None,) or rs ==('',):
       return 0
    else:
       return rs[0].count(',')+1

async def query_wtd_detail(p_wtd_no,p_userid):
    sql = """SELECT 
                 order_no,
                 order_env,
                 order_type,
                 order_status,                
                 creator,
                 date_format(a.create_date,'%Y-%m-%d') as  create_date,
                 order_handler,
                 date_format(a.handler_date,'%Y-%m-%d') as  handler_date,
                 (SELECT db_desc FROM t_db_source WHERE id=a.order_env) AS order_env_name,
                 (SELECT dmmc FROM t_dmmx WHERE dm='17' AND dmm=a.order_type) AS order_type_name,
                 (SELECT dmmc FROM t_dmmx WHERE dm='19' AND dmm=a.order_status) AS order_status_name,                
                 (SELECT NAME FROM t_user WHERE id=a.creator) AS creator_name,
                 (SELECT NAME FROM t_user WHERE id=a.order_handler) AS order_handler_name,             
                 order_desc,
                 attachment_path,
                 attachment_name,
                 '{0}' as curr_user
                FROM t_wtd a where order_no='{1}'""".format(p_userid,p_wtd_no)
    rs = await async_processer.query_one(sql)
    return rs

async def query_order_no():
    sql = '''SELECT 
                   CASE WHEN (COUNT(0)+1)<10 THEN 
                      CONCAT('0',CAST(COUNT(0)+1 AS CHAR))
                   ELSE
                      CAST(COUNT(0)+1 AS CHAR)
                   END AS order_no   
               FROM t_wtd FOR UPDATE'''
    rs = await async_processer.query_one(sql)
    return rs[0]

async def save_order(order_number,order_env,order_type,order_status,order_handle,order_desc,p_user,p_attachment_path,p_attachment_name):
    result = {}
    try:
        sql = '''insert into t_wtd(order_no,order_env,order_type,order_status,order_handler,order_desc,creator,create_date,attachment_path,attachment_name)
                  values('{0}','{1}','{2}','{3}','{4}','{5}','{6}',now(),'{7}','{8}')
              '''.format(order_number,order_env,order_type,order_status,order_handle,order_desc,p_user,p_attachment_path,p_attachment_name)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='保存成功!'
        return result
    except :
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '保存失败!'
        return result

async def upd_order(order_number, order_env, order_type, order_status,order_handler, order_desc, p_attachment_path, p_attachment_name):
    result = {}
    try:
        sql = '''update t_wtd set                     
                      order_env          = '{0}',
                      order_type         = '{1}',
                      order_status       = '{2}',
                      order_handler      = '{3}',
                      order_desc         = '{4}',
                      attachment_path    = '{5}',
                      attachment_name    = '{6}'
                 where order_no ='{7}'
              '''.format(order_env, order_type, order_status, order_handler, order_desc,
                         p_attachment_path, p_attachment_name,order_number)
        await async_processer.exec_sql(sql)
        result['code'] = '0'
        result['message'] = '更新成功!'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '更新失败!'
        return result

async def delete_wtd(order_number):
    result = {}
    try:
        sql = "delete from t_wtd  where order_no='{0}'".format(order_number)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='删除成功!'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '删除失败!'
        return result

async def delete_order(p_release_id):
    result = {}
    try:
        release = await get_sql_release(p_release_id)
        if release['status'] in('1','3','4','5'):
            result['code'] = '-1'
            result['message'] = '不能删除已审核工单!'
            return result
        sql = "delete from t_sql_release  where id='{0}'".format(p_release_id)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='删除成功!'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '删除失败!'
        return result

async def update_order(p_release_id,p_run_time):
    result = {}
    try:
        release = await get_sql_release(p_release_id)
        if release['status'] in('3','4','5'):
            result['code'] = '-1'
            result['message'] = '不能更新已执行工单!'
            return result
        sql = "update  t_sql_release set run_time='{}' where id='{}'".format(p_run_time,p_release_id)
        print(sql)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='更新成功!'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '更新失败!'
        return result

async def release_order(p_order_no,p_userid):
    result = {}
    try:
        user = await get_user_by_userid(p_userid)
        sql  = """update t_wtd set order_status='2' where order_no='{0}'""".format(p_order_no)
        await async_processer.exec_sql(sql)
        v_handle  = await query_wtd_detail(p_order_no,p_userid)['order_handler']
        v_email   = await get_user_by_userid(v_handle)['email']
        v_content ='{}发布了问题单，编号：{},请尽时处理!'.format(user['username'],p_order_no)
        send_mail('190343@lifeat.cn', 'Hhc5HBtAuYTPGHQ8',v_email , '发布工单', v_content)
        result['code']='0'
        result['message']='发布成功!'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '发布失败!'
        return result

async def get_order_xh(p_type,p_rq,p_dbid):
    result = {}
    try:
        st ="""SELECT MAX(a.message)  as xh FROM t_sql_release a
                    WHERE a.dbid={} 
                      and a.TYPE='{}' 
                      and a.creation_date=(SELECT MAX(creation_date) 
                                           FROM t_sql_release b 
                                           WHERE b.dbid=a.dbid 
                                             and b.TYPE=a.type
                                             and DATE_FORMAT(b.creation_date,'%Y%m%d')='{}')
                     """.format(p_dbid,p_type,p_rq)
        res = await async_processer.query_dict_one(st)
        print(st)
        result['code']='0'
        if res['xh']=='':
           result['message'] = 1
        else:
           print('xh=',res['xh'])
           result['message']=int(res['xh'].split('-')[-1])+1
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = traceback.format_exc()
        return result

async def check_order_xh(p_message):
    result = {}
    try:
        st ="""SELECT COUNT(0) as xh FROM t_sql_release WHERE message='{}'""".format(p_message)
        res = await async_processer.query_dict_one(st)
        print(st)
        result['code']='0'
        result['message']=res['xh']
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = traceback.format_exc()
        return result

async def query_audit_sql(id):
    sql = """select a.sqltext,a.error,b.rollback_statement,a.run_time,a.db,a.dbid from t_sql_release a left join t_sql_backup b  on  a.id=b.release_id where a.id={0}""".format(id)
    rs = await async_processer.query_dict_one(sql)

    ds = await get_ds_by_dsid(rs['dbid'])
    ds['service'] = rs['db']
    rs['ds'] = ds

    result = {}
    result['code'] = '0'
    result['message'] = rs
    return result

async def save_sql(p_dbid,p_sql,desc,logon_user):
    result = {}
    try:
        if p_dbid == '':
            result['code'] = '1'
            result['message'] = '请选择数据源!'
            return result

        p_ds = await get_ds_by_dsid(p_dbid)
        if p_ds['db_type'] == '0':
            val = check_mysql_ddl(p_dbid, p_sql,logon_user)

        if val['code']!='0':
           return val
        sql="""insert into t_sql_release(id,dbid,sqltext,status,message,creation_date,creator,last_update_date,updator) 
                values('{0}','{1}',"{2}",'{3}','{4}','{5}','{6}','{7}','{8}')""".format(get_sqlid(),p_dbid,p_sql,'0',desc,current_time(),'DBA',current_time(),'DBA');
        await async_processer.exec_sql(sql)
        result={}
        result['code']='0'
        result['message']='发布成功！'
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '发布失败！'
        return result

async def check_sql(p_dbid,p_cdb,p_sql,desc,logon_user,type):
    result = {}
    result['code'] = '0'
    result['message'] = '发布成功！'
    try:
        if p_dbid == '':
            result['code'] = '1'
            result['message'] = '请选择数据源!'
            return result

        p_ds = await get_ds_by_dsid(p_dbid)
        if p_ds['db_type'] == '0':
            val = await check_mysql_ddl(p_dbid,p_cdb, p_sql,logon_user,type)

        if val == False:
            result['code'] = '1'
            result['message'] = '发布失败!'
            return result
        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '发布失败！'
        return result

async def save_sql(p_dbid,p_cdb,p_sql,desc,p_user,type,time,p_username,p_host):
    result = {}
    try:
        if check_validate(p_dbid,p_cdb,p_sql,desc,p_user,type)['code']!='0':
           return check_validate(p_dbid,p_cdb,p_sql,desc,p_user,type)

        p_ds = await get_ds_by_dsid(p_dbid)
        p_sqlid = await get_sqlid()

        if p_ds['db_type'] == '0':
            val = check_mysql_ddl(p_dbid,p_cdb, p_sql,p_user,type)

        if val == False:
            result['code'] = '1'
            result['message'] = '发布失败!'
            return result

        sql="""insert into t_sql_release(id,dbid,db,sqltext,status,message,creation_date,creator,last_update_date,updator,type,run_time) 
                 values('{0}','{1}',"{2}",'{3}','{4}','{5}','{6}','{7}','{8}','{9}','{10}','{11}')
            """.format(p_sqlid,p_dbid,p_cdb,fmt_sql(p_sql),'0',desc,current_time(),p_user['login_name'],current_time(),p_user['login_name'],type,time)

        print('release=>',sql)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='发布成功！'

        # 2021.09.09 add send mail
        p_ds['service'] = p_cdb
        sql = await get_sql_by_sqlid(p_sqlid)
        email = (await get_user_by_loginame(p_username))['email']
        settings = await get_sys_settings()
        # send success mail
        wkno = await get_sql_release(p_sqlid)
        v_title = '工单发布情况[{}]'.format(wkno['message'])
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator = (await get_user_by_loginame(wkno['creator']))['name']
        otype   = (await get_dmmc_from_dm('13', wkno['type']))[0]
        status  = (await get_dmmc_from_dm('41', wkno['status']))[0]
        v_content = get_html_contents_release()
        v_content = v_content.replace('$$TIME$$', nowTime)
        v_content = v_content.replace('$$DBINFO$$',  p_ds['url'] + p_ds['service'] if p_ds['url'].find(p_ds['service']) < 0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$TYPE$$', otype)
        v_content = v_content.replace('$$STATUS$$', status)
        if p_host == "124.127.103.190":
            p_host = "124.127.103.190:65482"
        elif p_host.find(':') >= 0:
            p_host = p_host
        else:
            p_host = p_host + ':81'
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host,p_sqlid))
        v_content = v_content.replace('$$ERROR$$', '')
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,
                        settings.get('CC'), v_title, v_content)

        return result
    except:
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '发布失败!'
        return result

async def upd_sql(p_sqlid,p_username,p_status,p_message,p_host):
    result={}
    try:
        sql="""update t_sql_release 
                  set  status ='{}' ,
                       last_update_date =now(),
                       updator='{}',
                       audit_date =now() ,
                       auditor='{}',
                       audit_message='{}'
                where id='{}'""".format(p_status,p_username,p_username,p_message,p_sqlid)
        await async_processer.exec_sql(sql)

        # send audit mail
        wkno = await get_sql_release(p_sqlid)
        p_ds = await get_ds_by_dsid(wkno['dbid'])
        p_ds['service'] = wkno['db']
        email = (await get_user_by_loginame(p_username))['email']
        settings = await get_sys_settings()

        v_title = '工单审核情况[{}]'.format(wkno['message'])
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator = (await get_user_by_loginame(wkno['creator']))['name']
        print('creater=',creator)
        creater_mail =  (await get_user_by_loginame(wkno['creator']))['email']
        print('creater_mail=', creater_mail)
        auditor = (await get_user_by_loginame(wkno['auditor']))['name']
        otype = (await get_dmmc_from_dm('13', wkno['type']))[0]
        status = (await get_dmmc_from_dm('41', wkno['status']))[0]
        v_content = get_html_contents()
        v_content = v_content.replace('$$TIME$$', nowTime)
        v_content = v_content.replace('$$DBINFO$$',p_ds['url'] + p_ds['service']
                                                   if p_ds['url'].find(p_ds['service']) < 0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$AUDITOR$$', auditor)
        v_content = v_content.replace('$$TYPE$$', otype)
        v_content = v_content.replace('$$STATUS$$', status)
        if p_host=="124.127.103.190":
           p_host = "124.127.103.190:65482"
        elif p_host.find(':')>=0:
           p_host = p_host
        else:
           p_host = p_host+':81'
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host,p_sqlid))
        v_content = v_content.replace('$$ERROR$$', '')
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,
                        creater_mail, v_title, v_content)

        result['code']='0'
        result['message']='审核成功!'
        return result
    except :
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '审核异常!'
        return result

async def upd_sql_run_status(p_sqlid):
    result={}
    try:
        sql="""update t_sql_release  set  status ='7' ,last_update_date =now() where id='{}'""".format(p_sqlid)
        await async_processer.exec_sql(sql)
        result['code']='0'
        result['message']='已在后台运行!'
        return result
    except :
        traceback.print_exc()
        result['code'] = '-1'
        result['message'] = '设置运行状态异常!'
        return result

async def upd_run_status(p_sqlid,p_username,p_flag,p_err=None,binlog_file=None,start_pos=None,stop_pos=None):
    try:
        if p_flag == 'before':
            sql = """update t_sql_release set  status ='3',last_update_date ='{0}',executor = '{1}',exec_start ='{2}' where id='{3}'""".format(current_time(),p_username,current_time(),str(p_sqlid))
        elif p_flag =='after':
            sql = """update t_sql_release set status ='4',last_update_date ='{0}',exec_end ='{1}',binlog_file='{2}',start_pos='{3}',stop_pos='{4}', error = '' where id='{5}'""".format(current_time(), current_time(),binlog_file,start_pos,stop_pos,str(p_sqlid))
        elif p_flag=='error':
            sql = """update t_sql_release set  status ='5',last_update_date ='{0}',exec_end ='{1}',error = '{2}',failure_times=failure_times+1 where id='{3}'""".format(current_time(), current_time(), p_err,str(p_sqlid))
        else:
           pass
        logging.info(("upd_run_status:",sql))
        await async_processer.exec_sql(sql)
    except :
        logging.error((traceback.format_exc()))
        traceback.print_exc()

def upd_run_status_sync(p_sqlid,p_username,p_flag,p_err=None,binlog_file=None,start_pos=None,stop_pos=None):
    try:
        if p_flag == 'before':
            sql = """update t_sql_release set  status ='3',last_update_date ='{0}',executor = '{1}',exec_start ='{2}' where id='{3}'""".format(current_time(),p_username,current_time(),str(p_sqlid))
        elif p_flag =='after':
            sql = """update t_sql_release set status ='4',last_update_date ='{0}',exec_end ='{1}',binlog_file='{2}',start_pos='{3}',stop_pos='{4}', error = '' where id='{5}'""".format(current_time(), current_time(),binlog_file,start_pos,stop_pos,str(p_sqlid))
        elif p_flag=='error':
            sql = """update t_sql_release set  status ='5',last_update_date ='{0}',exec_end ='{1}',error = '{2}',failure_times=failure_times+1 where id='{3}'""".format(current_time(), current_time(), p_err,str(p_sqlid))
        else:
           pass
        logging.info(("upd_run_status:",sql))
        sync_processer.exec_sql(sql)
    except :
        logging.error((traceback.format_exc()))
        traceback.print_exc()

def get_html_contents_release():
    v_html='''<html>
		<head>
		   <style type="text/css">
			   .xwtable {width: 90%;border-collapse: collapse;border: 1px solid #ccc;}
			   .xwtable thead td {font-size: 12px;color: #333333;
					      text-align: center;background: url(table_top.jpg) repeat-x top center;
				              border: 1px solid #ccc; font-weight:bold;}
			   .xwtable thead th {font-size: 12px;color: #333333;
				              text-align: center;background: url(table_top.jpg) repeat-x top center;
					      border: 1px solid #ccc; font-weight:bold;}
			   .xwtable tbody tr {background: #fff;font-size: 12px;color: #666666;}
			   .xwtable tbody tr.alt-row {background: #f2f7fc;}
			   .xwtable td{line-height:20px;text-align: left;padding:4px 10px 3px 10px;height: 18px;border: 1px solid #ccc;}
		   </style>
		</head>
		<body>
              <table class='xwtable'>
                  <tr><td width="20%">发送时间</td><td width="80%">$$TIME$$</td></tr>
                  <tr><td>数据库名</td><td>$$DBINFO$$</td></tr>
                  <tr><td>提交人员</td><td>$$CREATOR$$</td></tr>
                  <tr><td>工单类型</td><td>$$TYPE$$</td></tr>
                  <tr><td>工单状态</td><td>$$STATUS$$</td></tr>
                  <tr><td>工单详情</td><td>$$DETAIL$$</td></tr>
              </table>    
		</body>
	    </html>'''
    return v_html

def get_html_contents():
    v_html='''<html>
		<head>
		   <style type="text/css">
			   .xwtable {width: 90%;border-collapse: collapse;border: 1px solid #ccc;}
			   .xwtable thead td {font-size: 12px;color: #333333;
					      text-align: center;background: url(table_top.jpg) repeat-x top center;
				              border: 1px solid #ccc; font-weight:bold;}
			   .xwtable thead th {font-size: 12px;color: #333333;
				              text-align: center;background: url(table_top.jpg) repeat-x top center;
					      border: 1px solid #ccc; font-weight:bold;}
			   .xwtable tbody tr {background: #fff;font-size: 12px;color: #666666;}
			   .xwtable tbody tr.alt-row {background: #f2f7fc;}
			   .xwtable td{line-height:20px;text-align: left;padding:4px 10px 3px 10px;height: 18px;border: 1px solid #ccc;}
		   </style>
		</head>
		<body>
              <table class='xwtable'>
                  <tr><td width="20%">发送时间</td><td width="80%">$$TIME$$</td></tr>
                  <tr><td>数据库名</td><td>$$DBINFO$$</td></tr>
                  <tr><td>提交人员</td><td>$$CREATOR$$</td></tr>
                  <tr><td>审核人员</td><td>$$AUDITOR$$</td></tr>
                  <tr><td>工单类型</td><td>$$TYPE$$</td></tr>
                  <tr><td>工单状态</td><td>$$STATUS$$</td></tr>
                  <tr><td>工单详情</td><td>$$DETAIL$$</td></tr>
              </table>    
		</body>
	    </html>'''
    return v_html

async def exe_sql(p_dbid, p_db_name,p_sql_id,p_username,p_host):
    res = {}
    p_ds = await get_ds_by_dsid(p_dbid)
    p_ds['service'] = p_db_name
    await upd_run_status(p_sql_id,p_username,'before')
    sql   = await get_sql_by_sqlid(p_sql_id)
    email = (await get_user_by_loginame(p_username))['email']
    settings = await get_sys_settings()

    try:
        # get binlog ,start_position
        await async_processer.exec_sql_by_ds(p_ds, 'FLUSH /*!40101 LOCAL */ TABLES')
        await async_processer.exec_sql_by_ds(p_ds, 'FLUSH TABLES WITH READ LOCK')
        rs1 = await async_processer.query_one_by_ds(p_ds, 'show master status')
        binlog_file=rs1[0]
        start_position=rs1[1]

        logging.info(('check_statement_count(sql)=',check_statement_count(sql)))
        if check_statement_count(sql) == 1:
            logging.info(('exec single statement:'))
            logging.info(('-----------------------------------------'))
            logging.info(('statement:', sql))
            await async_processer.exec_sql_by_ds(p_ds, sql)
        elif check_statement_count(sql) > 1:
            logging.info(('exec multi statement:'))
            logging.info(('-----------------------------------------'))
            #await async_processer.exec_sql_by_ds_multi(p_ds, sql)
            for st in reReplace(sql):
                logging.info(('statement=',st))
                await async_processer.exec_sql_by_ds(p_ds, st)
        else:
            pass

        # get stop_position
        rs2 = await async_processer.query_one_by_ds(p_ds, 'show master status')
        stop_position=rs2[1]
        logging.info('binlog:{},{},{}'.format(binlog_file,str(start_position),str(stop_position)))
        await upd_run_status(p_sql_id, p_username, 'after',None,binlog_file,start_position,stop_position)

        # write rollback statement
        write_rollback(p_sql_id,p_ds,binlog_file,start_position,stop_position)

        # send success mail
        wkno      = await get_sql_release(p_sql_id)
        v_title   = '工单执行情况[{}]'.format(wkno['message'])
        nowTime   = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator   = (await get_user_by_loginame(wkno['creator']))['name']
        auditor   = (await get_user_by_loginame(wkno['auditor']))['name']
        otype     = (await get_dmmc_from_dm('13',wkno['type']))[0]
        status    = (await get_dmmc_from_dm('41',wkno['status']))[0]
        v_content = get_html_contents()
        v_content = v_content.replace('$$TIME$$',   nowTime)
        v_content = v_content.replace('$$DBINFO$$',  p_ds['url']+p_ds['service'] if p_ds['url'].find(p_ds['service'])<0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$AUDITOR$$', auditor )
        v_content = v_content.replace('$$TYPE$$',    otype)
        v_content = v_content.replace('$$STATUS$$',  status)
        if p_host == "124.127.103.190":
            p_host = "124.127.103.190:65482"
        elif p_host.find(':') >= 0:
            p_host = p_host
        else:
            p_host = p_host + ':81'
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host,p_sql_id))
        v_content = v_content.replace('$$ERROR$$','')
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,settings.get('CC'), v_title,v_content)
        res['code'] = '0'
        res['message'] = '执行成功!'
        return res
    except Exception as e:
        error = str(e).split(',')[1][:-1].replace("\\","\\\\").replace("'","\\'").replace('"','')+'!'
        res['code'] = '-1'
        res['message'] = '执行失败!'
        logging.error(traceback.format_exc())
        await upd_run_status(p_sql_id, p_username, 'error', error)
        delete_rollback(p_sql_id)

        # send error mail
        wkno    = await get_sql_release(p_sql_id)
        v_title = '工单执行情况[{}]'.format(wkno['message'])
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator = (await get_user_by_loginame(wkno['creator']))['name']
        auditor = (await get_user_by_loginame(wkno['auditor']))['name']
        otype   = (await get_dmmc_from_dm('13', wkno['type']))[0]
        status  = (await get_dmmc_from_dm('41', wkno['status']))[0]
        v_content = get_html_contents()
        v_content = v_content.replace('$$TIME$$', nowTime)
        v_content = v_content.replace('$$DBINFO$$',
                                      p_ds['url'] + p_ds['service'] if p_ds['url'].find(p_ds['service']) < 0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$AUDITOR$$', auditor)
        v_content = v_content.replace('$$TYPE$$',    otype)
        v_content = v_content.replace('$$STATUS$$',  status)
        if p_host == "124.127.103.190":
            p_host = "124.127.103.190:65482"
        elif p_host.find(':') >= 0:
            p_host = p_host
        else:
            p_host = p_host + ':81'
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host, p_sql_id))
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,settings.get('CC'), v_title,
                        v_content)

        return res

def exe_sql_sync(p_dbid, p_db_name,p_sql_id,p_username):
    res = {}
    p_ds = get_ds_by_dsid_sync(p_dbid)
    p_ds['service'] = p_db_name
    upd_run_status_sync(p_sql_id,p_username,'before')
    sql   = get_sql_by_sqlid_sync(p_sql_id)
    email = get_user_by_loginame_sync(p_username)['email']
    settings = get_sys_settings_sync()

    try:
        # get binlog ,start_position
        sync_processer.exec_sql_by_ds(p_ds, 'FLUSH /*!40101 LOCAL */ TABLES')
        sync_processer.exec_sql_by_ds(p_ds, 'FLUSH TABLES WITH READ LOCK')
        rs1 = sync_processer.query_one_by_ds(p_ds, 'show master status')
        binlog_file=rs1[0]
        start_position=rs1[1]

        logging.info(('check_statement_count(sql)=',check_statement_count(sql)))
        if check_statement_count(sql) == 1:
            sync_processer.exec_sql_by_ds(p_ds, sql)
        elif check_statement_count(sql) > 1:
            for st in reReplace(sql):
                sync_processer.exec_sql_by_ds(p_ds, st)
        else:
            pass

        # get stop_position
        rs2 = sync_processer.query_one_by_ds(p_ds, 'show master status')
        stop_position=rs2[1]
        logging.info('binlog:{},{},{}'.format(binlog_file,str(start_position),str(stop_position)))
        upd_run_status_sync(p_sql_id, p_username, 'after',None,binlog_file,start_position,stop_position)

        # write rollback statement
        write_rollback(p_sql_id,p_ds,binlog_file,start_position,stop_position)

        # send success mail
        wkno      =  get_sql_release_sync(p_sql_id)
        v_title   = '工单执行情况[{}]'.format(wkno['message'])
        nowTime   = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator   = get_user_by_loginame_sync(wkno['creator'])['name']
        auditor   = get_user_by_loginame_sync(wkno['auditor'])['name']
        otype     = get_dmmc_from_dm_sync('13',wkno['type'])[0]
        status    = get_dmmc_from_dm_sync('41',wkno['status'])[0]
        v_content = get_html_contents()
        v_content = v_content.replace('$$TIME$$',   nowTime)
        v_content = v_content.replace('$$DBINFO$$',  p_ds['url']+p_ds['service'] if p_ds['url'].find(p_ds['service'])<0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$AUDITOR$$', auditor )
        v_content = v_content.replace('$$TYPE$$',    otype)
        v_content = v_content.replace('$$STATUS$$',  status)
        p_host = "124.127.103.190:65482"
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host,p_sql_id))
        v_content = v_content.replace('$$ERROR$$','')
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,settings.get('CC'), v_title,v_content)
        res['code'] = '0'
        res['message'] = '工单:{}执行成功!'.format(wkno['message'])
        #return json.dumps(res)
        return res
    except Exception as e:
        error = str(e).split(',')[1][:-1].replace("\\","\\\\").replace("'","\\'").replace('"','')+'!'
        logging.error(traceback.format_exc())
        upd_run_status_sync(p_sql_id, p_username, 'error', error)
        delete_rollback(p_sql_id)
        # send error mail
        wkno    =  get_sql_release_sync(p_sql_id)
        v_title = '工单执行情况[{}]'.format(wkno['message'])
        nowTime = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        creator = get_user_by_loginame_sync(wkno['creator'])['name']
        auditor = get_user_by_loginame_sync(wkno['auditor'])['name']
        otype   = get_dmmc_from_dm_sync('13', wkno['type'])[0]
        status  = get_dmmc_from_dm_sync('41', wkno['status'])[0]
        v_content = get_html_contents()
        v_content = v_content.replace('$$TIME$$', nowTime)
        v_content = v_content.replace('$$DBINFO$$',
                                       p_ds['url'] + p_ds['service'] if p_ds['url'].find(p_ds['service']) < 0 else p_ds['url'])
        v_content = v_content.replace('$$CREATOR$$', creator)
        v_content = v_content.replace('$$AUDITOR$$', auditor)
        v_content = v_content.replace('$$TYPE$$',    otype)
        v_content = v_content.replace('$$STATUS$$',  status)
        p_host = "124.127.103.190:65482"
        v_content = v_content.replace('$$DETAIL$$', 'http://{}/sql/detail?release_id={}'.format(p_host, p_sql_id))
        send_mail_param(settings.get('send_server'), settings.get('sender'), settings.get('sendpass'), email,settings.get('CC'), v_title,
                        v_content)
        res['code'] = '-1'
        res['message'] = '工单执行失败!'
        #return json.dumps(res)
        return res

def check_validate(p_dbid,p_cdb,p_sql,desc,logon_user,type):
    result = {}
    result['code'] = '0'
    result['message'] = '发布成功！'

    if p_dbid == '':
       result['code'] = '1'
       result['message'] = '请选择数据源!'
       return result

    if p_cdb == '':
       result['code'] = '1'
       result['message'] = '当前数据库不能为空!'
       return result

    if desc == '':
       result['code'] = '1'
       result['message'] = '请输入工单描述!'
       return result

    if type == '':
       result['code'] = '1'
       result['message'] = '工单类型不能为空!'
       return result

    return result

def format_sql(p_sql):
    result = {}
    result['code'] = '0'
    v_sql_list=sqlparse.split(p_sql)
    v_ret=''
    for v in v_sql_list:
        v_sql = sqlparse.format(v, reindent=True, keyword_case='upper')
        if v_sql.upper().count('CREATE') > 0 or v_sql.upper().count('ALTER') > 0:
            v_tmp = re.sub(' {5,}', '  ', v_sql).strip()
        else:
            v_tmp = re.sub('\n{2,}', '\n\n', v_sql).strip(' ')
        v_ret=v_ret+v_tmp+'\n\n'
    result['message'] = v_ret[0:-2]
    return result

