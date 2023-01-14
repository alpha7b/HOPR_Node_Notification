from settings import TELEGRAM_TOKEN, TELEGRAM_ID, NODES, ON_CHANGE
import requests, time

URL = "https://network.hoprnet.org/api/getNodes?env=36"
stats = {}

while True:
    try:
        response = requests.request("GET", URL)
        msg = ""
        change = False
        for node in response.json():
            if node["peerId"] in NODES:
                if ON_CHANGE:
                    if node["peerId"] in stats:
                        if stats[node["peerId"]] != node["availability24h"]:
                            change = True
                    else:
                        change = True
                    print("node['availability24h'] is: " + str(node["availability24h"]))
                    stats[node["peerId"]] =  node["availability24h"]
                    print("current stats is: ")
                    print(stats)    
                now = time.time()
                lastSeenInMinute = (now - node["lastSeen"]/1000)/60                
                msg += "Node: " + node["peerId"] + "\nAvailability: " + str(node["availability"]*100) + "%\nAvailability 24h: " + str(node["availability24h"]*100) + "%\nLatency:" + str(node["latencyAverage"]) + "ms\nLastSeen:" + str(lastSeenInMinute) + "mins\n\n"
                print("msg is: \n" + msg)
        print(change)
        if (not ON_CHANGE) or (ON_CHANGE and change):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>{msg}</code>"
            requests.get(url)
    except:
        print("something went wrong")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>Something went wrong!</code>"
        requests.get(url)        
    time.sleep(1800)
