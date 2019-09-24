import json
from datetime import datetime

# changer ça
with open('data/input.json') as f:
    read_data = json.load(f)


class Car:
    def __init__(self, id, price_per_day, price_per_km):
        self.id = id
        self.price_per_day = price_per_day
        self.price_per_km = price_per_km

class Actor:
    def __init__(self, total, days, options):
        self.options = options
        self.days = days

    def get_actions(self):
        raise NotImplementedError("Implement this method")

    def get_options(self):
        if self.options == []:
            return 0
        else:
            return sum([Option(option, self.days).get_option_fee() for option in self.own_options if option in self.options])

class CarOwner(Actor):
    def __init__(self, total, days, options):
        super().__init__(total, days, options)
        self.commission = total * (70 / 100)
        self.own_options = ["gps", "baby_seat"]

    def get_actions(self):
        return {
            "who": "owner",
            "type": "credit",
            "amount": self.commission + self.get_options()
        }



class Drivy(Actor):
    def __init__(self, total, days, options):
        super().__init__(total, days, options)
        self.commission = total * (30 / 100)
        self.own_options = ["additional_insurance"]

    def get_insurance_fee(self):
        return {
            "who": "insurance",
            "type": "credit",
            "amount": self.commission / 2
        }

    def get_assistance_fee(self):
        return {
            "who": "assistance",
            "type": "credit",
            "amount": self.days * 100
        }

    def get_drivy_fee(self):
        return {
            "who": "drivy",
            "type": "credit",
            "amount": self.commission + self.get_options() - self.get_assistance_fee()["amount"] - self.get_insurance_fee()["amount"]
        }

    def get_actions(self):
        return [self.get_insurance_fee(), self.get_assistance_fee(), self.get_drivy_fee()]


class Driver(Actor):
    def __init__(self, id, options):
        self.id = id
        self.car_id = read_data["rentals"][id - 1]["car_id"]
        self.car = Car(self.car_id, read_data["cars"][self.car_id - 1]
                       ["price_per_day"], read_data["cars"][self.car_id - 1]["price_per_km"])
        self.start_date = datetime.strptime(
            read_data["rentals"][id - 1]["start_date"], "%Y-%m-%d")
        self.end_date = datetime.strptime(
            read_data["rentals"][id - 1]["end_date"], "%Y-%m-%d")
        self.distance = read_data["rentals"][id - 1]["distance"]
        self.options = options

    def get_rental_days(self):
        return (self.end_date - self.start_date).days + 1

    def get_time_component(self):
        rental_days = self.get_rental_days()
        decreasing_price = 0
        while rental_days > 0:
            if rental_days > 10:
                decreasing_price += self.car.price_per_day - \
                    self.car.price_per_day * (50 / 100)
            elif rental_days > 4 and rental_days <= 10:
                decreasing_price += self.car.price_per_day - \
                    self.car.price_per_day * (30 / 100)
            elif rental_days > 1 and rental_days <= 4:
                decreasing_price += self.car.price_per_day - \
                    self.car.price_per_day * (10 / 100)
            else:
                decreasing_price += self.car.price_per_day
            rental_days -= 1
        return decreasing_price

    def get_distance_component(self):
        return self.distance * self.car.price_per_km

    def get_total_options(self):
        return self.get_distance_component() + self.get_time_component() + sum([Option(option, self.get_rental_days()).get_option_fee() for option in self.options])

    def get_total_no_options(self):
        return self.get_distance_component() + self.get_time_component()

    def get_actions(self):
        return {
            "who": "driver",
            "type": "debit",
            "amount": self.get_total_options()
        }


class Option:
    def __init__(self, option, days):
        self.option = option
        self.days = days

    def get_option_fee(self):
        options = {
            "gps": 500 * self.days,
            "baby_seat": 200 * self.days,
            "additional_insurance": 1000 * self.days
        }
        return options[self.option]


data = {}
data["rentals"] = []
for d in read_data["rentals"]:
    options = [option["type"] for option in read_data["options"]
               if option["rental_id"] == d["id"]]
    driver = Driver(d["id"], options)
    drivy = Drivy(driver.get_total_no_options(),
                  driver.get_rental_days(), options)
    car_owner = CarOwner(driver.get_total_no_options(),
                         driver.get_rental_days(), options)
    data["rentals"].append({
        "id": driver.id,
        "options": options,
        "actions": [driver.get_actions(), car_owner.get_actions(), *drivy.get_actions()]
    })

with open('data/output.json', 'w') as out:
    json.dump(data, out, indent=2)
