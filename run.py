from typing import List, Dict

from libs import plots, functions as fn
from test import stats
import process_data as pr
from config import DATA_DIR, DATA_TEMP


# =========================
# Configuration constants
# =========================

TO_DATETIME_COLUMNS: List[str] = [
    'fecha_muerte', 'fecha_alta', 'fecha_cirugia', 'fecha_eco',
    'fecha_trat1', 'fecha_prev1', 'fecha_prev2', 'fecha_prev3'
]

DROP_COLUMNS: List[str] = [
    'comentarios', 'fecha_trat2', 'revisar medida', 'diam_ao',
    'diam_mitral', 'diam_ao_2', 'diam_mitral_2', 'result',
    'indicacion_cirugia', 'fecha_diagnostico'
]


# =========================
# Core analysis functions
# =========================

def run_basic_statistics(
    df_data,
    show_plots: bool,
    analysis_ia: bool
) -> None:
    print('\n================= BASIC STATISTICS =================\n')

    df_cases = df_data[df_data['event'] == 1]
    df_controls = df_data[df_data['event'] == 0]

    print(f'Cases: {df_cases.shape[0]} | Controls: {df_controls.shape[0]}')

    df_cases.to_excel(f'{DATA_TEMP}df_cases.xlsx', index=False)
    df_controls.to_excel(f'{DATA_TEMP}df_controls.xlsx', index=False)

    cases_diam = df_cases['diameter']
    controls_diam = df_controls['diameter']

    mean_c, std_c, mean_ctrl, std_ctrl = fn.mean_and_std(cases_diam, controls_diam)

    print(f'Mean Final Cases: {mean_c:.3f} ± {std_c:.3f}')
    print(f'Mean Final Controls: {mean_ctrl:.3f} ± {std_ctrl:.3f}')

    if analysis_ia:
        cases_ia = df_cases['diam_IA']
        controls_ia = df_controls['diam_IA']

        mean_c_ia, std_c_ia, mean_ctrl_ia, std_ctrl_ia = fn.mean_and_std(
            cases_ia, controls_ia
        )

        print(f'Mean Final Cases IA: {mean_c_ia:.3f} ± {std_c_ia:.3f}')
        print(f'Mean Final Controls IA: {mean_ctrl_ia:.3f} ± {std_ctrl_ia:.3f}')

    if show_plots and analysis_ia:
        plots.labeled_boxplot(
            [cases_diam, cases_ia, controls_diam, controls_ia],
            ['Cases', 'Cases IA', 'Controls', 'Controls IA'],
            title='Diameter Comparison',
            ylabel='Diameter'
        )

    print('\n================= P-VALUE & ROC =================\n')

    stats.p_value(cases_diam, controls_diam)
    auc, fpr, tpr = stats.roc(cases_diam, controls_diam)

    if show_plots:
        plots.labeled_plot(
            fpr, tpr, auc,
            title='ROC Curve',
            x_name='False Positive Rate',
            y_name='True Positive Rate'
        )


def run_cox_ph(
    df_data,
    show_plots: bool,
    analysis_ia: bool
) -> None:
    print('\n================= COX PROPORTIONAL HAZARDS =================\n')

    df_cox_diam = df_data[['days', 'event', 'diameter']]

    stats.prop_hazard(
        df=df_cox_diam,
        duration_col='days',
        event_col='event',
        show_plots=show_plots
    )

    if analysis_ia:
        df_cox_ia = df_data[['days', 'event', 'diam_IA']]
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
    print('\n================= COX TIME-VARYING =================\n')

    df_time = pr.pr_2(event_map, df_analysis)
    df_time = df_time[['id', 'start', 'stop', 'event', 'diameter', 'surgery']]

    df_time.to_excel(f'{DATA_TEMP}df_data_time.xlsx', index=False)

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
    print('\n================= FINE & GRAY =================\n')

    df_fg = pr.pr_3(df_analysis, event_map_gray)

    stats.fine_gray(
        df=df_fg,
        covars_names_list=['diameter'],
        col_time='days',
        col_event='event'
    )


# =========================
# Main pipeline
# =========================

def main(
    data_file_path: str,
    analysis_to_perform: List[str],
    event_map: Dict[str, int],
    event_map_gray: Dict[str, int],
    show_plots: bool,
    analysis_ia: bool
) -> None:

    df = pr.clean_excel(
        data_file_path,
        drop_columns=DROP_COLUMNS,
        to_datetime_columns=TO_DATETIME_COLUMNS
    )

    df_data, df_analysis = pr.pr_1(event_map, df)
    df_data.to_excel(f'{DATA_TEMP}df_data.xlsx', index=False)

    if 'basic_stats' in analysis_to_perform:
        run_basic_statistics(df_data, show_plots, analysis_ia)

    if 'cox_ph' in analysis_to_perform:
        run_cox_ph(df_data, show_plots, analysis_ia)

    if 'cox_tv' in analysis_to_perform:
        run_cox_time_varying(df_analysis, event_map, show_plots)

    if 'fine_gray' in analysis_to_perform:
        run_fine_gray(df_analysis, event_map_gray)


# =========================
# Entry point
# =========================

if __name__ == '__main__':

    DATA_FILE_PATH = f'{DATA_DIR}data_22_01_26.xlsx'

    ANALYSIS_TO_PERFORM = [
        'basic_stats',
        'cox_ph',
        'cox_tv',
        'fine_gray'
    ]

    EVENT_MAP = {'surg': 0, 'prev': 1, 'embo': 1, 'muer': 0, 'alta': 0}
    EVENT_MAP_GRAY = {'surg': 0, 'prev': 1, 'embo': 1, 'muer': 2, 'alta': 0}

    main(
        data_file_path=DATA_FILE_PATH,
        analysis_to_perform=ANALYSIS_TO_PERFORM,
        event_map=EVENT_MAP,
        event_map_gray=EVENT_MAP_GRAY,
        show_plots=True,
        analysis_ia=False
    )
