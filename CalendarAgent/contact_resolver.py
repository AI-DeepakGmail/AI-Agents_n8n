# CalendarAgent\contact_resolver.py
import win32com.client
import pythoncom
_cached_contacts = None

def with_com_initialized(func):
    def wrapper(*args, **kwargs):
        import pythoncom
        pythoncom.CoInitialize()
        try:
            return func(*args, **kwargs)
        finally:
            pythoncom.CoUninitialize()
    return wrapper

def get_outlook_contacts():
    pythoncom.CoInitialize()  # Initialize COM for this thread
    global _cached_contacts
    if _cached_contacts is not None:
        return _cached_contacts

    outlook = win32com.client.Dispatch("Outlook.Application")
    namespace = outlook.GetNamespace("MAPI")
    contacts_folder = namespace.GetDefaultFolder(10)  # olFolderContacts

    contacts = {}
    for contact in contacts_folder.Items:
        try:
            name = contact.FullName.strip().lower()
            email = contact.Email1Address.strip()
            #print(name,email)
            if name and email:
                contacts[name] = email
        except Exception:
            continue

    _cached_contacts = contacts
    return contacts

def search_contacts_by_name(query: str):
    query = query.strip().lower()
    contacts = get_outlook_contacts()

    matches = []
    for name, email in contacts.items():
        if query in name:
            matches.append((name.title(), email))
    return matches

def resolve_name_interactive(name: str):
    matches = search_contacts_by_name(name)
    if not matches:
        return name  # fallback

    if len(matches) == 1:
        return matches[0][1]  # single match → return email

    print(f"🔍 Multiple contacts found for '{name}':")
    for i, (n, e) in enumerate(matches, start=1):
        print(f"{i}. {n} <{e}>")

    choice = input("👉 Please choose the correct contact number: ")
    try:
        index = int(choice) - 1
        return matches[index][1]
    except Exception:
        print("⚠️ Invalid choice. Using name as-is.")
        return name
