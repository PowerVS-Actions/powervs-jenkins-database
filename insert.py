#!/usr/bin/python3

import os
import sys
import psycopg2
import ibm_db
from datetime import datetime,timezone

from configparser import ConfigParser

def config(filename='database.ini', section='postgresql'):
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)
    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return db
    

def insert_data(table,date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id,jenkins_url_job):

    sql = "INSERT INTO " + table + " (date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id,jenkins_url_job) \
    VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cluster_id;"
    conn = None
    powervs_id = None
    try:
        # read database configuration
        params = config()
        # connect to the PostgreSQL database
        conn = psycopg2.connect(**params)
        # create a new cursor
        cur = conn.cursor()
        # execute the INSERT statement
        cur.execute(sql, (date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id,jenkins_url_job,))
        # get the powervs_id back
        powervs_id = cur.fetchone()[0]
        # commit the changes to the database
        conn.commit()
        # close communication with the database
        cur.close()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()
    return powervs_id

# expects the table already there
# CREATE TABLE clusters (date_utc VARCHAR(10), time_utc VARCHAR(16), cluster_id VARCHAR(32), powervs_guid VARCHAR(32), powervs_region VARCHAR(8), powervs_zone VARCHAR(8), ocp_version VARCHAR(16), ocp_size INT, requestor_email VARCHAR(64), requestor_id VARCHAR(16), jenkins_url_job VARCHAR(256))
def insert_db2(table, date, time_utc, cluster_id, powervs_guid, powervs_region, powervs_zone, ocp_version, ocp_size, requestor_email, requestor_id, jenkins_url_job):
    conn = None
    rowid = -1
    try:
        p = ConfigParser()
        p.read('database.ini')
        conn_str = 'database=' + p.get('db2', 'database') + ';hostname=' + p.get('db2', 'host') + ';port=50000;protocol=tcpip;uid=' + p.get('db2', 'uid') + ';pwd=' + p.get('db2', 'pwd')
        conn = ibm_db.connect(conn_str, '', '')
        sql = 'INSERT INTO ' + table + ' VALUES(?,?,?,?,?,?,?,?,?,?,?)'
        stmt = ibm_db.prepare(conn, sql)
        params = (date, time_utc, cluster_id, powervs_guid, powervs_region, powervs_zone, ocp_version, ocp_size, requestor_email, requestor_id, jenkins_url_job)
        ibm_db.execute(stmt, params)
        #select = 'SELECT rowid FROM ' + table + ' WHERE cluster_id=\'' + cluster_id + '\''
        #stmt = ibm_db.exec_immeadiate(conn, select)
        #cols = ibm_db.fetch_tuple(stmt)
        #rowid = cols[0]
    except Exception as error: 
        print(error)
    finally:
        if conn is not None:
            ibm_db.close(conn)
    return cluster_id #rowid

if __name__ == '__main__':
    print (len(sys.argv))
    if len(sys.argv) != 11:
        sys.exit('''
    ERROR: The number of arguments is not correct.
           We expect: table,date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id,jenkins_url_job
        ''')
    else:
        print ('Argument List:', str(sys.argv))
        
        #table,date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id, jenkins_url_job
        today = datetime.today().strftime('%m/%d/%Y')
        time = str(datetime.utcnow()).split(" ")[1]

        insert_data(str(sys.argv[1]),str(today),str(time),str(sys.argv[2]),str(sys.argv[3]),str(sys.argv[4]),str(sys.argv[5]),str(sys.argv[6]),str(sys.argv[7]),str(sys.argv[8]),str(sys.argv[9]),str(sys.argv[10]))
        insert_db2('clusters',str(today),str(time),str(sys.argv[2]),str(sys.argv[3]),str(sys.argv[4]),str(sys.argv[5]),str(sys.argv[6]),int(sys.argv[7]),str(sys.argv[8]),str(sys.argv[9]),str(sys.argv[10]))

