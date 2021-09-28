
class ICON_ARRAY:

    out_of = 10000
    marker = 'o'
    n_rows = 50
    colors = ['red', 'orange', 'gray']
    other_string = 'unaffected'
    scale = 10
    n_cols = out_of/n_rows
    def __init__(self, **kwargs):
        classes = {}
        for key, value in kwargs.items():
            classes[key] = value

        self.classes = classes

    def plot(self, **kwargs):

        x = np.arange(int(self.n_cols/self.scale))
        y = np.arange(int(self.n_rows/self.scale))

        X, Y = np.meshgrid(x, y)
        xx = np.hstack(X)
        yy = np.hstack(Y)

        fig, ax = plt.subplots(1, 1, figsize=(self.n_cols/10, self.n_rows/10))
        missing = []
        i = 0
        v0 = 0
        labels = []
        for key, value in self.classes.items():
            value = int(value/self.scale)
            ax.scatter(xx[v0:v0+value], yy[v0:v0+value],
                       marker='o', c=self.colors[i], label=key, **kwargs)
            missing.append(value)
            labels.append(key)
            v0 = v0+value
            i = i+1

        ax.scatter(xx[v0:], yy[v0:], marker='o',
                   c=self.colors[i], label=self.other_string, **kwargs)
        ax.axes.xaxis.set_ticks([])
        ax.axes.yaxis.set_ticks([])
        ax.legend(labels, loc="lower center",
                  bbox_to_anchor=(0.1, -0.2), fontsize=15)
        fig.subplots_adjust(bottom=0.1)
        plt.show()
