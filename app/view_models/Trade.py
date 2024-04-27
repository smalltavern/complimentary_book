from app.view_models.book import BookViewModel


class TradeInfo:
    def __init__(self, trades):
        self.total = 0
        self.trades = []
        self._parse(trades)

    def _parse(self, trades):
        self.total = len(trades)
        self.trades = [TradeInfo._map_to_trade(single) for single in trades]

    @staticmethod
    def _map_to_trade(single):
        time = single.create_datetime.strftime('%Y-%m-%d') if single.create_datetime else '未知'
        return dict(
            user_name=single.user.nickname,
            time=time,
            id=single.id
        )


class MyTrades:
    def __init__(self, trades_of_mine, trade_count_list):
        self.trades = []
        self.__trades_of_mine = trades_of_mine
        self.__trade_count_list = trade_count_list

        self.trades = self.parse()

    def parse(self):
        temp_trades = []
        for trade in self.__trades_of_mine:
            my_trade = self.__matching(trade)
            temp_trades.append(my_trade)
        return temp_trades

    def __matching(self, trade):
        count = 0
        for trade_count in self.__trade_count_list:
            if trade.isbn == trade_count['isbn']:
                count = trade_count['count']
        return MyTrade(trade.id, BookViewModel(trade.book), count)


class MyTrade:
    def __init__(self, id, book, trade_count):
        self.id = id
        self.book = book
        self.trade_count = trade_count