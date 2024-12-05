import json,time
from flask import Flask
import requests
import json
import matplotlib.pyplot as plt

app = Flask(__name__)

baseUrl = "http://127.0.0.1:5000"

payload_on = {"charging": "on"} 
payload_off = {"charging": "off"}
discharge_payload = {"discharging": "on"}

headers = {'Content-Type': 'application/json'} 

avrigePrise = 83
canCharge = 3.6
maxCharge = 10
stopCharge = 79
prev_battery = 20
isDoneCharging = False

rec_time = []
rec_price = []
rec_energi = []
rec_current_baseload = []
rec_baseload = []


requests.post(baseUrl + "/discharge", data=json.dumps(discharge_payload), headers=headers)

while isDoneCharging == False:
    server_i_op = requests.get(baseUrl + "/info")
    server_pph_op = requests.get(baseUrl + "/priceperhour")
    server_c_op = requests.get(baseUrl + "/charge")
    server_bl_op = requests.get(baseUrl + "/baseload")

    if server_i_op.status_code == 200 and server_pph_op.status_code == 200 and server_c_op.status_code == 200 and server_bl_op.status_code == 200:
        serverInfo = json.loads(server_i_op.text)
        serverPrice = json.loads(server_pph_op.text)
        serverBattery = json.loads(server_c_op.text)
        serverbaseload = json.loads(server_bl_op.text)
        hour = serverInfo["sim_time_hour"]
        minutes = serverInfo["sim_time_min"]
        loading = serverInfo["ev_battery_charge_start_stopp"]
        battery = serverBattery
        
        rec_time.append(float(hour + (minutes / 60)))
        rec_energi.append(battery)
        rec_price.append(serverPrice[hour])
        rec_baseload.append(serverbaseload[hour])
        rec_current_baseload.append(serverInfo["base_current_load"])
        
        print("________________\n") 

        print("H: " + str(hour) + " M: " + str(minutes))
        print("current base load: " + str(serverInfo["base_current_load"]))
        print("price: " + str(serverPrice[hour]) + " [H: " + str(hour) + " - " + str(hour + 1) + " ]")
        print("base load " + str(serverbaseload[hour]) + " at [H: " + str(hour) + " ]")
        print(str(battery) + "%")

        print("________________\n") 
        
        if serverPrice[hour] < avrigePrise and battery < stopCharge:
            if serverInfo["base_current_load"] < canCharge and loading == False:
                res = requests.post(baseUrl + "/charge", data=json.dumps(payload_on), headers=headers)
                loading = True

            elif serverInfo["base_current_load"] > maxCharge:
                res = requests.post(baseUrl + "/charge", data=json.dumps(payload_off), headers=headers)
                loading = False
            print("Charge: +" + str(battery - prev_battery) + "%")
            prev_battery = battery
        else:
            if loading == True:
                res = requests.post(baseUrl + "/charge", data=json.dumps(payload_off), headers=headers)
                loading = False

        if hour == 23 and minutes == 45:
            isDoneCharging = True
    time.sleep(1)

plt.figure() 
plt.plot(rec_time, rec_energi) 
plt.yscale('linear') 
plt.xscale('linear') 
plt.title('energi per time') 

plt.show() 

#current baseload
plt.figure() 
plt.plot(rec_time, rec_current_baseload) 
plt.yscale('linear') 
plt.xscale('linear') 
plt.title('curent baseload per time') 

plt.show() 

#baseload
plt.figure() 
plt.plot(rec_time, rec_baseload) 
plt.yscale('linear') 
plt.xscale('linear') 
plt.title('baseload per time') 

plt.show() 

#price
plt.figure() 
plt.plot(rec_time, rec_price) 
plt.yscale('linear') 
plt.xscale('linear') 
plt.title('price per time') 

plt.show() 