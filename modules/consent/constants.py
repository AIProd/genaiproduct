COMMON_GROUP_COLUMNS = [
    'employee_uuid',
    'account_uuid',
    'hcp_uuid',
    'territory'
]

METRIC_TYPE_CONSENT = 'consent'

INDICATOR_APPROVED_EMAIL = 'approved_email'
INDICATOR_MARKETING_EMAIL = 'marketing_email'
INDICATOR_PHONE = 'phone'
INDICATOR_POSTAL = 'postal'


PERIOD_DATE = 'date'
CONSENT_TYPES = {
    'Consent Approved Email Opt-In': INDICATOR_APPROVED_EMAIL,
    'Consent Approved Email Opt-Out': INDICATOR_APPROVED_EMAIL,
    'Consent Marketing Email Opt-In': INDICATOR_MARKETING_EMAIL,
    'Consent Marketing Email Opt-Out': INDICATOR_MARKETING_EMAIL,
    'Consent Phone Opt-In': INDICATOR_PHONE,
    'Consent Phone Opt-Out': INDICATOR_PHONE,
    'Consent Postal Opt-In': INDICATOR_POSTAL,
    'Consent Postal Opt-Out': INDICATOR_POSTAL
}

METRIC_OPT_IN = 'opt-in'
METRIC_OPT_OUT = 'opt-out'

CONSENT_STATUS = {
    'Consent Approved Email Opt-In': METRIC_OPT_IN,
    'Consent Approved Email Opt-Out': METRIC_OPT_OUT,
    'Consent Marketing Email Opt-In': METRIC_OPT_IN,
    'Consent Marketing Email Opt-Out': METRIC_OPT_OUT,
    'Consent Phone Opt-In': METRIC_OPT_IN,
    'Consent Phone Opt-Out': METRIC_OPT_OUT,
    'Consent Postal Opt-In': METRIC_OPT_IN,
    'Consent Postal Opt-Out': METRIC_OPT_OUT
}


COLUMN_MAPPING = {
    'account_uuid': 'account_uuid',
    'hcp_uuid': 'hcp_uuid',
    'employee_uuid': 'employee_uuid',
    'ter_code': 'territory',
    'int_title': 'title',
    'cases_date': 'timestamp',
    'cust_ae_consent_flag': 'ae_consent',
    'cust_me_consent_flag': 'me_consent',
}

COLUMN_TIMESTAMP = 'timestamp'

TITLE = 'title'
DATE_OUTPUT_FORMAT = "%Y-%m-%d"
TYPE_CONSENT = "consent"
EMPTY_VALUE = ""

STATUS_REJECTED = "rejected"
STATUS_ACCEPTED = "accepted"
STATUS_NOT_YET = "not yet"
REQUIRED_COLUMNS = [
    'timestamp', 'period', 'employee_uuid', 'hcp_uuid', 'account_uuid',
    'territory', 'type', 'indicator', 'value', 'metrics'
]
