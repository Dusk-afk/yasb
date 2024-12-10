DEFAULTS = {
    'label': "{wifi_icon}",
    'label_alt': "{wifi_icon} {wifi_name}",
    'update_interval': 1000,
    'callbacks': {
        'on_left': 'toggle_label',
        'on_middle': 'do_nothing',
        'on_right': 'do_nothing'
    },
    'wifi_icons': [
        "\udb82\udd2e",  # Icon for 0% strength
        "\udb82\udd1f",  # Icon for 1-24% strength
        "\udb82\udd22",  # Icon for 25-49% strength
        "\udb82\udd25",  # Icon for 50-74% strength
        "\udb82\udd28"   # Icon for 75-100% strength
    ],
    'ethernet_icon': "\ueba9"
}

VALIDATION_SCHEMA = {
    'label': {
        'type': 'string',
        'default': DEFAULTS['label']
    },
    'label_alt': {
        'type': 'string',
        'default': DEFAULTS['label_alt']
    },
    'update_interval': {
        'type': 'integer',
        'default': DEFAULTS['update_interval'],
        'min': 0,
        'max': 60000
    },
    'wifi_icons': {
        'type': 'list',
        'default': DEFAULTS['wifi_icons'],
        "schema": {
            'type': 'string',
            'required': False
        }
    },
    'ethernet_icon': {
        'type': 'string',
        'default': DEFAULTS['ethernet_icon']
    },
    'callbacks': {
        'type': 'dict',
        'schema': {
            'on_left': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_left'],
            },
            'on_middle': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_middle'],
            },
            'on_right': {
                'type': 'string',
                'default': DEFAULTS['callbacks']['on_right'],
            }
        },
        'default': DEFAULTS['callbacks']
    }
}
