# 2019 Emir Erbasan (humanova)

import tinydb
from tinydb.operations import increment, set
import datetime
from tabulate import tabulate

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
    

    def getCCTimeLeft(self, userid):

        User = tinydb.Query()
        user = self.cc_table.search(User.userid == userid)[0]

        now = datetime.datetime.now()
        end_date = datetime.datetime.fromtimestamp(int(user['uncc_timestamp']))

        td = end_date - now
        diff = td.days, td.seconds // 3600, (td.seconds // 60) % 60
        
        return diff


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


    def updateCCTable(self, members):

        User = tinydb.Query()
        q_res = self.cc_table.search(User.isCC == True)

        noncc_members = members
        # remove members that already are in database
        for idx, mem in enumerate(members):
            for db_user in q_res:
                if db_user['userid'] == mem.id:
                    noncc_members.pop(idx)

        # cc not cc'ed(in db) members
        for mem in noncc_members:
            self.ccUser(mem.id, mem.name)
        
        # uncc not cc'ed(in db) member
        cc_members = [m.id for m in members]
        cc_members_db = [u['userid'] for u in q_res]
        for m_id in cc_members_db:
            if not m_id in cc_members:
                self.unccUser(m_id)
         
        print(f"{len(members)} users got CC'd with !ccupdate command")

        return noncc_members

    def getCCTable(self):

        User = tinydb.Query()
        q_res = self.cc_table.search(User.isCC == True)

        cc_users = [[0 for x in range(3)] for y in range(len(q_res))] 
        for idx, mem in enumerate(q_res):

            diff = self.getCCTimeLeft(mem['userid'])
            time_left_str = f"{diff[0]}d {diff[1]}h"

            user = []
            cc_users[idx][0] = mem['userid']
            cc_users[idx][1] = mem['username']
            cc_users[idx][2] = time_left_str

            cc_users.append(user)
        
        table = tabulate(cc_users, ["userid", "username", "time_left"], tablefmt="ortabgtbl")

        return table