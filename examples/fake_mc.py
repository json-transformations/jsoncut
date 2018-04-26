from faker import Faker
import uuid
import datetime as dt
from random import random, randint

def fake_mc_contacts_dict(dict_name: str, list_len: int) -> dict:
    """
    Given a range of list_len, this function returns a dict of list_len
    number of contacts imitating the JSON contacts list data returned 
    by the MailChimp API. This is purely for testing JSON manipulation.
    
    APIs change and this imitation structure may no longer be accurate.
    """
    fake = Faker()
    date_diff = dt.timedelta(days=365)
    bogus = []
    for item in range(list_len):
        blist_id, e_id = str(uuid.uuid4()).replace("-","")[:10], str(uuid.uuid4()).replace("-","")[:10]
        b_id = str(uuid.uuid4()).replace("-","")
        b_email = fake.email()
        date_obj = fake.date_time_this_year()
        date_changed = date_obj.astimezone().isoformat()
        date_opt = (date_obj - date_diff).astimezone().isoformat()
        l_name = fake.last_name()
        f_name = fake.first_name()
        rating = randint(0,5)
        open_rate = float("{:.4f}".format(random()))
        if open_rate > 0:
            click_rate = float("{:.4f}".format(random()))
        else:
            click_rate = 0.0000

        row = {'_links': [{'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}',
                           'method': 'GET',
                           'rel': 'self',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Response.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members',
                           'method': 'GET',
                           'rel': 'parent',
                           'schema': 'https://us13.api.mailchimp.com/schema/3.0/CollectionLinks/Lists/Members.json',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/CollectionResponse.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}',
                           'method': 'PATCH',
                           'rel': 'update',
                           'schema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/PATCH.json',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Response.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}',
                           'method': 'PUT',
                           'rel': 'upsert',
                           'schema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/PUT.json',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Response.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}',
                           'method': 'DELETE',
                           'rel': 'delete'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}/activity',
                           'method': 'GET',
                           'rel': 'activity',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Activity/Response.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}/goals',
                           'method': 'GET',
                           'rel': 'goals',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Goals/Response.json'},
                          {'href': f'https://us13.api.mailchimp.com/3.0/lists/{blist_id}/members/{b_id}/notes',
                           'method': 'GET',
                           'rel': 'notes',
                           'targetSchema': 'https://us13.api.mailchimp.com/schema/3.0/Definitions/Lists/Members/Notes/CollectionResponse.json'}],
               'email_address': b_email,
               'email_client': 'Apple Mail',
               'email_type': 'html',
               'id': b_id,
               'ip_opt': '',
               'ip_signup': '',
               'language': '',
               'last_changed': date_changed,
               'list_id': blist_id,
               'location': {'country_code': 'US',
                            'dstoff': -4,
                            'gmtoff': -5,
                            'latitude': 40.9406,
                            'longitude': -73.8226,
                            'timezone': 'America/New_York'},
               'member_rating': rating,
               'merge_fields': {'FNAME': f_name, 'LNAME': l_name},
               'stats': {'avg_click_rate': click_rate, 'avg_open_rate': open_rate},
               'status': 'subscribed',
               'timestamp_opt': date_opt,
               'timestamp_signup': '',
               'unique_email_id': e_id,
               'vip': False}

        bogus.append(row)
    return {dict_name: bogus}