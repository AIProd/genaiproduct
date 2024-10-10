# Constants

COMMON_GROUP_COLUMNS = [
    'employee_uuid',
    'account_uuid',
    'hcp_uuid',
    'product_name',
    'territory',
    'channel',
    'type',
    'category',
    'source',
]

COLUMN_TOTAL_ACTIONS = 'total_actions'
COLUMN_TOTAL_OPENS = 'total_opens'
COLUMN_REJECTION = 'rejection'
COLUMN_ACCEPTATION = 'acceptation'
COLUMN_REACTION = 'reaction'

COLUMN_TIMESTAMP = 'timestamp'

COLUMN_LAST_YEAR_TOTAL_ACTIONS = 'total_actions_last_year'

PERCENTAGE_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR = 'total_actions_change_last_year'
PERCENTAGE_COLUMN_REACTION = 'reaction_percentage'
PERCENTAGE_COLUMN_ACCEPTATION = 'acceptation_percentage'
PERCENTAGE_COLUMN_REJECTION = 'rejection_percentage'

MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS = 'total_actions_moving_annual_total'

MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_TOTAL_ACTIONS = 'total_actions_moving_annual_total_last_year'

PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR = 'moving_annual_total_total_actions_change_last_year'

ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS = 'total_actions_rolling_quarter'

ROLLING_QUARTER_COLUMN_LAST_YEAR_TOTAL_ACTIONS = 'total_actions_rolling_quarter_last_year'

PERCENTAGE_ROLLING_QUARTER_COLUMN_TOTAL_ACTIONS_CHANGE_LAST_YEAR = 'rolling_quarter_total_actions_change_last_year'

METRIC_PERCENTAGE = '%'
METRIC_INTERACTIONS = 'interactions'

METRIC_TYPE_INTERACTIONS = 'interactions'

METRIC_ROLQ_CHANGE = 'rolling_quarter_change'
METRIC_MOVING_ANNUAL_TOTAL = 'moving_annual_total'
METRIC_ROLLING_QUARTER = 'rolling_quarter'
METRIC_COUNT = 'count'
METRIC_DATE = 'date'
METRIC_DAYS = 'days'
PERCENTAGE_METRIC = 'percentage'
CURRENCY_METRIC = 'CHF'
UNIT_METRIC = 'units'
DATE_METRIC = 'date'

INDICATOR_TOTAL_ACTIONS = 'total_actions'
INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR = 'rolling_quarter_change_previous_year'
INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR = 'mat_growth_change_previous_year'
INDICATOR_ROLLING_QUARTER = 'rolling_quarter'
INDICATOR_MOVING_ANNUAL_TOTAL = 'moving_annual_total'
INDICATOR_TOTAL_ACTIONS_CHANGE_PREVIOUS_YEAR = 'total_actions_change_previous_year'
INDICATOR_NEXT_CALL = 'next_call_date'
INDICATOR_CALL = 'call_date'
INDICATOR_MARKETING_EMAIL = 'marketing_email'
INDICATOR_HIGH_PRIORITY_ACCOUNT_DAYS_WITHOUT_INTERACTION = 'high_priority_account_days_without_interaction'
INDICATOR_REACTION_PERCENTAGE = 'reaction_percentage'
INDICATOR_REJECTION_PERCENTAGE = 'rejection_percentage'
INDICATOR_ACCEPTATION_PERCENTAGE = 'acceptation_percentage'


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
    'int_channel': 'channel',
    'int_type': 'type',
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
    'ter_target': 'ter_target',
}

EMAIL_CHANNELS = ['AE - Veeva', 'SFMC Marketing Email']

PERCENTAGE_METRICS = ['rejection', 'acceptation', 'reaction']

FINDING_TYPE_HIGH_PRIORITY_ENGAGEMENT = "high_priority_engagement"
FINDING_TYPE_EMAIL_FINDINGS = 'email_summary'

INTERACTION_CHANNEL_CALL = 'CALLS - Veeva'
INTERACTION_TYPE_IN_PERSON = 'In Person'

HIGH_PRIORITY_TERRITORY_TARGETS = ['A', 'B']