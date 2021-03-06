import copy
import numpy as np
from Point import Point

class Plot(object):

    ID = None
    corners = None
    ab_line = None
    end_points = None
    width = None
    ignored = False
    force_direction = False

    work = True
    hitch_height = 0.0
    working_speed = 1.0
    pto_rpm = 0

    _source = None

    _corners_are_sorted = False

    _longside_idx = None
    _shortside_idx = None

    _HITCH_HEIGHT_MIN = 0.16
    _HITCH_HEIGHT_MAX = 0.6
    _WORKING_SPEED_MIN = 0.1
    _WORKING_SPEED_MAX = 6.0
    _PTO_RPM_MIN = 0
    _PTO_RPM_MAX = 1000

    def __init__(self, corners=None, ab_line=None, end_points=None, width=None, ID=None, ignored=False, force_direction=False, work=True, hitch_height=0.6, working_speed=1.0, pto_rpm=0):
        if corners is not None:
            self.corners = copy.deepcopy(corners)
            self._source = 'corners'
            self._sort_corners()
            plot_side_warning_flag = self._corners_to_ab_line(corners)

        elif ab_line is not None and end_points is not None:
            # Estimate corners
            self._source = 'ab_line'
            self.ab_line = copy.deepcopy(ab_line)
            self.end_points = copy.deepcopy(end_points)
            self.width = copy.deepcopy(width)
            if (width is not None):
                #TODO: Estimate corners
                pass
        else:
            pass
        
        self.ID = copy.deepcopy(ID)
        self.force_direction = copy.deepcopy(force_direction)
        self.ignored = copy.deepcopy(ignored)
        self.work = copy.deepcopy(work)
        self.hitch_height = copy.deepcopy(hitch_height)
        self.working_speed = copy.deepcopy(working_speed)
        self.pto_rpm = copy.deepcopy(pto_rpm)

    def __str__(self):
        str_out = ''
        str_out += 'Plot ID   : ' + str(self.ID) + '\n'
        str_out += 'Corners   : ' + str(len(self.corners)) + '\n'
        for p in self.corners:
            str_out += '   ' + str(p)
        str_out += 'AB-line   : ' + str(len(self.ab_line)) + '\n'
        for p in self.ab_line:
            str_out += '   ' + str(p)
        str_out += 'End points: ' + str(len(self.end_points)) + '\n'
        for p in self.end_points:
            str_out += '   ' + str(p)
        
        return str_out

    def _sort_corners(self):
        plot_side_warning_flag = False

        # Step 1: Sort the points in anti-clockwise order
        x = np.asarray([p.east for p in self.corners])
        y = np.asarray([p.north for p in self.corners])
        theta = np.arctan2(y-np.mean(y),x-np.mean(x))
        theta, corners = (list(t) for t in zip(*sorted(zip(theta, self.corners))))

        # Step 2: Determine short side and long side of plot
        d01 = corners[0].distance(corners[1])
        d12 = corners[1].distance(corners[2])
        d23 = corners[2].distance(corners[3])
        d30 = corners[3].distance(corners[0])

        if (np.abs(d01-d23) > 0.05) or (np.abs(d12 - d30) > 0.05):
            plot_side_warning_flag = True

        if (d01 + d23 > d12 + d30):
            longside_idx = [0, 1, 2, 3]
            shortside_idx = [1, 2, 3, 0]
        else:
            longside_idx = [1, 2, 3, 0]
            shortside_idx = [0, 1, 2, 3]

        self.corners = corners
        self._longside_idx = longside_idx
        self._shortside_idx = shortside_idx

        return plot_side_warning_flag

    def _corners_to_ab_line(self, corners=None):
        # Assume ab-line same direction as longest sides of the plot
        plot_side_warning_flag = False

        # Step 1: Sort the corners (and determine short- & longside idx)
        plot_side_warning_flag = self._sort_corners()

        # Step 3: Determine ab-line from long side (and short sides)
        A = Point.midpoint([self.corners[self._shortside_idx[0]], self.corners[self._shortside_idx[1]]], method='utm')
        B = Point.midpoint([self.corners[self._shortside_idx[2]], self.corners[self._shortside_idx[3]]], method='utm')
        ab_line = [A, B]

        # Step 4: Determine point_1 and point_2 from ab-line intersection with short sides of plot
        # Set point_1 to A, and point_2 to B
        point_1 = copy.deepcopy(A)
        point_2 = copy.deepcopy(B)
        end_points = [point_1, point_2]

        # Step 5: Calculate width of plot
        # width = self.corners[self._shortside_idx[0]].distance(self.corners[self._shortside_idx[1]])

        self.ab_line = copy.deepcopy(ab_line)
        self.end_points = copy.deepcopy(end_points)

        return plot_side_warning_flag

    def _rectify_plot(self):
        # Turn approximately rectangular plot into a rectangular plot
        pass

    def draw(self, ax, show_ID=True, show_plot=True, show_AB_line=True, show_AB=True, show_end_points=True, hide_idle_plots=True, idle_alpha=0.3):

        if (self.corners is not None) and (show_plot):
            east = [point.east for point in self.corners]
            north = [point.north for point in self.corners]
            ax.fill(east, north, edgecolor=[0,0,0],hatch='///', alpha=0.3*idle_alpha)

        if (self.ab_line is not None) and (show_AB_line):
            east = [point.east for point in self.ab_line]
            north = [point.north for point in self.ab_line]
            ax.plot(east, north, marker='', linestyle='solid', color='grey', linewidth=2, alpha=idle_alpha)
            if show_AB:
                ax.text(east[0], north[0], 'A', horizontalalignment='center', verticalalignment='center', alpha=idle_alpha)
                ax.text(east[1], north[1], 'B', horizontalalignment='center', verticalalignment='center', alpha=idle_alpha)

        if (self.end_points is not None) and (show_end_points):
            east = [point.east for point in self.end_points]
            north = [point.north for point in self.end_points]
            ax.plot(east, north, marker='.', linestyle='dashed', color='black', linewidth=1, alpha=idle_alpha)
            
        if (show_ID and self.ID is not None):
            if (self.corners is not None):
                point = Point.midpoint(self.corners)
            else:
                point = Point.midpoint(self.end_points)
            ax.text(point.east, point.north, str(self.ID), horizontalalignment='center', verticalalignment='center', alpha=idle_alpha, picker=100)
# End of class Plot