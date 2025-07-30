import random
import discord
from discord import app_commands
from discord.ext import commands
import os
import requests
import re
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime, timezone

def backup_kanka():   
    # Keep track of date
    date = datetime.today()
    date = f"{datetime.date(date)}T{datetime.time(date)}Z"
    print(date)
    # data=api_call(os.getenv("pom_pom_pom_TOKEN"))
    i=0
    # campaignID = os.getenv(f"DM")
    with open('.env', "r") as f:
        while True:
            dm = str(f.readline())
            # print(re.search('.*TOKEN', dm))

            if re.search('.*TOKEN', dm) is None:

                var = str.split(dm)
                for id in var: 
                    # matches only digits (CampaignID)
                    if re.fullmatch(r"\d+", id):
                        print(id)
                # print(var)

            # print(f.read())
            
            if (i>10):
                break
            i= i+1
            # print(i)


    var = str.split(os.getenv("aileremedia_DM"))

    print(var[1])

    
backup_kanka()