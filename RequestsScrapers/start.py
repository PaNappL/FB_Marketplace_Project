from multiprocessing import Pool, Manager
from functools import partial
from beauty import Beautiful_Check2
from Exceptions.CustomExceptions import *
from userData import userFetch, userUpdate
import math
import msvcrt
import csv, time, os, random

mainPath = "../CSV_Files/"

def get_links() -> list:
    allPath = mainPath+"All_Listings/ALL.csv"
    links = []

    with open(allPath, 'r', encoding='utf-8') as r:
        reader = csv.reader(r, delimiter=',')
        for row in reader:
            links.append(row[0])
            
    return links[1:]

def start_analyser(link: str, used: list, failed: list, p_user: dict) -> None:

    pid = os.getpid()
    user = getUser(pid, p_user)

    sleep(2,5)

    failCount = 0
    savePath = mainPath+"Listing_data/Data.csv"

    if msvcrt.kbhit():
        if msvcrt.getch() == b'q':
            raise ForceEndException('End')

    if len(failed) > 500:
        raise TooManyFailsException("\nToo many failed attempts exception\n")

    if len(used)+len(failed) % 100 == 0:
        print("Checkpoint")

    if (len(used)+len(failed)) % 20 == 0 and (len(used)+len(failed)) != 0:
        sleep(50,120)

    if (len(used)+len(failed)) % 200 == 0 and (len(used)+len(failed)) != 0:
        sleep(250,350)

    if (len(used)+len(failed)) > 2000:
        raise Exception("Fin")

    while failCount<2:
        try:
            bc = Beautiful_Check2()
            bc.get_link_data_save(user, link, savePath)
            used.append(link)
            return
        except NoListingException:
            print("No Listing")
            failed.append(link)
            return
        except NoLoadException as e:
            raise NoLoadException(e)
        except UserDataFail:
            raise UserDataFail
        except Exception as e:
            print(e)
            failCount += 1

    failed.append(link)

def getUser(pid: int, p_user: dict) -> dict:
    pid = str(pid)

    if pid in p_user:
        user = p_user[pid]
    else:
        user = list(p_user["users"])[0]
        p_user["users"] = list(p_user["users"])[1:]
        p_user[pid] = user

    return userFetch().fetchUser(user)

def sleep(LBoundary: int, UBoundary: int) -> None:
    curr_time = time.time()
    sleep_time = random.randint(LBoundary,UBoundary)

    if LBoundary > 49:
        print(f'long sleep for: {sleep_time}')
    else:
        print(f'sleeping for: {sleep_time}')
    new_time = curr_time + sleep_time

    while time.time() < new_time:
        if msvcrt.kbhit():
            if msvcrt.getch() == b'q':
                raise ForceEndException('End')

def reformat_data(data: list) -> list:
    return [[x] for x in data]

def saveFinal(path: str, data: list) -> None:
    data = reformat_data(data)
    with open(path, 'a', newline='') as a:
        writer = csv.writer(a)
        writer.writerows(data)

def updateALL(links: list, used: list) -> None:
    path = mainPath+"All_Listings/ALL.csv"

    newLinks = [x for x in links if x not in used]
    newLinks = [x for x in links if x not in failed]
    newLinks = reformat_data(newLinks)

    with open(path, 'w', newline='') as w:
        writer = csv.writer(w)
        writer.writerow(["Links"])
        writer.writerows(newLinks)

def waited_try(f, path, data):
    fin = False
    while not fin:
        try:
            f(path, data)
            fin = True
        except:
            time.sleep(0.2)

if __name__ == '__main__':
    print("Program started with PID:", os.getpid())
    print(f'Start time: {time.strftime("%H:%M:%S", time.gmtime(time.time()))}')

    users = userFetch().get_users()

    failed = Manager().list()
    used = Manager().list()
    process_user = Manager().dict()

    process_user["users"] = users

    start_time = time.time()
    links = get_links()
    failPath = mainPath+"All_Listings/Failed.csv"
    usedPath = mainPath+"All_Listings/Used.csv"

    index = math.ceil(len(links)/2)

    try:
        with Pool(len(users)) as p:
            p.map(partial(start_analyser, used=used, failed=failed, p_user = process_user),  links[index:])
            # p.map(partial(start_analyser, used=used, failed=failed, user=users["2"]),  links[index:])
    except UserDataFail:
        userUpdate()
    except Exception as e:
        print(e)

    waited_try(saveFinal,failPath,failed)
    waited_try(saveFinal,usedPath,used)
    waited_try(updateALL,links,used)

    # saveFinal(failPath,failed)
    # saveFinal(usedPath,used)
    # updateALL(links, used)

    print(f'Program Finished Executing with {len(used)} processed links')
    print(f'Failed: {len(failed)} times')
    print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
