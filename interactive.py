import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button

fig, ax = plt.subplots()
plt.subplots_adjust(bottom=0.2)

freqs = np.arange(2, 20, 5)
t = np.arange(0.0, 1.0, 0.001)

test = {
    't1': {
        't1-1': None,
        't1-2': None,
    },
    't2': None,
    't3': None,
    't4': {
        't4-1': {
            't4-1-1': None,
            't4-1-2': None,
            't4-1-3': {
                't4-1-1-1': None
            }
        }
    }
}


def hideAll(bdata):
    if 'children' in bdata:
        for c in bdata['children']:
            hideAll(bdata['children'][c])
    bdata['button'].ax.set_visible(False)
    bdata['button'].color = 'grey'
    bdata['button'].hovercolor = 'lightgrey'
    bdata['state'] = False
    if 'ax' in bdata:
        bdata['ax'].set_visible(False)

def makeUI(data, bdata = {}, level=0, npp=1, r=0):
    nprops = len(list(data.keys()))*npp

    for i, prop in enumerate(data):

        bdata[prop] = {}
        if data[prop] == None:
            bdata[prop]['data'] = data[prop] = np.sin((i+1)*npp*np.pi*freqs[level]*t)    
            bdata[prop]['ax'], = ax.plot(t)
            bdata[prop]['ax'].set_visible(False)
        else:
            bdata[prop]['children'] = {}
            makeUI(data[prop], bdata[prop]['children'], level+1, nprops, r + i/nprops)
            
        bdata[prop]['state'] = False

        def onclick(bdata):
            def wrapped(_):
                bdata['state'] = not bdata['state']
                if bdata['state']:
                    if 'children' in bdata:
                        for b in bdata['children']:
                            bdata['children'][b]['button'].ax.set_visible(True)
                            bdata['children'][b]['state'] = False
                    else:
                        bdata['button'].color = 'green'
                        bdata['button'].hovercolor = 'lightgreen'
                        bdata['ax'].set_ydata(bdata['data'])
                        bdata['ax'].set_visible(True)
                        plt.draw()
                else:
                    bdata['button'].color = 'grey'
                    bdata['button'].hovercolor = 'lightgrey'
                    if 'children' in bdata:
                        for c in bdata['children']:
                            hideAll(bdata['children'][c])
                    if 'ax' in bdata:
                        bdata['ax'].set_visible(False)
                plt.draw()

            return wrapped
        height = 30
        axs = plt.axes([r + i/nprops, level/height, 1/nprops, 1/height])
        bdata[prop]['button'] = Button(axs, prop, color='grey', hovercolor='lightgrey')
        bdata[prop]['button'].on_clicked(onclick(bdata[prop]))
        
        if level != 0:
            bdata[prop]['button'].ax.set_visible(False)
        plt.draw()
        


makeUI(test)
plt.show()