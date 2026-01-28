from typing import List, Dict

from libs.logger_config import setup_logger
from libs import plots, functions as fn
from test import stats
import process_data as pr
from config import DATA_DIR, DATA_TEMP


logger = setup_logger(__name__)

TO_DATETIME_COLUMNS: List[str] = [
    'fecha_muerte', 'fecha_alta', 'fecha_cirugia', 'fecha_eco',
    'fecha_trat1', 'fecha_prev1', 'fecha_prev2', 'fecha_prev3'
]

DROP_COLUMNS: List[str] = [
    'comentarios', 'fecha_trat2', 'revisar medida', 'diam_ao',
    'diam_mitral', 'diam_ao_2', 'diam_mitral_2', 'result',
    'indicacion_cirugia', 'fecha_diagnostico'
]


def run_basic_statistics(
    df_data,
    show_plots: bool,
    analysis_ia: bool
) -> None:
    logger.info("Starting basic statistics analysis")

    df_cases = df_data[df_data['event'] == 1]
    df_controls = df_data[df_data['event'] == 0]

    logger.info("Cases: %d | Controls: %d",df_cases.shape[0],df_controls.shape[0])
    logger.debug("df_cases shape: %s", df_cases.shape)
    logger.debug("df_controls shape: %s", df_controls.shape)

    df_cases.to_excel(DATA_TEMP + 'df_cases.xlsx', index=False)
    df_controls.to_excel(f'{DATA_TEMP}df_controls.xlsx', index=False)

    cases_diam = df_cases['diameter']
    controls_diam = df_controls['diameter']

    mean_c, std_c, mean_ctrl, std_ctrl = fn.mean_and_std(
        cases_diam, controls_diam
    )

    logger.info("Mean Cases: %.3f ± %.3f", mean_c, std_c)
    logger.info("Mean Controls: %.3f ± %.3f", mean_ctrl, std_ctrl)

    if analysis_ia:
        logger.info("Running IA-based diameter analysis")

        cases_ia = df_cases['diam_IA']
        controls_ia = df_controls['diam_IA']

        mean_c_ia, std_c_ia, mean_ctrl_ia, std_ctrl_ia = fn.mean_and_std(
            cases_ia, controls_ia
        )

        logger.info("Mean Cases IA: %.3f ± %.3f", mean_c_ia, std_c_ia)
        logger.info("Mean Controls IA: %.3f ± %.3f", mean_ctrl_ia, std_ctrl_ia)

    if show_plots and analysis_ia:
        plots.labeled_boxplot(
            [cases_diam, cases_ia, controls_diam, controls_ia],
            ['Cases', 'Cases IA', 'Controls', 'Controls IA'],
            title='Diameter Comparison',
            ylabel='Diameter'
        )

    stats.p_value(cases_diam, controls_diam)
    auc, fpr, tpr = stats.roc(cases_diam, controls_diam)

    logger.debug("ROC AUC: %.4f", auc)

    if show_plots:
        plots.labeled_plot(
            fpr,
            tpr,
            auc,
            title='ROC Curve',
            x_name='False Positive Rate',
            y_name='True Positive Rate'
        )


def run_cox_ph(
    df_data,
    show_plots: bool,
    analysis_ia: bool
) -> None:
    logger.info("Starting Cox Proportional Hazards analysis")
    df_cox_diam = df_data[['days', 'event', 'diameter']]

    stats.prop_hazard(
        df=df_cox_diam,
        duration_col='days',
        event_col='event',
        show_plots=show_plots
    )

    if analysis_ia:
        logger.info("Running Cox PH with IA diameter")
        df_cox_ia = df_data[['days', 'event', 'diam_IA']]
        logger.debug("Cox PH dataframe (IA) shape: %s", df_cox_ia.shape)

        stats.prop_hazard(
            df=df_cox_ia,
            duration_col='days',
            event_col='event',
            show_plots=show_plots
        )


def run_cox_time_varying(
    df_analysis,
    event_map: Dict[str, int],
    show_plots: bool
) -> None:
    logger.info("Starting Cox time-varying analysis")

    df_time = pr.pr_2(event_map, df_analysis)
    df_time = df_time[['id', 'start', 'stop', 'event', 'diameter', 'surgery']]
    df_time.to_excel(DATA_TEMP +'df_data_time.xlsx', index=False)

    stats.cox_tvaryng(
        df=df_time,
        id_col='id',
        start_col='start',
        stop_col='stop',
        event_col='event',
        show_progress=True,
        show_plots=show_plots
    )


def run_fine_gray(
    df_analysis,
    event_map_gray: Dict[str, int]
) -> None:
    logger.info("Starting Fine & Gray competing risks analysis")

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
    analysis_ia: bool
) -> None:
    logger.info("Input file: %s", data_file_path)
    logger.info("Analyses requested: %s", analysis_to_perform)

    df = pr.clean_excel(
        data_file_path,
        drop_columns=DROP_COLUMNS,
        to_datetime_columns=TO_DATETIME_COLUMNS
    )

    logger.debug("Dataframe after cleaning: %s", df.shape)

    df_data, df_analysis = pr.pr_1(event_map, df)

    logger.debug(
        "df_data shape: %s | df_analysis shape: %s",
        df_data.shape,
        df_analysis.shape
    )

    df_data.to_excel(f'{DATA_TEMP}df_data.xlsx', index=False)

    if 'basic_stats' in analysis_to_perform:
        run_basic_statistics(df_data, show_plots, analysis_ia)

    if 'cox_ph' in analysis_to_perform:
        run_cox_ph(df_data, show_plots, analysis_ia)

    if 'cox_tv' in analysis_to_perform:
        run_cox_time_varying(df_analysis, event_map, show_plots)

    if 'fine_gray' in analysis_to_perform:
        run_fine_gray(df_analysis, event_map_gray)

    
if __name__ == '__main__':

    DATA_FILE_PATH = DATA_DIR + 'data_22_01_26.xlsx'

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
        show_plots=True,
        analysis_ia=False
    )
