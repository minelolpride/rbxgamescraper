import sys
import os
import requests
import json
import webbrowser

target_type = "users" # users, groups
target_id = 0
result_ids = []
result_names = []
last_response_code = 0

if sys.version_info < (3, 10):
	raise Exception("py version not at least 3.10!")

def Clear(clear_vars):
    global target_id, result_names, result_ids, last_response_code
    if clear_vars:
        target_id = 0
        result_ids.clear()
        result_names.clear()
        last_response_code = 0
    os.system("cls" if os.name in ("nt", "dos") else "clear")

def Request(url): 
    global last_response_code
    data_raw = requests.get(url)
    last_response_code = data_raw.status_code
    return json.loads(data_raw.content.decode('utf-8-sig'))

def OpenResult(ids):
    try: 
        for x in range(len(ids)): webbrowser.open("https://roblox.com/games/"+str(ids[x]), new=0)
    except TypeError: webbrowser.open("https://roblox.com/games/"+str(ids), new=0)

def SaveResult():
    global target_type, target_id, result_ids, result_names
    match target_type:
        case "users":
            target_info = Request("https://users.roblox.com/v1/users/"+str(target_id))
            target_name = "USER-"+str(target_info["id"])+" ("+str(target_info["name"])+").txt"
        case "groups":
            target_info = Request("https://groups.roblox.com/v1/groups/"+str(target_id))
            target_name = "GROUP-"+str(target_info["id"])+" ("+str(target_info["name"])+").txt"
    target_file = open(target_name, "w", encoding='utf-8-sig')
    for x in range(len(result_ids)): target_file.write(result_names[x]+" :: https://roblox.com/games/"+str(result_ids[x])+"\n")
    target_file.close()

def DisplayResult():
    global result_ids, result_names
    Clear(False)
    for x in range(len(result_ids)): print("["+str(x)+"] :: "+result_names[x]+" :: https://roblox.com/games/"+str(result_ids[x]))
    usel = input("\nWhat to do? [ (C)ontinue, (S)ave, Open (A)ll, Open (#) ]: ")
    match usel.lower():
        case 'c': return
        case 's':
            SaveResult()
            return
        case 'a': 
            OpenResult(result_ids)
            DisplayResult()
    
    try: OpenResult(result_ids[int(usel)])
    except ValueError: pass
    DisplayResult()

def ScrapeUsersGroups(access, cursor):
    global target_type, target_id, result_ids, result_names
    if cursor == None: rd = Request("https://games.roblox.com/v2/"+target_type+"/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50")
    else: rd = Request("https://games.roblox.com/v2/"+target_type+"/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50&cursor="+cursor)
    if "errors" in rd:
        if access == "All": return ScrapeUsersGroups("Public", cursor)
        else:
            print(str(rd))
            input("Press ENTER to continue.")
            return False
    if "data" in rd:
        for x in range(len(rd["data"])):
            result_ids.append(rd["data"][x]["rootPlace"]["id"])
            result_names.append(rd["data"][x]["name"])
    if "nextPageCursor" in rd:
        if rd["nextPageCursor"] != None: return ScrapeUsersGroups(access, str(rd["nextPageCursor"]))
    return True

def RunInput(uin):
    global target_type, target_id
    match uin:
        case 'u': target_type = "users"
        case 'g': target_type = "groups"
    try: target_id = int(uin)
    except ValueError: return False
    return ScrapeUsersGroups("All", None)

if __name__=="__main__":
    while True:
        Clear(True)
        print("Type 'u' to scrape user\nType 'g' to scrape group")
        if RunInput(input(target_type+" :: ")):
            DisplayResult()
        
