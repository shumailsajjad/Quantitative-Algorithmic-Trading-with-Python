# -*- coding: utf-8 -*-
"""
Piotroski f score implementation using selenium based webscraping

"""

import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

path = "C:\\Users\\Mayank\\OneDrive\\Udemy\\Quant Investing Using Python\\1.5_Web Scraping\\scripts\\chromedriver.exe"
service = webdriver.chrome.service.Service(path)
service.start()
options = Options()
options.add_argument("--headless") #use this to not render the actual browser

tickers = ["AXP","AAPL","BA","CAT","CVX","CSCO","DIS","DOW", "XOM",
           "HD","IBM","INTC","JNJ","KO","MCD","MMM","MRK","MSFT",
           "NKE","PFE","PG","UNH","VZ","V","WMT","WBA"]

def get_financial_statement(ticker,type_of_statement="income_statement",depth=1):
    """
    Parameters
    ----------
    ticker : str
    type_of_statement : str
        DESCRIPTION. either of income_statement, balance_sheet and cashflow_statement. The default is income_statement.
    depth : int
        DESCRIPTION. till what depth of the statement you need to go. if depth is 2, the code will iterate the button finding process twice

    Returns
    -------
    df : dataframe

    """
    if type_of_statement=="income_statement":
        url = "https://finance.yahoo.com/quote/{}/financials?p={}".format(ticker,ticker)
    elif type_of_statement=="balance_sheet":
        url = "https://finance.yahoo.com/quote/{}/balance-sheet?p={}".format(ticker,ticker)
    elif type_of_statement=="cashflow_statement":
        url = "https://finance.yahoo.com/quote/{}/cash-flow?p={}".format(ticker,ticker)
        
    service = webdriver.chrome.service.Service(path)
    service.start()
    options = Options()
    options.add_argument("--headless") #use this to not render the actual browser    
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(url)
    driver.implicitly_wait(0.2)

    clicked_buttons = []
    for i in range(depth):
        buttons = driver.find_elements(By.XPATH,  '//div[@class="tableContainer yf-1pgoo1f"]//button')
        buttons = [i for i in buttons if i not in clicked_buttons]
        for button in buttons:
            print(button.accessible_name)
            if button.accessible_name in ["Quarterly","Expand All"]:
                pass
            else:
                WebDriverWait(driver, 0.5).until(EC.element_to_be_clickable(button)) #may need to increase the wait time if the buttons are not getting clicked
                driver.execute_script("arguments[0].click();", button) #this way of clicking may be required for some of the wrapped buttons
        clicked_buttons+=buttons
        
    temp = {}
    table = driver.find_elements(By.XPATH,  '//div[@class="tableBody yf-1pgoo1f"]')
    table_heading = driver.find_elements(By.XPATH,  '//div[@class="tableHeader yf-1pgoo1f"]')    
    for cell in table_heading:
        headings = cell.text.split(" ")
      
    for cell in table:            
        vals = cell.text.split("\n")
        for count, element in enumerate(vals):
            if count%len(headings) == 0:
                key = element
                temp[key] = []
            else:
                temp[key].append(element)
        
    df = pd.DataFrame(temp).T
    df.columns = headings[1:]
    
    for col in df.columns:
        df[col] = df[col].str.replace(',|- ','')
        df[col] = pd.to_numeric(df[col], errors = 'coerce')

    if df.columns[0] == "TTM": #delete TTM column from income statement and cashfow statement to make it consistent with balance sheet
        df.drop("TTM",axis=1,inplace=True)
    driver.close() #important to close the browser else you may run out of memory if too many chrome browsers get opened by the program
    return df

#list of tickers whose financial data needs to be extracted
financial_dir = {}
for ticker in tickers:
    try:
        df1 = get_financial_statement(ticker,"income_statement")
        df1 = df1.iloc[:,:3]
        df2 = get_financial_statement(ticker,"balance_sheet",3)
        df2 = df2.iloc[:,:3]
        df3 = get_financial_statement(ticker,"cashflow_statement",2)
        df3 = df3.iloc[:,:3]
        df = pd.concat([df1,df2,df3])
        financial_dir[ticker] = df
        print("data extracted for ",ticker)
        financial_dir[ticker] = df
    except Exception as e:
        print(ticker,":", e)

# selecting relevant financial information for each stock using fundamental data
stats = ["Net Income from Continuing Operations",
         "Total Assets",
         "Operating Cash Flow",
         "Long Term Debt And Capital Lease Obligation",
         "Total Non Current Liabilities Net Minority Interest",
         "Current Assets",
         "Current Liabilities",
         "Stockholders' Equity",
         "Total Revenue",
         "Gross Profit"] # change as required

