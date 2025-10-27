NIMC_DB = [
    {
        "nin": "12345678901",
        "full name": "Fatima Adeleke",
        "date of birth": "2000-04-12",
        "home address": "12 Adeola Street, Surulere, Lagos",
        "phone number": "+2348012345678",
        "email address": "fatima.adeleke@example.com",
        "national identification number": "12345678901",
        "bvn number": "2244668899",
        "passport number": "A00987654",
        "gender": "Female",
        "marital status": "Single",
        "country": "Nigeria"
    },
    {
        "nin": "98765432109",
        "full name": "Chidi Okafor",
        "date of birth": "1995-09-23",
        "home address": "45 Ogui Road, Enugu",
        "phone number": "+2348098765432",
        "email address": "chidi.okafor@example.com",
        "national identification number": "98765432109",
        "bvn number": "1122334455",
        "passport number": "B00654321",
        "gender": "Male",
        "marital status": "Married",
        "country": "Nigeria"
    },
    {
        "nin": "11122233344",
        "full name": "Zainab Musa",
        "date of birth": "2003-01-10",
        "home address": "8 Aliyu Close, Kaduna",
        "phone number": "+2348055555555",
        "email address": "zainab.musa@example.com",
        "national identification number": "11122233344",
        "bvn number": "5566778899",
        "passport number": "C00321456",
        "gender": "Female",
        "marital status": "Single",
        "country": "Nigeria"
    }
]


def get_nimc_record(nin: str):
    """
    Simulates fetching a verified NIMC identity record using a NIN.
    Returns a subset of relevant fields matching privacy keywords.
    """
    for record in NIMC_DB:
        if record["nin"] == nin:
            # Extract a clean subset of the most essential info
            return {
                "full name": record.get("full name"),
                "date of birth": record.get("date of birth"),
                "country": record.get("country"),
                "gender": record.get("gender"),
                "national identification number": record.get("national identification number")
            }
    return None


# Optional standalone test
if __name__ == "__main__":
    test_nin = "12345678901"
    data = get_nimc_record(test_nin)
    if data:
        print(f"NIMC record for {test_nin}:\n", data)
    else:
        print(f"NIN {test_nin} not found in NIMC records.")
