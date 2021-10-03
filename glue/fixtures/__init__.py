price_example_1 = {
    "type": "PRICE",
    "instrument": "AUD_USD",
    "time": "1631165485.250146716",
    "status": "tradeable",
    "tradeable": True,
    "bids": [
        {"price": 0.7351, "liquidity": 1000000},
    ],
    "asks": [
        {"price": 0.73518, "liquidity": 1000000},
    ],
    "closeoutBid": 0.73503,
    "closeoutAsk": 0.73524,
}

price_example_2 = {
    "type": "PRICE",
    "instrument": "USD_AUD",
    "time": "1631165504.356735359",
    "status": "tradeable",
    "tradeable": True,
    "bids": [
        {"price": 0.73513, "liquidity": 1000000},
        {"price": 0.7351, "liquidity": 4000000},
        {"price": 0.73506, "liquidity": 5000000},
    ],
    "asks": [
        {"price": 0.73521, "liquidity": 1000000},
        {"price": 0.73524, "liquidity": 4000000},
        {"price": 0.73527, "liquidity": 5000000},
    ],
    "closeoutBid": 0.73506,
    "closeoutAsk": 0.73527,
}
