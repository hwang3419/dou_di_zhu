from collections import Counter
from itertools import combinations
import functools


class NotSameType(Exception):
    pass


class NotSameLength(Exception):
    pass


class NotValidInput(Exception):
    pass


class Hand():
    handName = None

    valueMap = {
        '3': 3,
        '4': 4,
        '5': 5,
        '6': 6,
        '7': 7,
        '8': 8,
        '9': 9,
        'x': 10,
        'j': 11,
        'q': 12,
        'k': 13,
        'a': 14,
        '2': 16,
        'y': 20,  # joker1
        'z': 30,  # joker2
    }

    def __init__(self, cards: list):
        self.cards = sorted([card.lower() for card in cards],
                            key=lambda x: self.valueMap.get(x))
        self.cardsValue = [self.valueMap[card] for card in self.cards]
        self.cardsValue.sort()
        self.isBomb = False
        self.majorCard = self.cardsValue[0]

    def checkInput(self):
        if not self.isValid():
            raise(NotValidInput('%s, is invalid %s type' %
                                (self.cards, self.handName)))

    def isValid(self):
        pass

    def __eq__(self, other):
        return

    def __lt__(self, other):
        if other.isBomb:
            return True
        self.isComparable(other)
        return self.majorCard < other.majorCard

    def __gt__(self, other):
        if other.isBomb:
            return False
        self.isComparable(other)
        return self.majorCard > other.majorCard

    def isComparable(self, other):
        if other.handName != self.handName:
            raise(NotSameType('can not compare %s,%s' %
                              (self.handName, other.handName)))
        if len(other.cardsValue) != len(self.cardsValue):
            raise(NotSameLength('%s, %s length \
                is not equal' % (len(self.cardsValue), len(other.cardsValue))))
        return True

    def __hash__(self):
        return hash(tuple(self.cardsValue))

    def __str__(self):
        return "%s-%s" % (self.handName, self.cardsValue)


class One(Hand):
    handName = 'One'

    def isValid(self) -> bool:
        return len(self.cards) == 1


class Pair(Hand):
    handName = 'Pair'
    totalCount = 2

    def isValid(self) -> bool:
        return len(self.cards) == 2 and self.cards[0] == self.cards[1]


class MultiPair(Hand):
    handName = 'MultiPair'

    def isValid(self) -> bool:
        if len(self.cardsValue) % 2 != 0 or len(self.cardsValue) < 6:
            return False
        result = []
        for i, v in enumerate(self.cardsValue):
            if i % Pair.totalCount != Pair.totalCount-1:
                continue
            pair = Pair(self.cards[i-1:i+1])
            if not pair.isValid():
                return False
            result.append(pair)
        for index, pair in enumerate(result):
            if index == 0:
                continue
            if pair.majorCard - 1 == result[index-1].majorCard:
                continue
            return False
        return True


class MultiTriple(Hand):
    handName = 'MultiTriple'

    def isValid(self) -> bool:
        if len(self.cardsValue) % 3 != 0 or len(self.cardsValue) < 6:
            return False
        result = []
        for i, v in enumerate(self.cardsValue):
            if i % 3 != Triple.totalCount-1:
                continue
            x = Triple(self.cards[i-2:i+1])
            if not x.isValid():
                return False
            result.append(x)
        for index, x in enumerate(result):
            if index == 0:
                continue
            if x.majorCard - 1 == result[index-1].majorCard:
                continue
            return False
        return True


class Triple(Hand):
    handName = 'Triple'
    totalCount = 3

    def isValid(self) -> bool:
        return len(self.cards) == 3 and \
            self.cards[0] == self.cards[1] == self.cards[2]


class Flush(Hand):
    handName = "Flush"

    def isValid(self) -> bool:
        if len(self.cardsValue) < 5:
            return False
        for i, value in enumerate(self.cardsValue):
            if i == 0:
                continue
            if value - self.cardsValue[i-1] != 1:
                return False
        return True


class FullHouse(Hand):
    handName = "FullHouse"
    majorCardCount = 3
    totalCount = 5

    def __init__(self, cards):
        self.cards = [card.lower() for card in cards]
        self.cardsValue = [self.valueMap[card] for card in self.cards]
        self.isBomb = False
        self.cardsCounter = Counter(self.cardsValue)
        for k, v in self.cardsCounter.items():
            if v == self.majorCardCount:
                self.majorCard = k

    def checkInput(self):
        if not self.isValid():
            raise(NotValidInput('%s, is invalid %s type' %
                                (self.cards, self.handName)))

    def isValid(self) -> bool:
        self.cardsCounter = Counter(self.cardsValue)
        if len(self.cardsValue) != self.totalCount:
            return False
        return sorted(self.cardsCounter.values()) == [2, 3]

    def __lt__(self, other):
        if other.isBomb:
            return True
        self.isComparable(other)
        return self.majorCard < other.majorCard

    def __gt__(self, other):
        if other.isBomb:
            return False
        self.isComparable(other)
        return self.majorCard > other.majorCard


