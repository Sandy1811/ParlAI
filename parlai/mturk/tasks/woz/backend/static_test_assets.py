
def get_book_ride_item():
    kb_item =  {
        "id": 660,
        "Price": 22,
        "AllowsChanges": False,
        "MinutesTillPickup": 20,
        "ServiceProvider": "Uber",
        "DriverName": "Ella",
        "CarModel": "Ford",
        "LicensePlate": "432 LSA",
        "DepartureLocation": "Tegel Airport, International Arrivals",
        "ArrivalLocation": "Hyatt Alexanderplatz",
    }

    utterances = [
        'Right, Could you provide your name?',
        'No problem, where can the driver pick you up from?',
        'whats your name?',
        'where do you like to go, sir?',
        'thats all booked for you now.',
        'Your car will arrive in 34 minutes and your driver will be Carl in some old car. He is from Uber btw.',
        'i can filter for another service provider if you want'
    ]

    return kb_item, utterances, 'book_ride'


def get_ride_status_item():
    kb_item = {
        "Price": 22,
        "AllowsChanges": False,
        "DurationMinutes": 12,
        "ServiceProvider": "Uber",
        "DriverName": "Ella",
        "CarModel": "Ford",
        "LicensePlate": "432 LSA",
        "DepartureLocation": "Tegel Airport, International Arrivals",
        "ArrivalLocation": "Hyatt Alexanderplatz",
        "id": 678
    }

    utterances = [
        "Your driver Jack will arrive shortly. He got held up due to traffic.",
        "Your ride will arrive in about 7 minutes.",
        "Can I have your name?",
        "Whats your booking id?",
        "hi",
        "Bye"
    ]

    return kb_item, utterances, 'ride_status'


def get_ride_change_item():
    kb_item = {

    }

    utterances = [
        "howdy cowboy",
        "What do you want changed?",
        "Whats your confirmation code?",
        "You need to to tell me your name",
        "Yes, successfully changed the ride for you",
        "Sorry, changes are not possible",
        "cya"
    ]

    return kb_item, utterances, 'ride_change'


def get_hotel_search_item():
    kb_item_1 = {
        "Name": "Old Town Inn",
        "Cost": "Cheap",
        "TakesReservations": True,
        "Service": False,
        "Location": "North",
        "AverageRating": 3,
        "ServiceStartHour": 10,
        "ServiceStopHour": 4
    }

    kb_item_2 = {
        "Name": "The Fake Hyatt",
        "Cost": "Cheap",
        "TakesReservations": True,
        "Service": True,
        "Location": "East",
        "AverageRating": 2,
        "ServiceStartHour": 10,
        "ServiceStopHour": 4
    }

    utterances = [
        "hohoho",
        "I can search for other things such as cost or location",
        "What hotel do you want?",
        "Its the Marriott",
        "Where do you want to go?",
        "In the North",
        "How much money do you want to spend?",
        "The hotel is a moderately priced place",
        "What rating should the place have?",
        "The hotel has an average rating of 3.3",
        "Great, I found a hotel in the south that matches your search criterea.",
        "Anything else you want to search for?",
        "bybo"
    ]

    return kb_item_2, utterances, 'hotel_search'


def get_hotel_reserve_item():
    kb_item = {
        "Name": "Old Town Inn",
        "StartDate": 12,
        "EndDate": 27,
        "CustomerName": "Ben",
        "CustomerRequest": "vegan breakfast"
    }

    utterances = [
        "hohoho",
        "howdy partner",
        "Hello, what can I do for you today?",
        "Whats your name, please?",
        "When are you going to checkin?",
        "And checkout is when?",
        "Anything special the hotel should provide you with?",
        "Oh no, I'm sorry, but there doesn't seem to be a room available.",
        "Great, I found a hotel that matches your criteria, can I book this for you now?",
        "Yay, booking completed successfully!",
        "Sorry, but the booking request failed.",
        "Bye"
    ]

    return kb_item, utterances, 'hotel_reserve'