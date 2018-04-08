from functools import reduce
from abc import ABCMeta, abstractmethod


class Player:
    def __init__(self, name):
        self.name = name


class Match(metaclass=ABCMeta):
    def __init__(self, number_of_holes, arr_with_players):
        self.number_of_holes = number_of_holes
        self.arr_with_players = arr_with_players
        self.table = [tuple([player.name for player in arr_with_players])]
        self.lap = [None for player in self.arr_with_players]
        self.count = 0
        self.finished = False

    def get_table(self):
        result_table = self.table.copy()
        if self.lap.count(None) != len(self.lap):
            result_table.append(tuple(self.lap))
        for hole in range(self.number_of_holes - len(result_table) + 1):
            result_table.append(tuple([None for player in self.arr_with_players]))
        return result_table

    def get_winners(self):
        table = self.get_table()[1:]
        try:
            table = [reduce(lambda x, y: x + y, i) for i in (zip(*table))]
            if type(self) == HitsMatch:
                return [self.arr_with_players[index] for index, score in enumerate(table) if score == min(table)]
            elif type(self) == HolesMatch:
                return [self.arr_with_players[index] for index, score in enumerate(table) if score == max(table)]
        except TypeError:
            raise RuntimeError

    @abstractmethod
    def hit(self, success=False):
        pass


class HitsMatch(Match):
    def __init__(self, number_of_holes, arr_with_players):
        Match.__init__(self, number_of_holes, arr_with_players)
        self.drop = [False for player in self.arr_with_players]
        self.buff = [None for player in self.arr_with_players]

    def hit(self, success=False):
        if self.finished:
            raise RuntimeError
        else:
            if self.count == len(self.lap):
                self.count = 0
            # Забившие игроки, пропускают удар
            if self.drop[self.count]:
                try:
                    self.count = self.drop.index(False, self.count, len(self.drop) - 1)
                except ValueError:
                    self.count = self.drop.index(False, 0, self.count)

            try:
                self.buff[self.count] += 1
            except TypeError:
                self.buff[self.count] = 1
            if success:
                self.drop[self.count] = True
                self.lap[self.count] = self.buff[self.count]

            self.count += 1
            # Условие перехода к следующей лунке
            if all(self.drop) or self.buff.count(9) > 0:
                self.buff = [item + 1 if item == 9 else item for item in self.buff]
                self.lap = self.buff
                # добваить lap в таблицу
                self.table.append(tuple(self.lap))
                # отчистить lap
                self.lap = [None for player in self.arr_with_players]
                self.buff = [None for player in self.arr_with_players]
                # Определяю какой игрок делает следующий удар
                if success:
                    if self.count == len(self.lap):
                        self.count = 0
                else:
                    self.count -= 1
                self.drop = [False for player in self.arr_with_players]
            table = self.get_table()
            if len(table) - 1 == self.number_of_holes and table[-1].count(None) == 0:
                self.finished = True


class HolesMatch(Match):
    def __init__(self, number_of_holes, arr_with_players):
        Match.__init__(self, number_of_holes, arr_with_players)
        self.num_of_try = [0 for player in self.arr_with_players]
        self.num_of_hit = 0
        self.round = 0

    def hit(self, success=False):
        self.num_of_hit += 1
        if self.finished:
            raise RuntimeError
        else:
            if self.count == len(self.lap):
                self.count = 0
            if success:
                self.lap[self.count] = 1
            try:
                self.num_of_try[self.count] += 1
            except TypeError:
                self.num_of_try[self.count] = 1
            self.count += 1
            # Условие перехода к следующей лунке
            if self.num_of_hit % len(self.arr_with_players) == 0 and (
                            self.lap.count(1) > 0 or self.num_of_try.count(10) > 0):
                # Определяю какой игрок делает следующий удар
                self.round += 1
                if self.round > len(self.arr_with_players):
                    self.count = 0
                else:
                    self.count = self.round
                # Сбрасываю переменные на дефолтные значения
                self.table.append(tuple([0 if score is None else score for score in self.lap]))
                self.lap = [None for player in self.arr_with_players]
                self.num_of_try = [0 for player in self.arr_with_players]
            table = self.get_table()
            if len(table) - 1 == self.number_of_holes and table[-1].count(None) == 0:
                self.finished = True



