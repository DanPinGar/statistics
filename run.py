import process_data


def main(data_file_path):

    to_datetime_columns = ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']
    drop_columns =['comments','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','indicacion_cirugia','fecha_diagnostico']
    
    df_data = process_data.main(
        data_file_path,
        drop_columns = drop_columns,
        to_datetime_columns=to_datetime_columns
        )
    
    df_cases =  df_data[ df_data['event']==1]
    df_controls = df_data[df_data['event']==0]

    print('Cases:',df_cases.shape[0])
    print('Controls:',df_controls.shape[0])

    mean_cases = df_cases['diameter'].mean()
    std_cases = df_cases['diameter'].std()

    mean_controls = df_controls['diameter'].mean()
    std_controls = df_controls['diameter'].std()

    print("Mean Final Cases:", mean_cases)
    print("Std Final Cases:", std_cases)
    print("Mean Final Controls:", mean_controls)
    print("Std Final Controls:", std_controls)
    

if __name__ == '__main__':

    data_file_path = './data.xlsx'

    
    main(data_file_path)