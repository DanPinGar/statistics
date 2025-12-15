import process_data_1, process_data_2
from libs import plots
from test import stats

def main(data_file_path):

    to_datetime_columns = ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']
    drop_columns =['comments','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','indicacion_cirugia','fecha_diagnostico']
    
    df_data,df_analysis = process_data_1.main(
        data_file_path,
        drop_columns = drop_columns,
        to_datetime_columns = to_datetime_columns
        )
    
    # ================= MEAN =================

    df_cases =  df_data[ df_data['event']==1]
    df_controls = df_data[df_data['event']==0]

    cases_final = df_cases['diameter']
    controls_final = df_controls['diameter']

    mean_cases = cases_final.mean()
    std_cases = cases_final.std()

    mean_controls = controls_final.mean()
    std_controls = controls_final.std()

    print('Cases:',df_cases.shape[0],'Controls:',df_controls.shape[0])
    print(f'Mean Final Cases:, {mean_cases} +- {std_cases}')
    print(f'Mean Final Controls: {mean_controls} +- {std_controls}')

    plots.labeled_boxplot([cases_final, controls_final],['Cases', 'Controls'],title = 'diam',ylabel= 'diam' )

    # ================= P-VALUE,ROC =================

    stats.p_value(cases_final,controls_final)

    auc,fpr,tpr = stats.roc(cases_final,controls_final)
    plots.labeled_plot(
        fpr,tpr,auc,title = 'ROC',x_name = 'FP Rate',y_name ='TP Rate'
        )

    # ================= COX PH FITTER =================

    df_data_cox = df_data[[ 'days','event','diameter']]
    stats.prop_hazard(
        df = df_data_cox, duration_col = 'days', event_col = 'event'
        )
    
    # ================= COX TV FITTER =================

    df_data_time = process_data_2.main(df_analysis)

    stats.conx_tvaryng(
        df = df_data_time,
        id_col = 'id',
        start_col = 'start',
        stop_col = 'stop',
        event_col = 'event',
        show_progress=True
    )
   
    

if __name__ == '__main__':

    data_file_path = './data.xlsx'
    
    main(data_file_path)