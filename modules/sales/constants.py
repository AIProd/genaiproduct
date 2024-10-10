# Constants
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

COLUMN_MAPPING = {
    'account_uuid': 'account_uuid',
    'hcp_uuid': 'hcp_uuid',
    'employee_uuid': 'employee_uuid',
    'brand_name': 'product_name',
    'product_priority': 'product_priority',
    'ter_code': 'territory',
    'sales': 'sales',
    'units': 'units',
    'sales_channel': 'channel',
    'order_source': 'source',
    'order_category': 'category',
    'cases_date': 'timestamp',
}

COLUMN_SALES = 'sales'
COLUMN_SALES_PER_YEAR = 'sales_per_year'
COLUMN_UNITS = 'units'
COLUMN_UNITS_PER_YEAR = 'units_per_year'

COLUMN_LAST_YEAR_SALES = 'sales_last_year'
COLUMN_LAST_YEAR_UNITS = 'units_last_year'

PERCENTAGE_COLUMN_SALES_CHANGE_LAST_YEAR = 'sales_change_last_year'
PERCENTAGE_COLUMN_UNITS_CHANGE_LAST_YEAR = 'units_change_last_year'

MOVING_ANNUAL_TOTAL_COLUMN_SALES = 'sales_moving_annual_total'
MOVING_ANNUAL_TOTAL_COLUMN_UNITS = 'units_moving_annual_total'

MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_SALES = 'sales_moving_annual_total_last_year'
MOVING_ANNUAL_TOTAL_COLUMN_LAST_YEAR_UNITS = 'units_moving_annual_total_last_year'

PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_SALES_CHANGE_LAST_YEAR = 'moving_annual_total_sales_change_last_year'
PERCENTAGE_MOVING_ANNUAL_TOTAL_COLUMN_UNITS_CHANGE_LAST_YEAR = 'moving_annual_total_units_change_last_year'

ROLLING_QUARTER_COLUMN_SALES = 'sales_rolling_quarter'
ROLLING_QUARTER_COLUMN_UNITS = 'units_rolling_quarter'

ROLLING_QUARTER_COLUMN_LAST_YEAR_SALES = 'sales_rolling_quarter_last_year'
ROLLING_QUARTER_COLUMN_LAST_YEAR_UNITS = 'units_rolling_quarter_last_year'

PERCENTAGE_ROLLING_QUARTER_COLUMN_SALES_CHANGE_LAST_YEAR = 'rolling_quarter_sales_change_last_year'
PERCENTAGE_ROLLING_QUARTER_COLUMN_UNITS_CHANGE_LAST_YEAR = 'rolling_quarter_units_change_last_year'


METRIC_TYPE_STATISTICS = 'statistics'
METRIC_TYPE_SALES = 'sales'


METRIC_CURRENCY = 'CHF'
METRIC_UNIT = 'units'
METRIC_PERCENTAGE = '%'

INDICATOR_SALES = 'sales'
INDICATOR_UNITS = 'units'
INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR_SALES = 'rolling_quarter_change_previous_year_sales'
INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_SALES = 'mat_growth_change_previous_year_sales'
INDICATOR_ROLLING_QUARTER_SALES = 'rolling_quarter_sales'
INDICATOR_MOVING_ANNUAL_TOTAL_SALES = 'moving_annual_total_sales'
INDICATOR_ROLLING_QUARTER_CHANGE_PREVIOUS_YEAR_UNITS = 'rolling_quarter_change_previous_year_units'
INDICATOR_MOVING_ANNUAL_TOTAL_CHANGE_PREVIOUS_YEAR_UNITS = 'mat_growth_change_previous_year_units'
INDICATOR_ROLLING_QUARTER_UNITS = 'rolling_quarter_units'
INDICATOR_MOVING_ANNUAL_TOTAL_UNITS = 'moving_annual_total_units'
INDICATOR_SALES_CHANGE_PREVIOUS_YEAR = 'sales_change_previous_year'
INDICATOR_UNITS_CHANGE_PREVIOUS_YEAR = 'units_change_previous_year'


FINDING_TYPE_TRENDS = 'trends'
FINDING_TYPE_MSD_ORDERS_RECOMMENDATIONS = 'msd_orders_recommendations'
FINDING_TYPE_CROSS_SELLING_OPPORTUNITIES = 'cross_selling_opportunities'
FINDING_TYPE_CANTONAL_PROGRAM = 'cantonal_program_recommendation'
FINDING_TYPE_HIGH_PERFORMING_ACCOUNT = 'high_performing_account'
FINDING_TYPE_UNDER_PERFORMING_ACCOUNT = 'under_performing_account'