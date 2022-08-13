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
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import threading
from PIL import ImageTk,Image
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
        # self.scraper()

    def get_options(self,set_options,choose_set_button):

        option = ChromeOptions()
        option.headless = True
        option.add_argument("window-size=1920,1080")
        self.driver = Chrome(options=option)

        print("Loading Website................")
        self.driver.get(self.base_url)
        self.driver.maximize_window()

        print("Loading Options................")
        self.options = self.list_options()[1:]
        print(self.options)

        set_options.pack(side=LEFT, padx=5, pady=5)
        choose_set_button.pack(side=LEFT)

        set_options['values'] = self.options

    def get_html_from_driver(self,option_chosen):
        self.option_chosen = option_chosen


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
                card_info_intern = card_info_intern.replace('Card Set(s)','')
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
            options.append(each.get_attribute("innerText"))

        return options


    def write_to_output(self,data):
        header = ["card_type","card_language","card_year","card_name","card_set_name","card_number","card_rarity","card_rarity_short","card_detail","set_type","image_url","card_special","info_intern"]
        name_csv = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M.csv")
        name_excel = datetime.datetime.today().strftime("%Y_%m_%d_%H_%M.xlsx")

        with open(name_csv,'w',encoding='utf8',errors='ignore',newline='') as file:
            csv_writer = csv.writer(file)
            csv_writer.writerow(header)
            for each in data:
                csv_writer.writerow(each)

        df = pandas.DataFrame(data,columns=header)
        df.to_excel(name_excel)


class ScraperUI:
    def __init__(self,base_url,card_type,card_language,card_year):
        self.one_piece_scraper = OnePieceScraper(base_url,card_type,card_language,card_year)
        self.language_dict = {
                                    "Asian-English":"https://asia-en.onepiece-cardgame.com/cardlist/",
                                    "Japanese":"https://www.onepiece-cardgame.com/cardlist/",
                                    "English":"https://en.onepiece-cardgame.com/cardlist"
                                }

        self.gui()


    def gui(self):
        root = Tk()
        background_image = Image.open('background.jpg')
        background_image = ImageTk.PhotoImage(background_image)
        w = background_image.width()+700
        h = background_image.height()
        root.geometry('%dx%d+0+0' % (w,h))
        root.resizable(True,False)





        frame_parent = Frame(root,bg="black")
        frame_parent.pack(fill=BOTH,expand=True)

        frame_image = Frame(frame_parent,bg="black")
        frame_image.pack(side=RIGHT,fill=Y)

        background_label = Label(frame_image, image=background_image)
        background_label.image = background_image
        background_label.pack()


        frame_left = Frame(frame_parent,bg="black")
        frame_left.pack(side=LEFT,fill=BOTH,expand=True)

        frame_combo = Frame(frame_left,bg="black")
        frame_combo.pack(side=TOP,fill=X)

        frame_combo_centre = Frame(frame_combo,bg="black")
        frame_combo_centre.pack()

        language_list = ["Asian-English", "Japanese", "English"]

        language_combo = ttk.Combobox(frame_combo_centre, values=language_list)
        language_combo.set("Choose Language")
        language_combo.pack(side=LEFT,padx=5, pady=5)

        choose_language_button = Button(frame_combo_centre,text="Choose Language",relief=GROOVE,bg="yellow",fg="black")
        choose_language_button.pack(side=LEFT)



        frame_options = Frame(frame_left, bg="black")
        frame_options.pack(side=TOP, fill=X)

        frame_options_centre = Frame(frame_options, bg="black")
        frame_options_centre.pack()

        self.options_list = []

        set_options = ttk.Combobox(frame_options_centre, values=self.options_list,width=40)
        set_options.set("Choose Set")
        set_options.pack(side=LEFT, padx=5, pady=5)

        choose_set_button = Button(frame_options_centre, text="Choose Set", relief=GROOVE, bg="yellow",fg="black")
        choose_set_button.pack(side=LEFT)



        set_options.pack_forget()
        choose_set_button.pack_forget()





        def choose_language_btn_func(event):


            lang = language_combo.get()
            if lang!="Choose Language":
                self.one_piece_scraper.base_url = self.language_dict[lang]
            else:
                messagebox.showerror("Error","Please choose a language first")
            thread = threading.Thread(target=self.one_piece_scraper.get_options,args=(set_options,choose_set_button))
            thread.start()
        choose_language_button.bind("<Button-1>",choose_language_btn_func)




        root.mainloop()

if __name__ == '__main__':
    base_url = 'https://asia-en.onepiece-cardgame.com/cardlist/'
    card_type = "One Piece Card Game"
    card_language = "Japanese"
    card_year = datetime.datetime.today().year

    ScraperUI(base_url,card_type,card_language,card_year)