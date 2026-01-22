from libs import plots
from test import stats

import process_data as pr

from libs import functions as fn

from config import DATA_DIR


def main(data_file_path):

    to_datetime_columns = ['fecha_muerte', 'fecha_alta', 'fecha_cirugia','fecha_eco','fecha_trat1','fecha_prev1','fecha_prev2', 'fecha_prev3']
    drop_columns =['comentarios', 'fecha_trat2','revisar medida','diam_ao', 'diam_mitral','diam_ao_2','diam_mitral_2','result','indicacion_cirugia','fecha_diagnostico']
    
    df = pr.clean_excel(
        data_file_path,
        drop_columns = drop_columns,
        to_datetime_columns = to_datetime_columns
    )

    df_data,df_analysis = pr.pr_1(event_map,df)
    df_data.to_excel(DATA_DIR + 'df_dat.xlsx', index = False) 

    if 'basic_stats' in analysis_to_perform:

        print('\n================= MEAN =================\n')

        df_cases =  df_data[ df_data['event']==1]
        df_controls = df_data[df_data['event']==0]

        print('Cases:',df_cases.shape[0],'Controls:',df_controls.shape[0])

        df_cases.to_excel(DATA_DIR + 'df_cases.xlsx', index = False) 
        df_controls.to_excel(DATA_DIR + 'df_controls.xlsx', index = False) 

        cases_final_diam = df_cases['diameter']
        controls_final_diam = df_controls['diameter']
        mean_cases_diam,std_cases_diam,mean_controls_diam,std_controls_diam = fn.mean_and_std(
            cases_final_diam,controls_final_diam)
        
        print(f'Mean Final Cases:, {mean_cases_diam} +- {std_cases_diam}')
        print(f'Mean Final Controls: {mean_controls_diam} +- {std_controls_diam}')
        
        if analysis_IA:
            cases_final_IA = df_cases['diam_IA']
            controls_final_IA = df_controls['diam_IA']
            mean_cases_IA,std_cases_IA,mean_controls_IA,std_controls_IA = fn.mean_and_std(
                cases_final_IA,controls_final_IA)
            
            print(f'Mean Final Cases IA:, {mean_cases_IA} +- {std_cases_IA}')
            print(f'Mean Final Controls IA: {mean_controls_IA} +- {std_controls_IA}')

        if show_plots and analysis_IA:
            plots.labeled_boxplot(
                [cases_final_diam,cases_final_IA, controls_final_diam,controls_final_IA],
                ['Cases','Cases IA','Controls', 'Controls IA'],
                title = 'diam',
                ylabel= 'diam'
            )

        print('\n================= P-VALUE,ROC =================\n')

        stats.p_value(cases_final_diam,controls_final_diam)
        auc,fpr,tpr = stats.roc(cases_final_diam,controls_final_diam)

        if show_plots:
            plots.labeled_plot(
                fpr,tpr,auc,title = 'ROC',x_name = 'FP Rate',y_name ='TP Rate'
                )


    if 'cox_ph' in analysis_to_perform:
        print('\n================= COX PH FITTER =================\n')

        df_data_cox_diam = df_data[[ 'days','event','diameter']]
        df_data_cox_IA = df_data[[ 'days','event','diam_IA']]

        stats.prop_hazard(
            df = df_data_cox_diam,
            duration_col = 'days',
            event_col = 'event',
            show_plots = show_plots,
        )

        if analysis_IA:
            stats.prop_hazard(
                df = df_data_cox_IA,
                duration_col = 'days',
                event_col = 'event',
                show_plots = show_plots,
            )

    
    if 'cox_tv' in analysis_to_perform:
        print('\n================= COX TV FITTER =================\n')

        df_data_time = pr.pr_2(event_map,df_analysis)
        df_data_time = df_data_time[['id','start','stop','event','diameter','surgery']]

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

    if 'fine_gray' in analysis_to_perform:
        print('\n================= FINE GRAY =================\n')

        df_fine_gray = pr.pr_3(df_analysis,event_map_gray)  
        stats.fine_gray(
            df = df_fine_gray,covars_names_list = ['diameter'],col_time = 'days', col_event = 'event'
        )


if __name__ == '__main__':

    data_file_path = DATA_DIR + 'data_22_01_26.xlsx'
    show_plots = True
    analysis_IA = False

    analysis_to_perform = [
        'basic_stats','cox_ph','cox_tv','fine_gray' # Options: 'basic_stats','cox_ph','cox_tv','fine_gray'
    ]

    event_map = {'surg': 0,'prev': 1,'embo': 1,'muer': 0,'alta': 0}
    event_map_gray = {'surg': 0,'prev': 1,'embo': 1,'muer': 2,'alta': 0 }
    
    main(data_file_path)