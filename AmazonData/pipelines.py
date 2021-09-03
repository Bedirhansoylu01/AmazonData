from itemadapter import ItemAdapter
from .settings import BASE_DIR
import sqlite3
from pathlib import Path


class AmazondataPipeline:
    def __init__(self):
        self.setupDBCon()

    def setupDBCon(self):
        self.con = sqlite3.connect(Path(BASE_DIR)/'Scrapy.db')
        self.cur = self.con.cursor()

    # def createTables(self,item):
        # self.dropAmazonTable(item)
        # self.createAmazonTable(self,item)

    # def dropAmazonTable(self,item):
    #    #drop amazon table if it exists
    #    self.cur.execute("DROP TABLE IF EXISTS :category",item)

    def closeDB(self):
        self.con.close()

    def __del__(self):
        self.closeDB()

    def createAmazonTable(self, item):
        category = item["category"]
        self.cur.execute(f"""CREATE TABLE IF NOT EXISTS  '{category}'( id INTEGER PRIMARY KEY NOT NULL, 
            asin TEXT,
            Title TEXT,
            NumberOfReviews REAL, 
            Rating REAL, 
            Price TEXT,
            MainImage TEXT,
            Description TEXT,
            SellerRank TEXT
            )""")

    def storeInDb(self, item):
        category = item["category"]
        self.cur.execute(f"""INSERT INTO '{category}'(
            asin,Title,Rating,NumberOfReviews,MainImage,Price,Description,SellerRank) 
            VALUES( ?,?,?,?,?,?,?,?)""",
                         (item['asin'], item['Title'], item['Rating'], item['NumberOfReviews'], item['MainImage'], item['Price'], item['Description'], item['SellerRank']))

        print(f"""   
        ------------------------------------------------------
                Data Stored in {category} table
        ------------------------------------------------------""")

        self.con.commit()

    def process_item(self, item, spider):
        for k, v in item.items():
            if not v:
                item[k] = ''  # replace empty list or None with empty string
                continue
            if k == 'Title':
                item[k] = v.strip()
            elif k == 'Rating':
                item[k] = v.replace(' out of 5 stars', '')
            elif k == 'AvailableSizes' or k == 'AvailableColors':
                item[k] = ", ".join(v)
            elif k == 'Description':
                item[k] = ", ".join([i.strip() for i in v if i.strip()])
            elif k == 'SellerRank':
                item[k] = " ".join([i.strip() for i in v if i.strip()])
            elif k == 'category':
                item[k] == v.replace(' ', '').replace('\n', '')
        self.createAmazonTable(item)
        self.storeInDb(item)
        return item
