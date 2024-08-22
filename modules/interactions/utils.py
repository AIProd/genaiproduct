import pandas as pd

from modules.interactions.constants import COMMON_GROUP_COLUMNS

def _create_time_series(df):
    all_groups = df.groupby(COMMON_GROUP_COLUMNS)
    all_time_series = []

    for name, group in all_groups:
        resampled_group = _resample_and_add_metadata(group, name)
        all_time_series.append(resampled_group)

    df = pd.concat(all_time_series).reset_index(drop=True)
    df = df.drop_duplicates(subset=COMMON_GROUP_COLUMNS + ['cases_date'])
    return df


def _resample_and_add_metadata(group, name):
    resampled = group.set_index('cases_date').resample('MS').sum().reset_index()
    resampled['employee_uuid'] = name[0]
    resampled['account_uuid'] = name[1]
    resampled['hcp_uuid'] = name[2]
    resampled['product_name'] = name[3]
    resampled['territory'] = name[4]
    resampled['channel'] = name[5]
    resampled['category'] = name[6]
    resampled['source'] = name[7]
    return resampled
