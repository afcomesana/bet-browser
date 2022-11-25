from bet_browser import BetBrowser

if __name__ == '__main__':
    bet_browser = BetBrowser()
    
    try:
        bet_browser.open_browser()

        match_prices_dict_ps = bet_browser.get_matches_and_prices(bh='ps', competition='football-spain-second-league')
        match_prices_dict_bf = bet_browser.get_matches_and_prices(bh='bf', competition='football-spain-second-league')
        match_prices_dict_wh = bet_browser.get_matches_and_prices(bh='wh', competition='football-spain-second-league')

        bet_browser.pair_matches(ps=match_prices_dict_ps,bf=match_prices_dict_bf,wh=match_prices_dict_wh)

        bet_browser.get_max_bets_for_match()
        bet_browser.find_potential_bets()
        
        bet_browser.calculate_investing()
        bet_browser.calculate_net_profit()

        for match in bet_browser.potential_bet_matches.keys():
            print(match,'---',bet_browser.potential_bet_matches[match]['net_profit'])
    finally:
        bet_browser.close_browser()