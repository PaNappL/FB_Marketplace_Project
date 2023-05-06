import csv
import pandas as pd

filesPath = "C:/Users/zorko/Desktop/Uni/Year3-Project/CSV_Files/All_Listings/"
allPath = filesPath+"ALL.csv"
usedPath = filesPath+"Used.csv"
failedPath = filesPath+"Failed.csv"

class clean_links():

    allL,usedL,failedL,newAll = [],[],[],[]

    def __init__(self) -> None:
        self.load_Files()
        self.remove_copies()
        self.update_file()

    def load_Files(self):
        df = pd.read_csv(allPath)
        udf = pd.read_csv(usedPath)
        fdf = pd.read_csv(failedPath)
        # df = df.drop_duplicates()
        # print(len(df.index))

        self.allL = df["Links"].to_list()
        self.usedL = udf["Links"].to_list()
        self.failedL = fdf["Links"].to_list()

    def remove_copies(self):
        allSet = set(self.allL)
        usedSet = set(self.usedL)

        self.newAll = allSet - usedSet
        print(f'Removed {len(self.allL)-len(self.newAll)} Links :)')
        print(f'Before: {len(self.allL)}, After: {len(self.newAll)}')

    def update_file(self):
        with open(allPath, 'w', newline="") as w:
            writer = csv.writer(w)
            writer.writerow(["Links"])
            for link in self.newAll:
                writer.writerow([link])

if __name__ == "__main__":
    clean_links()