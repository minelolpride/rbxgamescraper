import sys
import os
import glob
import requests
import json
import webbrowser

target_type = "users" # users, groups, groupusers
target_id = 0
result_ids = []
result_uids = []
result_names = []
gresult_ids = []
gresult_uids = []
gresult_names = []
last_response_code = 0
echo_last_response_info = False

loaded_ids = []
loaded_uids = []
loaded_names = []


if sys.version_info < (3, 10):
	raise Exception("py version not at least 3.10!")

def DoNothing(): return

def Clear(clear_vars):
    global last_response_code, target_id
    global result_ids, result_uids, result_names
    global gresult_ids, gresult_uids, gresult_names
    global loaded_ids, loaded_uids, loaded_names

    if clear_vars:
        target_id = 0
        result_ids.clear()
        result_uids.clear()
        result_names.clear()
        gresult_ids.clear()
        gresult_uids.clear()
        gresult_names.clear()
        loaded_ids.clear()
        loaded_uids.clear()
        loaded_names.clear()
        last_response_code = 0

    os.system("cls" if os.name in ("nt", "dos") else "clear")

def LoadCurrentStoredData(filep):
    global target_type, target_id, loaded_ids, loaded_uids, loaded_names
    loaded_ids.clear()
    loaded_uids.clear()
    loaded_names.clear()
    try: utx = open(filep, "r", encoding="utf-8-sig")
    except OSError: return False # probably no file
    udat = utx.read()
    lines = udat.splitlines()
    for l in range(len(lines)): 
        f = lines[l].split(" | ")
        loaded_names.append(f[0]) # name
        loaded_uids.append(f[1][4:]) # uid
        loaded_ids.append(f[2][25:]) # pid

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
    global target_type, target_id, result_ids, result_uids, result_names, loaded_ids, loaded_uids, loaded_names
    print("Saving places...")
    match target_type:
        case "users":
            target_info = Request("https://users.roblox.com/v1/users/"+str(target_id))
            target_name = "USER-"+str(target_info["id"])+" ("+str(target_info["name"])+").txt"
        case "groups":
            target_info = Request("https://groups.roblox.com/v1/groups/"+str(target_id))
            target_name = "GROUP-"+str(target_info["id"])+" ("+str(target_info["name"])+").txt"
    
    LoadCurrentStoredData(target_name)

    target_file = open(target_name, "w", encoding='utf-8-sig')
    for x in range(len(result_ids)): 
        if len(loaded_ids) > 0:
            if str(result_ids[x]) in loaded_ids:
                del loaded_ids[loaded_ids.index(str(result_ids[x]))]
                del loaded_names[loaded_names.index(str(result_names[x]))]
                del loaded_uids[loaded_uids.index(str(result_uids[x]))]

        target_file.write(result_names[x]+" | UID:"+str(result_uids[x])+" | https://roblox.com/games/"+str(result_ids[x])+"\n")
    if len(loaded_ids) > 0:
        for x in range(len(loaded_ids)):
            target_file.write(loaded_names[x]+" | UID:"+str(loaded_uids[x])+" | https://roblox.com/games/"+str(loaded_ids[x])+"\n")
    target_file.close()

def DisplayResult():
    global result_ids, result_uids, result_names
    Clear(False)

    for x in range(len(result_ids)): print("["+str(x)+"] | "+result_names[x]+" | UID:"+str(result_uids[x])+" | https://roblox.com/games/"+str(result_ids[x]))
    usel = input("\nWhat to do? [ (C)ontinue, (S)ave, Open (A)ll, Open (#) ]: ")
    match usel.lower():
        case 'c': return
        case 's': SaveResult(); return
        case 'a': OpenResult(result_ids)
    
    try: OpenResult(result_ids[int(usel)]) if int(usel) < len(result_ids) and int(usel) >= 0 else DoNothing()
    except ValueError: pass
    DisplayResult()

