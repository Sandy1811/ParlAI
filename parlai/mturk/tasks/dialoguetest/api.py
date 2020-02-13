import random
from itertools import combinations
from typing import Dict, Text, Any, List, Optional


def is_equal_to(value):
    return lambda x: x == value


def contains(value):
    return lambda x: value in x


def is_one_of(value):
    return lambda x: x in value


def is_greater_than(value):
    return lambda x: x >= value


def is_less_than(value):
    return lambda x: x <= value


def contain_all_of(value):
    return lambda x: all([e in x for e in value])


def contain_at_least_one_of(value):
    return lambda x: all([e in value for e in x])


def is_not(constraint):
    return lambda x: not constraint(x)


def contains_substring(value):
    return lambda x: value in x

is_equal_to, contains, is_one_of, is_greater_than, is_less_than, contain_all_of, contain_at_least_one_of, is_not, contains_substring,


class KnowledgeBaseItem:
    def __init__(self, settings):
        self._id = hash(str(settings))
        self._settings = settings

    def __str__(self):
        return str(self._settings)

    def __hash__(self):
        return self._id

    def __eq__(self, other: "KnowledgeBaseItem") -> bool:
        return self._id == other._id

    def match(self, constraints: Dict[Text, Any]) -> bool:
        for parameter_name, constraint in constraints.items():
            row_value = self._settings.get(parameter_name)
            if not callable(constraint) and row_value != constraint:
                return False
            elif callable(constraint) and not constraint(row_value):
                return False
        return True


class KnowledgeBaseAPI:
    parameters = []
    descriptor_templates = {"General": lambda s: "{}".format(s)}

    def __init__(
        self, num_items: int = 1, required_parameters: Optional[List[Text]] = None
    ):
        self._dataset = []
        self._generate(num_items)
        self.required_parameters = required_parameters or []

    def _generate(self, num_items: int) -> None:
        for n in range(num_items):
            self._dataset.append(self._create_random_item(n))

    def _create_random_item(self, identification_number: int) -> KnowledgeBaseItem:
        # Build the settings by randomly choosing from the options
        # or from the constraints
        settings = {"id": identification_number}
        for parameter in self.parameters:
            settings.update(self._random_value(parameter, settings))

        return KnowledgeBaseItem(settings)

    def _random_value(
        self, parameter: Dict[Text, Any], settings: Dict[Text, Any]
    ) -> Dict[Text, Any]:

        check_enabled = parameter.get("Enabled")
        if callable(check_enabled) and not check_enabled(settings):
            return {}

        if parameter.get("Type") == "Integer":
            _min = parameter.get("Min", 0)
            _max = parameter.get("Max", 100)
            _min = _min(settings) if callable(_min) else _min
            _max = _max(settings) if callable(_max) else _max
            return {parameter["Name"]: random.randint(_min, _max)}
        elif parameter.get("Type") == "Categorical":
            return {parameter["Name"]: random.choice(parameter.get("Categories"))}
        elif parameter.get("Type") == "Boolean":
            return {parameter["Name"]: random.choice([False, True])}
        else:
            raise ValueError(
                f"Unknown parameter type '{parameter.get('Type')}' for parameter '{parameter.get('Name')}'."
            )

    def lookup(self, constraints: Dict[Text, Any]) -> List[KnowledgeBaseItem]:
        self._check_if_required_parameters_provided(constraints)

        return [item for item in self._dataset if item.match(constraints)]

    def get_all(
        self, constraints: Optional[Dict[Text, Any]] = dict()
    ) -> Optional[KnowledgeBaseItem]:
        filtered_items = self.lookup(constraints)
        return filtered_items

    def sample(
        self, constraints: Optional[Dict[Text, Any]] = dict()
    ) -> Optional[KnowledgeBaseItem]:
        filtered_items = self.lookup(constraints)
        if filtered_items:
            return random.choice(filtered_items), len(filtered_items)
        else:
            return None, 0

    def _check_if_required_parameters_provided(self, constraints):
        for parameter_name in self.required_parameters:
            if parameter_name not in constraints:
                raise ValueError(
                    f"Parameter '{parameter_name}' is required but was not provided."
                )


