from bet_browser import BetBrowser

if __name__ == '__main__':
    bet_browser = BetBrowser()
    
    try:
        bet_browser.open_browser()
        match_prices_dict_ps = bet_browser.get_matches_and_prices(bh='ps', league='spain-second-league')
        match_prices_dict_bf = bet_browser.get_matches_and_prices(bh='bf', league='spain-second-league')
        bet_browser.pair_matches(ps=match_prices_dict_ps,bf=match_prices_dict_bf)
        bet_browser.get_max_bets_for_match()
    finally:
        bet_browser.close_browser()