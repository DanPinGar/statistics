
from lifelines import CoxPHFitter,CoxTimeVaryingFitter
from scipy.stats import ttest_ind
from sklearn.metrics import roc_curve, roc_auc_score


def p_value(group_a,group_b):

    stat, p_value = ttest_ind(group_a, group_b)
    print("p-valor:", f"{p_value:.6f}")


def roc(cases=None,controls=None):

    y_true = [1]*len(cases) + [0]*len(controls)
    y_scores = cases + controls                       # Junta los valores de 'diameter' de ambos grupos

    fpr, tpr, thresholds = roc_curve(y_true, y_scores)
    auc = roc_auc_score(y_true, y_scores)


def prop_hazard(df = None, duration_col=None, event_col=None):

    cph = CoxPHFitter()
    cph.fit(df, duration_col = duration_col, event_col=event_col)
    print(cph.summary)
    cph.plot()


def conx_tvaryng(
        df = None,
        id_col = None,
        start_col = None,
        stop_col = None,
        event_col = None,
        **kwargs,
        ):
    
    default = {
        'show_progress':True,
    }

    args = {**default,**kwargs}

    ctv = CoxTimeVaryingFitter()
    ctv.fit(df,id_col=id_col, start_col=start_col, stop_col=stop_col, event_col=event_col, show_progress=args['show_progress'])
    ctv.print_summary()

