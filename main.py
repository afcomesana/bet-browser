from bet_browser import BetBrowser

if __name__ == '__main__':
    bet_browser = BetBrowser()

    try:
        bet_browser.open_browser()
        bet_browser.get_matches_and_prices(bh='ps', league='spain-second-league')
        bet_browser.get_matches_and_prices(bh='bf', league='spain-second-league')
    finally:
        bet_browser.close_browser()