class ApartmentAPI(KnowledgeBaseAPI):
    parameters = [
        {"Name": "Level", "Type": "Integer", "Min": 0, "Max": 15},
        {
            "Name": "MaxLevel",
            "Type": "Integer",
            "Min": lambda p: p["Level"],
            "Max": 15,
        },
        {"Name": "HasBalcony", "Type": "Boolean"},
        {
            "Name": "BalconySide",
            "Type": "Categorical",
            "Categories": ["east", "north", "south", "west"],
            "Enabled": lambda p: p["HasBalcony"],
        },
        {
            "Name": "HasElevator",
            "Type": "Boolean",
            "Enabled": lambda p: p["MaxLevel"] > 0,
        },
        {"Name": "NumRooms", "Type": "Integer", "Min": 1, "Max": 7},
        {
            "Name": "FloorSquareMeters",
            "Type": "Integer",
            "Min": lambda p: p["NumRooms"] * 10,
            "Max": lambda p: p["NumRooms"] * 50,
        },
        {
            "Name": "NearbyPOIs",
            "Type": "Categorical",
            "Categories": list(combinations(["School", "TrainStation", "Park"], 2)),
        },
        {
            "Name": "Name",
            "Type": "Categorical",
            "Categories": ["One on Center Apartments", "Shadyside Apartments", "North Hill Apartments"],
        }
    ]

def apartment_search(apartment_api, constraints: Optional[Dict[Text, Any]] = dict()):
    row, count = apartment_api.sample(constraints)
    return row._settings, count

class RestaurantAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "Name",
            "Type": "Categorical",
            "Categories": ["Cactus Club", "Tamarind", "Legume", "Lucca", "The Porch"],
        },
        {
            "Name": "Cost",
            "Type": "Categorical",
            "Categories": ["Cheap", "Moderate", "Expensive"],
        },
        {"Name": "TakesReservations", "Type": "Boolean"},
        {"Name": "DoesDelivery", "Type": "Boolean"},
        {"Name": "AverageRating", "Type": "Integer", "Min": 1, "Max": 5,},
        {
            "Name": "Food",
            "Type": "Categorical",
            "Categories": [
                "Pizza",
                "Chinese",
                "Indian",
                "Burgers",
                "Italian",
                "Thai",
                "Steak",
            ],
        },
        {"Name": "AverageWaitMinutes", "Type": "Integer", "Min": 0, "Max": 60},
        {"Name": "OpenTimeHour", "Type": "Integer", "Min": 6, "Max": 10},
        {"Name": "CloseTimeHour", "Type": "Integer", "Min": 15, "Max": 23},
        {"Name": "MaxPartySize", "Type": "Integer", "Min": 2, "Max": 50},
        {
            "Name": "Location",
            "Type": "Categorical",
            "Categories": ["South", "West", "East", "North", "Center"],
        },
    ]


def restaurant_search(restaurant_api, constraints: Optional[Dict[Text, Any]] = dict()):
    return restaurant_api.sample(constraints)


