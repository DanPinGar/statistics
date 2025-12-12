
import pandas as pd

def main(data_file_path = None,**kwargs):

    print('processing data ...')

    default = {
        'drop_columns' : [],
        'to_datetime_columns':[],
    }

    args = {**default,**kwargs}

    df_data = pd.read_excel(data_file_path, decimal = ',')

    for columna in args['to_datetime_columns']:
        df_data[columna] = pd.to_datetime(df_data[columna], errors = 'coerce')

    df_data =df_data.drop(args['drop_columns'],axis=1)

    

    return df_data
    

if __name__ == '__main__':

    main()