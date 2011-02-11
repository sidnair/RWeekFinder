#import pymongo
#from pymongo import Connection
import re

def dictify(lst):
    dicty={}
    for elt in lst:
        dicty[lst[0]]=lst[1]
    return dicty

def total_dictify(lst):
#    for pos in range(len(lst)):
#        lst[pos]=dictify(lst[pos])
    dicty={}
    for elt in map(dictify,lst):
        dicty.update(elt)
    return dicty

def get_database():
    host= 'flame.mongohq.com'
    port = 27041
    dbName = 'RWeek'
    connection=Connection(host,port)
        #name of database
    db = connection[dbName]
    username = "admin"
    password = "sekret"
    db.authenticate(username,password)
    return db

def get_all():
    file_name = "scrapee.html"
    file_ptr = open(file_name)

    file_str = file_ptr.read()

    weekdays = ["monday","tuesday","wednesday","thursday","friday"]

    #for line in file_str.


    pattern = re.compile(r'<td align="left" style="width:302px;"><b>([^<]+)</b><br>([^/]+)/td><td align="left">([^<]+)</td><td align="left">([^<]+)</td>')

    iterator = pattern.finditer(file_str)

    #db = get_database()

    data = []
    for line in iterator:
        keep_going=True
        dicty =  {"name":line.group(1),"neighborhood":line.group(3),"cuisine":line.group(4)}
        stri=line.group(2)[:-6]
        str_ls = stri.split(" <br>")
        for pos in range(len(str_ls)):
            ls = str_ls[pos].lower().split(": ")
            lst=ls[1].split(" & ")
            ls[1]={}
            for elt in lst:
                ls[1][elt] = 1
            str_ls[pos] = ls
        if str_ls[0][0] == "monday - friday":
            tmp=str_ls.pop(0)
            for day in weekdays:
                str_ls.append([day,tmp[1]])
        str_ls=total_dictify(str_ls)
        str_ls.update({"name":line.group(1),"neighborhood":line.group(3),"cuisine":line.group(4)})
        #db.restaurants.insert(str_ls)
        data.append(str_ls)
    return data
