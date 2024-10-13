from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
import pandas as pd


def scrape_trade_data(country,commodity_code,trade_flow) :
    driverpath = 'chromedriver.exe'
    chrome_options = Options()

    serv = Service(executable_path=driverpath)
    driver = webdriver.Chrome(service=serv,options=chrome_options)
    driver.get("https://comtradeplus.un.org/")
    time.sleep(10)
    # login to the webpage
    login_button = driver.find_element(By.XPATH,"//div[@id='login']/a")
    login_button.click()
    time.sleep(20)
    ## We're on the login page right now
    name = driver.find_element(By.ID,'signInName')
    pwd = driver.find_element(By.ID,'password')
    name.send_keys("paulsendonna640@gmail.com")
    pwd.send_keys("khaoula123_")
    connect= driver.find_element(By.ID,'next')
    connect.click()
    time.sleep(15)
    ## we will start first with two countries as  an example, making it more generalized further.
    # Lets work on the uae exports for this initial baseline scrapping
    advanced_search = driver.find_element(By.XPATH,'//*[@id="main"]/div/div/div[1]/div/div[2]/div[2]/div/div[4]/a')
    advanced_search.click()
    time.sleep(10)

    '''
    SELECTING THE TOP 3 COMMODITIES :
    # considering you have as an input : the country and the commodity code we're going to have this : 
    2709 : Petroleum oils and oils obtained from bituminous minerals
    2711 : Petroleum gases and other gaseous hydrocarbons.
    7108 : Gold (including gold plated with platinum), unwrought or in semi-manufactured forms, or in powder form.
    1001 : Wheat and muesli  
    '''


    inputs  = [country,commodity_code,trade_flow]

    xpaths=['/html/body/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[5]/div[1]/div[1]',
             '/html/body/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[5]/div[1]/div[2]',
             '/html/body/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[5]/div[2]/div[1]',
             '/html/body/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[5]/div[2]/div[2]',
             '/html/body/div[1]/div[2]/div/div/div/div[3]/div/div/div/div[5]/div[3]/div[1]'
           ]
    values = [inputs[1],
              'Recent Periods',
               inputs[0],
               'All',
               inputs[2]]

    for idx,xpath in enumerate(xpaths) :
        field = driver.find_element(By.XPATH, xpath)
        reset=field.find_element(By.TAG_NAME,'span').find_elements(By.TAG_NAME,'span')[1]
        reset.click()
        time.sleep(3)
        dropDownMenu = field.find_element(By.TAG_NAME, 'div').find_element(By.TAG_NAME, 'div')
        dropDownMenu.click()
        input = dropDownMenu.find_element(By.TAG_NAME, 'input')
        input.send_keys(values[idx])
        input.send_keys(Keys.TAB)
        input.send_keys(Keys.ENTER)

    preview = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div/div[3]/div/div[1]/div/div[8]/div')
    preview.find_element(By.TAG_NAME,'button').click()
    time.sleep(3)
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(3)

    target_span = driver.find_element(By.XPATH,'/html/body/div[1]/div[2]/div/div/div/div[3]/div/div[2]/div/div[1]/div/div[4]/div[2]/div[1]/span[2]')
    options_button = target_span.find_element(By.ID, 'pageDropDown')

    for i in range(2) :
        options_button.click()
    driver.implicitly_wait(4)
    ## click on the 500 Button option  :
    try :
        display = target_span.find_element(By.TAG_NAME,'ul').find_elements(By.TAG_NAME,'li')[-1].find_element(By.TAG_NAME,'a')
        driver.execute_script("arguments[0].click();", display)
        driver.implicitly_wait(4)
    except Exception as e  :
        print(str(e))


    page = driver.page_source
    parser = BeautifulSoup(page, 'html.parser')
    trade_data = []

    try :
        table = parser.find('table',{'class':'table table-bordered'})
        body  =  table.findChildren('tbody')[-1]
        target_indices =  [0,1,2,3,7,8,9,12]
        for row in body.find_all('tr'):
            cols = row.find_all('td')
            data = [cols[i] for i in  target_indices]
            row_data =  [x.text.strip() for x in data]
            trade_data.append(row_data)
    except Exception as e :
        print(str(e))
    df = pd.DataFrame(trade_data,columns=['Period','Trade Flow','Reporter','Partner','Commodity Code','Trade Value (US$)','Net Weight(kg)','Qty Unit'])
    df.to_csv('USA_IMPORTS_wheat.csv')
    time.sleep(10)
    driver.quit()








