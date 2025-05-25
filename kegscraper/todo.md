## misc

- [ ] maybe add support for https://logon.kegs.org.uk/adfs/portal/updatepassword/
- [ ] Requests wrapper?

## Library

- [ ] News: https://kegs.oliverasp.co.uk/library/home/api/news

# vle

## https://vle.kegs.org.uk/tag/user.php

`GET`

Remove interest of a tag

query string parameters:

```py
params = {
    "action": "removeinterest",
    "sesskey": "<sesskey>",
    "tag": "<tag name>"
}
```

---
`GET`

Add interest of a tag

query string parameters:

```py
params = {
    "action": "addinterest",
    "sesskey": "<sesskey>",
    "tag": "<tag name>"
}
```

---
`GET`

Flag tag as inappropriate

```py
params = {
    "action": "flaginappropriate",
    "sesskey": "<sesskey>",
    "id": "<tag id>"
}
```

## https://vle.kegs.org.uk/tag/search.php

`GET`

HTML contains 150 most popular tags

---
`GET`

query params:

```py
params = {
    "query": "<search param>",
    "go": "Search"  # This doesn't seem to be a required param
}
```

will return some html

## https://vle.kegs.org.uk/lib/ajax/service.php?sesskey=H1tDtZ5sK2&info=core_calendar_submit_create_update_form

`POST`

Create a calander event
e
params:
```py
params = {
    "sesskey": ...,
    "info": "core_calendar_submit_create_update_form"
}
json = [
    {
        "index": 0, 
     "methodname": "core_calendar_submit_create_update_form",
        "args": {
            "formdata": """id=0
                        &userid=4053
                        &modulename=
                        &instance=0
                        &visible=1
                        &eventtype=user
                        &sesskey=H1tDtZ5sK2
                        &_qf__core_calendar_local_event_forms_create=1
                        &mform_showmore_id_general=1
                        &name=%3Cevent%20title%3E
                        &timestart%5Bday%5D=1
                        &timestart%5Bmonth%5D=1
                        &timestart%5Byear%5D=2025
                        &timestart%5Bhour%5D=9
                        &timestart%5Bminute%5D=47
                        &description%5Btext%5D=%3Ch1%3E%26lt%3Bevent%20description%26gt%3B%3C%2Fh1%3E%0D%0A%3Cp%3E%3Cem%3E%26lt%3Bsample%20text%26gt%3B%3C%2Fem%3E%3C%2Fp%3E
                        &description%5Bformat%5D=1
                        &description%5Bitemid%5D=188911336
                        &location=%3CLocation%3E
                        &duration=0"""
        }
    }
]

```