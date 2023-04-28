from settings_nodename import TELEGRAM_TOKEN, TELEGRAM_ID, NODES, ON_CHANGE, INTERVAL
import requests, time, pandas

URL = "https://network.hoprnet.org/api/getNodes?env=36"
REWARD_URL = "https://stake.hoprnet.org/api/getRewards?peerId="
stats = {}
reward = 0

while True:
    try:
        response = requests.request("GET", URL)
        nodes_data = response.json()['nodes']
        msg = ""
        change = False
        totalNextEstRewards = 0
        for node_name, hopr_address in NODES.items():
            found_node = None
            for node in nodes_data:
                if node["peerId"] == hopr_address:
                    found_node = node
                    break
            
            if found_node:
                if ON_CHANGE:
                    if node_name in stats:
                        if stats[node_name] != found_node["availability24h"]:
                            change = True
                    else:
                        change = True
                    stats[node_name] = found_node["availability24h"]

                totalNextEstRewards += found_node["nextEstRewards"]
                now = time.time()
                lastSeenInMinute = (now - found_node["lastSeen"] / 1000) / 60

                msg += "Node: " + node_name + "\n" + \
                       "HOPR Address: " + hopr_address + "\n" + \
                       "Availability: " + str(format(found_node["availability"] * 100, '.2f')) + "%\n" + \
                       "Availability 24h: " + str(format(found_node["availability24h"] * 100, '.2f')) + "%\n" + \
                       "Latency:" + str(format(found_node["latencyAverage"], '.2f')) + "ms\n" + \
                       "Last Seen:" + str(format(lastSeenInMinute, '.2f')) + "min\n" + \
                       "Ping:" + str(found_node["count"]) + "\n" + \
                       "Next Estimated Rewards:" + str(format(found_node["nextEstRewards"], '.2f')) + " HOPR\n\n"

        print("Total Next Estimated Rewards: " + str(totalNextEstRewards))
        print("Is status changed? " + str(change))

        if (not ON_CHANGE) or (ON_CHANGE and change):
            msg += "💸 Total rewards: " + str(totalNextEstRewards) + " HOPR"
            url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>{msg}</code>"
            requests.get(url)

    except Exception as e:
        print(str(e))
        print("Something went wrong")
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_ID}&parse_mode=HTML&text=<code>Something went wrong!</code>"
        requests.get(url)

    time.sleep(int(INTERVAL))
