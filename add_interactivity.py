""" Module to add interactivity to matplotlib legends"""
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import TextBox
coords = None
legn = None
mlist = []

class add_interactivity_class():
    def __init__(self, legend=None, lines=None, fig=None, lines2=None, ncol=1, loc=0, ax=None, nodrag=False, legsize=12):
        self.ncol = ncol
        self.loc = loc
        self.nodrag = nodrag
        self.legsize = legsize
        if ax is None:
            ax = plt.gca()
        self.ax = ax
        self.legend, self.lines, self.linedic = self._setup(legend, lines, lines2, ncol, loc, ax, nodrag, legsize)
        if fig is None:
            self.fig = ax.figure
        else:
            self.fig = fig
        _ = self.fig.canvas.toolbar.actions()[7].triggered.connect(self.renew)
        _ = self.fig.canvas.mpl_connect('pick_event', self.onpick)
        if not "update" in self.fig.canvas.toolbar.actions()[-1].text():
            _ = self.fig.canvas.toolbar.addAction("update")
        _ = self.fig.canvas.toolbar.actions()[-1].triggered.connect(self.renew)

    def _setup(self, legend, lines, lines2, ncol, loc, ax, nodrag, legsize):
        if lines is None:
            lines = ax.get_lines()
            all_indices = []
            for iidd, line in enumerate(lines):
                if len(line.get_data()[0]) == 0 and not line.get_visible():
                    all_indices.append(iidd)
            for in_iidd in all_indices[::-1]:
                _ = lines.pop(in_iidd)
        for line in lines:
            if line.get_label()[0] == "_":
                line.set_label(line.get_label()[1:])
        if legend is None:
            legend = ax.legend(loc=loc, ncol=ncol, prop={"size": legsize})
        if not nodrag:
            if int(matplotlib.__version__[0]) >= 3:
                legend.set_draggable(True)
            else:
                legend.draggable(True)
        linedic = {}
        for legline, line, text in zip(legend.get_lines(), lines, legend.get_texts()):
            if legline.get_linestyle() == "None":
                legline.set_linewidth(0)
                legline.set_linestyle("-")
            linedic[legline] = (line, text)
            if not legline.get_picker():
                if float(".".join(matplotlib.__version__.split(".")[:2])) < 3.3:
                    legline.set_picker(5)
                else:
                    legline.set_picker(True)
                    legline.set_pickradius(5)
        if lines2 is not None:
            for line2, line in zip(lines2, lines):
                linedic[line2] = (line, " ")
                if float(".".join(matplotlib.__version__.split(".")[:2])) < 3.3:
                    legline.set_picker(5)
                else:
                    legline.set_picker(True)
                    legline.set_pickradius(5)
        return legend, lines, linedic

    def renew(self, event=None):
        self.legend, self.lines, self.linedic = self._setup(None, None, None, self.ncol, self.loc, self.ax, self.nodrag, self.legsize)
        self.fig.canvas.draw()

    def onpick(self, event):
        """
        function to be called on click (left, middle, right) on an artist
        """
        fig = event.artist.figure
        ax = event.artist.axes
        legend = ax.get_legend()
        leg = event.artist
        # print(event, event.mouseevent.button, leg, leg.get_label())
        try:
            (plotline, mtext) = self.linedic[leg]
            isline = True
        except:
            isline = False
            plotline = None
            mtext = None
        if event.mouseevent.button == 3 and isline:
            maxordernow = np.nanmax(
                np.array([self.linedic[ll][0].get_zorder() for ll in self.linedic]))
            plotline.set_zorder(maxordernow + 1)
            legend.set_zorder(maxordernow + 2)
        elif event.mouseevent.button == 1 and isline:
            if event.mouseevent.key is None:
                vis = not plotline.get_visible()
                plotline.set_visible(vis)
                if vis:
                    leg.set_alpha(1.0)
                    plotline.set_alpha(1.0)
                    leg._legmarker.set_alpha(1.0)  # for markers
                    mtext.set_visible(True)
                else:
                    mtext.set_visible(False)
                    leg.set_alpha(0.1)
                    plotline.set_alpha(0.0)  # for markers
                    leg._legmarker.set_alpha(0.1)  # for markers
                    leg.get_label()
            else:
                lw = leg.get_linewidth()
                ms = leg._legmarker.get_markersize()
                if event.mouseevent.key == "up":
                    if lw > 0:
                        leg.set_linewidth(lw + 1)
                        plotline.set_linewidth(lw + 1)
                    leg._legmarker.set_markersize(ms + 1)
                    plotline.set_markersize(ms + 1)
                elif event.mouseevent.key == "down":
                    if lw > 1:
                        leg.set_linewidth(lw - 1)
                        plotline.set_linewidth(lw - 1)
                    if ms > 1:
                        leg._legmarker.set_markersize(ms - 1)
                        plotline.set_markersize(ms - 1)
                elif event.mouseevent.key in ["g", "k", "b", "c", "m", "r", "y", "w"]:
                    leg.set_color(event.mouseevent.key)
                    leg._legmarker.set_color(event.mouseevent.key)
                    plotline.set_color(event.mouseevent.key)
                elif event.mouseevent.key in ["x", "0", "1", "2", "3", "*", "|","<",
                                              ">",'.', "+", "v", "8", "s","X", "d",
                                              "D", "_", "o", "^"]:
                    leg._legmarker.set_marker(event.mouseevent.key)
                    plotline.set_marker(event.mouseevent.key)
                elif event.mouseevent.key == "l":
                    if lw == 0:
                        if plotline.get_linestyle() == "None":
                            plotline.set_linestyle('-')
                        leg.set_linewidth(lw + 1)
                        plotline.set_linewidth(lw+1)
                    else:
                        leg.set_linewidth(0)
                        plotline.set_linewidth(0)
        elif event.mouseevent.button == 2 and isline:
            print("Type the new label in the box")
            def submit(stext):
                print("you typed", stext)
                plotline.set_label(stext)
                mtext.set_text(stext)
                leg.set_label(stext)
                ax2.remove()
                fig.canvas.draw()
                text_box.disconnect_events()
            ax2 = plt.axes([0.12, 0.05, 0.78, 0.075])
            text_box = TextBox(ax2, 'new leg ', initial="")
            text_box.on_submit(submit)
        elif event.mouseevent.key == "left" and not isline and event.mouseevent.button == 1:
            #if leg.parent == ax:
                if legend.texts[0].get_fontsize() > 1:
                    if float(".".join(matplotlib.__version__.split(".")[:2])) < 3.3:
                        legend.texts[0].set_fontsize(legend.texts[0].get_fontsize()-1)
                    else:
                        for i in range(len(legend.texts)):
                            legend.texts[i].set_fontsize(legend.texts[i].get_fontsize()-1)
        elif event.mouseevent.key == "right" and not isline and event.mouseevent.button == 1:
            #if leg.parent == ax:
                if float(".".join(matplotlib.__version__.split(".")[:2])) < 3.3:
                    legend.texts[0].set_fontsize(legend.texts[0].get_fontsize()+1)
                else:
                    for i in range(len(legend.texts)):
                        legend.texts[i].set_fontsize(legend.texts[i].get_fontsize()+1)
        fig.canvas.draw()

