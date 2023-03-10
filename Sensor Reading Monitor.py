### Code by David_Zhu.py ###
import os, re
import math
import time
import datetime
import matplotlib.pyplot as plt
import pandas as pd

def execCmd(cmd):
    r = os.popen(cmd)
    text = r.read()
    r.close()
    return text

def ipmicmd(interface, username, password, ip, raw):
    ipmiresponse = execCmd("ipmitool -I " + interface + " -U" + username + " -P" + password + " -H" + ip + " " + raw)
    ipmiresponse = ipmiresponse.strip()
    return ipmiresponse



def SensorReading(response):
    response = response.replace("|", ",")
    #response = response.replace(".", "")
    #response = response.replace(".000", "")
    #response = response.replace(" ", "")
    response = response.splitlines()
    response = list(response)

    list3 = []
    for i in range(len(response)):
        #print(i)
        list3.append(response[i].split(','))
        #print(list3)

    for i in range(len(list3)):
        for j in range(len(list3[0])):
            list3[i][j] = str(list3[i][j]).strip()
            #list3[i][j] = str(list3[i][j]).rstrip("00")
            #list3[i][j] = str(list3[i][j]).rstrip("0")
            list3[i][j] = str(list3[i][j]).rstrip(".")
            if list3[i][j] == "":
                list3[i][j] = " "
    # print(list3)
    return list3



if __name__ == '__main__':
    totaltime = int(input("Input Monitor Time (s): "))
    duringtime = int(input("Input During Time (s): "))
    BMCIP = str(input("Input BMCIP :"))
    BMCID = str(input("Input BMC User ID :"))
    BMCPW = str(input("Input BMC User PW :"))
    TotalData = []
    ThresholdList = []
    Timelist = []
    now = 0

    while now < totaltime:
        sensorread = ipmicmd("lanplus", BMCID, BMCPW, BMCIP, "sensor list")
        # print(sensorread)
        SensorReadings = SensorReading(sensorread)
        # print(SensorReadings)
        for i in range(len(SensorReadings)):
            # print(SensorReadings[i])
            if str(SensorReadings[i][2]) != " " and str(SensorReadings[i][2]) != 'discrete':
                # print(SensorReadings[i])
                ThresholdList.append(SensorReadings[i][0])
                buffer = []
                buffer.append(SensorReadings[i][0])
                buffer.append(SensorReadings[i][1])
                localtime = time.asctime(time.localtime(time.time()))
                Timelist.append(localtime)
                buffer.append(localtime)
                TotalData.append(buffer)           
        time.sleep(duringtime)
        now = now + duringtime
        print("Time Spend : " + str(now) + " s")

    TotalData = sorted(TotalData)
    Timelist = list(dict.fromkeys(Timelist))
    # print(Timelist)

    datajoin = pd.DataFrame(Timelist, columns = ['Time'])
    datajoin = datajoin.set_index('Time')

    ThresholdList = list(dict.fromkeys(ThresholdList))
    # print(datajoin)

    for i in ThresholdList:
        response = pd.DataFrame(TotalData, columns = ['Sensor Nmae', 'Reading', 'Time'])
        response = response.set_index('Sensor Nmae')
        # print(response)
        # print(response.loc[i])
        Data = response.loc[i]
        Data = Data.set_index('Time')
        Data = Data.rename(columns={"Reading":i})
        # Databuffer = Data
        print(Data)
        datajoin = datajoin.join(Data)
    print(datajoin) 



    datajoin = datajoin.replace(to_replace= "na", value = 0)
    datajoin = datajoin.apply(pd.to_numeric,errors='ignore')
    datajoin.to_excel("Sensor Monitor Result.xlsx")

    # print(datajoin['CPU1 Temperature'], 1111111111)

    
    for SensorName in ThresholdList:
        buffer = datajoin[[SensorName]]
        buffer = buffer.apply(pd.to_numeric,errors='ignore')
        # print(buffer, "1111111111111111111111111")
        chart = buffer.plot(title= SensorName + ' Reading Monitor', 
                        xlabel='Time',  
                        ylabel='Reading',  
                        legend=True,  
                        figsize=(100, 50))
        plt.savefig(SensorName +'.pdf', dpi=600)
        # plt.ion()
        # plt.show()
    

    chart = datajoin.plot(title= ' Summary Reading Monitor', 
                        xlabel='Time',  
                        ylabel='Reading',  
                        legend=True,  
                        figsize=(100, 500)) 
    plt.savefig('Summary Reading Monitor.pdf', dpi=600)
    plt.show()
