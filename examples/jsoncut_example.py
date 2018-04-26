import fake_mc
from jsoncut.core import cut
from pandas.io.json import json_normalize

# import json

contacts = fake_mc.fake_mc_list('mc_contacts', 100)

contacts_df = json_normalize(contacts['mc_contacts'])

cut()