def add_interactivity(*args, **kwargs):
    global mlist
    element = add_interactivity_class(*args, **kwargs)
    mlist.append(element)

def add_ai_toall():
    '''
    add interactive legend to all axes in all open figures
    '''
    for mfignum in plt.get_fignums():
        mfig = plt.figure(mfignum)
        for ax in mfig.axes:
            add_interactivity(fig=mfig, ncol=1, loc=0, ax=ax, nodrag=False, legsize=10)
    return

def cp_one(ax, mfig):
    def update_self(event):
        #mfig = event.canvas.figure
        #print(ax,mfig)
        update_components(ax, mfig)
    def onpick(event):
        global coords, legn, artist, ax
        artist = event.artist
        if event.mouseevent.button == 3 and type(artist) != matplotlib.legend.Legend:
            try:
                leglines = event.artist.axes.get_legend().get_lines()
            except AttributeError:
                leglines = []
            if not artist in leglines:
                coords = artist.get_data()
                legn = artist.get_label()
                print("copied ",legn)
            else:
                pass
        elif event.mouseevent.dblclick and type(artist) != matplotlib.legend.Legend:
            try:
                ax = artist.axes
                # print("axes figure: ", ax, artist)
                artist.remove()
                #add_interactivity(ax=ax, legsize=legsize)
                ax.figure.canvas.draw()
            except NotImplementedError:
                pass
            except ValueError as verr:
                pass
                #print(verr)
        else:
            pass
    def onclick(event):
        global coords, legn
        if event.button == 2:
            if legn is not None:
                # print("pasted ", legn)
                # print("coordrange x: ", np.nanmin(coords[0]), np.nanmax(coords[0]))
                # print("coordrange y: ", np.nanmin(coords[1]), np.nanmax(coords[1]))
                ax = event.inaxes
                ax.plot(coords[0], coords[1], label=legn)
                update_components(ax, mfig)
                # add_interactivity(ax=ax, legsize=legsize)
                ax.figure.canvas.draw()
                legn = None
    def update_components(ax, mfig):
        for lin in ax.lines:
            if not lin.get_picker():
                if float(".".join(matplotlib.__version__.split(".")[:2])) < 3.3:
                    lin.set_picker(5)
                else:
                    lin.set_picker(True)
                    lin.set_pickradius(5)
            else:
                pass
                #print(lin, " already has picker")
    d = mfig.canvas.mpl_connect("pick_event", onpick)
    f = mfig.canvas.mpl_connect('button_press_event', onclick)
    update_components(ax, mfig)
    mfig.canvas.toolbar.actions()[7].triggered.connect(update_self)
    mfig.canvas.mpl_connect('draw_event', update_self)
    return d, f

