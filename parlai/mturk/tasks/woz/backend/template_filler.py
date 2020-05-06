from typing import Dict, Text, Any, List, Optional

from parlai.mturk.tasks.woz.backend import constants


def fill_hello(intent2reply, *_):
    return intent2reply[constants.INTENT_HELLO]


def fill_ask_name(intent2reply, *_):
    return intent2reply[constants.INTENT_ASK_NAME]


def fill_out_of_scope(intent2reply, *_):
    return intent2reply[constants.INTENT_OUT_OF_SCOPE]


def fill_anything_else(intent2reply, *_):
    return intent2reply[constants.INTENT_ANYTHING_ELSE]


def fill_ride_ask_destination(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_ASK_DESTINATION]


def fill_ride_ask_departure(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_ASK_DEPARTURE]


def fill_ride_ask_confirm_booking(intent2reply, kb_item):
    if not check_kb_item(
        kb_item,
        [
            "ServiceProvider",
            "Price",
            "MinutesTillPickup",
            "DepartureLocation",
            "ArrivalLocation",
        ],
    ):
        return None
    return intent2reply[constants.INTENT_RIDE_ASK_CONFIRM_BOOKING].format(
        service_provider=kb_item["ServiceProvider"],
        departure_location=kb_item["DepartureLocation"],
        arrival_location=kb_item["ArrivalLocation"],
        price=kb_item["Price"],
        minutes_till_pickup=kb_item["MinutesTillPickup"],
    )


def fill_ride_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_BYE]


def fill_ride_confirm_booking(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["CarModel", "id", "LicensePlate"]):
        return None
    return intent2reply[constants.INTENT_RIDE_CONFIRM_BOOKING].format(
        car_model=kb_item["CarModel"],
        booking_id=kb_item["id"],
        license_plate=kb_item["LicensePlate"],
    )


def fill_ride_inform_search_criteria(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_INFORM_SEARCH_CRITERIA]


def fill_ride_provide_driver_details(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["DriverName"]):
        return None
    return intent2reply[constants.INTENT_RIDE_PROVIDE_DRIVER_DETAILS].format(
        driver_name=kb_item["DriverName"],
    )


def fill_ride_inform_changes_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_INFORM_CHANGES_FAILED]


def fill_ride_inform_changes_successful(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_INFORM_CHANGES_SUCCESSFUL]


def fill_ride_ask_change(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_ASK_CHANGE]


def fill_ride_ask_booking_number(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_ASK_BOOKING_NUMBER]


def fill_ride_provide_booking_status(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["RideWait"]):
        return None
    return intent2reply[constants.INTENT_RIDE_PROVIDE_BOOKING_STATUS].format(
        minutes_till_pickup=int(kb_item["RideWait"])
    )


def fill_ride_provide_booking_status_update(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["RideWait"]):
        return None
    return intent2reply[constants.INTENT_RIDE_PROVIDE_BOOKING_STATUS_UPDATE].format(
        minutes_till_pickup=int(kb_item["RideWait"])
    )


def fill_hotel_inform_search_criteria(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_INFORM_SEARCH_CRITERIA]


def fill_hotel_ask_name(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_NAME]


def fill_hotel_inform_name(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_INFORM_NAME].format(
        hotel_name=kb_item["Name"]
    )


def fill_hotel_ask_location(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_LOCATION]


def fill_hotel_inform_location(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Location"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_INFORM_LOCATION].format(
        hotel_location=kb_item["Location"]
    )


def fill_hotel_ask_price(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_PRICE]


def fill_hotel_inform_price(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name", "Cost"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_INFORM_PRICE].format(
        price_range=kb_item["Cost"], hotel_name=kb_item["Name"]
    )


def fill_hotel_ask_rating(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_RATING]


def fill_hotel_inform_rating(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name", "AverageRating"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_INFORM_RATING].format(
        hotel_name=kb_item["Name"], average_rating=kb_item["AverageRating"]
    )


