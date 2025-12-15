
import pandas as pd

def main(data_file_path = None,**kwargs):

    print('processing data ...')

    default = {
        'drop_columns' : [],
        'to_datetime_columns':[],
    }

    args = {**default,**kwargs}

    df = pd.read_excel(data_file_path, decimal = ',')

    for columna in args['to_datetime_columns']:
        df[columna] = pd.to_datetime(df[columna], errors = 'coerce')

    df = df.drop(args['drop_columns'],axis=1)

    df_data = pd.DataFrame(columns = ['id', 'days','event','diameter']) 

    # ====================== PARTICULAR DATA PROCESSING FOR THE STUDY ====================== 


    df_analysis = df[df['Valido'] == True].copy()
    # print(df.columns.to_list())

    df_analysis['cirugia'] = df_analysis['fecha_cirugia'].notna()
    df_analysis['embolia'] = df_analysis['fecha_trat1'].notna()
    df_analysis['muerte'] = df_analysis['fecha_muerte'].notna()
    df_analysis['previa'] = df_analysis['fecha_prev1'].notna()

    df_analysis = df_analysis.drop(['Valido','result','PatientID','fecha_trat2'], axis=1)

    for index, row in df_analysis.iterrows():
    
        lista_fechas = [ row['fecha_cirugia'], row['fecha_alta'], row['fecha_muerte']]
        lista_eventos = [ 'ciru', 'alta', 'muer']

        if pd.notna(row['fecha_trat1']) and row['fecha_trat1'] >= row['fecha_eco']: # solo tener en cuenta fechas embolias posteriores a la embolia o iguales
            
            lista_fechas.insert(0, row['fecha_trat1']) # importante insertarlo al principio por si las fechas son las mismas, no puede morir antes de una embolia
            lista_eventos.insert(0, 'embo')

        fecha_prev_max = max((f for f in [row['fecha_prev1'], row['fecha_prev2'], row['fecha_prev3']] if pd.notna(f)), default=pd.NaT)
        if pd.notna(fecha_prev_max) and fecha_prev_max > row['fecha_eco']: # solo tener en cuenta fechas embolias posteriores a la embolia
            
            lista_fechas.insert(0, fecha_prev_max) # importante insertarlo al principio por si las fechas son las mismas, no puede morir antes de una embolia
            lista_eventos.insert(0, 'prev')

        fecha_min = min(fecha for fecha in lista_fechas if pd.notna(fecha))
        fecha_temprana = lista_eventos[lista_fechas.index(fecha_min)]

        fila_data = {'id': row['record_id'],'diameter': row['Final'],'days': (fecha_min - row['fecha_eco']).days}

        if fecha_temprana == 'prev':
            fila_data['event'] = 1

        elif fecha_temprana == 'embo': 
            fila_data['event'] = 1
            
        elif fecha_temprana == 'ciru':
            fila_data['event'] = 0

        elif fecha_temprana == 'muer': 
            fila_data['event'] = 0

        elif fecha_temprana == 'alta':
            fila_data['event'] = 0
        
        else: 
            print('error:',row['record_id'])
            
        df_data.loc[len(df_data)] = fila_data

        #print(fecha_temprana,fila_data)


    # ====================================================================================== 



    return df_data,df_analysis
    

if __name__ == '__main__':

    main()