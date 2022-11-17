import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from exceptions import BrowserException

class BetBrowser:
    # Load variables helpful to dig into the betting houses websites:
    def __init__(self):
        # Related to betting houses
        bh_info_file = open('betting-houses.json')
        self.bh_info = json.load(bh_info_file)
        bh_info_file.close()
        
        # Related to leagues
        fl_info_file = open('football-leagues.json')
        self.fl_info = json.load(fl_info_file)
        fl_info_file.close()

    # ACCESSING URLS:
    def get_url(self, bf, league = None):
        # bf short for "betting_houses"
        url = 'https://%s' % self.bh_info[bf]['domain']
        
        if league != None:
            url += self.fl_info[league][bf]
        
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
    def get_matches(self, bf, league):
        url = self.get_url(bf, league)
        
        if not self.access_to_page(url, self.bh_info[bf]['event_class_name']):
            raise BrowserException('Could not open page')
        
        matches = self.browser_driver.find_elements(
            by=By.CLASS_NAME,
            value=self.bh_info
        )
        
        return matches
    
        
    ### OPEN AND CLOSE THE WEB BROWSER:
    def open_browser(self):
        self.browser_driver = webdriver.Firefox()
        
    def close_browser(self):
        self.browser_driver.quit()
        
    