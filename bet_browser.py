import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from exceptions import BrowserException
from utils import min_levenshtein_distance,calculate_result_inversion
from numpy import amax,unique

class BetBrowser:
    # Load variables helpful to dig into the betting houses websites:
    def __init__(self):
        # Related to betting houses
        with open('betting-houses.json','r') as bh_info_file:
            self.bh_info = json.load(bh_info_file)
        
        # Related to leagues
        with open('competitions.json','r') as comp_info_file:
            self.comp_info = json.load(comp_info_file)

    # ACCESSING URLS:
    def get_url(self, bh:str, competition:str= None):
        '''Build the url for accesing to matches.'''

        # bh short for "betting_houses"
        url = 'https://%s' % self.bh_info[bh]['domain']
        
        if competition != None:
            url += self.comp_info[bh][competition]['domain']
        
        return url
    
    def access_to_page(self, url, wait_for_element_class_name = None, delay = 5):
        success = True
        try:
            self.browser_driver.get(url)
            
            # If we want to wait for a concrete element to load before doing anything else:
            if wait_for_element_class_name != None:
                
                wait_for_element = EC.presence_of_element_located((By.CLASS_NAME, wait_for_element_class_name))
                WebDriverWait(
                    self.browser_driver,
                    delay
                ).until(wait_for_element)

        # The element was not found, at least with the delay provided:
        except TimeoutException:
            success = False
            print('Element with class name "%s" was not found in %s' % (wait_for_element_class_name, url))
            
        except Exception:
            success = False
            print('It was not possible to access the URL provided.')
            
        return success
    
    def get_elements_from_browser(self,bh:str,competition:str,json_class_name:str,json_css_selector:str,json_id_name:str):
        '''Download elements from the browser. Mainly deisgned for getting matches and bet prices.'''
        if json_class_name in self.comp_info[bh][competition].keys():
            if json_css_selector in self.comp_info[bh][competition].keys():
                return self.browser_driver.find_elements(
                            by=By.CSS_SELECTOR,
                            value=f"{self.comp_info[bh][competition][json_css_selector]}.{self.comp_info[bh][competition][json_class_name]}" )
            else:
                return self.browser_driver.find_elements(
                    by=By.CLASS_NAME,
                    value=self.comp_info[bh][competition][json_class_name] )
        return self.browser_driver.find_elements(
                    by=By.CSS_SELECTOR,
                    value=f"[id^='{self.comp_info[bh][competition][json_id_name]}']" )

    ### FIND INFORMATIVE PARTS OF ELEMENTS:
    def get_matches_and_prices(self, bh:str, competition:str, possible_results:int=3):
        '''Browse the bh page and use web scrapping to download the matches and bet prices.'''
        url = self.get_url(bh=bh, competition=competition)
        
        if not self.access_to_page(url=url, wait_for_element_class_name=self.comp_info[bh][competition]['event_class_name']):
            raise BrowserException('Could not open page')
        
        matches = self.get_elements_from_browser(
                bh=bh,
                competition=competition,
                json_class_name='teams_class_name',
                json_css_selector='css_team_selector',
                json_id_name='match_id_name')
        matches = [ match.text.replace('\n','-').replace('@','-').replace(' ','_') for match in matches ]

        prices = self.get_elements_from_browser(
                bh=bh,
                competition=competition,
                json_class_name='prices_class_name',
                json_css_selector='css_price_selector',
                json_id_name='prices_id_name')
        prices = [ price.text.replace('\n','-').replace('@','-').split('-') for price in prices if len(price.text.replace('\n','-').split('-'))==possible_results ]
        
        # Check if we have gotten the same matches as prices
        assert len(matches) == len(prices)

        match_prices_dict = dict(zip(matches, prices))

        return match_prices_dict
    
    def pair_matches(self,**kwargs:dict):
        '''Match matches from different bh, keeping the bet prices from each bh.'''
        self.unique_matches = {}
        for iter in enumerate(kwargs.items()):
            iter,key,value = iter[0],iter[1][0],iter[1][1]
            for match in value.keys():
                if iter == 0: self.unique_matches[match] = { key: value[match] }
                else:
                    coincidence = min_levenshtein_distance( match, *self.unique_matches.keys() )
                    if coincidence: self.unique_matches[coincidence][key] = value[match]
    
    def get_max_bets_for_match(self):
        '''Get max bet prices for each possibility(1,X,2) for each match between different bh.'''
        for key,value in self.unique_matches.items():
            bet_prices = []
            for key2,value2 in value.items():
                bet_prices += [ [float(val.replace(',','.')) for val in value2] ]
            self.unique_matches[key]['max_bets'] = amax(bet_prices,axis=0).tolist()
    
    def find_potential_bets(self):
        self.potential_bet_matches = self.unique_matches.copy()
        for match in self.unique_matches.keys():
            L = calculate_result_inversion(*self.unique_matches[match]['max_bets'])
            self.potential_bet_matches[match]['L'] = L
            if self.potential_bet_matches[match]['L'] >= 1: self.potential_bet_matches.pop( match )

    def calculate_investing(self,invest_amount:int=1000):
        for match in self.potential_bet_matches.keys():#self..keys():
            invest = []
            for price in self.potential_bet_matches[match]['max_bets']:
                invest += [ invest_amount/(self.potential_bet_matches[match]['L']*price) ]
            self.potential_bet_matches[match]['amount_to_invest'] = invest
    
    def calculate_net_profit(self):
        for match in self.potential_bet_matches.keys():#self.potential_bet_matches.keys():
            net_profit = []
            for iter in range(len(self.potential_bet_matches[match]['amount_to_invest'])):
                profit = self.potential_bet_matches[match]['amount_to_invest'][iter] * self.potential_bet_matches[match]['max_bets'][iter]
                net_profit += [ round( profit - sum(self.potential_bet_matches[match]['amount_to_invest']), 3 ) ]
            
            assert len(unique(net_profit)) == 1

            self.potential_bet_matches[match]['net_profit'] = net_profit[0]

    ### OPEN AND CLOSE THE WEB BROWSER:
    def open_browser(self):
        '''Open a Firefox web browser.'''
        try:
            self.browser_driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()))
        except Exception as e:
            print(f'Could not open a browser:\n{e}.')
        
    def close_browser(self):
        '''Close opened web browser.'''
        self.browser_driver.quit()
        
    