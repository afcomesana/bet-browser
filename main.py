from bet_browser import BetBrowser

bet_browser = BetBrowser()

try:
    bet_browser.open_browser()
    bet_browser.get_matches('ps', 'spain-second-league')
finally:
    bet_browser.close_browser()