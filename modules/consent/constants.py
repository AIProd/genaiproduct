# Constants
import pandas as pd

COMMON_GROUP_COLUMNS = [
    'employee_uuid',
    'account_uuid',
    'hcp_uuid',
    'territory'
]
METRIC_TYPE_STATISTICS = 'statistics'
INDICATOR_CONSENT = 'consent'
PERIOD_DATE = 'date'
CONSENT_TYPES = {
    'Consent Approved Email Opt-In': 'approved email',
    'Consent Approved Email Opt-Out': 'approved email',
    'Consent Marketing Email Opt-In': 'marketing email',
    'Consent Marketing Email Opt-Out': 'marketing email',
    'Consent Phone Opt-In': 'phone',
    'Consent Phone Opt-Out': 'phone',
    'Consent Postal Opt-In': 'postal',
    'Consent Postal Opt-Out': 'postal'
}
CONSENT_STATUS = {
    'Consent Approved Email Opt-In': 'opt-in',
    'Consent Approved Email Opt-Out': 'opt-out',
    'Consent Marketing Email Opt-In': 'opt-in',
    'Consent Marketing Email Opt-Out': 'opt-out',
    'Consent Phone Opt-In': 'opt-in',
    'Consent Phone Opt-Out': 'opt-out',
    'Consent Postal Opt-In': 'opt-in',
    'Consent Postal Opt-Out': 'opt-out'
}
CONSENT_FLAGS = {
    'ae_consent': 'approved email',
    'me_consent': 'marketing email'
}
CONSENT_FLAG_STATUS = {
    0: 'rejected',
    1: 'accepted',
    pd.NA: 'not yet'
}
