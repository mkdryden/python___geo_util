
import math

import gtk
import numpy as np
from geo_util import CartesianSpace


class TestCartesianSpace(gtk.Window):
    '''
    ____________________________________________________________
    |__Title bar________________________________________________|
    | _________________________________________________________ |
    ||                                                         ||
    || Area A                                                  ||
    ||       ____________________________________________      ||
    ||      | Area B                                     |     ||
    ||      |                                            |     ||
    ||      |                                            |     ||
    ||      |                                            |     ||
    ||<---->|____________________________________________|     ||
    || padding                                                 ||
    ||                                                         ||
    ||                                                         ||
    ||_________________________________________________________||
    | _________________________________________________________ |
    ||                                                         ||
    || Area C                                                  ||
    ||                                                         ||
    ||                                                         ||
    ||                                                         ||
    ||_________________________________________________________||
    |___________________________________________________________|

    Create two GTK DrawingArea widgets: one for Area A and one for Area C.
    Track mouse cursor movement in Area A, while mapping the cursor position
    relative to Area B to to Area C.

    To do this, create CartesianSpace instances for Area B and Area C.  The
    normalized_coords and translate_normalized methods can then be used to
    translate coordinates from the Area B coordinate space to Area C.
    '''
    def __init__(self, dims=(640, 480)):
        super(TestCartesianSpace, self).__init__()
        self._a_dims = np.array(dims)
        self._c_dims = self._a_dims / 2
        self.vbox = gtk.VBox()
        self.area_a = gtk.DrawingArea()
        self.area_c = gtk.DrawingArea()
        self.vbox.pack_start(self.area_a, expand=False, fill=False, padding=10)
        self.vbox.pack_start(self.area_c, expand=False, fill=False, padding=10)
        self.connect('destroy', gtk.main_quit)

        self.area_a.set_events(gtk.gdk.POINTER_MOTION_MASK)
        self.area_a.connect('motion_notify_event', self.draw_cursor)
        self.area_a.connect('expose-event', self.expose_a)
        self.area_c.connect('expose-event', self.expose_c)

        self.area_a.set_size_request(*self._a_dims.astype(int))
        self.area_c.set_size_request(*self._c_dims.astype(int))
        self.vbox.show_all()
        self.add(self.vbox)
        self.cursor_position_a = None
        self.cursor_position_c = None
        self.padding = 0.1

        self.space_a = None
        self.space_b = None
        self.space_c = None

    def draw_cursor(self, area, event):
        self.cursor_position_a = (event.x, event.y)
        self.area_a.queue_draw()
        if self.space_b:
            normalized_coords = self.space_b.normalized_coords(event.x, event.y)
            self.cursor_position_c = self.space_c.translate_normalized(
                    *normalized_coords)
            self.area_c.queue_draw()

    def draw_b(self, cairo_context):
        x, y, w, h = self.area_a.get_allocation()
        padding = (self.padding * w, self.padding * h)
        self.space_b = CartesianSpace(w - 2 * padding[0], h - 2 * padding[1],
                                      offset=(padding[0], padding[1]))
        cairo_context.rectangle(*(self.space_b._offset + self.space_b.dims))
        cairo_context.stroke()

    def expose_c(self, widget, event):
        x, y, w, h = self.area_a.get_allocation()
        self.space_a = CartesianSpace(w, h)
        x, y, w, h = self.area_c.get_allocation()
        self.space_c = CartesianSpace(w, h)

        cr = self.area_c.window.cairo_create()

        cr.set_source_rgb(0.1, 0.1, 0.8)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cr.set_line_width(9)
        cr.set_source_rgb(0.7, 0.2, 0.0)

        if self.cursor_position_c is not None:
            cursor_dims = (40, 40)
            cr.move_to(self.cursor_position_c[0] - cursor_dims[0] / 2,
                       self.cursor_position_c[1])
            cr.line_to(self.cursor_position_c[0] + cursor_dims[0] / 2,
                       self.cursor_position_c[1])
            cr.move_to(self.cursor_position_c[0],
                       self.cursor_position_c[1] - cursor_dims[1] / 2)
            cr.line_to(self.cursor_position_c[0],
                       self.cursor_position_c[1] + cursor_dims[1] / 2)
            cr.stroke()

    def expose_a(self, widget, event):
        cr = self.area_a.window.cairo_create()
        x, y, w, h = widget.get_allocation()

        cr.set_source_rgb(0.1, 0.1, 0.1)
        cr.rectangle(0, 0, w, h)
        cr.fill()

        cr.set_line_width(9)
        cr.set_source_rgb(0.7, 0.2, 0.0)

        self.draw_b(cr)

        cr.save()
        cr.translate(w/2, h/2)

        cr.move_to(0, 0)
        cr.arc(0, 0, 50, 0, 2*math.pi)
        cr.stroke_preserve()

        cr.set_source_rgb(0.3, 0.4, 0.6)
        cr.fill()
        cr.restore()

        if self.cursor_position_a is not None:
            cursor_dims = (40, 40)
            cr.move_to(self.cursor_position_a[0] - cursor_dims[0] / 2,
                       self.cursor_position_a[1])
            cr.line_to(self.cursor_position_a[0] + cursor_dims[0] / 2,
                       self.cursor_position_a[1])
            cr.move_to(self.cursor_position_a[0],
                       self.cursor_position_a[1] - cursor_dims[1] / 2)
            cr.line_to(self.cursor_position_a[0],
                       self.cursor_position_a[1] + cursor_dims[1] / 2)
            cr.stroke()



if __name__ == '__main__':
    t = TestCartesianSpace()
    t.show_all()
    gtk.main()
