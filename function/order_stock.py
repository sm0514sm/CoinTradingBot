import jwt
import uuid
import hashlib
import time
from urllib.parse import urlencode
import requests


def buy_stock(access_key: str, secret_key: str, market: str, price: float, sleep: float = 3.0) -> dict:
    query = {
        'market': market,
        'side': 'bid',
        'price': price,
        'ord_type': 'price',
    }
    m = hashlib.sha512()
    m.update(urlencode(query).encode())
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post("https://api.upbit.com/v1/orders", params=query, headers=headers)
    time.sleep(sleep)
    return res.json()


def sell_stock(access_key: str, secret_key: str, market: str, volume: float, sleep: float = 3.0) -> dict:
    query = {
        'market': market,
        'side': 'ask',
        'volume': volume,
        'ord_type': 'market',
    }
    m = hashlib.sha512()
    m.update(urlencode(query).encode())
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.post("https://api.upbit.com/v1/orders", params=query, headers=headers)
    time.sleep(sleep)
    return res.json()


def get_total_buy_price(access_key: str, secret_key: str, market):
    query = {
        'market': f'KRW-{market}',
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get("https://api.upbit.com/v1/orders/chance", params=query, headers=headers).json()
    ask_account = res.get('ask_account')
    return float(ask_account.get('balance')) * float(ask_account.get('avg_buy_price'))


def get_total_sell_price(access_key: str, secret_key: str, uuidd):
    query = {
        'uuid': uuidd,
    }
    query_string = urlencode(query).encode()

    m = hashlib.sha512()
    m.update(query_string)
    query_hash = m.hexdigest()

    payload = {
        'access_key': access_key,
        'nonce': str(uuid.uuid4()),
        'query_hash': query_hash,
        'query_hash_alg': 'SHA512',
    }

    jwt_token = jwt.encode(payload, secret_key).decode('utf-8')
    authorize_token = 'Bearer {}'.format(jwt_token)
    headers = {"Authorization": authorize_token}

    res = requests.get("https://api.upbit.com/v1/order", params=query, headers=headers).json()

    sell_price = -float(res.get('paid_fee'))
    for trade in res.get('trades'):
        sell_price += float(trade.get('price')) * float(trade.get('volume'))
    return sell_price
