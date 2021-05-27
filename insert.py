#!/usr/bin/python3

import os
import sys
import psycopg2
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

if __name__ == '__main__':
    print (len(sys.argv))
    if len(sys.argv) != 11:
        sys.exit('''
    ERROR: The nuber of arguments is not correct.
           We expect: table,date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id,jenkins_url_job
        ''')
    else:
        print ('Argument List:', str(sys.argv))
        
        #table,date,time_utc,cluster_id,powervs_guid,powervs_region,powervs_zone,ocp_version,ocp_size,requestor_email,requestor_id, jenkins_url_job
        today = datetime.today().strftime('%m/%d/%Y')
        time = str(datetime.utcnow()).split(" ")[1]

        insert_data(str(sys.argv[1]),str(today),str(time),str(sys.argv[2]),str(sys.argv[3]),str(sys.argv[4]),str(sys.argv[5]),str(sys.argv[6]),str(sys.argv[7]),str(sys.argv[8]),str(sys.argv[9]),str(sys.argv[10]))

