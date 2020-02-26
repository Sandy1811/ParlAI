from typing import List, Text


class MTurkQualificationManager:
    def __init__(self):
        self.qualifications = []

    def require_locales(self, country_codes: List[Text]) -> None:
        self.qualifications.append(
            {
                "QualificationTypeId": "00000000000000000071",
                "Comparator": "In",
                "LocaleValues": [
                    {"Country": country_code} for country_code in country_codes
                ],
                "RequiredToPreview": True,
            }
        )

    def reject_locales(self, country_codes: List[Text]) -> None:
        self.qualifications.append(
            {
                "QualificationTypeId": "00000000000000000071",
                "Comparator": "NotIn",
                "LocaleValues": [
                    {"Country": country_code} for country_code in country_codes
                ],
                "RequiredToPreview": True,
            }
        )

    def require_min_approved_hits(self, min_approved_hits: int) -> None:
        self.qualifications.append(
            {
                "QualificationTypeId": "00000000000000000040",
                "Comparator": "GreaterThan",
                "IntegerValues": [min_approved_hits],
                "RequiredToPreview": True,
            }
        )

    def require_age(self, adult: bool = True) -> None:
        self.qualifications.append(
            {
                "QualificationTypeId": "00000000000000000060",
                "Comparator": "EqualTo",
                "IntegerValues": [1] if adult else [0],
                "RequiredToPreview": True,
            }
        )
