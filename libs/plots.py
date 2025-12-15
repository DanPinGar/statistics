import matplotlib as plt


def labeled_plot(x,y,label,**kwargs):

    default = {
        'title':'',
        'x_name':'',
        'y_name':'',
    }

    args = {**default,**kwargs}
    
    plt.plot(x, y, label=f'AUC = {label:.3f}')
    plt.plot([0, 1], [0, 1], 'k--')
    plt.xlabel(args['x_name'])
    plt.ylabel(args['y_name'])
    plt.title(args['title'])
    plt.legend()
    plt.show()