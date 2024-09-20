import pandas as pd

from modules.sales import constants


def _create_time_series(df):
    all_groups = df.groupby(constants.COMMON_GROUP_COLUMNS)
    all_time_series = []

    for name, group in all_groups:
        resampled_group = _resample_and_add_metadata(group, name)
        all_time_series.append(resampled_group)

    df = pd.concat(all_time_series).reset_index(drop=True)
    df[['sales', 'units']] = df[['sales', 'units']].fillna(0)
    df = df.drop_duplicates(subset=constants.COMMON_GROUP_COLUMNS + ['timestamp'])
    return df


def _resample_and_add_metadata(group, name):
    today = pd.Timestamp.today()
    last_month_end = (today - pd.offsets.MonthBegin(1)) - pd.Timedelta(days=1)

    resampled = group.set_index('timestamp').resample('MS').sum()
    resampled = (
        resampled.reindex(pd.date_range(start=resampled.index.min(), end=last_month_end, freq='MS')).reset_index()
    )
    resampled = resampled.rename(columns={'index': 'timestamp'})

    resampled['employee_uuid'] = name[0]
    resampled['account_uuid'] = name[1]
    resampled['hcp_uuid'] = name[2]
    resampled['product_name'] = name[3]
    resampled['territory'] = name[4]
    resampled['channel'] = name[5]
    resampled['category'] = name[6]
    resampled['source'] = name[7]
    return resampled
