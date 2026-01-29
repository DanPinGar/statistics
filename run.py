from typing import List, Dict

from libs.logger_config import setup_logger
from libs import plots, functions as fn
from test import stats
import process_data as pr
from config import DATA_DIR, DATA_TEMP


TO_DATETIME_COLUMNS: List[str] = [
    'fecha_muerte', 'fecha_alta', 'fecha_cirugia', 'fecha_eco',
    'fecha_trat1', 'fecha_prev1', 'fecha_prev2', 'fecha_prev3'
]

DROP_COLUMNS: List[str] = [
    'comentarios', 'fecha_trat2', 'revisar medida', 'diam_ao',
    'diam_mitral', 'diam_ao_2', 'diam_mitral_2', 'result',
    'indicacion_cirugia', 'fecha_diagnostico'
]

logger = setup_logger(__name__)


def run_basic_statistics(
    df_data,
    show_plots: bool,
    analysis_AI: bool
) -> None:

    df_cases = df_data[df_data['event'] == 1]
    df_controls = df_data[df_data['event'] == 0]

    logger.info("Cases: %d | Controls: %d \n",df_cases.shape[0],df_controls.shape[0])

    df_cases.to_excel(DATA_TEMP + 'df_cases.xlsx', index=False)
    df_controls.to_excel(f'{DATA_TEMP}df_controls.xlsx', index=False)

    cases_diam = df_cases['diameter']
    controls_diam = df_controls['diameter']

    mean_c, std_c, mean_ctrl, std_ctrl = fn.mean_and_std(
        cases_diam, controls_diam
    )

    logger.info("Mean Cases: %.3f ± %.3f", mean_c, std_c)
    logger.info("Mean Controls: %.3f ± %.3f \n", mean_ctrl, std_ctrl)

    if analysis_AI:
        cases_ia = df_cases['diam_AI']
        controls_ia = df_controls['diam_AI']

        mean_c_ia, std_c_ia, mean_ctrl_ia, std_ctrl_ia = fn.mean_and_std(
            cases_ia, controls_ia
        )

        logger.info("Mean Cases IA: %.3f ± %.3f", mean_c_ia, std_c_ia)
        logger.info("Mean Controls IA: %.3f ± %.3f", mean_ctrl_ia, std_ctrl_ia)

        if show_plots:
            plots.labeled_boxplot(
                [cases_diam, cases_ia, controls_diam, controls_ia],
                ['Cases', 'Cases IA', 'Controls', 'Controls IA'],
                title='Diameter Comparison',
                ylabel='Diameter'
            )

    stats.p_value(cases_diam, controls_diam)
    auc, fpr, tpr = stats.roc(cases_diam, controls_diam)
    logger.info("ROC AUC: %.4f", auc)

    if analysis_AI:
        stats.p_value(cases_ia, controls_ia, title ='AI')
        auc_AI, fpr_AI, tpr_AI = stats.roc(cases_ia, controls_ia)
        logger.info("ROC AUC AI: %.4f \n", auc_AI)

    if show_plots:
        plots.labeled_plot(
            fpr,
            tpr,
            auc,
            title='ROC Curve',
            x_name='False Positive Rate',
            y_name='True Positive Rate'
        )

        if analysis_AI:
            plots.labeled_plot(
            fpr_AI,
            tpr_AI,
            auc_AI,
            title='ROC Curve AI',
            x_name='False Positive Rate',
            y_name='True Positive Rate'
        )


def run_cox_ph(
    df_data,
    show_plots: bool,
    analysis_AI: bool
) -> None:
    logger.info(" COX PROPORTIONAL HAZARDS: \n")
    df_cox_diam = df_data[['days', 'event', 'diameter']]

    stats.prop_hazard(
        df=df_cox_diam,
        duration_col='days',
        event_col='event',
        show_plots=show_plots
    )

    if analysis_AI:
        logger.info("COX PH AI DIAMETER: \n")
        df_cox_ia = df_data[['days', 'event', 'diam_AI']]

        stats.prop_hazard(
            df=df_cox_ia,
            duration_col='days',
            event_col='event',
            show_plots=show_plots
        )


def run_cox_time_varying(
    df_analysis,
    event_map: Dict[str, int],
    show_plots: bool,
    analysis_AI: bool
) -> None:
    logger.info("COX TIME VARYING")

    df_time = pr.pr_2(event_map, df_analysis)
    df_time = df_time[['id', 'start', 'stop', 'event', 'diameter', 'surgery']]
    df_time.to_excel(DATA_TEMP +'df_data_time.xlsx', index=False)

    stats.cox_tvaryng(
        df=df_time,
        id_col='id',
        start_col='start',
        stop_col='stop',
        event_col='event',
        covariate = 'diameter',
        show_progress=False,
        show_plots=show_plots
    )

    if analysis_AI:
        df_time = pr.pr_2(event_map, df_analysis)
        df_time = df_time[['id', 'start', 'stop', 'event', 'diam_AI', 'surgery']]
        df_time.to_excel(DATA_TEMP +'df_data_time_AI.xlsx', index=False)

        stats.cox_tvaryng(
            df=df_time,
            id_col='id',
            start_col='start',
            stop_col='stop',
            event_col='event',
            covariate = 'diam_AI',
            show_progress=False,
            show_plots=show_plots
        )


def run_fine_gray(
    df_analysis,
    event_map_gray: Dict[str, int]
) -> None:
    logger.info("FINE GRAY: \n")

    df_fg = pr.pr_3(event_map_gray,df_analysis)

    stats.fine_gray(
        df=df_fg,
        covars_names_list=['diameter'],
        col_time='days',
        col_event='event'
    )


def main(
    data_file_path: str,
    analysis_to_perform: List[str],
    event_map: Dict[str, int],
    event_map_gray: Dict[str, int],
    show_plots: bool,
    analysis_AI: bool
) -> None:
    
    logger.info("\n Input file: %s \n", data_file_path)

    df = pr.clean_excel(
        data_file_path,
        drop_columns=DROP_COLUMNS,
        to_datetime_columns=TO_DATETIME_COLUMNS
    )

    logger.debug("Dataframe after cleaning: %s", df.shape)

    df_data, df_analysis = pr.pr_1(event_map, df)

    df_data.to_excel(f'{DATA_TEMP}df_data.xlsx', index=False)

    if 'basic_stats' in analysis_to_perform:
        run_basic_statistics(df_data, show_plots, analysis_AI)

    if 'cox_ph' in analysis_to_perform:
        run_cox_ph(df_data, show_plots, analysis_AI)

    if 'cox_tv' in analysis_to_perform:
        run_cox_time_varying(df_analysis, event_map, show_plots,analysis_AI)

    if 'fine_gray' in analysis_to_perform:
        run_fine_gray(df_analysis, event_map_gray)

    
if __name__ == '__main__':

    DATA_FILE_PATH = DATA_DIR + 'excels/data_29_01_26.xlsx'

    ANALYSIS_TO_PERFORM = [
        'basic_stats',
        'cox_ph',
        'cox_tv',
        'fine_gray'
    ]

    EVENT_MAP = {
        'surg': 0,
        'prev': 1,
        'embo': 1,
        'muer': 0,
        'alta': 0
    }

    EVENT_MAP_GRAY = {
        'surg': 0,
        'prev': 1,
        'embo': 1,
        'muer': 2,
        'alta': 0
    }

    main(
        data_file_path=DATA_FILE_PATH,
        analysis_to_perform=ANALYSIS_TO_PERFORM,
        event_map=EVENT_MAP,
        event_map_gray=EVENT_MAP_GRAY,
        show_plots= False,
        analysis_AI= True
    )
