import json
import sys

class Tests:

    @staticmethod
    def test_one():
        choice = input("which folder ? (1, 2, 3, 4, 5) ")
        while choice != "q":
            print(Tests.test(choice))
            choice = input("which folder ? (1, 2, 3, 4, 5) ")


    @staticmethod
    def test_all(max):
        current = 1
        while current <= max:
            print(Tests.test(current))
            current += 1
            input()

    @staticmethod
    def test(choice):
        folder = "level{}/data/".format(choice)

        with open(folder + "output.json") as f:
            my_output = json.load(f)

        with open(folder + "expected_output.json") as f:
            expected_output = json.load(f)
        print("Comparing between your output and the expected output in level{}...".format(choice))
        if (expected_output == my_output):
            return "Result: ✅"
        else:
            return "Result: ❌"

if sys.argv[1] == "all":
    Tests.test_all(5)
elif sys.argv[1] == "one":
    Tests.test_one()
else:
    print("Type one or all")