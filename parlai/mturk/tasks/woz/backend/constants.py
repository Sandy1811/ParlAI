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

# Intent names for book_hotel, hotel_search
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