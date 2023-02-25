from settings import TELEGRAM_TOKEN, TELEGRAM_ID, NODES, ON_CHANGE, INTERVAL, STAKE_WALLETS, ON_REWARD_CHANGE
import requests, time, pandas

URL = "https://network.hoprnet.org/api/getNodes?env=36"
REWARD_URL = "https://stake.hoprnet.org/api/getRewards?peerId="
stats = {}
reward = 0

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
                    print("node['availability24h'] is: " + str(node["availability24h"]) + "\n\n")
                    print("node['nextEstRewards'] is: " + str(node["nextEstRewards"]) + "\n\n")
                    print("node['count'] is: " + str(node["count"]) + "\n\n")
                    stats[node["peerId"]] =  node["availability24h"]
                    print("current stats is: " + str(stats) + "\n\n")
                    
                now = time.time()
                lastSeenInMinute = (now - node["lastSeen"]/1000)/60                
                msg += "Node: " + node["peerId"] + "\n" + \
                "Availability: " + str(format(node["availability"]*100, '.2f')) + "%\n" + \
                "Availability 24h: " + str(format(node["availability24h"]*100, '.2f')) + "%\n" + \
                "Latency:" + str(format(node["latencyAverage"], '.2f')) + "ms\n" + \
                "LastSeen:" + str(format(lastSeenInMinute, '.2f')) + "min\n" + \
                "Ping:" + str(node["count"]) + "\n" + \
                "nextEstRewards:" + str(format(node["nextEstRewards"], '.2f')) + " HOPR\n\n"

                print("msg is: \n" + msg + "\n\n")
        print("Is status changed? " + str(change))

        total_reward = 0
        for address in STAKE_WALLETS:
            response = requests.request("GET", REWARD_URL+address)
            total_reward += (response.json()[0]['rewards'])
        msg+= "\n💸Totoal Reward:" + str(total_reward) + " HOPR\n\n"
        print("msg with reward is: \n" + msg)

        if (not ON_CHANGE) or (ON_CHANGE and change):
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>{msg}</code>"
            requests.get(url)
        elif (ON_REWARD_CHANGE and (reward  != total_reward)):
            msg = "💸Reward:" + str(total_reward) + " HOPR"
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>{msg}</code>"
            requests.get(url)
            reward = total_reward

    except Exception as e:
        print(str(e))
        print("something went wrong")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>Something went wrong!</code>"
        requests.get(url)        
    time.sleep(int(INTERVAL))
