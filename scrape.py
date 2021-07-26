import os
import requests
import json

target_id = 0
result_ids = []
result_names = []

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

def DisplayResult():
    global result_ids, result_names
    for x in range(len(result_ids)): print(str(result_names[x])+" :: https://roblox.com/games/"+str(result_ids[x]))
    input("\nPress ENTER to continue")

def RunInput(uin):
    global target_id
    try: target_id = int(uin)
    except ValueError: return False
    return ScrapeUser("All", None)

if __name__=="__main__":
    while True:
        Clear()
        print("Input UserID.")
        if RunInput(input(":: ")):
            DisplayResult()
        
