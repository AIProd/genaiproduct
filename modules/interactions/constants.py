HCP_COLUMN = 'hcp'
EMPLOYEE_NAME_COLUMN = 'employee_name'
EMPLOYEE_EMAIL_COLUMN = 'emp_email'
CALL_DATETIME_COLUMN = 'call_datetime'
PLANNED_CALL_FLAG_COLUMN = 'planned_call_flag'
PERIOD_DAILY = 'daily'
TIME_FORMAT = '%Y-%m-%d'
COMMON_GROUP_COLUMNS = [
    'employee_uuid',
    'account_uuid',
    'hcp_uuid',
    'product_name',
    'territory',
    'channel',
    'category',
    'source',
]

INDICATOR_SUBJECT = 'subject'

TYPE_INTERACTIONS = 'interactions'
METRIC_ROLQ_CHANGE = 'rolling_quarter_change'
METRIC_MOVING_ANNUAL_TOTAL = 'moving_annual_total'
METRIC_ROLLING_QUARTER = 'rolling_quarter'
METRIC_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR = 'rolling_quarter_change_previous_year'
METRIC_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR = 'mat_growth_change_previous_year'
METRIC_INTERACTIONS_CHANGE_PREVIOUS_YEAR = 'interactions_change_previous_year'
METRIC_COUNT = 'count'
PERCENTAGE_METRIC = 'percentage'
CURRENCY_METRIC = 'CHF'
UNIT_METRIC = 'units'
DATE_METRIC = 'date'

PERIOD_MONTH = 'month'
PERIOD_YEAR = 'year'
PERIOD_DAY = 'day'

METRICS = ['rejection', 'acceptation', 'reaction', 'total_opens', 'total_actions', 'planned_call']

COLUMN_MAPPING = {
            'account_uuid': 'account_uuid',
            'hcp_uuid': 'hcp_uuid',
            'employee_uuid': 'employee_uuid',
            'brand_name': 'product_name',
            'ter_code': 'territory',
            'sales': 'sales',
            'units': 'units',
            'int_channel': 'channel',
            'int_rejection': 'rejection',
            'int_acceptation': 'acceptation',
            'int_reaction': 'reaction',
            'total_opens': 'total_opens',
            'total_actions': 'total_actions',
            'planned_call_flag': 'planned_call',
            'order_source': 'source',
            'order_category': 'category',
            'cases_date': 'timestamp',
            'int_title': 'subject',
        }

EMAIL_CHANNELS = ['AE - Veeva', 'SFMC Marketing Email']

PERCENTAGE_METRICS = ['rejection', 'acceptation', 'reaction']


FINDING_TYPE_EMAIL_FINDINGS = 'email_summary'