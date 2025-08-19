

class Test():
    def __init__(self, testnum):
        self.testnum = testnum

    def function(self):
        print(self.testnum)


def main():
    num = 0
    test = Test(num)
    while True:
        num += 1
        test.function()

if __name__ == '__main__':
    main()