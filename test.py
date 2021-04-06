import configparser

def init_file():
    coin_pair_indicator = 'coin_pair_indicator.dat'
    config = configparser.ConfigParser()
    config['indicator'] = { 'rsi_level'             : '0',
                            'is_sma5_over_sma_10'   : '0'}

    with open(coin_pair_indicator, 'w') as configfile:
        config.write(configfile)

def update_file():
    config = configparser.ConfigParser()
    config.read(coin_pair_indicator)
    indicator = config['indicator']
    indicator['rsi_level'] = '10'
    # rsi_level = indicator.getint('rsi_level')
    # rsi_level = config.getint('indicator', 'rsi_level_a',
    #                 fallback='There no a')

    # config.set('indicator', 'rsi_levelb', '1')
    # print(rsi_level)
    with open(coin_pair_indicator, 'w') as configfile:
        config.write(configfile)


init_file