import schedule 
import time
import os
import requests
import re
import json
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

REQUEST_PATH = "https://api.kanka.io/1.0/"
MSG_ENTITY_NOT_FOUND = "Entity not found."
MSG_REQUIRE_TOKEN = "Please provide token"
MSG_NO_MATCHING_CAMPAIGN = "Found no matching campaign. \nPlease check that server matches Kanka campaign"
ENTITY_TYPE = ["characters", "locations", "journals", "notes", "maps", "creatures"]

def backup():
    campaign_name =[]
    campaign_id = []
    player_name= []
    player_id=[]
    campaign_number=0

    with open(".env", "r") as f:

        line =f.readline()

        # This will parse the env to create players and campaigns
        while True:
            line =f.readline()
            if line == "" or line == EOFError:
                break
            else:
                current_line = line

                # if not a token we will treat as campaign
                if re.search("TOKEN", current_line) is None:
                    splitEnv = str.split(current_line)

                    # Seperate campaign into ID and Name
                    campaign_name.append(splitEnv[0].replace('_'," "))
                    campaign_id.append(splitEnv[-1])
                # otherwise treat as player
                else: 
                    splitEnv = str.split(current_line)
                    
                    #sperate player and token
                    
                    player_name.append(re.sub('_TOKEN', "", splitEnv[0]))
                    player_id.append(splitEnv[-1])
        print(campaign_name)
        print (campaign_id)
        print(player_name)

        for id in campaign_id:
            if not os.path.exists(f"./backup"):
                os.makedirs(f"./backup")
            if os.path.exists(f"./campaigns/{campaign_name[campaign_number]}"):
                os.rename(f"./campaigns/{campaign_name[campaign_number]}", f"./backup/{campaign_name[campaign_number]}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}")
                    
            player_number = 0
            for player in player_id:
                for type in ENTITY_TYPE:
                    page = 1
                    data = []

                    while True:
                        success = False
                        while not success:
                            url = f"{REQUEST_PATH}campaigns/{id}/{type}?page={page}"

                            headers = {
                                'Content-Type': 'application/json',
                                'Accept': 'application/json',
                                'Authorization': 'Bearer ' + player
                            }
                            response = requests.request("GET", url, headers=headers)

                            print (f"Player: {player_name[player_number]}")
                            print(f"Campaign: {id}")
                            # Check if rate limit if no continue
                            if response.status_code == 429:
                                print(f"Error: {response.status_code} - {response.text}")
                                print("Waiting for 60 seconds")
                                time.sleep(60)
                            else:
                                success = True

                        # If other problem print and tell me
                        if response.status_code != 200:
                            print(f"Error: {response.status_code} - {response.text}")
                            break
                        elif response.headers["Content-Type"] != "application/json":
                            print(f"Error: {response.status_code} - {response.headers['Content-Type']}")
                            break

                        # If no problem add to the list
                        response = response.json()
                        data.extend(response["data"])

                        # if end of data move on
                        if response["links"]["next"] is None:
                            print("Reached end of pages")
                            break

                        page+=1
                    # after specific type is done make file and folders
                    # if path doesn't exist make new path
                    if not os.path.exists(f"./campaigns/{campaign_name[campaign_number]}/{player_name[player_number]}"):
                        os.makedirs(f"./campaigns/{campaign_name[campaign_number]}/{player_name[player_number]}")
                    # Creates the jsons for player info
                    with open(f'./campaigns/{campaign_name[campaign_number]}/{player_name[player_number]}/{type}.json', 'w', encoding='utf-8') as f:
                        json.dump(data, f, ensure_ascii=False, indent=4)
                # Update plyaer number after types are collected
                player_number=player_number+1
            # Update campaign after campaign is done
            campaign_number=campaign_number+1

schedule.every().day.at("01:00").do(backup)
print("this is where we are")

while True:
    print("Should bot run backup?")
    schedule.run_pending()
    time.sleep(60)