"""
Copyright 2012 Christian Fobel

This file is part of geo_util.

geo_util is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

geo_util is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with geo_util.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import division

import numpy as np

first_dim = 0
second_dim = 1


class CartesianSpace(object):
    def __init__(self, width, height, offset=None):
        self.dims = (width, height)
        self._scale = 1.
        if offset is None:
            self._offset = (0, 0)
        else:
            self._offset = offset
        if width >= height:
            self.largest_dim = first_dim
        else:
            self.largest_dim = second_dim

    @property
    def height(self):
        return self.dims[second_dim]

    @property
    def width(self):
        return self.dims[first_dim]

    @property
    def scale(self):
        return self._scale

    def translate_normalized(self, x, y):
        '''
        Return x, y coordinates in space domain (with offset applied).

        Arguments
        ---------

         - `x`: Numeric or array-like coordinate(s) in domain [0, 1].
         - `y`: Numeric or array-like coordinate(s) in domain [0, 1].
        '''
        return np.array([x, y]).T * self.dims + self._offset

    def normalized_coords(self, x, y):
        '''
        Return x, y coordinates normalized to within range [0, 1].

        Arguments
        ---------

         - `x`: Numeric or array-like coordinate(s) in domain
           [`self._offset[0]`, `self._offset[0] + self.width`].
         - `y`: Numeric or array-like coordinate(s) in domain
           [`self._offset[1]`, `self._offset[1] + self.height`].
        '''
        return np.array([(x - self._offset[first_dim]) / self.width,
                         (y - self._offset[second_dim]) / self.height])

    def update_scale(self, scale_dims):
        dim = self.largest_dim
        self._scale = scale_dims[dim] / self.dims[dim]


def scale_to_fit_a_in_b(a_shape, b_shape):
    '''
    Return scale factor (scalar float) to fit `a_shape` into `b_shape` while
    maintaining aspect ratio.

    Arguments
    ---------

     - `a_shape`: A `pandas.Series`-like object with a `width` and a `height`.
     - `b_shape`: A `pandas.Series`-like object with a `width` and a `height`.
    '''
    # Normalize the shapes to allow comparison.
    a_shape_normal = a_shape / a_shape.max()
    b_shape_normal = b_shape / b_shape.max()

    if a_shape_normal.width > b_shape_normal.width:
        a_shape_normal *= b_shape_normal.width / a_shape_normal.width

    if a_shape_normal.height > b_shape_normal.height:
        a_shape_normal *= b_shape_normal.height / a_shape_normal.height

    return a_shape_normal.max() * b_shape.max() / a_shape.max()


def fit_points_in_bounding_box(df_points, bounding_box, padding_factor=0):
    '''
    Return dataframe with `x`, `y` columns scaled to fit points from
    `df_points` to fill `bounding_box` while maintaining aspect ratio.

    Arguments
    ---------

     - `df_points`: A `pandas.DataFrame`-like object with `x`, `y` columns,
       containing one row per point.
     - `bounding_box`: A `pandas.Series`-like object with a `width` and a
       `height`.
     - `padding_factor`: Fraction of padding to add around points.
    '''
    df_scaled_points = df_points.copy()
    offset, padded_scale = fit_points_in_bounding_box_params(df_points,
                                                             bounding_box,
                                                             padding_factor)
    df_scaled_points[['x', 'y']] *= padded_scale
    df_scaled_points[['x', 'y']] += offset
    return df_scaled_points


def fit_points_in_bounding_box_params(df_points, bounding_box,
                                      padding_factor=0):
    '''
    Return offset and scale factor to scale `x`, `y` columns of `df_points` to
    fill `bounding_box` while maintaining aspect ratio.

    Arguments
    ---------

     - `df_points`: A `pandas.DataFrame`-like object with `x`, `y` columns,
       containing one row per point.
     - `bounding_box`: A `pandas.Series`-like object with a `width` and a
       `height`.
     - `padding_factor`: Fraction of padding to add around points.
    '''
    import pandas as pd

    width, height = df_points[['x', 'y']].max()

    points_bbox = pd.Series([width, height], index=['width', 'height'])
    fill_scale = 1 - 2 * padding_factor
    assert(fill_scale > 0)

    scale = scale_to_fit_a_in_b(points_bbox, bounding_box)

    padded_scale = scale * fill_scale
    offset = .5 * (bounding_box - points_bbox * padded_scale)
    offset.index = ['x', 'y']
    return offset, padded_scale
