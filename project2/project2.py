"""
contact_book.py
---------------
A console-based Contact Book application built with Python.
Contacts are stored persistently in a JSON file (contacts.json).

Features:
  - Add a new contact (Name, Phone, Address, Email)
  - View all contacts
  - Search for a contact by name
  - Delete a contact by name
  - Input validation (no numbers in names, digits-only phone numbers)

Author  : Generated for Project 2
Course  : Intro to Programming
"""

import json       # Built-in Python library for reading/writing JSON files
import os         # Built-in library for file/path operations
import re         # Built-in library for regular expressions (pattern matching)

# ------------------------------------------------------------------
# CONSTANT – the name of the file where all contacts will be saved.
# Using a constant means we only have to change it in one place if
# we ever rename the file.
# ------------------------------------------------------------------
CONTACTS_FILE = "contacts.json"


# ==================================================================
#  FILE HELPERS  –  load and save the contacts dictionary
# ==================================================================

def load_contacts():
    """
    Read the contacts JSON file from disk and return its contents
    as a Python dictionary.

    The dictionary uses the contact's name (lowercase) as the key
    and a dict of {phone, address, email} as the value.

    If the file does not exist yet (first run), return an empty dict.
    """
    # os.path.exists() checks whether the file is actually on disk
    if os.path.exists(CONTACTS_FILE):
        # Open the file in read mode ("r") using UTF-8 encoding so
        # accented characters are handled correctly
        with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
            # json.load() parses the JSON text into a Python object
            return json.load(f)
    # No file yet – start with an empty contact list
    return {}


def save_contacts(contacts):
    """
    Write the contacts dictionary to the JSON file on disk.

    Parameters
    ----------
    contacts : dict
        The full contacts dictionary to persist.
    """
    # Open (or create) the file in write mode ("w").
    # indent=4 makes the JSON human-readable with 4-space indentation.
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
        json.dump(contacts, f, indent=4)


# ==================================================================
#  VALIDATION HELPERS  –  check that user input is sensible
# ==================================================================

def is_valid_name(name):
    """
    Return True if `name` contains only letters and spaces.
    Names like "John Smith" are fine; "J0hn" or "123" are rejected.

    re.fullmatch() checks that the ENTIRE string matches the pattern.
    [A-Za-z ]+ means: one or more characters that are a–z, A–Z, or space.
    """
    return bool(re.fullmatch(r"[A-Za-z ]+", name))


def is_valid_phone(phone):
    """
    Return True if `phone` contains only digit characters (0-9).
    Spaces, dashes, and parentheses are intentionally NOT allowed so
    storage stays consistent.  A minimum length of 7 is required.

    re.fullmatch(r"[0-9]+", phone) means: one or more digits, nothing else.
    """
    return bool(re.fullmatch(r"[0-9]{7,15}", phone))


def is_valid_email(email):
    """
    Return True if `email` looks like a real e-mail address.
    We check for the pattern:  something @ something . something
    This is a basic check – it won't catch every edge case but
    it rejects obvious garbage like "notanemail".
    """
    return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", email))


# ==================================================================
#  CORE CRUD OPERATIONS
# ==================================================================

def add_contact(contacts):
    """
    Prompt the user for contact details, validate each field,
    then store the new contact in the contacts dictionary and save
    it to disk.

    Parameters
    ----------
    contacts : dict
        The current contacts dictionary (modified in-place).
    """
    print("\n--- Add New Contact ---")

    # ---- Name -------------------------------------------------------
    name = input("Enter name: ").strip()          # .strip() removes leading/trailing whitespace
    if not is_valid_name(name):
        # Reject the input immediately and return to the menu
        print("ERROR: Name must contain only letters and spaces.")
        return
    # Use the lowercase name as the dictionary key so that lookups
    # are case-insensitive ("Alice" == "alice" when searching)
    key = name.lower()
    if key in contacts:
        print(f"ERROR: A contact named '{name}' already exists.")
        return

    # ---- Phone ------------------------------------------------------
    phone = input("Enter phone number (digits only, 7-15 digits): ").strip()
    if not is_valid_phone(phone):
        print("ERROR: Phone number must contain only digits (7–15 digits).")
        return

    # ---- Address ----------------------------------------------------
    address = input("Enter address: ").strip()
    if not address:
        print("ERROR: Address cannot be empty.")
        return

    # ---- Email ------------------------------------------------------
    email = input("Enter email: ").strip()
    if not is_valid_email(email):
        print("ERROR: Please enter a valid email address (e.g. user@example.com).")
        return

    # ---- Store and save --------------------------------------------
    # Build an inner dictionary for this contact's details
    contacts[key] = {
        "name":    name,       # Keep original casing for display
        "phone":   phone,
        "address": address,
        "email":   email
    }
    save_contacts(contacts)   # Write updated dict to contacts.json
    print(f"Contact '{name}' added successfully!")


