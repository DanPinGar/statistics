
import pandas as pd

def main(data_file_path = None,**kwargs):

    default = {
        'drop_columns' : []
    }

    args = {**default,**kwargs}

    print('processing data ...')
    df_data = pd.read_excel(data_file_path, decimal = ',')
    for columna in ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']:
    df_data[columna] = pd.to_datetime(df_data[columna], errors = 'coerce')

    df_data =df_data.drop(['comments','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','indicacion_cirugia','fecha_diagnostico'],axis=1)

    data_processed = []

    return data_processed
    

if __name__ == '__main__':


    main()