indx = ["NetIncome","TotAssets","CashFlowOps","LTDebt","TotLTLiab",
        "CurrAssets","CurrLiab","CommStock","TotRevenue","GrossProfit"]


def info_filter(df,stats,indx,lookback):
    """function to filter relevant financial information
       df = dataframe to be filtered
       stats = headings to filter
       indx = rename long headings
       lookback = number of years of data to be retained"""
    for stat in stats:
        if stat not in df.index:
            print("unable to find {} in {}".format(stat,df.columns[0]))
            return
    df_new = df.loc[stats,df.columns[:3]]
    df_new.rename(dict(zip(stats,indx)),inplace=True)
    df_new.loc["OtherLTDebt",:] = df_new.loc["TotLTLiab",:] - df_new.loc["LTDebt",:]
    return df_new

#applying filtering to the finacials
transformed_df = {}
for ticker in financial_dir:
    transformed_df[ticker] = info_filter(financial_dir[ticker],stats,indx,3)


def piotroski_f(df_dict):
    """function to calculate f score of each stock and output information as dataframe"""
    f_score = {}
    for ticker in df_dict:
        columns = df_dict[ticker].columns
        ROA_FS = int(df_dict[ticker].loc["NetIncome",columns[0]]/((df_dict[ticker].loc["TotAssets",columns[0]] + df_dict[ticker].loc["TotAssets",columns[1]])/2) > 0)
        CFO_FS = int(df_dict[ticker].loc["CashFlowOps",columns[0]] > 0)
        ROA_D_FS = int((df_dict[ticker].loc["NetIncome",columns[0]]/((df_dict[ticker].loc["TotAssets",columns[0]] + df_dict[ticker].loc["TotAssets",columns[1]])/2)) > (df_dict[ticker].loc["NetIncome",columns[1]]/((df_dict[ticker].loc["TotAssets",columns[1]] + df_dict[ticker].loc["TotAssets",columns[2]])/2)))
        CFO_ROA_FS = int(df_dict[ticker].loc["CashFlowOps",columns[0]]/df_dict[ticker].loc["TotAssets",columns[0]] > df_dict[ticker].loc["NetIncome",columns[0]]/((df_dict[ticker].loc["TotAssets",columns[0]] + df_dict[ticker].loc["TotAssets",columns[1]])/2))
        LTD_FS = int((df_dict[ticker].loc["LTDebt",columns[0]] + df_dict[ticker].loc["OtherLTDebt",columns[0]]) < (df_dict[ticker].loc["LTDebt",columns[1]] + df_dict[ticker].loc["OtherLTDebt",columns[1]]))
        CR_FS = int((df_dict[ticker].loc["CurrAssets",columns[0]] / df_dict[ticker].loc["CurrLiab",columns[0]]) > (df_dict[ticker].loc["CurrAssets",columns[1]] / df_dict[ticker].loc["CurrLiab",columns[1]]))
        DILUTION_FS = int(df_dict[ticker].loc["CommStock",columns[0]] <= df_dict[ticker].loc["CommStock",columns[1]])
        GM_FS = int((df_dict[ticker].loc["GrossProfit",columns[0]]/df_dict[ticker].loc["TotRevenue",columns[0]]) > (df_dict[ticker].loc["GrossProfit",columns[1]]/df_dict[ticker].loc["TotRevenue",columns[1]]))
        ATO_FS = int((df_dict[ticker].loc["TotRevenue",columns[0]]/((df_dict[ticker].loc["TotAssets",columns[0]] + df_dict[ticker].loc["TotAssets",columns[1]])/2)) > (df_dict[ticker].loc["TotRevenue",columns[1]]/((df_dict[ticker].loc["TotAssets",columns[1]] + df_dict[ticker].loc["TotAssets",columns[2]])/2)))
        f_score[ticker] = [ROA_FS,CFO_FS,ROA_D_FS,CFO_ROA_FS,LTD_FS,CR_FS,DILUTION_FS,GM_FS,ATO_FS]
    f_score_df = pd.DataFrame(f_score,index=["PosROA","PosCFO","ROAChange","Accruals","Leverage","Liquidity","Dilution","GM","ATO"])
    return f_score_df

# sorting stocks with highest Piotroski f score to lowest
f_score_df = piotroski_f(transformed_df)
f_score_df.sum().sort_values(ascending=False)