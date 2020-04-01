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
    return intent2reply[constants.INTENT_RIDE_ASK_CONFIRM_BOOKING].format(departure_location=kb_item['DepartureLocation'],
                                                                          arrival_location=kb_item['ArrivalLocation'])


def fill_ride_bye(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_BYE]


def fill_ride_confirm_booking(intent2reply, kb_item):
    return intent2reply[constants.INTENT_RIDE_CONFIRM_BOOKING].format(service_provider=kb_item['ServiceProvider'])


def fill_ride_inform_search_criteria(intent2reply, *_):
    return intent2reply[constants.INTENT_RIDE_INFORM_SEARCH_CRITERIA]


def fill_ride_provide_driver_details(intent2reply, kb_item):
    return intent2reply[constants.INTENT_RIDE_PROVIDE_DRIVER_DETAILS].format(service_provider=kb_item["ServiceProvider"],
                                                                            driver_name=kb_item['DriverName'],
                                                                            price=kb_item['Price'],
                                                                            minutes_till_pickup=kb_item["MinutesTillPickup"],
                                                                            car_model=kb_item['CarModel'],
                                                                            booking_id=kb_item['id'],
                                                                            license_plate=kb_item["LicensePlate"])
