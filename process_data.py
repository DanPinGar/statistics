from typing import Dict, Iterable, List, Optional, Tuple

import pandas as pd



def clean_excel(data_file_path:str=None, **kwargs) -> pd.DataFrame:

    default = {
        'drop_columns': [],
        'to_datetime_columns': [],
    }

    args = {**default, **kwargs}
    df = pd.read_excel(data_file_path, decimal=',')

    for columna in args['to_datetime_columns']:
        df[columna] = pd.to_datetime(df[columna], errors='coerce')

    return df.drop(args['drop_columns'], axis=1)


def _get_fecha_prev_max(row):
    return max(
        (f for f in [row['fecha_prev1'], row['fecha_prev2'], row['fecha_prev3']] if pd.notna(f)),
        default=pd.NaT
    )


def _get_fecha_temprana(lista_fechas, lista_eventos):
    fecha_min = min(f for f in lista_fechas if pd.notna(f))
    return fecha_min, lista_eventos[lista_fechas.index(fecha_min)]


# ---------------------------------------------------------------------
# pr_1
# ---------------------------------------------------------------------


def pr_1(event_map, df:pd.DataFrame) -> Tuple[pd.DataFrame,pd.DataFrame]:

    df_data = pd.DataFrame(columns=['id', 'days', 'event', 'diameter','diam_AI'])

    df_analysis = df[df['Valido'] == True].copy()

    df_analysis['cirugia'] = df_analysis['fecha_cirugia'].notna()
    df_analysis['embolia'] = df_analysis['fecha_trat1'].notna()
    df_analysis['muerte'] = df_analysis['fecha_muerte'].notna()
    df_analysis['previa'] = df_analysis['fecha_prev1'].notna()

    df_analysis = df_analysis.drop(['Valido', 'PatientID'], axis=1)

    for _, row in df_analysis.iterrows():

        lista_fechas = [row['fecha_cirugia'], row['fecha_alta'], row['fecha_muerte']]
        lista_eventos = ['surg', 'alta', 'muer']

        if pd.notna(row['fecha_trat1']) and row['fecha_trat1'] >= row['fecha_eco']:
            lista_fechas.insert(0, row['fecha_trat1'])
            lista_eventos.insert(0, 'embo')

        fecha_prev_max = _get_fecha_prev_max(row)
        if pd.notna(fecha_prev_max) and fecha_prev_max > row['fecha_eco']:
            lista_fechas.insert(0, fecha_prev_max)
            lista_eventos.insert(0, 'prev')

        fecha_min, fecha_temprana = _get_fecha_temprana(lista_fechas, lista_eventos)

        fila_data = {
            'id': row['record_id'],
            'diameter': row['Final'],
            'diam_AI': row['IA'],
            'days': (fecha_min - row['fecha_eco']).days,
            'event': event_map.get(fecha_temprana)
        }

        if fila_data['event'] is None:
            print('error:', row['record_id'])

        df_data.loc[len(df_data)] = fila_data

    return df_data, df_analysis


# ---------------------------------------------------------------------
# pr_2
# ---------------------------------------------------------------------


def add_file_data_time(df,evm, fecha_temprana, ident, fecha_eco=None, fecha_init=None,
                       fecha_end=None, diameter=None,diam_AI=None, surgery=None):

    fila_data = {
        'id': ident,
        'diameter': diameter,
        'diam_AI': diam_AI,
        'start': (fecha_init - fecha_eco).days,
        'stop': (fecha_end - fecha_eco).days + 0.5,
        'surgery': surgery
    }

    fila_data['event'] = evm.get(fecha_temprana)

    if fila_data['event'] is None:
        print('error:', ident)

    # print(fecha_temprana, fila_data)
    df.loc[len(df)] = fila_data

    return df


def pr_2(event_map,df_analysis:pd.DataFrame) -> pd.DataFrame:

    df_data_time = pd.DataFrame(
        columns=['id', 'start', 'stop', 'event', 'diameter','diam_AI', 'surgery']
    )

    for _, row in df_analysis.iterrows():

        lista_fechas = [row['fecha_alta'], row['fecha_muerte']]
        lista_eventos = ['alta', 'muer']

        if pd.notna(row['fecha_trat1']) and row['fecha_trat1'] >= row['fecha_eco']:
            lista_fechas.insert(0, row['fecha_trat1'])
            lista_eventos.insert(0, 'embo')

        fecha_prev_max = _get_fecha_prev_max(row)
        if pd.notna(fecha_prev_max) and fecha_prev_max > row['fecha_eco']:
            lista_fechas.insert(0, fecha_prev_max)
            lista_eventos.insert(0, 'prev')

        fecha_min, fecha_temprana = _get_fecha_temprana(lista_fechas, lista_eventos)

        if row['cirugia'] and row['fecha_cirugia'] >= row['fecha_eco'] and row['fecha_cirugia'] < fecha_min:

            df_data_time = add_file_data_time(
                df_data_time,event_map, 'surg', row['record_id'],
                fecha_eco=row['fecha_eco'],
                fecha_init=row['fecha_eco'],
                fecha_end=row['fecha_cirugia'],
                diameter=row['Final'],
                diam_AI=row['IA'],
                surgery=0
            )

            df_data_time = add_file_data_time(
                df_data_time,event_map, fecha_temprana, row['record_id'],
                fecha_eco=row['fecha_eco'],
                fecha_init=row['fecha_cirugia'],
                fecha_end=fecha_min,
                diameter=row['Final'],
                diam_AI=row['IA'],
                surgery=1
            )
        else:
            df_data_time = add_file_data_time(
                df_data_time,event_map, fecha_temprana, row['record_id'],
                fecha_eco=row['fecha_eco'],
                fecha_init=row['fecha_eco'],
                fecha_end=fecha_min,
                diameter=row['Final'],
                diam_AI=row['IA'],
                surgery=0
            )

    return df_data_time


# ---------------------------------------------------------------------
# pr_3
# ---------------------------------------------------------------------


def pr_3(event_map,df_analysis:pd.DataFrame) -> pd.DataFrame:

    df_data = pd.DataFrame(columns=['id', 'days', 'event', 'diameter','diam_AI'])

    for _, row in df_analysis.iterrows():

        lista_fechas = [row['fecha_cirugia'],row['fecha_alta'], row['fecha_muerte']]
        lista_eventos = ['surg', 'alta', 'muer']

        if pd.notna(row['fecha_trat1']) and row['fecha_trat1'] >= row['fecha_eco']:
            lista_fechas.insert(0, row['fecha_trat1'])
            lista_eventos.insert(0, 'embo')

        fecha_prev_max = _get_fecha_prev_max(row)
        if pd.notna(fecha_prev_max) and fecha_prev_max > row['fecha_eco']:
            lista_fechas.insert(0, fecha_prev_max)
            lista_eventos.insert(0, 'prev')

        fecha_min, fecha_temprana = _get_fecha_temprana(lista_fechas, lista_eventos)

        fila_data = {
            'id': row['record_id'],
            'diameter': row['Final'],
            'diam_AI': row['IA'],
            'days': (fecha_min - row['fecha_eco']).days,
            'event': event_map.get(fecha_temprana),
        }

        if fila_data['event'] is None:
            print('error:', row['record_id'])

        df_data.loc[len(df_data)] = fila_data

    return df_data[['days', 'event', 'diameter', 'diam_AI']]
