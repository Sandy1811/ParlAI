DEFAULT_RASA_NLU_SERVER_ADDRESS = "http://localhost:5005/model/parse"
RASA_NLU_SERVER_ADDRESS_TEMPLATE = "http://localhost:{port:s}/model/parse"
RASA_NLU_SERVER_ADDRESS_KEY = 'rasa_nlu_server_address'
INTENT_TO_REPLY_KEY = 'intent2reply'
INTENT_TO_REPLY_FILE_NAME = 'intent2reply.json'
START_NLU_SERVER_SCRIPT_PATH_KEY = 'start_nlu_server_script_path'
START_NLU_SERVER_SCRIPT_FILE_NAME = 'start_nlu_server.sh'
RASA_NLU_SERVER_PROCESS_KEY = 'nlu_server_process'

# Common Intent Names
INTENT_HELLO = 'hello'
INTENT_ASK_NAME = 'ask_name'
INTENT_OUT_OF_SCOPE = 'out_of_scope'

# Intent Names for book_ride, ride_status, ride_change
INTENT_RIDE_ASK_DESTINATION = 'ride_ask_destination'
INTENT_RIDE_ASK_DEPARTURE = 'ride_ask_departure'
INTENT_RIDE_ASK_CONFIRM_BOOKING = 'ride_ask_confirm_booking'
INTENT_RIDE_BYE = 'ride_bye'
INTENT_RIDE_CONFIRM_BOOKING = 'ride_confirm_booking'
INTENT_RIDE_PROVIDE_DRIVER_DETAILS = 'ride_provide_driver_details'
INTENT_RIDE_PROVIDE_RIDE_DETAILS = 'ride_provide_ride_details'
INTENT_RIDE_INFORM_SEARCH_CRITERIA = 'ride_inform_search_criteria'
INTENT_RIDE_ASK_CHANGE = 'ride_ask_change'
INTENT_RIDE_ASK_BOOKING_NUMBER = 'ride_ask_booking_number'
INTENT_RIDE_INFORM_CHANGES_SUCCESSFUL = 'ride_inform_changes_successful'
INTENT_RIDE_INFORM_CHANGES_FAILED = 'ride_inform_changes_failed'
INTENT_RIDE_PROVIDE_BOOKING_STATUS = 'ride_provide_booking_status'
INTENT_RIDE_PROVIDE_BOOKING_STATUS_UPDATE = 'ride_provide_booking_status_update'

# Intent names for hotel_reserve, hotel_search
INTENT_HOTEL_INFORM_SEARCH_CRITERIA = 'hotel_inform_search_criteria'
INTENT_HOTEL_ASK_NAME = 'hotel_ask_name'
INTENT_HOTEL_INFORM_NAME = 'hotel_inform_name'
INTENT_HOTEL_ASK_LOCATION = 'hotel_ask_location'
INTENT_HOTEL_INFORM_LOCATION = 'hotel_inform_location'
INTENT_HOTEL_ASK_PRICE = 'hotel_ask_price'
INTENT_HOTEL_INFORM_PRICE = 'hotel_inform_price'
INTENT_HOTEL_ASK_RATING = 'hotel_ask_rating'
INTENT_HOTEL_INFORM_RATING = 'hotel_inform_rating'
INTENT_HOTEL_PROVIDE_SEARCH_RESULT = 'hotel_provide_search_result'
INTENT_HOTEL_ASK_SEARCH_MORE = 'hotel_ask_search_more'
INTENT_HOTEL_BYE = 'hotel_bye'
INTENT_HOTEL_ASK_HOTEL = 'hotel_ask_hotel'
INTENT_HOTEL_ASK_DATE_FROM = 'hotel_ask_date_from'
INTENT_HOTEL_ASK_DATE_TO = 'hotel_ask_date_to'
INTENT_HOTEL_ASK_CUSTOMER_REQUEST = 'hotel_ask_customer_request'
INTENT_HOTEL_UNAVAILABLE = 'hotel_unavailable'
INTENT_HOTEL_ASK_CONFIRM_BOOKING = 'hotel_ask_confirm_booking'
INTENT_HOTEL_RESERVATION_SUCCEEDED = 'hotel_reservation_succeeded'
INTENT_HOTEL_RESERVATION_FAILED = 'hotel_reservation_failed'

