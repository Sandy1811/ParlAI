
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
        "RideStatus": "Your Driver is arriving",
        "RideWait": 12,
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


def get_plane_reserve_item():
    kb_item = {
        "id": 666,
        "CustomerName": "Sally"
    }

    utterances = [
        "Heyho partner",
        "Whats your name?",
        "Find your flight ID for me please",
        "That flight, however, is not available any more",
        "Got that, can i reserve that for you?",
        "Alright, your reservation is done!",
        "Sorry, but your reservation failed for some reason",
        "cheers and bye"
    ]

    return kb_item, utterances, 'plane_reserve'


def get_party_plan_item():
    kb_item = {
        "Name": "The Awesome Party Venue",
        "HostName": "Joni",
        "Day": "Saturday",
        "StartTimeHour": 16,
        "EndTimeHour": 22,
        "NumberGuests": 12
    }

    utterances = [
        'Heyho, whats up?',
        'Where do you want to get hammered?',
        'Whos hosting this?',
        'How many of you will be dancing and drinking?',
        'When do you want to start?',
        'When should we shove you out of the door again?',
        'What day of the week are you thinkging of?',
        'Any spefific food wishes?',
        'Any drinks prefs you\'ve got?',
        'Sorry mate, but this is not going to work out.',
        'Right, they are happy to have you, can I book this now?',
        'Cool, all booked and all done!',
        'Oops, something went horribly wrong.'
    ]

    return kb_item, utterances, 'party_plan'


def get_party_rsvp_item():
    kb_item = {
        "Name": "John",
        "HostName": "Joanne",
        "GuestName": "Mike",
        "ArrivalTime": 20,
        "NumberGuests": 12,
        "NeedParking": False
    }

    utterances = [
        'Howdie buddy',
        'Your name?',
        'Where is shit going down?',
        'Who is hosting this?',
        'Whats your ETA?',
        'How many of your lads will come with you?',
        'Any of you vegan or got a food allergy?',
        'Your rsvp is done.'
    ]

    return kb_item, utterances, 'party_rsvp'


def get_plane_search_item():
    kb_item = {
        "DepartureCity": "Vienna",
        "ArrivalCity": "New York",
        "Price": 300,
        "Date": 12,
        "Class": "Economy",
        "Duration": 6,
        "Airline": "Virgin"
    }

    utterances = [
        'Hey, whats up?',
        'What did they call you when you were born?',
        'From where are you going?',
        'Going to where?',
        'When do you want to go?',
        'I can filter for other things such as price or duration if you want.',
        'Great, I found an American flight in business class for 500 bucks. Takes 8 hours though.',
        'Want to search for anything else?',
        'Cheers and see you.',
    ]

    return kb_item, utterances, 'plane_search'


def get_restaurant_reserve_item():
    kb_item = {
        "Name": "Cactus Club",
        "Time": 21,
        "PartySize": 4,
        "CustomerName": "Jane"
    }

    utterances = [
        'Hi',
        'Can you give me your esteemed name sir?',
        'What shed to you want to eat at?',
        'When do you want to stuff yourselves?',
        'How many of you are going to be there?',
        'Sorry but this place doesnt want you.',
        'Great, the Cactus Club is delighted to take your booking.',
        'Booking successful',
        'Booking failed!',
        'Bye'
    ]

    return kb_item, utterances, 'restaurant_reserve'


def get_restaurant_search_item():
    kb_item = {
        "Name": "Harmonium",
        "Cost": "Moderate",
        "TakesReservations": True,
        "DoesDelivery": False,
        "AverageRating": 5,
        "Food": "Burgers",
        "AverageWaitMinutes": 32,
        "OpenTimeHour": 11,
        "CloseTimeHour": 23,
        "MaxPartySize": 12,
        "Location": "North"
    }

    utterances = [
        'Hello my friend, what can I do for you today?',
        'Whats your name?',
        'Any restaurant you have in mind?',
        'What district do you want to go to?',
        'Any wishes cuisinewise?',
        'Whats your rating criteria?',
        'Do you need a delivery service?',
        'Do you need a place where you can reserve a table?',
        'Right, there is the Hove Kitchen that serves great food and its in the West part of town. Its average rating is 4 and its in the Expensive price category.',
        'Do you want to search for any more eateries?'
    ]

    return kb_item, utterances, 'restaurant_search'