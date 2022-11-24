import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.common.exceptions import TimeoutException
from webdriver_manager.firefox import GeckoDriverManager
from exceptions import BrowserException
from utils import min_levenshtein_distance

class BetBrowser:
    # Load variables helpful to dig into the betting houses websites:
    def __init__(self):
        # Related to betting houses
        with open('betting-houses.json','r') as bh_info_file:
            self.bh_info = json.load(bh_info_file)
        
        # Related to leagues
        with open('football-leagues.json','r') as fl_info_file:
            self.fl_info = json.load(fl_info_file)

    # ACCESSING URLS:
    def get_url(self, bh:str, league:str= None):
        '''Build the url for accesing to matches.'''

        # bh short for "betting_houses"
        url = 'https://%s' % self.bh_info[bh]['domain']
        
        if league != None:
            url += self.fl_info[league][bh]
        
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
        
    ### FIND INFORMATIVE PARTS OF ELEMENTS:
    def get_matches_and_prices(self, bh:str, league:str):
        '''Browse the bh page and use web scrapping to download the matches and bet prices.'''
        url = self.get_url(bh=bh, league=league)
        
        if not self.access_to_page(url=url, wait_for_element_class_name=self.bh_info[bh]['event_class_name']):
            raise BrowserException('Could not open page')
        
        if 'teams_class_name' in self.bh_info[bh].keys():
            matches = self.browser_driver.find_elements(
                    by=By.CLASS_NAME,
                    value=self.bh_info[bh]['teams_class_name']
                    )
        else:
            matches = self.browser_driver.find_elements(
                    by=By.CSS_SELECTOR,
                    value=f"[id^='{self.bh_info[bh]['match_id_name']}']"
                    )
        matches = [ match.text.replace('\n','-').replace(' ','_') for match in matches ]

        prices = self.browser_driver.find_elements(
                by=By.CLASS_NAME,
                value=self.bh_info[bh]['prices_class_name']
                )
        prices = [ price.text.replace('\n','-').split('-') for price in prices if len(price.text.replace('\n','-').split('-'))==3 ]

        # Check if we have gotten the same matches as prices
        assert len(matches) == len(prices)

        match_prices_dict = dict(zip(matches, prices))

        return match_prices_dict
    
    def pair_matches(self,**kwargs:dict):
        '''Match matches from different bh, keeping the bet prices from each bh.'''
        unique_matches = {}
        for iter in enumerate(kwargs.items()):
            iter,key,value = iter[0],iter[1][0],iter[1][1]
            for match in value.keys():
                if iter == 0: unique_matches[match] = { key: value[match] }
                else:
                    coincidence = min_levenshtein_distance( match, *unique_matches.keys() )
                    if coincidence: unique_matches[coincidence][key] = value[match]

        return unique_matches
        
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
        
    