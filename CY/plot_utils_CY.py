import matplotlib.pyplot as plt
from matplotlib.font_manager import FontProperties
from matplotlib.ticker import StrMethodFormatter
from matplotlib.ticker import ScalarFormatter

### Chuan Yin ###

# Define Tableau 10 Colors
tableau_colors = [
    (31, 119, 180),  # Blue 0, science, blue detuning
    (255, 127, 14),  # Orange 1
    (44, 160, 44),   # Green 2
    (214, 39, 40),   # Red 3, red detuning
    (148, 103, 189), # Purple 4, excited state (black being ground state), bid-ask spread
    (140, 86, 75),   # Brown 5
    (227, 119, 194), # Pink 6, loadlock, volatility
    (127, 127, 127), # Gray 7
    (188, 189, 34),  # Yellow 8
    (23, 190, 207),  # Cyan 9 
]

# Normalize RGB values to range [0, 1]
tableau_colors = [(r / 255, g / 255, b / 255) for r, g, b in tableau_colors]
font = {'family': 'Georgia', 'color':  'black', 'weight': 'normal', 'size': 20}
title_font = {'family': 'Georgia', 'color':  'black', 'weight': 'bold', 'style': 'italic', 'size': 20}
suptitle_font = FontProperties(family='Georgia', weight='bold', size=22)
legend_font = {'family': 'Georgia', 'weight': 'normal', 'size': 16}
tick_font = {'family': 'Georgia', 'size': 18}

plt.rcParams['mathtext.fontset'] = 'stix'

class ScatterPlot:
    def __init__(self, x, y, 
                 figsize=(12, 8), ptsize=20,
                 color=tableau_colors[0],
                 xlim=None, ylim=None,
                 xlabel='', ylabel='', datalabel='', title='',
                 xticks=None, yticks=None,
                 xprecision=0, yprecision=0,
                 legendloc='upper right',
                 saveflag=False, savename='example'):
        self.x = x
        self.y = y
        self.figsize = figsize
        self.ptsize = ptsize
        self.color = color
        self.xlim = xlim
        self.ylim = ylim
        self.xlabel = xlabel
        self.ylabel = ylabel
        self.datalabel = datalabel
        self.title = title
        self.xticks = xticks
        self.yticks = yticks
        self.xprecision = xprecision
        self.yprecision = yprecision
        self.legendloc = legendloc
        self.saveflag = saveflag
        self.savename = savename

    
    def plot(self):
        fig = plt.figure(figsize=self.figsize)
        ax = plt.gca()
        ax.scatter(self.x, self.y, color=self.color, s=self.ptsize)
        if self.xlim:
            ax.set_xlim(self.xlim)
        if self.ylim:
            ax.set_ylim(self.ylim)
        # tick stuff
        ax.tick_params(axis='both', which='major', labelsize=18, length=6)  # Adjust label size and tick length
        if self.xticks:
            ax.set_xticks(self.xticks)
        if self.yticks:
            ax.set_yticks(self.yticks)
        ax.set_xticklabels(ax.get_xticks(), fontdict=tick_font)
        ax.set_yticklabels(ax.get_yticks(), fontdict=tick_font)
        ax.xaxis.set_major_formatter(StrMethodFormatter(
                    '{x:.' + str(self.xprecision) + 'f}'))
        ax.yaxis.set_major_formatter(StrMethodFormatter(
                    '{x:.' + str(self.yprecision) + 'f}'))
        plt.xlabel(self.xlabel, fontdict=font)
        plt.ylabel(self.ylabel, fontdict=font)
        plt.gcf().set_facecolor('white')
        fig.suptitle(self.title, fontproperties=suptitle_font, y=0.93)
        plt.legend(loc=self.legendloc, prop=legend_font)
        if self.saveflag:
            plt.savefig(self.savename + '.png')
            # plt.savefig(self.title + '.pdf')
        plt.show()

# Example usage
# scatter = ScatterPlot(x, y, 
#                       xlabel='X', 
#                       ylabel='Y', 
#                       title='Scatter Plot Example',
#                       saveflag=True, savename='pi_error_analysis')
# scatter.plot()

