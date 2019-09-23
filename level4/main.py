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


class CarOwner:
    def __init__(self, car_id, total):
        self.car_id = car_id
        self.commission = total * (70 / 100)

    def get_action(self):
        return {
            "who": "owner",
            "type": "credit",
            "amount": self.commission
        }

class Drivy:
    def __init__(self, total, days):
        self.total = total
        self.commission = total * (30 / 100)
        self.days = days

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
            "amount": self.commission - self.get_assistance_fee()["amount"] - self.get_insurance_fee()["amount"]
        }

    def get_actions(self):
        return [self.get_assistance_fee(), self.get_drivy_fee(), self.get_insurance_fee()]


class Driver:
    def __init__(self, id):
        self.id = id
        self.car_id = read_data["rentals"][id - 1]["car_id"]
        self.car = Car(self.car_id, read_data["cars"][self.car_id - 1]
                       ["price_per_day"], read_data["cars"][self.car_id - 1]["price_per_km"])
        self.start_date = datetime.strptime(
            read_data["rentals"][id - 1]["start_date"], "%Y-%m-%d")
        self.end_date = datetime.strptime(
            read_data["rentals"][id - 1]["end_date"], "%Y-%m-%d")
        self.distance = read_data["rentals"][id - 1]["distance"]

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

    def get_total(self):
        return self.get_distance_component() + self.get_time_component()

    def get_action(self):
        return {
            "who": "driver",
            "type": "debit",
            "amount": self.get_total()
        }


data = {}
data["rentals"] = []
for d in read_data["rentals"]:
    driver = Driver(d["id"])
    drivy = Drivy(driver.get_total(), driver.get_rental_days())
    carOwner = CarOwner(d["id"], driver.get_total())
    data["rentals"].append({
        "id": driver.id,
        "actions": [driver.get_action(), carOwner.get_action(), *drivy.get_actions()]
    })

with open('data/output.json', 'w') as out:
    json.dump(data, out)
