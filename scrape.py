import sys
import os
import requests
import json

target_type = "user" # user, group
target_id = 0
result_ids = []
result_names = []

if sys.version_info < (3, 10):
	raise Exception("py version not at least 3.10!")

def Clear():
    os.system("cls" if os.name in ("nt", "dos") else "clear")
    
def ScrapeUser(access, cursor):
    global target_id, result_ids, result_names
    if cursor == None: rd = requests.get("https://games.roblox.com/v2/users/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50").json()
    else: rd = requests.get("https://games.roblox.com/v2/users/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50&cursor="+cursor).json()
    if "errors" in rd:
        if access == "All":
            return ScrapeUser("Public", cursor)
        else:
            print(str(rd))
            input("Press ENTER to continue.")
            return False
    if "data" in rd:
        for x in range(len(rd["data"])):
            result_ids.append(rd["data"][x]["rootPlace"]["id"])
            result_names.append(rd["data"][x]["name"])
    if rd["nextPageCursor"] != None: return ScrapeUser(access, str(rd["nextPageCursor"]))
    else: return True

def ScrapeGroup(access, cursor):
    global target_id, result_ids, result_names
    if cursor == None: rd = requests.get("https://games.roblox.com/v2/groups/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50").json()
    else: rd = requests.get("https://games.roblox.com/v2/groups/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50&cursor="+cursor).json()
    if "errors" in rd:
        if access == "All":
            return ScrapeGroup("Public", cursor)
        else:
            print(str(rd))
            input("Press ENTER to continue.")
            return False
    if "data" in rd:
        for x in range(len(rd["data"])):
            result_ids.append(rd["data"][x]["rootPlace"]["id"])
            result_names.append(rd["data"][x]["name"])
    if rd["nextPageCursor"] != None: return ScrapeGroup(access, str(rd["nextPageCursor"]))
    else: return True

def DisplayResult():
    global result_ids, result_names
    for x in range(len(result_ids)): print(result_names[x]+" :: https://roblox.com/games/"+str(result_ids[x]))
    input("\nPress ENTER to continue")

def RunInput(uin):
    global target_type, target_id
    match uin:
        case 'u': target_type = "user"
        case 'g': target_type = "group"
    try: target_id = int(uin)
    except ValueError: return False
    match target_type:
        case "user": return ScrapeUser("All", None)
        case "group": return ScrapeGroup("All", None)

if __name__=="__main__":
    while True:
        Clear()
        print("Type 'u' to scrape user\nType 'g' to scrape group")
        if RunInput(input(target_type+" :: ")):
            DisplayResult()
        
