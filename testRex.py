# -*- coding: utf-8 -*-
import re
import itertools
import time
import datetime
import pytz

testData = ["6/3(日)下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"2017/6/3(日)下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"06/03聚餐，在一二三餐廳",
"06.03聚餐，在一二三餐廳",
"0603聚餐，在一二三餐廳",
"06 03聚餐，在一二三餐廳",
"6月3日聚餐，在一二三餐廳",
"六月三日聚餐，在一二三餐廳",
"六月三號聚餐，在一二三餐廳",
"十二月二十日\n聚餐，在一二三餐廳"]
testData = ["6/3(日)下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"2017/6/3(日)下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"2017年6月3日(日)下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"今天下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"明天下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"後天下午20:00聚餐，在一二三餐廳，每人1680，現場付款。",
"大後天下午8:00聚餐，在一二三餐廳，每人1680，現場付款。"]
testData = ["明天下午20:00聚餐，在一二三餐廳，每人1680，現場付款。"]




if __name__ == "__main__":
    print(testData)
    for message in testData:
        print("m: "+message)
        temp_message = message
        temp_message = temp_message.replace("一","1")
        temp_message = temp_message.replace("二","2")
        temp_message = temp_message.replace("三","3")
        temp_message = temp_message.replace("四","4")
        temp_message = temp_message.replace("五","5")
        temp_message = temp_message.replace("六","6")
        temp_message = temp_message.replace("七","7")
        temp_message = temp_message.replace("八","8")
        temp_message = temp_message.replace("九","9")
        temp_message = temp_message.replace("十","1")
        print(temp_message)
        #Find Date
        dates = re.findall("\d{3,4}[ |.|\/|-]\d{1,2}[ |.|\/|-]\d{1,2}|\d{3,4}年\d{1,2}月\d{1,2}[日|號]|\d{1,2}[ |.|\/|-]\d{1,2}|\d{1,2}月\d{1,2}[日|號]|今天|明天|後天|大後天",temp_message)
    
        for i in range(len(dates)):
            dates[i] = re.sub("[ |.|\/|-|年|月]","-",dates[i])
            dates[i] = re.sub("[日|號]","",dates[i])
            if dates[i] == "今天" or dates[i] == "今日":
                dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8)).strftime("%Y-%m-%d")
            elif dates[i] == "明天" or dates[i] == "明日":
                dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 1)).strftime("%Y-%m-%d")
            elif dates[i] == "後天":
                dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 2)).strftime("%Y-%m-%d")
            elif dates[i] == "大後天":
                dates[i] = (datetime.datetime.now() + datetime.timedelta(hours = 8) + datetime.timedelta(days = 3)).strftime("%Y-%m-%d")
            if dates[i].count("-") < 2:
                dates[i] = str(time.strftime("%Y", time.localtime()))+"-"+dates[i]
        print(dates)
        #Find Time
        times = re.findall("\d{1,2}[:|：]\d{1,2}|(?:am|pm|早上|中午|下午|傍晚|凌晨)\d{1,2}[:|：]\d{1,2}",temp_message)

        
        for i in range(len(times)):
            term = re.findall("am|pm|早上|中午|下午|傍晚|凌晨",times[i])[0]
            times[i] = re.sub("am|pm|早上|中午|下午|傍晚|凌晨","",times[i])
            
            h = re.split(":|：",times[i])[0]
            m = re.split(":|：",times[i])[1]
            if term == "pm" or term == "中午" or term == "下午" or term == "傍晚":
                if 0 < int(h) and int(h) < 12:
                    h=str(int(h)+12)
            
            times[i] = h+":"+m+":00"
        print(times)
        #Find Summary
        temp_message = re.sub("\d{1,2}[:|：]\d{1,2}|(?:am|pm|早上|中午|下午|傍晚|凌晨)\d{1,2}[:|：]\d{1,2}","",temp_message)
        temp_message = re.sub("\d{3,4}[ |.|\/|-]\d{1,2}[ |.|\/|-]\d{1,2}|\d{3,4}年\d{1,2}月\d{1,2}[日|號]|\d{1,2}[ |.|\/|-]\d{1,2}|\d{1,2}月\d{1,2}[日|號]|今天|明天|後天|大後天","",temp_message)
        print(temp_message)
        message_list = re.split("[ |,|.|;|，|。|；]",temp_message)        
        try:
            message_list.remove("")
        except:
            print()
        print(message_list)
        
        
        if len(dates)>0:
            _date = dates[0]
        else:
            _date = ""
        if len(times)>0:
            _time = times[0]
        else:
            _time = ""
        _date_Time=_date +"T"+ _time
        _description=temp_message
        if len(message_list)>0:
            _summary = message_list[0]
        else:
            _summary = ""

    
        print(_date_Time)
        print(_summary)
        print(_description)