def fill_hotel_provide_search_result(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name", "Location", "Cost", "AverageRating"]):
        return None

    return intent2reply[constants.INTENT_HOTEL_PROVIDE_SEARCH_RESULT].format(
        hotel_name=kb_item["Name"], hotel_location=kb_item["Location"], price_range=kb_item["Cost"],
        average_rating=kb_item["AverageRating"]
    )


def fill_hotel_ask_search_more(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_SEARCH_MORE]


def fill_hotel_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_BYE]


def fill_hotel_ask_hotel(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_HOTEL]


def fill_hotel_ask_date_from(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_DATE_FROM]


def fill_hotel_ask_date_to(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_DATE_TO]


def fill_hotel_ask_customer_request(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_ASK_CUSTOMER_REQUEST].format(hotel_name=kb_item['Name'])


def fill_hotel_unavailable(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_UNAVAILABLE].format(hotel_name=kb_item['Name'])


def fill_hotel_ask_confirm_booking(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["Name"]):
        return None
    return intent2reply[constants.INTENT_HOTEL_ASK_CONFIRM_BOOKING].format(hotel_name=kb_item['Name'])


def fill_hotel_reservation_succeeded(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_RESERVATION_SUCCEEDED]


def fill_hotel_reservation_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_RESERVATION_FAILED]


def fill_hotel_ask_room_number(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_ROOM_NUMBER]


def fill_hotel_ask_service_request(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_SERVICE_REQUEST]


def fill_hotel_ask_time(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_ASK_TIME]


def fill_hotel_inform_service_request_successful(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['RoomNumber', 'Time']):
        return None

    return intent2reply[constants.INTENT_HOTEL_INFORM_SERVICE_REQUEST_SUCCESSFUL].format(
        room_number=kb_item['RoomNumber'], time=kb_item['Time']
    )


def fill_hotel_inform_service_request_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_HOTEL_INFORM_SERVICE_REQUEST_FAILED]


def fill_plane_ask_flight_id(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_ASK_FLIGHT_ID]


def fill_plane_flight_available(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_FLIGHT_AVAILABLE]


def fill_plane_flight_unavailable(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['id']):
        return None
    return intent2reply[constants.INTENT_PLANE_FLIGHT_UNAVAILABLE].format(flight_id=kb_item['id'])


def fill_plane_reservation_succeeded(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_RESERVATION_SUCCEEDED]


def fill_plane_reservation_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_RESERVATION_FAILED]


def fill_plane_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_BYE]


def fill_plane_ask_departure_city(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_ASK_DEPARTURE_CITY]


def fill_plane_ask_arrival_city(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_ASK_ARRIVAL_CITY]


def fill_plane_ask_date(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_ASK_DATE]


def fill_plane_request_optional(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_REQUEST_OPTIONAL]


