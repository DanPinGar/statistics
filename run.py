import process_data


def main(data_file_path):

    to_datetime_columns = ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']
    drop_columns =['comments','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','indicacion_cirugia','fecha_diagnostico']
    
    df_data = process_data.main(data_file_path, drop_columns = drop_columns, to_datetime_columns= to_datetime_columns)
    print(df_data)
    

if __name__ == '__main__':

    data_file_path = './data.xlsx'

    
    main(data_file_path)