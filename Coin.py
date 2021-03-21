import time
from enum import IntEnum

from function.get_account import get_account
from function.order_stock import buy_stock
from function.order_stock import sell_stock
from function.sm_util import *

config = configparser.ConfigParser()
config.read('config.ini', encoding='UTF8')

access_key: str = config['UPBIT']['UPBIT_OPEN_API_ACCESS_KEY']
secret_key: str = config['UPBIT']['UPBIT_OPEN_API_SECRET_KEY']


class State(IntEnum):
    WAIT = 1
    BOUGHT = 2
    TRYBUY = 3


class Coin:
    # price는 코인의 가격, amount는 원화가
    # amount = price * volume
    def __init__(self, coin_name: str):
        self.coin_name: str = coin_name
        self.check_time: str = ""
        self.balance: float = 0
        self.state: IntEnum = State.WAIT
        self.variability: float = 0
        self.buy_price: float = 0  # 목표 매수 금액
        self.uuid: str = ""
        self.bought_amount: float = 0  # 구매한 가격
        self.avg_buy_price: float = 0  # 구매한 코인 평균가격
        self.high_price: float = 0

    # 매수 개수 확인
    def update_balance(self):
        for _ in range(10):
            time.sleep(0.3)
            for account in get_account():
                if account.get('currency') == self.coin_name:
                    self.balance = account.get('balance')
                    self.avg_buy_price = float(account.get('avg_buy_price'))
                    break
            if self.balance:
                break

    def buy_coin(self, price, limit=False):
        try:
            if limit:
                buy_result = buy_stock(f'KRW-{self.coin_name}',
                                       price=self.buy_price, volume=price / self.buy_price, ord_type="limit")
                self.state = State.TRYBUY
            else:
                buy_result = buy_stock(f'KRW-{self.coin_name}', price=price)
                self.state = State.BOUGHT
        except ConnectionError:
            return ""
        self.uuid = buy_result.get('uuid')
        self.bought_amount = buy_result.get('locked')
        self.update_balance()
        return buy_result

    def sell_coin(self):
        if self.state != State.BOUGHT:
            return "Not bought"
        self.update_balance()
        sell_result = sell_stock(f'KRW-{self.coin_name}', self.balance)
        self.state = State.WAIT
        return sell_result.get('uuid')

    def cansel_buy(self):
        pass


if __name__ == "__main__":
    coin = Coin("ETH")
    coin.buy_coin(10000)
    # print(buy_stock(f'KRW-ETH', price=10000, sleep=3))
