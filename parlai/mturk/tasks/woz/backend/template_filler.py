from typing import Dict, Text, Any, List, Optional

from parlai.mturk.tasks.woz.backend import constants


def fill_hello(intent2reply, *_):
    return intent2reply[constants.INTENT_HELLO]


def fill_ask_name(intent2reply, *_):
    return intent2reply[constants.INTENT_ASK_NAME]


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
    if not check_kb_item(kb_item, ["DriverName", "DurationMinutes", "ServiceProvider"]):
        return None
    return intent2reply[constants.INTENT_RIDE_PROVIDE_BOOKING_STATUS].format(
        driver_name=kb_item["DriverName"], minutes_till_pickup=kb_item["DurationMinutes"],
        service_provider=kb_item["ServiceProvider"]
    )


def fill_ride_provide_booking_status_update(intent2reply, kb_item):
    if not check_kb_item(kb_item, ["DurationMinutes"]):
        return None
    return intent2reply[constants.INTENT_RIDE_PROVIDE_BOOKING_STATUS_UPDATE].format(
        minutes_till_pickup=kb_item["DurationMinutes"]
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
    if not check_kb_item(kb_item, ["Name", "Location", "Cost", "AverageRating", "Service", "TakesReservations",
                                   "ServiceStartHour", "ServiceStopHour"]):
        return None
    has_service = f"offer service (from {kb_item['ServiceStartHour']}am to {kb_item['ServiceStopHour']}pm)" \
        if kb_item["Service"] else "not offer service"
    takes_reservations = "accept reservations" if kb_item["TakesReservations"] else "not accept reservations"

    return intent2reply[constants.INTENT_HOTEL_PROVIDE_SEARCH_RESULT].format(
        hotel_name=kb_item["Name"], hotel_location=kb_item["Location"], price_range=kb_item["Cost"],
        average_rating=kb_item["AverageRating"], has_service=has_service, takes_reservations=takes_reservations
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


def check_kb_item(
    kb_item: Dict[Text, Any], required_fields: Optional[List[Text]] = None
) -> bool:
    if not required_fields:
        return kb_item is not None
    else:
        return kb_item and all(key in kb_item for key in required_fields)
