
#    mycharts.py  
from reportlab.graphics.shapes import Drawing, String
from reportlab.graphics.charts.lineplots import LinePlot, GridLinePlot
from reportlab.graphics.charts.lineplots import ScatterPlot
from reportlab.lib import colors
from reportlab.graphics.charts.legends import Legend, LineLegend
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.widgets.markers import makeMarker


class MyLineChartDrawing(Drawing):
    def __init__(self, width=600, height=400, *args, **kw):
        apply(Drawing.__init__,(self,width,height)+args,kw)
        self.add(LinePlot(), name='chart')

        self.add(String(200,180,''), name='title')

        #set any shapes, fonts, colors you want here.  We'll just
        #set a title font and place the chart within the drawing.
        #pick colors for all the lines, do as many as you need
        self.chart.x = 20
        self.chart.y = 30
        self.chart.width = self.width - 100
        self.chart.height = self.height - 75
        self.chart.lines[0].strokeColor = colors.blue
        self.chart.lines[1].strokeColor = colors.red

    
        self.chart.fillColor = colors.white
        self.title.fontName = 'Times-Roman'
        self.title.fontSize = 18
        #self.chart.data = [((0, 50), (100,100), (200,200), (250,210), (300,300), (400,500))]
        self.chart.xValueAxis.labels.fontSize = 12
        self.chart.xValueAxis.forceZero = 0
        self.chart.xValueAxis.gridEnd =  self.width - self.width*0.60 
        self.chart.yValueAxis.gridEnd =  self.height - self.height*0.2
        self.chart.xValueAxis.tickDown = 3
        self.chart.xValueAxis.visibleGrid = 1
        self.chart.yValueAxis.visibleGrid = 1
        self.chart.yValueAxis.tickLeft = 3
        self.chart.yValueAxis.labels.fontName = 'Times-Roman'
        self.chart.yValueAxis.labels.fontSize = 12
        self.title.x = self.width/2
        self.title.y = 0
        self.title.textAnchor ='middle'
        self.add(LineLegend(),name='Legend')
        self.Legend.fontName = 'Times-Roman'
        self.Legend.fontSize = 12
        self.Legend.x = self.width-10
        self.Legend.y = 70
        self.Legend.dxTextSpace = 5
        self.Legend.dy = 5
        self.Legend.dx = 5
        self.Legend.deltay = 5
        self.Legend.alignment ='right'
        self.Legend.colorNamePairs  = [(colors.blue, 'Tiempo Estimado')]
        self.add(Label(),name='XLabel')
        self.XLabel.fontName = 'Times-Roman'
        self.XLabel.fontSize = 12
        self.XLabel.x = 100
        self.XLabel.y = 5
        self.XLabel.textAnchor ='middle'
        self.XLabel.height = 20
        self.XLabel._text = "que tal"
        self.add(Label(),name='YLabel')
        self.YLabel.fontName = 'Times-Roman'
        self.YLabel.fontSize = 12
        self.YLabel.x = -10
        self.YLabel.y = 100
        self.YLabel.angle = 90
        self.YLabel.textAnchor ='middle'
        self.YLabel._text = "Hola"
        self.chart.yValueAxis.forceZero = 1
        self.chart.xValueAxis.forceZero = 1
        self.chart.lines[0].symbol = makeMarker('FilledCircle')
        self.chart.lines[1].symbol = makeMarker('Circle')
        
       
        
       
        
     
        
        