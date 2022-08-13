import bs4
import time
import pandas
import datetime
import chromedriver_autoinstaller
chromedriver_autoinstaller.install()
# from selenium.webdriver import Keys, ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver import Chrome,ChromeOptions
import csv


class OnePieceScraper:
    def __init__(self,url,card_type,card_language,card_year):
        self.base_url = url
        self.card_type = card_type
        self.card_language = card_language
        self.card_year = card_year
        self.rarity = {
                            "L":"Leader",
                            "C":"Common",
                            "UC":"Uncommon",
                            "R":"Rare",
                            "SR":"Super Rare",
                            "SEC":"Secret Rare",
                            "P":"Promo"
                        }
        self.scraper()

    def scraper(self):
        option = ChromeOptions()
        # option.headless = True
        # option.add_argument("window-size=1920,1080")
        self.driver = Chrome(options=option)

        print("Loading Website................")
        self.driver.get(self.base_url)
        self.driver.maximize_window()

        print("Loading Options................")
        options = self.list_options()[1:]
        self.option_chosen = 'all'


        button = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "#cardlist > main > article > div > div.searchCol > form > div.formsetDefaultArea > div.seriesCol > button")))
        button.click()

        el = self.driver.find_element(By.CLASS_NAME, 'selModalList')




        choices = el.find_elements(By.CLASS_NAME, "selModalClose")
        for each in choices:
            if each.get_attribute("innerHTML").lower()==self.option_chosen:
                each.click()

        searchBtn = WebDriverWait(self.driver, 5).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR,
                                        "#cardlist > main > article > div > div.searchCol > form > div.commonBtn.submitBtn > input[type=submit]")))
        searchBtn.click()


        time.sleep(5)

        html = self.driver.page_source


        self.driver.close()

        self.data = self.scrape_html(html)
        self.write_to_output(self.data)

    def scrape_html(self,html):
        data = []
        soup = bs4.BeautifulSoup(html,'lxml')

        a_tags  = soup.find_all("a",attrs={"class":"modalOpen"})
        dl_tags = soup.find_all("dl",attrs={"class":"modalCol"})

        if len(a_tags)!=len(dl_tags):
            raise Exception("Error, Contact dev.")

        max_len = len(dl_tags)
        for each in range(max_len):
            a_t = a_tags[each]
            dl_t = dl_tags[each]
            card_image = a_t.find("img")["src"]
            card_image = card_image.replace('..','https://asia-en.onepiece-cardgame.com/')

            card_infor = dl_t.find("div",attrs={"class":["infoCol"]})
            card_infor = card_infor.text

            card_number,card_rarity_short,card_detail = card_infor.split('|')
            card_number, card_rarity_short, card_detail = card_number.strip(),card_rarity_short.strip(),card_detail.strip()
            card_rarity = self.rarity[card_rarity_short.upper()]


            card_name = dl_t.find("div",attrs={"class":["cardName"]})
            card_name = card_name.text

            card_info_intern = dl_t.find("div", attrs={"class": ["getInfo"]})
            card_info_intern = card_info_intern.text
            try:
                card_info_intern.replace('Card Set(s)','')
            except:
                pass


            card_set_name = card_info_intern if self.option_chosen.lower().strip()=='all' else self.option_chosen

            try:
                card_set_type = card_info_intern.split('- ')[1]
            except:
                card_set_type = ""
            print("-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------")
            print(self.card_type)
            print(self.card_language)
            print(self.card_year)
            print(card_name)
            print(card_set_name)
            print(card_number)
            print(card_rarity)
            print(card_rarity_short)
            print(card_detail)
            print(card_set_type)
            print(card_image)
            print("")
            print(card_info_intern)
            data.append([self.card_type,self.card_language,self.card_year,card_name,card_set_name,card_number,card_rarity,card_rarity_short,card_detail,card_set_type,card_image,"",card_info_intern])


        return data


    def list_options(self):
        options = []
        el = self.driver.find_element(By.CLASS_NAME, 'selModalList')

        choices = el.find_elements(By.CLASS_NAME,"selModalClose")

        for each in choices:
            options.append(each.get_attribute("innerHTML"))

        return options


    def write_to_output(self,data):
        header = ["card_type","card_language","card_year","card_name","card_set_name","card_number","card_rarity","card_rarity_short","card_detail","set_type","image_url","card_special","info_intern"]
        name_csv = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M.csv")
        name_excel = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M.xlsx")

        with open(name_csv,'w',encoding='utf8',errors='ignore') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            for each in data:
                csv_writer.writerow(each)

        df = pandas.DataFrame(data,columns=header)
        df.to_excel(name_excel)



if __name__ == '__main__':
    base_url = 'https://asia-en.onepiece-cardgame.com/cardlist/'
    card_type = "One Piece Card Game"
    card_language = "Japanese"
    card_year = datetime.datetime.today().year

    OnePieceScraper(base_url,card_type,card_language,card_year)