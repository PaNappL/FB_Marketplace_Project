from multiprocessing import Pool, Manager
from functools import partial
from beauty import Beautiful_Check2
from Exceptions.CustomExceptions import *
from userData import userFetch
import csv, time, os, random, msvcrt

mainPath = "../CSV_Files/"

def get_links() -> list:
    allPath = mainPath+"All_Listings/ALL.csv"

    links = []

    with open(allPath, 'r', encoding='utf-8') as r:
        reader = csv.reader(r, delimiter=',')
        for row in reader:
            links.append(row[0])
            
    return links[1:]

def start_analyser(link: str, used: list, failed: list, user: dict) -> None:

    failCount = 0

    while failCount<2:
        bc = Beautiful_Check2()
        try:
            bc.get_link_data_test(user, link)
            used.append(link)
            return
        except NoListingException:
            print("No Listing")
            print(bc.check)
            failed.append(link)
            return
        except NoLoadException as e:
            print(bc.check)
            raise NoLoadException(e)
        except Exception as e:
            print(e)
            print(bc.check)
            failCount += 1

    failed.append(link)

def sleep(LBoundary: int, UBoundary: int):
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
            
if __name__ == '__main__':
    print("Program started with PID:", os.getpid())
    failed = Manager().list()
    used = Manager().list()

    start_time = time.time()
    links = get_links()
    failPath = mainPath+"All_Listings/Failed.csv"
    usedPath = mainPath+"All_Listings/Used.csv"

    links = ["https://www.facebook.com/marketplace/item/887346258940404/?hoisted=false&ref=search&referral_code=null&referral_story_type=post&tracking=browse_serp%3A5f6e8f8f-9e84-4e2b-9adc-57f7ab5c8ad7&__tn__=!%3AD","https://www.facebook.com/marketplace/item/1763250130716656/?hoisted=false&ref=search&referral_code=null&referral_story_type=post&tracking=browse_serp%3Aeceec259-a84a-473d-9fc5-68b38df3b710&__tn__=!%3AD","https://www.facebook.com/marketplace/item/3503113369918912/?hoisted=false&ref=search&referral_code=null&referral_story_type=post&tracking=browse_serp%3A37d724ee-6b46-4be8-85e3-8ca7f58a5ed4&__tn__=!%3AD"]

    user_i = userFetch().get_users()

    try:
        for i in user_i:
            user = userFetch().fetchUser(i)
            print(f'------------------------------------- User : {user["user_id"]} ------------------------------------------')
            start_analyser(links[1],used,failed,user)
    except Exception as e:
        print("err")
        print(e)

    print(f'Program Finished Executing with {len(used)} processed links')
    print(f'Failed: {len(failed)}')
    print('Execution time: ', time.strftime("%H:%M:%S", time.gmtime(time.time() - start_time)))
