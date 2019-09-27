# 2019 Emir Erbasan (humanova)

import tinydb
from tinydb.operations import increment, set
import datetime

class cwdb():

    def __init__(self):

        self.cc_table = tinydb.TinyDB('db/cc-database.json')

    def ccUser(self, userid, username):
        
        User = tinydb.Query()
        q_res = self.cc_table.search(User.userid == userid)

        cc_datetime = datetime.datetime.now()
        uncc_datetime =  datetime.datetime.now() + datetime.timedelta(days=7)
        cc_date = cc_datetime.strftime("%c")
        uncc_date = uncc_datetime.strftime("%c")
        cc_timestamp = cc_datetime.timestamp()
        uncc_timestamp = uncc_datetime.timestamp()

        if len(q_res) == 0:

            self.cc_table.insert({
                'userid' : userid,
                'username' : username,
                'isCC' : True,
                'ccCount' : 1,
                'penaltyDays' : 7,
                'cc_date' : cc_date,
                'uncc_date' : uncc_date,
                'cc_timestamp' : cc_timestamp,
                'uncc_timestamp' : uncc_timestamp
                })
        else:
            
            cc_count = q_res[0]['ccCount']
            uncc_days = 7 + (7 * (cc_count - 1)) # f(x) =  7 + (7 * (x-1))

            uncc_datetime = datetime.datetime.now() + datetime.timedelta(days=uncc_days)
            uncc_date = uncc_datetime.strftime("%c")
            uncc_timestamp = uncc_datetime.timestamp()

            self.cc_table.upsert({
                'userid' : userid,
                'username' : username,
                'isCC' : True,
                'ccCount' : q_res[0]['ccCount'] + 1,
                'penaltyDays' : uncc_days,
                'cc_date' : cc_date,
                'uncc_date' : uncc_date,
                'cc_timestamp' : cc_timestamp,
                'uncc_timestamp' : uncc_timestamp
                }, User.userid == userid)

        return self.cc_table.search(User.userid == userid)[0]

    def unccUser(self, userid):

        User = tinydb.Query()
        self.cc_table.update(set('isCC', False), User.userid == userid)

        return self.cc_table.search(User.userid == userid)[0]
    
    def checkUncc(self):

        User = tinydb.Query()
        q_res = self.cc_table.search(User.isCC == True)

        curr_timestamp = datetime.datetime.now().timestamp()
        uncc_list = []

        for mem in q_res:

            if curr_timestamp > mem['uncc_timestamp']: 
                
                uncc_list.append(mem['userid'])
                self.unccUser(mem['userid'])

        return uncc_list