def view_contacts(contacts):
    """
    Display every contact stored in the dictionary.
    If no contacts exist, inform the user.

    Parameters
    ----------
    contacts : dict
        The current contacts dictionary.
    """
    print("\n--- All Contacts ---")
    if not contacts:
        print("No contacts found.")
        return

    # Iterate over each entry; the key is the lowercase name,
    # the value is a dict with name/phone/address/email
    for idx, (key, info) in enumerate(contacts.items(), start=1):
        print(f"\n[{idx}] Name:    {info['name']}")
        print(f"     Phone:   {info['phone']}")
        print(f"     Address: {info['address']}")
        print(f"     Email:   {info['email']}")
    print()   # Blank line for readability


def search_contact(contacts):
    """
    Ask the user for a name and look it up in the contacts dictionary.
    The search is case-insensitive because keys are stored in lowercase.

    Parameters
    ----------
    contacts : dict
        The current contacts dictionary.
    """
    print("\n--- Search Contact ---")
    name = input("Enter name to search: ").strip()
    key  = name.lower()    # Convert to lowercase to match our stored keys

    if key in contacts:
        info = contacts[key]
        print(f"\nContact found:")
        print(f"  Name:    {info['name']}")
        print(f"  Phone:   {info['phone']}")
        print(f"  Address: {info['address']}")
        print(f"  Email:   {info['email']}")
    else:
        print(f"No contact found with the name '{name}'.")


def delete_contact(contacts):
    """
    Ask the user for a name, confirm the deletion, then remove the
    contact from the dictionary and save the updated file.

    Parameters
    ----------
    contacts : dict
        The current contacts dictionary (modified in-place).
    """
    print("\n--- Delete Contact ---")
    name = input("Enter name of contact to delete: ").strip()
    key  = name.lower()

    if key not in contacts:
        print(f"No contact found with the name '{name}'.")
        return

    # Ask for confirmation before permanently deleting
    confirm = input(f"Are you sure you want to delete '{contacts[key]['name']}'? (yes/no): ").strip().lower()
    if confirm == "yes":
        del contacts[key]         # Remove the entry from the dictionary
        save_contacts(contacts)   # Persist the change to disk
        print(f"Contact '{name}' deleted successfully.")
    else:
        print("Deletion cancelled.")


# ==================================================================
#  MENU  –  the main loop shown to the user
# ==================================================================

def display_menu():
    """
    Print the main menu options to the console.
    Called at the start of each loop iteration.
    """
    print("=" * 35)
    print("       CONTACT BOOK MENU")
    print("=" * 35)
    print("  1. Add Contact")
    print("  2. View All Contacts")
    print("  3. Search Contact")
    print("  4. Delete Contact")
    print("  5. Exit")
    print("=" * 35)


def main():
    """
    Entry point of the application.

    Loads contacts from disk, then enters an infinite loop that
    displays the menu and dispatches to the appropriate function
    based on the user's choice.  The loop ends when the user
    chooses option 5 (Exit).
    """
    # Load any previously saved contacts when the program starts
    contacts = load_contacts()
    print("Welcome to the Contact Book!")

    while True:          # Keep showing the menu until the user exits
        display_menu()
        choice = input("Enter your choice (1-5): ").strip()

        if choice == "1":
            add_contact(contacts)
        elif choice == "2":
            view_contacts(contacts)
        elif choice == "3":
            search_contact(contacts)
        elif choice == "4":
            delete_contact(contacts)
        elif choice == "5":
            print("Goodbye! Your contacts have been saved.")
            break        # Exit the while loop → program ends
        else:
            # The user typed something other than 1-5
            print("Invalid choice. Please enter a number between 1 and 5.")


# ------------------------------------------------------------------
# This block ensures main() is only called when the script is run
# directly (e.g., "python contact_book.py"), NOT when it is imported
# as a module by another script.
# ------------------------------------------------------------------
if __name__ == "__main__":
    main()