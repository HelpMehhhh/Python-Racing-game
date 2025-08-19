from enum import Enum


class Test():
    def __init__(self, testnum):
        self.testnum = testnum

    def function(self):
        self.testnum += 0.0001


def main():
    cars = [{"model": Test(1), "pram1": 1}]
    while True:
        cars[0]["model"].function()
        other_func(cars)


def other_func(cars):
    print(cars[0]["model"].testnum)

if __name__ == '__main__':
    main()