def restaurant_reserve(restaurant_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["Name", "PartySize", "Time"]
    outputs = ["Reservation Confirmed", "Reservation Failed"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "Name": constraints["Name"],
        "TakesReservations": True,
        "MaxPartySize": is_greater_than(constraints["PartySize"]),
        "OpenTimeHour": is_less_than(constraints["Time"]),
        "CloseTimeHour": is_greater_than(constraints["Time"]),
    }

    row, _ = restaurant_api.sample(new_constraints)
    if row is None:
        return {"ReservationStatus": outputs[1]}
    else:
        return dict(**row._settings, ReservationStatus=random.choice(outputs))


class HotelAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "Name",
            "Type": "Categorical",
            "Categories": [
                "Shadyside Inn",
                "Hilton Hotel",
                "Hyatt Hotel",
                "Old Town Inn",
            ],
        },
        {
            "Name": "Cost",
            "Type": "Categorical",
            "Categories": ["Cheap", "Moderate", "Expensive"],
        },
        {"Name": "TakesReservations", "Type": "Boolean"},
        {"Name": "Service", "Type": "Boolean"},
        {"Name": "AverageRating", "Type": "Integer", "Min": 1, "Max": 5,},
        {
            "Name": "ServiceStartHour",
            "Type": "Integer",
            "Min": 6,
            "Max": 10,
            "Enabled": lambda p: p["Service"],
        },
        {
            "Name": "ServiceStopHour",
            "Type": "Integer",
            "Min": 15,
            "Max": 23,
            "Enabled": lambda p: p["Service"],
        },
        {
            "Name": "Location",
            "Type": "Categorical",
            "Categories": ["South", "West", "East", "North", "Center"],
        },
    ]


def hotel_search(hotel_api, constraints: Optional[Dict[Text, Any]] = dict()):
    return hotel_api.sample(constraints)


def hotel_reserve(hotel_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["Name", "StartDate", "EndDate"]
    outputs = ["Reservation Confirmed", "Reservation Failed"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "Name": constraints["Name"],
        "TakesReservations": True,
    }

    row, _ = hotel_api.sample(new_constraints)
    if row is None:
        return {"ReservationStatus": outputs[1]}
    else:
        return dict(**row._settings, ReservationStatus=random.choice(outputs))


def hotel_service_request(hotel_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["Name", "RoomNumber", "Time", "Request"]
    outputs = ["Request Confirmed", "Request Failed"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "Name": constraints["Name"],
        "Service": True,
        "ServiceStartHour": is_less_than(constraints["Time"]),
        "ServiceStopHour": is_greater_than(constraints["Time"]),
    }

    row, _ = hotel_api.sample(new_constraints)
    if row is None:
        return {"ReservationStatus": outputs[1]}
    else:
        return dict(**row._settings, ReservationStatus=random.choice(outputs))


class PlaneAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "DepartureCity",
            "Type": "Categorical",
            "Categories": [
                "Los Angeles",
                "San Francisco",
                "Chicago",
                "Detroit",
                "New York City",
                "Pittsburgh",
            ],
        },
        {
            "Name": "ArrivalCity",
            "Type": "Categorical",
            "Categories": [
                "Los Angeles",
                "San Francisco",
                "Chicago",
                "Detroit",
                "New York City",
                "Pittsburgh",
            ],
        },
        {"Name": "Price", "Type": "Integer", "Min": 150, "Max": 500},
        {"Name": "SeatsAvailable", "Type": "Boolean"},
        {
            "Name": "Class",
            "Type": "Categorical",
            "Categories": ["First", "Business", "Economy"],
        },
        {"Name": "DurationHours", "Type": "Integer", "Min": 1, "Max": 8},
        {
            "Name": "Airline",
            "Type": "Categorical",
            "Categories": ["American", "United", "Delta", "Virgin"],
        },
        {"Name": "id", "Type": "Integer", "Min": 1, "Max": 1000},
    ]


