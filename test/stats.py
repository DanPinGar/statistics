
import pandas as pd
import matplotlib.pyplot as plt
from lifelines import CoxPHFitter,CoxTimeVaryingFitter
from scipy.stats import ttest_ind
from sklearn.metrics import roc_curve, roc_auc_score
import cmprsk.cmprsk as cmprsk
from cmprsk import utils


def p_value(cases,controls):
    stat, p_value = ttest_ind(cases, controls)
    print( f'\n p-value: {p_value:.6f} \n')


def roc(cases=None,controls=None):
    y_true = [1]*len(cases) + [0]*len(controls)
    y_scores = pd.concat([cases,controls])  # Junta los valores de 'diameter' de ambos grupos

    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    auc = roc_auc_score(y_true, y_scores)

    return auc,fpr, tpr


def prop_hazard(df = None, duration_col=None, event_col=None,**kwargs):
    cph = CoxPHFitter()
    cph.fit(df, duration_col = duration_col, event_col=event_col)
    print(cph.summary)
    cph.plot()
    if kwargs['show_plots']:
        plt.show()
    cph.check_assumptions(df, show_plots=True)  # Gráfico de residuos de Schoenfeld 
    if kwargs['show_plots']:
        plt.show()


def cox_tvaryng(
        df = None,
        id_col = None,
        start_col = None,
        stop_col = None,
        event_col = None,
        **kwargs,
        ):
    
    default = {
        'show_progress':True,
        'show_plots':True
    }

    args = {**default,**kwargs}

    ctv = CoxTimeVaryingFitter()
    ctv.fit(
        df,id_col=id_col, start_col=start_col, stop_col=stop_col, event_col=event_col, show_progress=args['show_progress']
    )
    ctv.print_summary()
    ctv.plot(columns=["diameter"])
    if args['show_plots']:
        plt.show()


def fine_gray(df = None,covars_names_list = None,col_time = None, col_event = None):
        
    X = utils.as_indicators(df[covars_names_list], [], bases = None)  # Preprocesar covariables
    crr_result = cmprsk.crr(df[col_time], df[col_event], X)  # Ajustar modelo Fine–Gray para “evento de interés = 1” 
    print(crr_result.summary)