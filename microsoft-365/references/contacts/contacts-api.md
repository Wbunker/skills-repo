# Outlook Contacts API (Microsoft Graph)

Access and manage Outlook contacts via Microsoft Graph.

## Permissions

| Scenario | Delegated | Application |
|----------|-----------|-------------|
| Read contacts | `Contacts.Read` | `Contacts.Read` |
| Read shared contacts | `Contacts.Read.Shared` | — |
| Read + write contacts | `Contacts.ReadWrite` | `Contacts.ReadWrite` |
| Read/write shared | `Contacts.ReadWrite.Shared` | — |

## Base Endpoints

```
GET  /me/contacts                                    # All contacts
GET  /me/contacts/{contact-id}                       # Specific contact
POST /me/contacts                                    # Create contact
GET  /me/contactFolders                              # List contact folders
GET  /me/contactFolders/{folder-id}/contacts         # Contacts in a folder
```

## List Contacts

```python
from msgraph import GraphServiceClient
from msgraph.generated.users.item.contacts.contacts_request_builder import (
    ContactsRequestBuilder,
)
from kiota_abstractions.base_request_configuration import RequestConfiguration

async def list_contacts(graph_client, top=50):
    query_params = ContactsRequestBuilder.ContactsRequestBuilderGetQueryParameters(
        select=["displayName", "emailAddresses", "businessPhones", "mobilePhone",
                "jobTitle", "companyName"],
        top=top,
        order_by=["displayName ASC"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    contacts = await graph_client.me.contacts.get(request_configuration=config)
    return contacts.value
```

## Get a Single Contact

```python
async def get_contact(graph_client, contact_id):
    contact = await graph_client.me.contacts.by_contact_id(contact_id).get()
    return contact
    # contact.display_name
    # contact.email_addresses  — list of EmailAddress objects
    # contact.business_phones  — list of strings
    # contact.mobile_phone
    # contact.job_title
    # contact.company_name
    # contact.department
    # contact.birthday
    # contact.home_address, .business_address
    # contact.notes (personal notes field)
```

## Create a Contact

```python
from msgraph.generated.models.contact import Contact
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.physical_address import PhysicalAddress

async def create_contact(graph_client, display_name, email, phone=None, company=None, job_title=None):
    contact = Contact(
        given_name=display_name.split(" ")[0] if " " in display_name else display_name,
        surname=display_name.split(" ", 1)[1] if " " in display_name else "",
        display_name=display_name,
        email_addresses=[
            EmailAddress(
                address=email,
                name=display_name,
            )
        ],
        business_phones=[phone] if phone else [],
        company_name=company,
        job_title=job_title,
    )
    created = await graph_client.me.contacts.post(contact)
    return created
```

## Update a Contact

```python
from msgraph.generated.models.contact import Contact

async def update_contact(graph_client, contact_id, **kwargs):
    """
    kwargs: any Contact properties to update, e.g.
    job_title="Senior Manager", mobile_phone="+1-555-1234"
    """
    update = Contact(**kwargs)
    await graph_client.me.contacts.by_contact_id(contact_id).patch(update)
```

## Delete a Contact

```python
await graph_client.me.contacts.by_contact_id(contact_id).delete()
```

## Search Contacts

```python
from msgraph.generated.users.item.contacts.contacts_request_builder import (
    ContactsRequestBuilder,
)

async def search_contacts(graph_client, name_query):
    """Search contacts by display name."""
    query_params = ContactsRequestBuilder.ContactsRequestBuilderGetQueryParameters(
        filter=f"startsWith(displayName, '{name_query}')",
        select=["displayName", "emailAddresses", "businessPhones"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    contacts = await graph_client.me.contacts.get(request_configuration=config)
    return contacts.value

async def find_contact_by_email(graph_client, email):
    """Find contact by exact email address."""
    query_params = ContactsRequestBuilder.ContactsRequestBuilderGetQueryParameters(
        filter=f"emailAddresses/any(e:e/address eq '{email}')",
        select=["displayName", "emailAddresses", "id"],
    )
    config = RequestConfiguration(query_parameters=query_params)
    contacts = await graph_client.me.contacts.get(request_configuration=config)
    return contacts.value
```

## Contact Folders

```python
# List all contact folders
folders = await graph_client.me.contact_folders.get()

# Create a new folder
from msgraph.generated.models.contact_folder import ContactFolder

new_folder = await graph_client.me.contact_folders.post(
    ContactFolder(display_name="Work Contacts")
)

# Create contact in a specific folder
contact = Contact(display_name="Alice Smith", ...)
await graph_client.me.contact_folders.by_contact_folder_id(new_folder.id).contacts.post(contact)

# List contacts in a folder
contacts = await graph_client.me.contact_folders.by_contact_folder_id(folder_id).contacts.get()
```

## Full Contact Properties

```python
from msgraph.generated.models.contact import Contact
from msgraph.generated.models.email_address import EmailAddress
from msgraph.generated.models.physical_address import PhysicalAddress
import datetime

contact = Contact(
    # Name
    given_name="Alice",
    surname="Smith",
    middle_name="Marie",
    nick_name="Ali",
    display_name="Alice Smith",
    title="Dr.",        # Honorific prefix
    generation="Jr.",   # Suffix

    # Email addresses (up to 3)
    email_addresses=[
        EmailAddress(address="alice@work.com", name="Alice Work"),
        EmailAddress(address="alice@personal.com", name="Alice Personal"),
    ],

    # Phone numbers
    business_phones=["+1-555-100-2000"],
    home_phones=["+1-555-300-4000"],
    mobile_phone="+1-555-500-6000",

    # Work info
    company_name="Contoso Ltd",
    job_title="Senior Engineer",
    department="Engineering",
    office_location="Building 3, Room 401",
    business_home_page="https://contoso.com",
    profession="Software Engineering",

    # Addresses
    business_address=PhysicalAddress(
        street="123 Main St",
        city="Redmond",
        state="WA",
        country_or_region="United States",
        postal_code="98052",
    ),
    home_address=PhysicalAddress(
        street="456 Oak Ave",
        city="Bellevue",
        state="WA",
        postal_code="98004",
    ),

    # Personal
    birthday=datetime.date(1985, 6, 15),
    spouse_name="Bob Smith",
    personal_notes="Met at TechConf 2023",

    # Categories (Outlook categories)
    categories=["VIP", "Customer"],
)
```

## OData Filter Examples

```
# By company name
$filter=companyName eq 'Contoso'

# By last name starting with
$filter=startsWith(surname, 'Sm')

# Contacts with an email address
$filter=emailAddresses/any(e:e/address ne null)

# Contacts modified since a date
$filter=lastModifiedDateTime ge 2024-01-01T00:00:00Z
```
