from matplotlib.pyplot import *
from numpy import *
from matplotlib import ticker

def julian_day():
    r = axes().get_xaxis().get_view_interval()
    r = r[1] - r[0]
    axes().get_xaxis().set_major_locator(ticker.IndexLocator(168*clip(r/168/9, 1, 5), 0))
    axes().get_xaxis().set_major_formatter(ticker.FuncFormatter(lambda hour, pos: str(int(hour/24))))
    xlabel('Julian Day')
