
def mean_and_std(cases_final_diam,controls_final_diam):

    mean_cases = cases_final_diam.mean()
    std_cases  = cases_final_diam.std()
    mean_controls = controls_final_diam.mean()
    std_controls  = controls_final_diam.std()

    return mean_cases,std_cases,mean_controls,std_controls
