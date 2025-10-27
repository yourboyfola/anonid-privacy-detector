# -------------
# Demo / quick test
# -------------
from anonid_core_aes import register_user_from_nin
if __name__ == "__main__":
    # Ask for user input safely
    test_nin = input("Enter NIN to register: ").strip()

    # Fetch and register user
    rec = register_user_from_nin(test_nin)

    # Handle invalid NIN gracefully
    if not rec:
        print(f"\n❌ No record found for NIN {test_nin}. Please check and try again.")
    else:
        # Mask NIN (first 2 + last 2 digits)
        masked_nin = f"{test_nin[:2]}{'*' * (len(test_nin) - 4)}{test_nin[-2:]}"
        minimal_output = {
            "anon_id": rec["anon_id"],
            "masked_nin": masked_nin
        }

        print("\n✅ Registration successful. Minimal public output:")
        print(minimal_output)
