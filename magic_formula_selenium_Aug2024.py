# -*- coding: utf-8 -*-
"""
Magic formula implementation using selenium based webscraping

"""

# ============================================================================
# Greenblatt's Magic Formula Implementation
# Author - Mayank Rasu

# Please report bugs/issues in the Q&A section
# =============================================================================

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

tickers = ["MMM","AXP","AAPL","BA","CAT","CVX","CSCO","KO","DIS",
           "XOM","GE","GS","HD","IBM","INTC","JNJ","JPM","MCD","MRK",
           "MSFT","NKE","PFE","PG","TRV","UNH","VZ","V","WMT"]

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

    driver.close() #important to close the browser else you may run out of memory if too many chrome browsers get opened by the program
    return df

def get_key_stat(ticker):
    #getting key statistics data from yahoo finance for the given ticker
    
    temp_dir = {}
    url = 'https://finance.yahoo.com/quote/'+ticker+'/key-statistics?p='+ticker
    
    service = webdriver.chrome.service.Service(path)
    service.start()
    options = Options()
    options.add_argument("--headless") #use this to not render the actual browser
    
    driver = webdriver.Chrome(service=service, options = options)
    driver.get(url)
    driver.implicitly_wait(0.2)
    
    #first scrape the table at the top of the page
    #the text is space delimited which is tricky because the key can also be space delimited but we only need to get the latest value so it should be achievable
    table = driver.find_elements(By.XPATH,  '//table[@class="table yf-104jbnt"]')
    for cell in table:          
        vals = cell.text.split("\n")
        for val in vals:
            values = val.split(" ")
            if values[0] == "Current":
                pass
            else:
                temp_dir[" ".join(values[:-6])] = values[-6]
            
    table = driver.find_elements(By.XPATH,  '//tr[@class="row yf-vaowmx"]')
    for cell in table:
        values = cell.text.split(" ")
        temp_dir[" ".join(values[:-1])] = values[-1]

    df = pd.DataFrame(temp_dir.values(),index=temp_dir.keys(),columns=["values"])
    df.iloc[:,0] = df.iloc[:,0].replace({'M': 'E+03','B': 'E+06','T': 'E+09','%': 'E-02'}, regex=True)
    df.iloc[:,0] = pd.to_numeric(df.iloc[:,0],errors="coerce")
    return df

#list of tickers whose financial data needs to be extracted
financial_dir = {}
for ticker in tickers:
    try:
        df1 = get_financial_statement(ticker,"income_statement")
        df1 = df1.iloc[:,[0]]
        df1.columns = [ticker]
        df2 = get_financial_statement(ticker,"balance_sheet",3)
        df2 = df2.iloc[:,[0]]
        df2.columns = [ticker]
        df3 = get_financial_statement(ticker,"cashflow_statement",2)
        df3 = df3.iloc[:,[0]]
        df3.columns = [ticker]
        df4 = get_key_stat(ticker)
        df4 = df4.iloc[:,[0]]
        df4.columns = [ticker]
        df = pd.concat([df1,df2,df3,df4])
        financial_dir[ticker] = df
        print("data extracted for ",ticker)
        financial_dir[ticker] = df
    except Exception as e:
        print(ticker,":", e)
        
        
# creating dataframe with relevant financial information for each stock using fundamental data
stats = ["EBITDA",
         "Depreciation Amortization Depletion",
         "Market Cap",
         "Net Income",
         "Operating Cash Flow",
         "Capital Expenditure",
         "Current Assets",
         "Current Liabilities",
         "Net PPE Purchase And Sale",
         "Stockholders' Equity",
         "Long Term Debt And Capital Lease Obligation",
         "Forward Annual Dividend Yield 4"] # change as required

indx = ["EBITDA","D&A","MarketCap","NetIncome","CashFlowOps","Capex","CurrAsset",
        "CurrLiab","PPE","BookValue","TotDebt","DivYield"]