def plane_search(plane_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["DepartureCity", "ArrivalCity", "Date"]
    outputs = ["Request Confirmed", "Request Failed"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    return plane_api.sample(dict(constraints, SeatsAvailable=True))


def plane_reserve(plane_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["id"]
    outputs = ["Request Confirmed", "Request Failed"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    row, _ = plane_api.sample(dict(constraints, SeatsAvailable=True))

    if row is None:
        return {"ReservationStatus": outputs[1]}
    else:
        return dict(**row._settings, ReservationStatus=outputs[0])


class TripAPI(KnowledgeBaseAPI):
    parameters = [
        {"Name": "TripLengthMinutes", "Type": "Integer", "Min": 15, "Max": 120},
        {
            "Name": "TravelMode",
            "Type": "Categorical",
            "Categories": ["Transit", "Driving", "Walking"],
        },
        {
            "Name": "DepartureTime",
            "Type": "Integer",
            "Min": 6,
            "Max": 23,
            "Enabled": lambda p: p["TravelMode"] == "Transit",
        },
        {
            "Name": "TransitInstructions",
            "Type": "Categorical",
            "Categories": [
                [
                    "Walk to the bus stop at Forbes and Murray.",
                    "Take the 61A until the last stop.",
                    "After you get off the stop, turn left and walk down Craig St for 2 blocks.",
                    "Your destination will be on the left.",
                ],
                [
                    "Go to the bus stop at the corner of the intersection.",
                    "Take the 28X to Forbes and Atwood.",
                    "Walk in the same direction as the bus for 1 block.",
                    "Turn left at the football field.",
                    "Your destination will be on the right.",
                ],
                [
                    "Walk for 14 minutes to the bus stop on Wilkins and Beechwood.",
                    "Take the 67 and get off the University.",
                    "Walk for 1 more block and turn right at the Starbucks.",
                    "After one more block, your destination will be on the right.",
                ],
            ],
            "Enabled": lambda p: p["TravelMode"] == "Transit",
        },
        {
            "Name": "DrivingInstructions",
            "Type": "Categorical",
            "Categories": [
                [
                    "Go east on Forbes towards Murray",
                    "Turn right and drive for 1.6 kilometers and turn left on Murray",
                    "Drive for 700 meters until you reach Wilkins Avenue",
                    "Your destination will be on the right",
                ],
                [
                    "Drive south on Cassiar for 3 blocks and turn left on Broadway",
                    "After 3 kilometers, turn right on Commercial Drive",
                    "After 3 blocks, your destination will be on the left opposite the park.",
                ],
                [
                    "Turn right on El Camino Real",
                    "After 5 kilometers, turn right on Castro St.",
                    "Drive for 3 blocks and turn left",
                    "Your destination will be on the left.",
                ],
            ],
            "Enabled": lambda p: p["TravelMode"] == "Driving",
        },
        {
            "Name": "WalkingInstructions",
            "Type": "Categorical",
            "Categories": [
                [
                    "Walk 2 blocks east on Forbes Avenue, towards Murray",
                    "Turn right and walk for 3 blocks until you arrive at the church",
                    "Turn left and walk for 5 minutes until you see the park on your left.",
                    "Your destination will be on the right",
                ],
                [
                    "Walk east for 10 minutes on University Boulevard",
                    "Turn right on Allison Road, right after the McDonalds.",
                    "Turn left after the park and your destination will be on the left.",
                ],
                [
                    "Turn right on El Camino Real",
                    "After 5 blocks, turn right on Castro St.",
                    "Walk for 3 blocks and turn left at the pub",
                    "Your destination will be on the left.",
                ],
            ],
            "Enabled": lambda p: p["TravelMode"] == "Walking",
        },
        {
            "Name": "Price",
            "Type": "Integer",
            "Min": 0,
            "Max": 5,
            "Enabled": lambda p: p["TravelMode"] == "Transit",
        },
    ]


def trip_directions(trip_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "DepartureLocation",
        "ArrivalLocation",
        "TravelMode",
        "DepartureTime",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "TravelMode": constraints["TravelMode"],
    }

    # Only need this logic for transit
    if constraints["TravelMode"] == "Transit":
        new_constraints["DepartureTime"] = is_greater_than(constraints["DepartureTime"])

        rows = trip_api.get_all(new_constraints)
        row = min(rows, key=lambda e: e._settings.get("DepartureTime"))
    else:
        row, _ = trip_api.sample(new_constraints)

    return row._settings


def trip_traffic(trip_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "DepartureLocation",
        "ArrivalLocation",
        "TravelMode",
        "DepartureTime",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "TravelMode": constraints["TravelMode"],
    }

    # Only need this logic for transit
    if constraints["TravelMode"] == "Transit":
        new_constraints["DepartureTime"] = is_greater_than(constraints["DepartureTime"])

        rows = trip_api.get_all(new_constraints)
        row = min(rows, key=lambda e: e._settings.get("TripLengthMinutes"))
    else:
        row, _ = trip_api.sample(new_constraints)

    return row._settings


class RideAPI(KnowledgeBaseAPI):
    parameters = [
        {"Name": "Price", "Type": "Integer", "Min": 5, "Max": 50},
        {"Name": "AllowsChanges", "Type": "Boolean"},
        {"Name": "DurationMinutes", "Type": "Integer", "Min": 5, "Max": 30},
        {
            "Name": "ServiceProvider",
            "Type": "Categorical",
            "Categories": ["Uber", "Lyft", "Taxi"],
        },
        {
            "Name": "DriverName",
            "Type": "Categorical",
            "Categories": ["Mark", "John", "Dave", "Connor", "Alex"],
        },
        {
            "Name": "CarModel",
            "Type": "Categorical",
            "Categories": ["Honda", "Toyota", "Corolla", "Tesla", "BMW", "Ford"],
        },
        {
            "Name": "LicensePlate",
            "Type": "Categorical",
            "Categories": ["432 LSA", "313 EA9", "901 FSA", "019 EAS", "031 NGA"],
        },
        {"Name": "id", "Type": "Integer", "Min": 1, "Max": 1000},
    ]


def book_ride(ride_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["DepartureLocation", "ArrivalLocation"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    del constraints["DepartureLocation"]
    del constraints["ArrivalLocation"]
    return ride_api.sample(constraints)


def ride_status(ride_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["id"]

    ride_status_outputs = [
        "Your driver is dropping off another passenger.",
        "Your ride is on its way.",
        "Your driver is arriving.",
    ]
    ride_wait_outputs = [
        "{0} minutes away".format(random.randint(0, 5)) for _ in range(30)
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    row, _ = ride_api.sample(constraints)

    return dict(
        **row._settings,
        RideStatus=random.choice(ride_status_outputs),
        RideWait=random.choice(ride_wait_outputs),
    )


def ride_change(ride_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["id"]

    outputs = [
        "Your trip has been successfuly changed.",
        "We are unable to change your trip.",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    if "DepartureLocation" not in constraints and "ArrivalLocation" not in constraints:
        raise ValueError(
            f"One of DepartureLocation or ArrivalLocation must be provided."
        )

    new_constraints = {
        "id": constraints["id"],
        "AllowsChanges": True,
    }
    row, _ = ride_api.sample(constraints)

    if row is None:
        return {"ChangeStatus": outputs[1]}
    else:
        return dict(**row._settings, ReservationStatus=outputs[0])


class MovieAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "Name",
            "Type": "Categorical",
            "Categories": [
                "The Joker",
                "Lion King",
                "Ford v Ferrari",
                "Now You See Me",
                "Forrest Gump",
                "Harry Potter",
                "Titanic",
                "Good Will Hunting",
            ],
        },
        {
            "Name": "Actors",
            "Type": "Categorical",
            "Categories": list(
                combinations(
                    [
                        "Leonardo DiCaprio",
                        "Matt Damon",
                        "Emma Watson",
                        "Jennifer Lawrence",
                        "Ben Afleck",
                        "Tom Cruise",
                        "Brad Pitt",
                    ],
                    2,
                )
            ),
        },
        {
            "Name": "Director",
            "Type": "Categorical",
            "Categories": [
                "Steven Spielberg",
                "Quentin Tarantino",
                "Christopher Nolan",
                "George Lucas",
                "Michael Bay",
                "Ron Howard",
            ],
        },
        {"Name": "DurationMinutes", "Type": "Integer", "Min": 90, "Max": 150},
        {
            "Name": "Genre",
            "Type": "Categorical",
            "Categories": ["Comedy", "Drama", "Fantasy", "SciFi", "Romance", "Action"],
        },
        {
            "Name": "Platforms",
            "Type": "Categorical",
            "Categories": ["Netflix", "Hulu", "Amazon Prime", "DVD"],
        },
    ]


def movie_search(movie_api, constraints: Optional[Dict[Text, Any]] = dict()):
    return movie_api.sample(constraints)


class WeatherAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "City",
            "Type": "Categorical",
            "Categories": [
                "Los Angeles",
                "San Francisco",
                "Chicago",
                "Detroit",
                "New York City",
                "Pittsburgh",
            ],
        },
        {
            "Name": "Weather",
            "Type": "Categorical",
            "Categories": ["Raining", "Snowing", "Sunny", "Partly Cloudy", "Cloudy"],
        },
        {"Name": "TemperatureCelsius", "Type": "Integer", "Min": -5, "Max": 30},
        {
            "Name": "Day",
            "Type": "Categorical",
            "Categories": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ],
        },
    ]


def weather(weather_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["City", "Day"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    return weather_api.sample(constraints)


class BankAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "BankName",
            "Type": "Categorical",
            "Categories": ["Chase", "Bank of America", "PNC", "Wells Fargo"],
        },
        {"Name": "BankBalance", "Type": "Integer", "Min": 0, "Max": 10000},
    ]


def bank_balance(bank_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "AccountNumber",
        "FullName",
        "BankName",
        "DateOfBirth",
        "PIN",
        "SecurityAnswer1",
        "SecurityAnswer2",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "BankName": constraints["BankName"],
    }

    return bank_api.sample(new_constraints)


def bank_fraud_report(bank_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "AccountNumber",
        "FullName",
        "BankName",
        "DateOfBirth",
        "PIN",
        "SecurityAnswer1",
        "SecurityAnswer2",
        "FraudReport",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "BankName": constraints["BankName"],
    }

    row, _ = bank_api.sample(new_constraints)
    if row is not None:
        return {"Confirmation": "Fraud report submitted successfully."}
    else:
        return {"Confirmation": "Error finding bank account."}


class ShoppingAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "ItemType",
            "Type": "Categorical",
            "Categories": [
                "Clothing",
                "Shoe",
                "Electronic",
                "Phone",
                "Appliance",
                "Furniture",
                "Toy",
            ],
        },
        {"Name": "Price", "Type": "Integer", "Min": 5, "Max": 1000},
        {
            "Name": "ItemName",
            "Type": "Categorical",
            "Categories": [
                "Blue Item",
                "Red Item",
                "Green Item",
                "Black Item",
                "White Item",
            ],
        },
        {
            "Name": "ItemSize",
            "Type": "Categorical",
            "Categories": ["XS", "S", "M", "L", "XL"],
            "Enabled": lambda p: p["ItemType"] == "Clothing",
        },
        {
            "Name": "ItemSize",
            "Type": "Integer",
            "Min": 5,
            "Max": 13,
            "Enabled": lambda p: p["ItemType"] == "Shoe",
        },
        {
            "Name": "ShippingSpeed",
            "Type": "Categorical",
            "Categories": list(
                combinations(
                    [
                        "Same Day",
                        "1 Business Day",
                        "2 Business Days",
                        "3 Business Days",
                        "7 Business Days",
                    ],
                    2,
                )
            ),
        },
        {"Name": "ItemNumber", "Type": "Integer", "Min": 100, "Max": 999},
    ]


def shopping_search(shopping_api, constraints: Optional[Dict[Text, Any]] = dict()):
    return shopping_api.sample(constraints)


def shopping_order_item(shopping_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "ItemNumber",
        "Address",
        "CreditCardInfo",
        "Name",
        "ShippingSpeed",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    new_constraints = {
        "ItemNumber": constraints["ItemNumber"],
        "ShippingSpeed": contains(constraints["ShippingSpeed"]),
    }

    row, _ = shopping_api.sample(new_constraints)

    if row is None:
        return dict(
            Message="Sorry we were unable to process the order. Please check the item number or the shipping speed."
        )
    else:
        return dict(
            **row._settings, Message="Order confirmed. Your item will be shipped soon."
        )


def shopping_order_item(shopping_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["ItemNumber", "Address", "Name"]
    outputs = [
        "Your order is being processed. It will be shipped soon.",
        "Your order is on its way.",
        "Your order is arriving soon.",
        "There is a delay in your order.",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    return dict(Message=random.choice(outputs))


class ScheduleAPI(KnowledgeBaseAPI):
    parameters = [
        {
            "Name": "Name",
            "Type": "Categorical",
            "Categories": [
                "John",
                "Michael",
                "Southside Venue",
                "Dr. Johnson",
                "North Heights Venue",
                "Dr. Morgan",
                "Fred",
                "George",
                "Dr. Alexis",
                "Conference Room 43",
                "Conference Room 91",
                "One on Center Apartments",
                "Shadyside Apartments",
                "North Hill Apartments",
            ],
        },
        {
            "Name": "Day",
            "Type": "Categorical",
            "Categories": [
                "Sunday",
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
            ],
        },
        {"Name": "StartTimeHour", "Type": "Integer", "Min": 0, "Max": 20},
        {
            "Name": "EndTimeHour",
            "Type": "Integer",
            "Min": lambda p: p["StartTimeHour"] + 2,
            "Max": lambda p: p["StartTimeHour"] + 2,
        },
        {
            "Name": "SizeLimit",
            "Type": "Integer",
            "Min": 3,
            "Max": 100,
            "Enabled": lambda p: "Conference" in p["Name"] or "Venue" in p["Name"],
        },
    ]


def schedule_meeting(schedule_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["Name", "Day", "StartTimeHour", "EndTimeHour"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    outputs = [
        "Your meeting has been successfuly scheduled.",
        "{0} has a conflicting meeting at that time. Try another meeting time.".format(
            constraints["Name"]
        ),
    ]

    new_constraints = {
        "Name": constraints["Name"],
        "Day": constraints["Day"],
        "StartTimeHour": is_greater_than(constraints["StartTimeHour"]),
        "EndTimeHour": is_greater_than(constraints["EndTimeHour"]),
    }

    row, _ = schedule_api.sample(new_constraints)
    if row is None:
        return dict(Message=outputs[0])
    else:
        return dict(Message=outputs[1])


def book_doctor_appointment(
    schedule_api, constraints: Optional[Dict[Text, Any]] = dict()
):
    required_parameters = [
        "Name",
        "PatientName",
        "StartTimeHour",
        "EndTimeHour",
        "Day",
        "Symptoms",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    outputs = [
        "Your appointment has been successfuly scheduled.",
        "{0} has a conflicting meeting at that time. Try another meeting time or another doctor.".format(
            constraints["Name"]
        ),
    ]
    new_constraints = {
        "Name": constraints["Name"],
        "Day": constraints["Day"],
        "StartTimeHour": is_greater_than(constraints["StartTimeHour"]),
        "EndTimeHour": is_greater_than(constraints["EndTimeHour"]),
    }
    row, _ = schedule_api.sample(new_constraints)
    if row is None:
        return dict(Message=outputs[0])
    else:
        return dict(Message=outputs[1])


def book_apartment(schedule_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "Name",
        "RenterName",
        "StartTimeHour",
        "EndTimeHour",
        "Day",
        "ApplicationFeePaid",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )
    outputs = [
        "Your apartment viewing has been successfuly scheduled.",
        "That time is unavailable for {0}. Please try another time.".format(
            constraints["Name"]
        ),
    ]
    new_constraints = {
        "Name": constraints["Name"],
        "Day": constraints["Day"],
        "StartTimeHour": is_greater_than(constraints["StartTimeHour"]),
        "EndTimeHour": is_greater_than(constraints["EndTimeHour"]),
    }
    row, _ = schedule_api.sample(new_constraints)
    if row is None:
        required_items = [
            "Passport",
            "Proof of Income",
            "SCHUFA certificate",
            "Bank Statement",
        ]
        return dict(
            Message=outputs[0]
            + " Please bring {0} and {1} with you.".format(
                random.choice(required_items), random.choice(required_items)
            )
        ), 1
    else:
        return dict(Message=outputs[1]), 1


def followup_doctor_appointment(
    schedule_api, constraints: Optional[Dict[Text, Any]] = dict()
):
    required_parameters = ["Name", "PatientName"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    outputs = [
        "You must take your medicine 2 times a day before meals.",
        "Take your medicine before you go to sleep. If you experience nausea, please contact your doctor immediately.",
    ]

    return dict(Message=random.choice(outputs))


def party_plan(schedule_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "Name",
        "HostName",
        "StartTimeHour",
        "EndTimeHour",
        "Day",
        "NumberGuests",
        "FoodRequest",
        "DrinksRequest",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    schedule_outputs = [
        "Your event has been successfuly scheduled.",
        "{0} is booked at that time. Try another meeting time or another venue.".format(
            constraints["Name"]
        ),
    ]
    size_outputs = [
        "Your event has been successfuly scheduled.",
        "{0} is too small for your party. Try another venue.".format(
            constraints["Name"]
        ),
    ]

    new_constraints = {
        "Name": constraints["Name"],
        "Day": constraints["Day"],
        "StartTimeHour": is_greater_than(constraints["StartTimeHour"]),
        "EndTimeHour": is_greater_than(constraints["EndTimeHour"]),
    }
    row, _ = schedule_api.sample(new_constraints)
    if row is not None:
        return dict(Message=schedule_outputs[1])

    new_constraints = {
        "Name": constraints["Name"],
        "SizeLimit": is_greater_than(constraints["NumberGuests"]),
    }
    row, _ = schedule_api.sample(new_constraints)
    if row is not None:
        return dict(Message=size_outputs[0])
    else:
        return dict(Message=size_outputs[1])


def party_rsvp(schedule_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = [
        "Name",
        "NumberOfGuests",
        "EventName",
        "ArrivalTime",
        "NeedParking",
        "DietaryRestrictions",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    return dict(Message="Thank you for your RSVP. See you there.")


def spaceship_access_codes(null_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["UserName", "UserRank", "Code", "CodeType"]
    outputs = [
        "The code is 431931",
        "Sorry, you are not authorized to receive the code. Please obtain a clearance code from the Captain.",
    ]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    if (
        constraints["UserRank"] not in ["Captain", "First Officer"]
        and constraints["CodeType"] != "Clearance"
    ):
        return dict(Message=outputs[1])
    else:
        return dict(Message=outputs[0])


def spaceship_life_support(null_api, constraints: Optional[Dict[Text, Any]] = dict()):
    required_parameters = ["LockManufacturer", "ColorOfTopCable", "ColorOfSecondCable"]
    outputs = ["Successful! Door opened"]

    for parameter in required_parameters:
        if parameter not in constraints:
            raise ValueError(
                f"Parameter '{parameter}' is required but was not provided."
            )

    return dict(Message=outputs[0])

apartment_api = ApartmentAPI(1000)
schedule_api = ScheduleAPI(100)
api_map = {
    'apartment_search': (apartment_search, apartment_api),
    'book_apartment': (book_apartment, schedule_api),
}

def call_api(api_name, constraints):
    api_fn, api_obj = api_map.get(api_name, (None, None))
    if api_fn is None:
        raise ValueError(
            f"API Name '{api_name}' is invalid."
        )

    return api_fn(api_obj, constraints)


if __name__ == "__main__":
    a = TripAPI(100)
    print(
        trip_traffic(
            a,
            {
                "DepartureLocation": "a",
                "ArrivalLocation": "b",
                "TravelMode": "Walking",
                "DepartureTime": 9,
            },
        )
    )
    