# Intent names for plane_search, plane_reserve
INTENT_PLANE_ASK_FLIGHT_ID = 'plane_ask_flight_id'
INTENT_PLANE_FLIGHT_AVAILABLE = 'plane_flight_available'
INTENT_PLANE_FLIGHT_UNAVAILABLE = 'plane_flight_unavailable'
INTENT_PLANE_RESERVATION_SUCCEEDED = 'plane_reservation_succeeded'
INTENT_PLANE_RESERVATION_FAILED = 'plane_reservation_failed'
INTENT_PLANE_BYE = 'plane_bye'
INTENT_PLANE_ASK_DEPARTURE_CITY = 'plane_ask_departure_city'
INTENT_PLANE_ASK_ARRIVAL_CITY = 'plane_ask_arrival_city'
INTENT_PLANE_ASK_DATE = 'plane_ask_date'
INTENT_PLANE_REQUEST_OPTIONAL = 'plane_request_optional'
INTENT_PLANE_INFORM_FLIGHT_DETAILS = 'plane_inform_flight_details'
INTENT_PLANE_ASK_MORE_QUESTIONS = 'plane_ask_more_questions'

# Intent names for party_plan, party_rsvp
INTENT_PARTY_ASK_VENUE = 'party_ask_venue'
INTENT_PARTY_ASK_NUMBER_OF_GUESTS = 'party_ask_number_of_guests'
INTENT_PARTY_ASK_STARTING_TIME = 'party_ask_starting_time'
INTENT_PARTY_ASK_END_TIME = 'party_ask_end_time'
INTENT_PARTY_ASK_DAY = 'party_ask_day'
INTENT_PARTY_ASK_FOOD = 'party_ask_food'
INTENT_PARTY_ASK_DRINKS = 'party_ask_drinks'
INTENT_PARTY_VENUE_NOT_AVAILABLE = 'party_venue_not_available'
INTENT_PARTY_ASK_CONFIRM_BOOKING = 'party_ask_confirm_booking'
INTENT_PARTY_BOOKING_SUCCESSFUL = 'party_booking_successful'
INTENT_PARTY_BOOKING_FAILED = 'party_booking_failed'
INTENT_PARTY_ASK_HOST = 'party_ask_host'
INTENT_PARTY_ASK_ARRIVAL_TIME = 'party_ask_arrival_time'
INTENT_PARTY_ASK_DIETARY_RESTRICTIONS = 'party_ask_dietary_restrictions'
INTENT_PARTY_CONFIRM_RSVP = 'party_confirm_rsvp'

# Intent names for restaurant_reserve, restaurant_search
INTENT_RESTAURANT_ASK_RESTAURANT = 'restaurant_ask_restaurant'
INTENT_RESTAURANT_ASK_TIME = 'restaurant_ask_time'
INTENT_RESTAURANT_ASK_SIZE = 'restaurant_ask_size'
INTENT_RESTAURANT_INFORM_UNAVAILABLE = 'restaurant_inform_unavailable'
INTENT_RESTAURANT_ASK_CONFIRM_BOOKING = 'restaurant_ask_confirm_booking'
INTENT_RESTAURANT_INFORM_BOOKING_SUCCESSFUL = 'restaurant_inform_booking_successful'
INTENT_RESTAURANT_INFORM_BOOKING_FAILED = 'restaurant_inform_booking_failed'
INTENT_RESTAURANT_BYE = 'restaurant_bye'
INTENT_RESTAURANT_ASK_LOCATION = 'restaurant_ask_location'
INTENT_RESTAURANT_ASK_FOOD_TYPE = 'restaurant_ask_food_type'
INTENT_RESTAURANT_ASK_RATING = 'restaurant_ask_rating'
INTENT_RESTAURANT_ASK_DELIVERY = 'restaurant_ask_delivery'
INTENT_RESTAURANT_ASK_TAKES_RESERVATIONS = 'restaurant_ask_takes_reservations'
INTENT_RESTAURANT_INFORM_SEARCH_RESULTS = 'restaurant_inform_search_results'
INTENT_RESTAURANT_ASK_CONTINUE_SEARCHING = 'restaurant_ask_continue_searching'

SCENARIO_PORT_MAP = {
    'book_ride': '5005',
    'ride_change': '5006',
    'ride_status': '5007',
    'hotel_search': '5008',
    'hotel_reserve': '5009',
    'party_plan': '5010',
    'party_rsvp': '5011',
    'plane_reserve': '5012',
    'plane_search': '5013',
    'restaurant_reserve': '5014',
    'restaurant_search': '5015'
}