def info_filter(df,stats,indx):
    """function to filter relevant financial information
       df = dataframe to be filtered
       stats = headings to filter
       indx = rename long headings
       lookback = number of years of data to be retained"""
    for stat in stats:
        if stat not in df.index:
            print("unable to find {} in {}".format(stat,df.columns[0]))
            return
    df_new = df.loc[stats]
    df_new = df_new[~df_new.index.duplicated(keep='first')]
    df_new.rename(dict(zip(stats,indx)),inplace=True)
    return df_new

#applying filtering to the finacials and calculating relevant financial metrics for each stock
transformed_df = {}
for ticker in financial_dir:
    transformed_df[ticker] = info_filter(financial_dir[ticker],stats,indx)
    if transformed_df[ticker] is None:
        del transformed_df[ticker]
        continue
    transformed_df[ticker].loc["EBIT",:] = transformed_df[ticker].loc["EBITDA",:] - transformed_df[ticker].loc["D&A",:]
    transformed_df[ticker].loc["TEV",:] =  transformed_df[ticker].loc["MarketCap",:] + \
                                           transformed_df[ticker].loc["TotDebt",:] - \
                                           (transformed_df[ticker].loc["CurrAsset",:]-transformed_df[ticker].loc["CurrLiab",:])
    transformed_df[ticker].loc["EarningYield",:] =  transformed_df[ticker].loc["EBIT",:]/transformed_df[ticker].loc["TEV",:]
    transformed_df[ticker].loc["FCFYield",:] = (transformed_df[ticker].loc["CashFlowOps",:]-transformed_df[ticker].loc["Capex",:])/transformed_df[ticker].loc["MarketCap",:]
    transformed_df[ticker].loc["ROC",:]  = (transformed_df[ticker].loc["EBITDA",:] - transformed_df[ticker].loc["D&A",:])/(transformed_df[ticker].loc["PPE",:]+transformed_df[ticker].loc["CurrAsset",:]-transformed_df[ticker].loc["CurrLiab",:])
    transformed_df[ticker].loc["BookToMkt",:] = transformed_df[ticker].loc["BookValue",:]/transformed_df[ticker].loc["MarketCap",:]

################################Output Dataframes##############################
final_stats_val_df = pd.DataFrame(columns=transformed_df.keys())
for key in transformed_df:
    final_stats_val_df[key] = transformed_df[key].values.flatten()
final_stats_val_df.set_index(transformed_df[key].index,inplace=True)
    

# finding value stocks based on Magic Formula
final_stats_val_df.loc["CombRank",:] = final_stats_val_df.loc["EarningYield",:].rank(ascending=False,na_option='bottom')+final_stats_val_df.loc["ROC",:].rank(ascending=False,na_option='bottom')
final_stats_val_df.loc["MagicFormulaRank",:] = final_stats_val_df.loc["CombRank",:].rank(method='first')
value_stocks = final_stats_val_df.loc["MagicFormulaRank",:].sort_values()
print("------------------------------------------------")
print("Value stocks based on Greenblatt's Magic Formula")
print(value_stocks)


# finding highest dividend yield stocks
high_dividend_stocks = final_stats_val_df.loc["DivYield",:].sort_values(ascending=False)
print("------------------------------------------------")
print("Highest dividend paying stocks")
print(high_dividend_stocks)

# # Magic Formula & Dividend yield combined
final_stats_val_df.loc["CombinedRank",:] =  final_stats_val_df.loc["EarningYield",:].rank(ascending=False,method='first') \
                                           +final_stats_val_df.loc["ROC",:].rank(ascending=False,method='first')  \
                                           +final_stats_val_df.loc["DivYield",:].rank(ascending=False,method='first')
value_high_div_stocks = final_stats_val_df.T.sort_values("CombinedRank").loc[:,["EarningYield","ROC","DivYield","CombinedRank"]]
print("------------------------------------------------")
print("Magic Formula and Dividend Yield combined")
print(value_high_div_stocks)
        
        
        
        
        
        
        