def fill_plane_inform_flight_details(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Price', 'Class', 'Airline', 'Duration', 'ArrivalCity']):
        return None

    if kb_item['Class'].lower() == 'economy':
        classy = f'an {kb_item["Class"]}'
    else:
        classy = f'a {kb_item["Class"]}'

    return intent2reply[constants.INTENT_PLANE_INFORM_FLIGHT_DETAILS].format(clazz=classy,
                                                                             airline=kb_item['Airline'],
                                                                             price=kb_item['Price'],
                                                                             duration=kb_item['Duration'],
                                                                             arrival_city=kb_item['ArrivalCity'])


def fill_plane_ask_more_questions(intent2reply, *_):
    return intent2reply[constants.INTENT_PLANE_ASK_MORE_QUESTIONS]


def fill_party_ask_venue(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_VENUE]


def fill_party_ask_number_of_guests(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_NUMBER_OF_GUESTS]


def fill_party_ask_starting_time(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_STARTING_TIME]


def fill_party_ask_end_time(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_END_TIME]


def fill_party_ask_day(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_DAY]


def fill_party_ask_food(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_FOOD]


def fill_party_ask_drinks(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_DRINKS]


def fill_party_venue_not_available(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name']):
        return None
    return intent2reply[constants.INTENT_PARTY_VENUE_NOT_AVAILABLE].format(venue_name=kb_item['Name'])


def fill_party_ask_confirm_booking(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name', 'Day']):
        return None
    return intent2reply[constants.INTENT_PARTY_ASK_CONFIRM_BOOKING].format(venue_name=kb_item['Name'],
                                                                           day=kb_item['Day'])


def fill_party_inform_food_drink_criteria(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_INFORM_FOOD_DRINK_CRITERIA]


def fill_party_no_venue_available(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_NO_VENUE_AVAILABLE]


def fill_party_booking_successful(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_BOOKING_SUCCESSFUL]


def fill_party_booking_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_BOOKING_FAILED]


def fill_party_ask_host(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_HOST]


def fill_party_ask_arrival_time(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_ARRIVAL_TIME]


def fill_party_confirm_rsvp(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_CONFIRM_RSVP]


def fill_party_ask_dietary_restrictions(intent2reply, *_):
    return intent2reply[constants.INTENT_PARTY_ASK_DIETARY_RESTRICTIONS]


def fill_restaurant_ask_restaurant(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_RESTAURANT]


def fill_restaurant_ask_time(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_TIME]


def fill_restaurant_ask_size(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_SIZE]


def fill_restaurant_inform_unavailable(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_INFORM_UNAVAILABLE]


def fill_restaurant_ask_confirm_booking(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name']):
        return None
    return intent2reply[constants.INTENT_RESTAURANT_ASK_CONFIRM_BOOKING].format(
        restaurant_name=kb_item['Name']
    )


def fill_restaurant_inform_booking_successful(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name']):
        return None
    return intent2reply[constants.INTENT_RESTAURANT_INFORM_BOOKING_SUCCESSFUL].format(
        restaurant_name=kb_item['Name']
    )


def fill_restaurant_inform_booking_failed(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_INFORM_BOOKING_FAILED]


def fill_restaurant_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_BYE]


def fill_restaurant_ask_location(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_LOCATION]


def fill_restaurant_ask_food_type(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_FOOD_TYPE]


def fill_restaurant_ask_rating(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_RATING]


def fill_restaurant_ask_delivery(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_DELIVERY]


def fill_restaurant_ask_takes_reservations(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_TAKES_RESERVATIONS]


def fill_restaurant_ask_continue_searching(intent2reply, *_):
    return intent2reply[constants.INTENT_RESTAURANT_ASK_CONTINUE_SEARCHING]


def fill_restaurant_inform_search_result(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name', 'Cost', 'Food', 'AverageRating', 'Location']):
        return None
    return intent2reply[constants.INTENT_RESTAURANT_INFORM_SEARCH_RESULTS].format(
        restaurant_name=kb_item['Name'], location=kb_item['Location'], cost=kb_item['Cost'],
        food_type=kb_item['Food'], rating=kb_item['AverageRating']
    )


def fill_apartment_inform_search_criteria(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_INFORM_SEARCH_CRITERIA]


def fill_apartment_ask_num_bedrooms(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_NUM_BEDROOMS]


def fill_apartment_ask_price(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_PRICE]


def fill_apartment_ask_floor(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_FLOOR]


def fill_apartment_ask_balcony(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_BALCONY]


def fill_apartment_ask_elevator(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_ELEVATOR]


def fill_apartment_ask_nearby_pois(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_NEARBY_POIS]


def fill_apartment_ask_search_more(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_SEARCH_MORE]


def fill_apartment_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_BYE]


def fill_apartment_ask_apartment_name(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_APARTMENT_NAME]


def fill_apartment_ask_day(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_DAY]


def fill_apartment_ask_start_time(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_START_TIME]


def fill_apartment_ask_end_time(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_END_TIME]


def fill_apartment_ask_application_fee_paid(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_APPLICATION_FEE_PAID]


def fill_apartment_ask_custom_message(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_ASK_CUSTOM_MESSAGE]


def fill_apartment_inform_viewing_available(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_INFORM_VIEWING_AVAILABLE]


def fill_apartment_inform_viewing_unavailable(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_INFORM_VIEWING_UNAVAILABLE]


def fill_apartment_inform_booking_successful(intent2reply, *_):
    return intent2reply[constants.INTENT_APARTMENT_INFORM_BOOKING_SUCCESSFUL]


def fill_apartment_inform_search_result(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Level', 'HasBalcony', 'BalconySide', 'HasElevator', 'NumRooms',
                                   'FloorSquareMeters', 'NearbyPOIs', 'Name', 'Price']):
        return None

    if len(kb_item['NearbyPOIs']) == 1:
        pois = f'a {kb_item["NearbyPOIs"][0]}'
    elif len(kb_item['NearbyPOIs']) >= 2:
        pois = ', '.join(map(lambda x: f'a {x}', kb_item['NearbyPOIs']))
        pois = ' and '.join(pois.rsplit(', ', 1))
    else:
        pois = 'nothing interesting'

    if kb_item['HasBalcony']:
        has_balcony = f'has a {kb_item["BalconySide"]} facing balcony'
    else:
        has_balcony = 'does not have a balcony'

    if kb_item['HasElevator']:
        has_elevator = 'has an elevator'
    else:
        has_elevator = 'does not have an elevator'

    return intent2reply[constants.INTENT_APARTMENT_INFORM_SEARCH_RESULT].format(
        apartment_name=kb_item['Name'], pois=pois, floor=kb_item['Level'],
        size=kb_item['FloorSquareMeters'], num_bedrooms=kb_item['NumRooms'],
        has_balcony=has_balcony, has_elevator=has_elevator, price=kb_item['Price']
    )


def fill_doctor_ask_doctor_name(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_ASK_DOCTOR_NAME]


def fill_doctor_ask_day(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_ASK_DAY]


def fill_doctor_ask_start_time(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_ASK_START_TIME]


def fill_doctor_ask_end_time(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_ASK_END_TIME]


def fill_doctor_ask_symptoms(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_ASK_SYMPTOMS]


def fill_doctor_inform_booking_unavailable(intent2eply, *_):
    return intent2eply[constants.INTENT_DOCTOR_INFORM_BOOKING_UNAVAILABLE]


def fill_doctor_inform_booking_available(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_INFORM_BOOKING_AVAILABLE]


def fill_doctor_inform_booking_successful(intent2reply, *_):
    return intent2reply[constants.INTENT_DOCTOR_INFORM_BOOKING_SUCCESSFUL]


def fill_doctor_inform_doctors_instructions(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Message']):
        return None

    return intent2reply[constants.INTENT_DOCTOR_INFORM_DOCTORS_INSTRUCTIONS].format(
        instructions=kb_item['Message']
    )


def fill_spaceship_ask_rank(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_RANK]


def fill_spaceship_ask_code(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_CODE]


def fill_spaceship_ask_code_type(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_CODE_TYPE]


def fill_spaceship_inform_outcome(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Message']):
        return None

    return intent2reply[constants.INTENT_SPACESHIP_INFORM_OUTCOME].format(
        message=kb_item['Message']
    )


def fill_spaceship_ask_lock_manufacturer(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_LOCK_MANUFACTURER]


def fill_spaceship_ask_colour_top_cable(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_COLOUR_TOP_CABLE]


def fill_spaceship_ask_colour_second_cable(intent2reply, *_):
    return intent2reply[constants.INTENT_SPACESHIP_ASK_COLOUR_SECOND_CABLE]


def fill_weather_ask_day(intent2reply, *_):
    return intent2reply[constants.INTENT_WEATHER_ASK_DAY]


def fill_weather_ask_location(intent2reply, *_):
    return intent2reply[constants.INTENT_WEATHER_ASK_LOCATION]


def fill_weather_inform_forecast(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Weather', 'Day', 'TemperatureCelsius', 'City']):
        return None

    return intent2reply[constants.INTENT_WEATHER_INFORM_FORECAST].format(
        weather=kb_item['Weather'], day=kb_item['Day'], city=kb_item['City'],
        temperature=kb_item['TemperatureCelsius']
    )


def fill_trivia_ask_question_number(intent2reply, *_):
    return intent2reply[constants.INTENT_TRIVIA_ASK_QUESTION_NUMBER]


def fill_trivia_ask_question(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Question']):
        return None

    return intent2reply[constants.INTENT_TRIVIA_ASK_QUESTION].format(
        question=kb_item['Question']
    )


def fill_trivia_inform_answer_ask_next(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['CorrectAnswer', 'UserAnswer']):
        return None

    if kb_item['CorrectAnswer'].lower() == kb_item['UserAnswer'].lower():
        answer_correct = 'correct! Good job!!'
    else:
        answer_correct = f'unfortunately wrong :(. The correct answer would have been "{kb_item["CorrectAnswer"]}".'

    return intent2reply[constants.INTENT_TRIVIA_INFORM_ANSWER_ASK_NEXT].format(
        answer_correct=answer_correct
    )


def fill_trivia_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_TRIVIA_BYE]


def fill_meeting_ask_guest_name(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_ASK_GUEST_NAME]


def fill_meeting_ask_day(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_ASK_DAY]


def fill_meeting_ask_start_time(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_ASK_START_TIME]


def fill_meeting_ask_end_time(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_ASK_END_TIME]


def fill_meeting_ask_reason(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_ASK_REASON]


def fill_meeting_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_MEETING_BYE]


def fill_meeting_inform_confirmed(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name', 'Day', 'StartTimeHour', 'EndTimeHour']):
        return None

    return intent2reply[constants.INTENT_MEETING_INFORM_CONFIRMED].format(
        guest_name=kb_item['Name'], day=kb_item['Day'], start_time=kb_item['StartTimeHour'],
        end_time=kb_item['EndTimeHour']
    )


def fill_meeting_inform_unavailable_ask_different_time(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['Name', 'Day', 'StartTimeHour']):
        return None

    return intent2reply[constants.INTENT_MEETING_INFORM_UNAVAILABLE_ASK_DIFFERENT_TIME].format(
        guest_name=kb_item['Name'], day=kb_item['Day'], start_time=kb_item['StartTimeHour']
    )


def fill_bank_ask_account_number(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_ACCOUNT_NUMBER]


def fill_bank_ask_pin(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_PIN]


def fill_bank_ask_dob(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_DOB]


def fill_bank_ask_mothers_maiden_name(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_MOTHERS_MAIDEN_NAME]


def fill_bank_ask_childhood_pets_name(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_CHILDHOOD_PETS_NAME]


def fill_bank_inform_cannot_authenticate(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_INFORM_CANNOT_AUTHENTICATE]


def fill_bank_ask_fraud_details(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_ASK_FRAUD_DETAILS]


def fill_bank_inform_fraud_report_submitted(intent2reply, *_):
    return intent2reply[constants.INTENT_BANK_INFORM_FRAUD_REPORT_SUBMITTED]


def fill_bank_inform_balance(intent2reply, kb_item):
    if not check_kb_item(kb_item, ['BankBalance']):
        return None

    return intent2reply[constants.INTENT_BANK_INFORM_BALANCE].format(
        balance=kb_item['BankBalance']
    )


def check_kb_item(
    kb_item: Dict[Text, Any], required_fields: Optional[List[Text]] = None
) -> bool:
    if not required_fields:
        return kb_item is not None
    else:
        return kb_item and all(key in kb_item for key in required_fields)
