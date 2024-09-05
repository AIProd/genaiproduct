def get_first_row(df):
    if df.empty:
        return None
    else:
        return df.iloc[0]
    