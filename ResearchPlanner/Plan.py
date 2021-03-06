import csv
import json
import matplotlib.pyplot as plt
from Point import Point
from Plot import Plot
from Field import Field
#from openpyxl import load_workbook # For readin xls(x)-files

class Plan(object):

    plots = None
    field = None

    def __init__(self):
        pass

    def read_plot_json(self, filename):
        # # Loads, sets and returns a research plan from a json-file.
        # fob = open(filename,'r')
        # plan = json.load(fob)
        # self.plan = plan
        # return self.plan
        pass

    def read_plot_csv(self, filename, is_utm=False, is_latlon=False, utm_zone=None, work=True, hitch_height=0.6, working_speed=1.0, pto_rpm=0):
        # Assumes, that csv-file has no header and 4 columns: latitude, longitude, altitude, and id.
        # If is_utm or is_latlon is set to True, it will try to reinforce that interpretation. Otherwise, it will try to guess it based on the size of the numbers.

        plot_id = []

        P = []
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if (is_utm):
                    P.append(Point(north=float(row[0]), east=float(row[1]), altitude=float(row[2])))
                elif (is_latlon):
                    P.append(Point(latitude=float(row[0]), longitude=float(row[1]), altitude=float(row[2])))
                else:
                    P.append(Point(x=float(row[0]), y=float(row[1]), altitude=float(row[2])))
                plot_id.append(str(row[3]))

        plot_ids_unique = list(set(plot_id))

        plots = []
        for this_id in plot_ids_unique:
            corner_points = [p for p, i in zip(P,plot_id) if (i == this_id)]
            assert(len(corner_points) == 4)
            
            plot = Plot(corners=corner_points, ID=this_id, work=work, hitch_height=hitch_height, working_speed=working_speed, pto_rpm=pto_rpm)
            plots.append(plot)

        self.plots = plots

    # def from_plot_xls(self, filename, sheetname=None, sheetIdx=0):
    #     wb = load_workbook(filename) # https://openpyxl.readthedocs.io/en/stable/usage.html#read-an-existing-workbook
    #     if (sheetname is None):
    #         sheetnames = wb.sheetnames
    #         sheetname = sheetnames[sheetIdx]
    #     print(sheetname)
    #     sheet = wb[sheetname]

    #     # Read header
    #     sheet.row

    #     # Read body
        
    #     for row in sheet.rows:
    #         print(row[0].value)
    #     pass

    def read_field_csv(self, filename, is_utm=False, is_latlon=False):

        P = []
        with open(filename, newline='') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if (is_utm):
                    P.append(Point(north=float(row[0]), east=float(row[1]), altitude=float(row[2])))
                elif (is_latlon):
                    P.append(Point(latitude=float(row[0]), longitude=float(row[1]), altitude=float(row[2])))
                else:
                    P.append(Point(x=float(row[0]), y=float(row[1]), altitude=float(row[2])))

        self.field = Field(points=P)

    def export_plots(self, filename):

        rows = []

        for plot in self.plots:
            A = {'latitude': float(plot.ab_line[0].latitude), 'longitude': float(plot.ab_line[0].longitude)}
            B = {'latitude': float(plot.ab_line[1].latitude), 'longitude': float(plot.ab_line[1].longitude)}
            ab_line = {'A': A, 'B': B}

            point_1 = {'latitude': float(plot.end_points[0].latitude), 'longitude': float(plot.end_points[0].longitude)}
            point_2 = {'latitude': float(plot.end_points[1].latitude), 'longitude': float(plot.end_points[1].longitude)}

            plot_dict = {'id': plot.ID,
                         'point_1': point_1,
                         'point_2': point_2,
                         'work': 0 if plot.work is False else 1,
                         'hitch_height': plot.hitch_height,
                         'working_speed': plot.working_speed,
                         'pto_rpm': plot.pto_rpm}
            row = {'ab_line': ab_line,
                    'plots': [plot_dict],
                    'ignored': 0 if plot.ignored is False else 1,
                    'force_direction': 0 if plot.force_direction is False else 1}
            rows.append(row)
        robotti_plan = {'rows': rows}
        
        fob = open(filename, 'w')
        json.dump(robotti_plan, fob, indent=3)

    def export_field(self, filename):

        field_dict = [{'latitude': float(point.latitude), 'longitude': float(point.longitude)} for point in self.field.points]

        robotti_field = {'field': field_dict}

        fob = open(filename, 'w')
        json.dump(robotti_field, fob, indent=3)

    def to_json(self, filename):
        # fob = open(filename, 'w')
        # json.dump(self.plan, fob, indent=3)
        pass

    def draw(self, ax=None, show_ID=True, show_plot=True, show_AB_line=True, show_AB=True, show_end_points=True, hide_idle_plots=True, show_field=True):
        if (ax is None):
            ax = plt.gca()

        if (self.field is not None and show_field):
            self.field.draw(ax=ax)
        
        if (self.plots is not None):
            for plot in self.plots:

                if (hide_idle_plots and (not plot.work or plot.ignored)):
                    idle_alpha = 0.3
                else:
                    idle_alpha = 1.0

                plot.draw(ax=ax, show_ID=show_ID, show_plot=show_plot, show_AB_line=show_AB_line, show_AB=show_AB, show_end_points=show_end_points, idle_alpha=idle_alpha)

        ax.axis('equal')
        ax.set_xlabel('East, m')
        ax.set_ylabel('North, m')

        return ax