class FullHouseWithOne(FullHouse):
    handName = "FullHouseWithOne"
    totalCount = 4

    def __init__(self, cards):
        super().__init__(cards)

    def isValid(self):
        self.cardsCounter = Counter(self.cardsValue)
        if len(self.cardsValue) != self.totalCount:
            return False
        return sorted(self.cardsCounter.values()) == [1, 3]


class FourWithTwo(FullHouse):
    handName = 'FourWithTwo'
    majorCardCount = 4
    totalCount = 6

    def __init__(self, cards):
        super().__init__(cards)

    def isValid(self):
        self.cardsCounter = Counter(self.cardsValue)
        if len(self.cardsValue) != self.totalCount:
            return False
        return sorted(self.cardsCounter.values()) == [2, 4]


class Bomb(Hand):
    handName = "Bomb"

    def __init__(self, cards):
        super().__init__(cards)
        self.isBomb = True

    def isValid(self) -> bool:
        if len(self.cardsValue) == 4:
            return len(set(self.cardsValue)) == 1
        elif len(self.cardsValue) == 2:
            return self.cardsValue == [20, 30]
        return False

    def isComparable(self, other):
        if len(self.cardsValue) in (2, 4) and\
                len(other.cardsValue) in (2, 4) and \
                self.handName == other.handName:
            return True
        raise(NotSameLength('%s, %s are not in same length' %
                            (self.cardsValue, other.cardsValue)))

    def __lt__(self, other):
        if len(other.cardsValue) == 2:
            return True
        if len(self.cardsValue) == 2:
            return False
        self.isComparable(other)
        return self.cardsValue[0] < other.cardsValue[0]

    def __gt__(self, other):
        if len(other.cardsValue) == 2:
            return False
        if len(self.cardsValue) == 2:
            return True
        self.isComparable(other)
        return self.cardsValue[0] > other.cardsValue[0]


class Player:
    cardsCountTypeMap = {
        1: [One],
        2: [Pair, Bomb],
        3: [Triple],
        4: [Bomb, FullHouseWithOne],
        5: [Flush, FullHouse],
        6: [Flush, FourWithTwo, MultiPair, MultiTriple],
        7: [Flush],
        8: [Flush, MultiPair],
        9: [Flush, MultiTriple]
    }

    def __init__(self, cards):
        self.cards = list(cards)

    def getPossibleHand(self, cardsInput):
        count = len(cardsInput)
        if count > 9:
            count = 7
        all_possible_hands = [handType(
            cardsInput) for handType in self.cardsCountTypeMap[count]
            if handType(cardsInput).isValid()]
        if not all_possible_hands:
            return None
        # print(all_possible_hands)
        return all_possible_hands[0]

    def getAllNextHand(self, hand=None):
        if hand is None:
            yield from self.getAllHand()
        else:
            for nextInput in combinations(self.cards, len(hand.cardsValue)):
                NextHand = self.getPossibleHand(nextInput)
                if NextHand is not None and NextHand > hand:
                    yield NextHand

    def getAllHand(self):
        for i in range(len(self.cards), 0, -1):
            for nextInput in combinations(self.cards, i):
                result = self.getPossibleHand(nextInput)
                if result:
                    yield result


def removeList(lst, delList):
    result = lst[:]
    for item in delList:
        result.remove(item)
    return result


class Match:

    def __init__(self):
        pass

    def nextA(self, a, b, inComeHand=None):
        hands = {}
        if not a.cards:
            return True
        if not b.cards:
            return False
        gen = set(a.getAllNextHand(inComeHand))
        if not gen:
            return self.nextB(a, b)
        for hand in gen:
            result = self.nextB(Player(
                removeList(a.cards, hand.cards)), b, hand)
            if result is False: continue
            hands['a', tuple(hand.cardsValue) ] = result
        return hands if hands else self.nextB(a, b)

    def nextB(self, a, b, inComeHand=None):
        hands = {}
        if not a.cards:
            return True
        if not b.cards:
            return False
        gen = set(b.getAllNextHand(inComeHand))
        if not gen:
            return self.nextA(a, b)
        for hand in gen:
            result = self.nextA(a, Player(removeList(
                    b.cards, hand.cards)), hand)
            if result is False: return False
            hands['b', tuple(hand.cardsValue)] = result

        return hands if hands else False


def printHelper(data, x=0):
    if isinstance(data, dict):
        for k, v in data.items():
            print(' '*x, k)
            printHelper(v, x+3)
    elif isinstance(data, list):
        print(' '*x, data)
    else:
        print(' '*x, data)

def startA(pa, pb):
    gen = set(pa.getAllNextHand())
    hands = {}
    for hand in gen:
        y = Match().nextB(Player(
                removeList(pa.cards, hand.cards if hand else [])), pb, hand)
        if y:
            hands['a',tuple(hand.cardsValue)] = y
        
        
        
    return hands


if __name__ == '__main__':
    pa = Player('2q639994')
    pa = Player('2q639994')
    pb = Player('zaaj43')
    #pa = Player('3478')
    #pb = Player('47')
    hands = startA(pa, pb)
    printHelper(hands)
    print(type(hands))