def enable_copy_paste(figs=None):
    '''
    Function to call after plots are created to be able to copy paste line plots

    A pick event on lines is activated and will copy the line data if 'c' is
    pressed when the line is selected.

    Clicking in any axes that was already present before this function had been
    called, and clicking again while pressing 'v' will add the currently copied
    plot
    '''
    print("to copy a line, click the right mouse button on a line")
    print("to paste, press the middle mouse button in an axes")
    print("to delete a line, double click on it")
    mlist = []
    if figs is None:
        figl = plt.get_fignums()
        figs = []
        for fi in figl:
            figs.append(plt.figure(fi))
    for mfig in figs:
        axs = mfig.axes
        for ax in axs:
            a,b = cp_one(ax, mfig)
            mlist.append(a)
            mlist.append(b)
    return mlist

def clear_all():
    global mlist
    mlist = []

def interactive():
    '''
    add add_interactivity and enable_copy_paste on all axes
    '''
    enable_copy_paste()
    add_ai_toall()

def main(notext=False):
    fig, ax = plt.subplots(1,2)
    ax[0].plot(np.arange(10), lw=6)
    ax[0].plot(np.arange(10) ** 1.5, 'o', ms=12)
    ax[0].plot(np.sin(np.arange(10)) * 5, lw=6)
    if not notext:
        print(
        "This is a simple plot to which interactivity has been added:\n",
        " \n",
        "* with any button pressed on the legend outside a legend line, you can drag and drop the legend\n",
        "* press the left mouse button on top of a legend line to turn it off/ on\n",
        "* down/ up arrows holding while pressing left button, de-/increases marker size and line width\n",
        "* press the right mouse button on top of a legend line (not label) to bring it to the front\n",
        "* press the middle mouse button on top of a legend line to open a textbox\n",
        "  in this text box, write the new label for that line, then press enter\n",
        "* press left/ right arrows while pressing left mouse button to in/de crease text size\n",
        "    New features: \n",
        "* a right mouse click on a line in the left plot copies the data.\n",
        "* click middle button in the right plot to paste it.\n"
        "* double click a line to remove it from the plot")
    mlist = add_ai_toall()
    #add_interactivity(ax=ax[1])
    enable_copy_paste()
    plt.show()


if __name__ == "__main__":
    main()
