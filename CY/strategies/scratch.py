    'STARFRUIT': {
        'POSITION_LIMIT': 20,
        'NUM_BID': 0, # amount buy per iteration, so don't submit too much
        'NUM_ASK': 0, # amount sell

        'METHOD': 'moving_average',
        'PRED_MID_PRICE': None,
        'MA_COEFF': [-0.01869561,  0.0455032 ,  0.16316049,  0.8090892],
        'MA_INTERCEPT': 4.481696494462085,
        'MID_PRICE_DEQUE': [], # deque of mid prices, size same as MA_coeff

        'TAKE_THRESHOLD': [0, 20], # absolute position thresholds, as market taker
        'TAKE_SPREAD_BA': [(1, 1), (1, 0)], # (bid, ask) offset from mid

        'MAKE_THRESHOLD': [20], # absolute position thresholds, as market maker
        'MAKE_SPREAD_BA': [(1, 1)], # (bid, ask) offset from mid
        'MAKE_MIN_RANGE': [1, 1],
    },