def ScrapeUsersGroups(access, cursor):
    global target_type, target_id, result_ids, result_uids, result_names

    if cursor == None: rd = Request("https://games.roblox.com/v2/"+target_type+"/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50")
    else: rd = Request("https://games.roblox.com/v2/"+target_type+"/"+str(target_id)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50&cursor="+cursor)

    if "data" in rd:
        for x in range(len(rd["data"])):
            result_ids.append(rd["data"][x]["rootPlace"]["id"])
            result_uids.append(rd["data"][x]["id"])
            result_names.append(rd["data"][x]["name"])
            print("\rPlaces: "+str(len(result_ids)), end="")
        if rd.get("nextPageCursor") != None: return ScrapeUsersGroups(access, str(rd["nextPageCursor"]))
        else: print()
    else:
        if echo_last_response_info: print("ScrapeUsersGroups(): STATUS ", last_response_code, rd)
        match str(last_response_code):
            case "501": return ScrapeUsersGroups("Public", cursor)
    return True

def ScrapeGroupUsers_ScrapeUser(uid, access, cursor, gid, gname):
    global last_response_code, gresult_ids, gresult_uids, gresult_names, loaded_ids, loaded_uids, loaded_names
    dont_write_empty_users_to_file = True # no reason to disable it but i'll leave that to you

    if cursor == None: rd = Request("https://games.roblox.com/v2/users/"+str(uid)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50")
    else: rd = Request("https://games.roblox.com/v2/users/"+str(uid)+"/games?sortOrder=Asc&accessFilter="+access+"&limit=50&cursor="+cursor)

    if "data" in rd:
        for x in range(len(rd["data"])):
            gresult_ids.append(rd["data"][x]["rootPlace"]["id"])
            gresult_uids.append(rd["data"][x]["id"])
            gresult_names.append(rd["data"][x]["name"])
        if rd.get("nextPageCursor") != None: return ScrapeGroupUsers_ScrapeUser(uid, access, str(rd["nextPageCursor"]))

        if dont_write_empty_users_to_file and len(gresult_ids) == 0: return False

        group_folder_name = "GROUP-"+str(gid)+" ("+gname+")"
        target_info = Request("https://users.roblox.com/v1/users/"+str(uid))

        try: os.mkdir(group_folder_name)
        except FileExistsError: pass
        out_name = os.path.join(os.path.dirname(__file__), group_folder_name, "USER-"+str(target_info["id"])+" ("+str(target_info["name"])+").txt")

        LoadCurrentStoredData(out_name)
        output_file = open(out_name, "w", encoding='utf-8-sig')

        for x in range(len(gresult_ids)): 
            if len(loaded_ids) > 0:
                if str(gresult_ids[x]) in loaded_ids:
                    del loaded_ids[loaded_ids.index(str(gresult_ids[x]))]
                    del loaded_names[loaded_names.index(str(gresult_names[x]))]
                    del loaded_uids[loaded_uids.index(str(gresult_uids[x]))]

            output_file.write(gresult_names[x]+" | UID:"+str(gresult_uids[x])+" | https://roblox.com/games/"+str(gresult_ids[x])+"\n")
        if len(loaded_ids) > 0:
            for x in range(len(loaded_ids)):
                output_file.write(loaded_names[x]+" | UID:"+str(loaded_uids[x])+" | https://roblox.com/games/"+str(loaded_ids[x])+"\n")
        output_file.close()
    else:
        if echo_last_response_info: print("ScrapeGroupUsers_ScrapeUser(): STATUS", last_response_code, rd)
        match str(last_response_code):
            case "501": return ScrapeGroupUsers_ScrapeUser(uid, "Public", cursor, gid, gname)

def ScrapeGroupUsers_GetUsers(g_id, r_id, cursor):
    global last_response_code
    userlist = []

    if r_id == "ALL":
        if cursor == None: rd = Request("https://groups.roblox.com/v1/groups/"+str(g_id)+"/users?limit=100&sortOrder=Asc")
        else: rd = Request("https://groups.roblox.com/v1/groups/"+str(g_id)+"/users?limit=100&sortOrder=Asc&cursor="+cursor)

        if "data" in rd:
            for x in range(len(rd["data"])): userlist.append(rd["data"][x]["user"]["userId"])
            if rd.get("nextPageCursor") != None: ScrapeGroupUsers_GetUsers(g_id, r_id, str(rd["nextPageCursor"]))
            else: return userlist
        else:
            print("STATUS ", last_response_code, rd)
    else:
        if cursor == None: rd = Request("https://groups.roblox.com/v1/groups/"+str(g_id)+"/roles/"+str(r_id)+"/users?limit=100&sortOrder=Asc")
        else: rd = Request("https://groups.roblox.com/v1/groups/"+str(g_id)+"/roles/"+str(r_id)+"/users?limit=100&sortOrder=Asc&cursor="+cursor)

        if "data" in rd:
            for x in range(len(rd["data"])): userlist.append(rd["data"][x]["userId"])
            if rd.get("nextPageCursor") != None: ScrapeGroupUsers_GetUsers(g_id, r_id, str(rd["nextPageCursor"]))
            else: return userlist
        else:
            if echo_last_response_info: print("ScrapeGroupUsers_GetUsers(): STATUS", last_response_code, rd)
    
def ScrapeGroupUsers_DisplayRanks(g_name, g_ucount, r_names, r_ucounts):
    Clear(False)

    print("group "+g_name+" has "+str(g_ucount)+" users in "+str(len(r_names))+" ranks")
    for x in range(len(r_names)): print("["+str(x)+"] | "+r_names[x]+" ("+str(r_ucounts[x])+" users)")
    usel = input("\nSelect a rank [ (#), (A)ll, (C)ancel ]: ")

    match usel.lower():
        case "a": return "ALL_USERS"
        case "c": return False

    try: return int(usel) if int(usel) < len(r_names) and int(usel) >= 0 else ScrapeGroupUsers_DisplayRanks(g_name, g_ucount, r_names, r_ucounts)
    except ValueError: pass

    return ScrapeGroupUsers_DisplayRanks(g_name, g_ucount, r_names, r_ucounts)

def ScrapeGroupUsers():
    global target_id, gresult_ids, gresult_uids, gresult_names
    group_info = Request("https://groups.roblox.com/v1/groups/"+str(target_id))
    group_name = group_info["name"]
    group_ucount = group_info["memberCount"]
    group_ranks = Request("https://groups.roblox.com/v1/groups/"+str(target_id)+"/roles")
    group_rank_ids = []
    group_rank_names = []
    group_rank_ucount = []

    for x in range(len(group_ranks["roles"])):
        group_rank_ids.append(group_ranks["roles"][x]["id"])
        group_rank_names.append(group_ranks["roles"][x]["name"])
        group_rank_ucount.append(group_ranks["roles"][x]["memberCount"])

    group_rank_to_scrape = ScrapeGroupUsers_DisplayRanks(group_name, group_ucount, group_rank_names, group_rank_ucount)
    if group_rank_to_scrape == "ALL_USERS": group_target_ids = ScrapeGroupUsers_GetUsers(target_id, "ALL", None)
    elif group_rank_to_scrape: group_target_ids = ScrapeGroupUsers_GetUsers(target_id, group_rank_ids[group_rank_to_scrape], None)
    else: return False

    try:
        for x in range(len(group_target_ids)):
            gresult_ids.clear()
            gresult_uids.clear()
            gresult_names.clear()
            print("\r"+str(x+1)+" / "+str(len(group_target_ids)), end="")
            ScrapeGroupUsers_ScrapeUser(group_target_ids[x], "All", None, target_id, group_name)
    except TypeError: ScrapeGroupUsers_ScrapeUser(group_target_ids, "All", None, target_id, group_name)

    return False


def RunInput(uin):
    global target_type, target_id

    match uin:
        case 'u': target_type = "users"
        case 'g': target_type = "groups"
        case 'z': target_type = "groupusers"
        case 'q': exit()

    try: target_id = int(uin)
    except ValueError: return False

    if target_type == "groupusers": return ScrapeGroupUsers()
    else: return ScrapeUsersGroups("All", None)

if __name__=="__main__":
    while True:
        Clear(True)
        print("Type 'u' to scrape user\n"\
            "Type 'g' to scrape group\n"\
            "Type 'z' to scrape group users\n"\
            "Type 'q' to quit")
        if RunInput(input(target_type+" :: ")):
            DisplayResult()
        
