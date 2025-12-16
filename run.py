from libs import plots
from test import stats

import process_data as pr

from config import DATA_DIR


def main(data_file_path):

    to_datetime_columns = ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']
    drop_columns =['comments', 'fecha_trat2','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','result','indicacion_cirugia','fecha_diagnostico']
    
    df = pr.clean_excel(
        data_file_path,
        drop_columns = drop_columns,
        to_datetime_columns = to_datetime_columns
    )

    event_map_1 = {'surg': 0,'prev': 1,'embo': 1,'muer': 0,'alta': 0}

    df_data,df_analysis = pr.pr_1(event_map_1,df)
    
    print('\n================= MEAN =================\n')

    df_cases =  df_data[ df_data['event']==1]
    df_controls = df_data[df_data['event']==0]

    df_cases.to_excel(DATA_DIR + 'df_cases.xlsx', index=False) 
    df_controls.to_excel(DATA_DIR + 'df_controls.xlsx', index=False) 

    cases_final = df_cases['diameter']
    controls_final = df_controls['diameter']

    mean_cases = cases_final.mean()
    std_cases  = cases_final.std()

    mean_controls = controls_final.mean()
    std_controls  = controls_final.std()

    print('Cases:',df_cases.shape[0],'Controls:',df_controls.shape[0])
    print(f'Mean Final Cases:, {mean_cases} +- {std_cases}')
    print(f'Mean Final Controls: {mean_controls} +- {std_controls}')

    if show_plots:
        plots.labeled_boxplot(
            [cases_final, controls_final],['Cases', 'Controls'],title = 'diam',ylabel= 'diam'
        )

    print('\n================= P-VALUE,ROC =================\n')

    stats.p_value(cases_final,controls_final)
    auc,fpr,tpr = stats.roc(cases_final,controls_final)

    if show_plots:
        plots.labeled_plot(
            fpr,tpr,auc,title = 'ROC',x_name = 'FP Rate',y_name ='TP Rate'
            )

    print('\n================= COX PH FITTER =================\n')

    df_data_cox = df_data[[ 'days','event','diameter']]
    df_data_cox.to_excel(DATA_DIR + 'df_data_cox.xlsx', index=False) 

    stats.prop_hazard(
        df = df_data_cox,
        duration_col = 'days',
        event_col = 'event',
        show_plots = show_plots,
    )
    

    print('\n================= COX TV FITTER =================\n')

    df_data_time = pr.pr_2(event_map_1,df_analysis)

    df_data_time.to_excel(DATA_DIR + 'df_data_time.xlsx', index=False) 

    stats.cox_tvaryng(
        df = df_data_time,
        id_col = 'id',
        start_col = 'start',
        stop_col = 'stop',
        event_col = 'event',
        show_progress = True,
        show_plots = show_plots,
    )


    print('\n================= FINE GRAY =================\n')

    event_map_2 = {'surg': 0,'prev': 1,'embo': 1,'muer': 2,'alta': 0 }

    df_fine_gray = pr.pr_3(df_analysis,event_map_2)  
    stats.fine_gray(
        df = df_fine_gray,covars_names_list = ['diameter'],col_time = 'days', col_event = 'event'
    )


if __name__ == '__main__':

    data_file_path = DATA_DIR + 'data.xlsx'
    show_plots = False
    
    main(data_file_path)