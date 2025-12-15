import pandas as pd

def add_file_data_time(df,fecha_temprana,ident,fecha_eco=None,fecha_init=None,fecha_end=None,diameter=None,surgery=None):

    fila_data = {'id': ident, 'diameter': diameter,'start': (fecha_init - fecha_eco).days, 'stop': (fecha_end - fecha_eco).days + 0.5,'surgery': surgery}

    if fecha_temprana   == 'surg':
        fila_data['event'] = 0

    elif fecha_temprana == 'prev':
        fila_data['event'] = 1

    elif fecha_temprana == 'embo':
        fila_data['event'] = 1
        
    elif fecha_temprana == 'muer':
        fila_data['event'] = 0

    elif fecha_temprana == 'alta':
        fila_data['event'] = 0

    else: 
        print('error:',ident)

    print(fecha_temprana,fila_data)
    df.loc[len(df)] = fila_data

    return df


def main(df_analysis):

    df_data_time = pd.DataFrame(columns = ['id', 'start','stop','event','diameter','surgery'])  # 1 = embolia, 2 = muerte

    for index, row in df_analysis.iterrows():
        
        lista_fechas = [ row['fecha_alta'], row['fecha_muerte']]
        lista_eventos = [ 'alta', 'muer']

        if pd.notna(row['fecha_trat1']) and row['fecha_trat1'] >= row['fecha_eco']: # solo tener en cuenta fechas embolias posteriores a la embolia o iguales
            
            lista_fechas.insert(0, row['fecha_trat1']) # importante insertarlo al principio por si las fechas son las mismas, no puede morir antes de una embolia
            lista_eventos.insert(0, 'embo')

        fecha_prev_max = max((f for f in [row['fecha_prev1'], row['fecha_prev2'], row['fecha_prev3']] if pd.notna(f)), default=pd.NaT)
        if pd.notna(fecha_prev_max) and fecha_prev_max > row['fecha_eco']:    # solo tener en cuenta fechas embolias posteriores a la embolia
            
            lista_fechas.insert(0, fecha_prev_max)    # importante insertarlo al principio por si las fechas son las mismas, no puede morir antes de una embolia
            lista_eventos.insert(0, 'prev')

        fecha_min = min(fecha for fecha in lista_fechas if pd.notna(fecha))
        fecha_temprana = lista_eventos[lista_fechas.index(fecha_min)]

        if row['cirugia'] and row['fecha_cirugia'] >= row['fecha_eco'] and row['fecha_cirugia'] < fecha_min:

            df_data_time = add_file_data_time(df_data_time,'surg'        ,row['record_id'],fecha_eco=row['fecha_eco'],fecha_init=row['fecha_eco'],    fecha_end=row['fecha_cirugia'],diameter=row['Final'],surgery=0)
            df_data_time = add_file_data_time(df_data_time,fecha_temprana,row['record_id'],fecha_eco=row['fecha_eco'],fecha_init=row['fecha_cirugia'],fecha_end=fecha_min,           diameter=row['Final'],surgery=1)

        else:
            df_data_time = add_file_data_time(df_data_time,fecha_temprana,row['record_id'],fecha_eco=row['fecha_eco'],fecha_init=row['fecha_eco'],fecha_end=fecha_min,diameter=row['Final'],surgery=0)
            

    return df_data_time


if __name__ == '__main__':

    main()