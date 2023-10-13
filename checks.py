import pandas as pd
import datetime


def date_check_(df: pd.DataFrame, n_time: int, type_time: str, date_col: str):
    """"
    Функция принимает на вход датафрейм, количество периодов времени, тип периода,
    название столбца с датами.
    Функция возвращает дату, которая была n периодов назад от даты последнего наблюдения
    """
    date_now = df.loc[df.shape[0] - 1, f'{date_col}']

    if type_time == 'год':
        try:
            date_check = date_now.replace(year=date_now.year - n_time)
        except ValueError:
            date_check = date_now.replace(month=2,
                                          day=28,
                                          year=date_now.year - n_time)

    elif type_time == 'день':
        date_check = date_now - datetime.timedelta(days=n_time)

    elif type_time == 'месяц':
        if n_time // 12 == 0:
            if date_now.month > n_time:
                try:
                    date_check = date_now.replace(month=date_now.month - n_time)
                except ValueError:
                    date_check = date_now.replace(month=date_now.month - n_time + 1,
                                                  day=1) - datetime.timedelta(days=1)
            else:
                n_time -= date_now.month
                try:
                    date_check = date_now.replace(month=12 - n_time,
                                                  year=date_now.year - 1)
                except ValueError:
                    date_check = date_now.replace(month=12 - n_time + 1,
                                                  day=1,
                                                  year=date_now.year - 1) - datetime.timedelta(days=1)
        else:
            full_years = n_time // 12
            n_time %= 12
            if date_now.month > n_time:
                try:
                    date_check = date_now.replace(month=date_now.month - n_time,
                                                  year=date_now.year - full_years)
                except ValueError:
                    date_check = date_now.replace(month=date_now.month - n_time + 1,
                                                  day=1,
                                                  year=date_now.year - full_years) - datetime.timedelta(days=1)
            else:
                n_time -= date_now.month
                try:
                    date_check = date_now.replace(month=12 - n_time,
                                                  year=date_now.year - full_years - 1)
                except ValueError:
                    date_check = date_now.replace(month=12 - n_time + 1,
                                                  day=1,
                                                  year=date_now.year - full_years - 1) - datetime.timedelta(days=1)
    return date_check


def check_1(df: pd.DataFrame, n_time: int, type_time: str, date_col: str, target_col: str) -> bool:
    """
    Функция принимает на вход датафрейм, количество периодов времени, тип периода
    название столбца с датами, название столбца с таргетами.
    Функция возвращает булевое значение, является ли таргет с той даты, которая была n периодов
    назад от даты последнего наблюдения, нулевым значением.
    True - ненулевое значение
    False - нулевое значение
    """

    df.sort_values(by=f'{date_col}', inplace=True)
    date_check = date_check_(df, n_time, type_time, date_col)

    return bool(df.loc[df[f'{date_col}'] == date_check, f'{target_col}'])


def check_2(df: pd.DataFrame, n_time: int, type_time: str, date_col: str, target_col: str) -> tuple:
    """
    Функция принимает на вход датафрейм, количество периодов времени, тип периода
    название столбца с датами, название столбца с таргетами.
    Функция возвращает кортеж (количество нулевых значений таргета за выбранный период,
    всего наблюдений за выбранный период).
    """
    df.sort_values(by=f'{date_col}', inplace=True)
    date_check = date_check_(df, n_time, type_time, date_col)
    df_null_check = df.loc[df[f'{date_col}'] >= date_check, f'{target_col}']
    return pd.isna(df_null_check).sum(), df_null_check.shape[0]


def check_3(df: pd.DataFrame, n_time: int, type_time: str, date_col: str, target_col: str, n_nans: int):
    """
    Функция принимает на вход датафрейм, количество периодов времени, тип периода
    название столбца с датами, название столбца с таргетами, определнное количество ненулевых значений.
    Функция возвращает булевое значение, соответсвуют ли таргеты за выбранный период
    определенному количеству ненулевых значений, и, если не соответствует, кортеж дат с нулевыми значениями.
    True - соответствует (количество нулевых значений меньше или равно заданному числу)
    Если количество нулевых значений больше заданного числа (количество дат с нулевыми таргетами,
    список дат с нулевыми таргетами)
    """
    df.sort_values(by=f'{date_col}', inplace=True)
    date_check = date_check_(df, n_time, type_time, date_col)
    df_null_check = df.loc[df[f'{date_col}'] >= date_check]
    if pd.isna(df_null_check[f'{target_col}']).sum() <= n_nans:
        return True
    res_ = df_null_check.loc[df_null_check[f'{target_col}'].isna() == True, f'{date_col}'].tolist()
    return pd.isna(df_null_check[f'{target_col}']).sum(), res_


def check_4(df: pd.DataFrame, n_time: int, type_time: str, date_col: str, target_col: str) -> int:
    """
    Функция принимает на вход датафрейм, количество периодов времени, тип периода
    название столбца с датами, название столбца с таргетами.
    Функция возвращает булевое значение, находится ли в выбранном периоде более 1 наблюдения с ненулевым таргетом
    """
    return check_2(
                    df, n_time, type_time, date_col, target_col
                  )[1] - check_2(df, n_time, type_time, date_col, target_col)[0] >= 2
