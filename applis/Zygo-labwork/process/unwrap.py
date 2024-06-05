# -*- coding: utf-8 -*-
"""*unwrap.py* file.

This file contains functions to unwrap the phase.
Note: These functions are direct translations from Matlab functions; some adjustments may be necessary.

This file is attached to a 1st year of engineer training labwork in photonics.

.. note:: LEnsE - Institut d'Optique - version 1.0

.. moduleauthor:: Dorian Mendes (Promo 2026) <dorian.mendes@institutoptique.fr>

"""

import numpy as np
from typing import Tuple, Optional
from scipy.interpolate import interp1d


def unwrap1D(arr: np.array, period: Optional[float] = 6.2831853072, axis: Optional[int] = 0) -> np.array:
    """
    Unwrap a 1D phase array along a specified axis, ignoring NaNs.

    Parameters
    ----------
    arr : np.ndarray
        Input array containing phase values to be unwrapped.

    period : float, optional
        The period of the phase (default is 2π).
        This defines the maximum allowed jump between values before unwrapping occurs.

    axis : int, optional
        The axis along which to unwrap the phase (default is 0).

    Returns
    -------
    np.ndarray
        The unwrapped phase array of the same shape as `arr`.

    Notes
    -----
    This function is similar to numpy's unwrap but with additional support for handling NaNs.
    The function unrolls the phase by changing absolute jumps greater than the specified period to their 2π complement.

    See Also
    --------
    np.unwrap : Numpy's function for unwrapping phase arrays.

    Examples
    --------
    >>> import numpy as np
    >>> x = np.linspace(0, 50)
    >>> x_wrapped = x % (2 * np.pi)
    >>> x_unwrapped = unwrap1D(x_wrapped)
    >>> print(np.allclose(x, x_unwrapped))
    True

    """

    assert isinstance(axis, int) and (axis >= 0), f"[unwrap1D] 'axis' must be an integer (here, 'axis'={axis})."
    assert axis < len(arr.shape), f"[unwrap1D] The array has only {len(arr.shape)} dimensions, so 'axis' must be between 0 and {len(arr.shape)-1} (here, 'axis'={axis})."

    # Permute the specified axis to be the first axis
    arr = np.moveaxis(arr, axis, 0)
    arr_copy = np.copy(arr)

    # Reshape the array to 2D for easier handling
    original_shape = arr_copy.shape
    arr_copy = arr_copy.reshape(arr_copy.shape[0], -1)

    # Iterate over the second dimension and beyond
    for i in range(arr_copy.shape[1]):
        column = arr_copy[:, i]

        # Identify non-NaN indices
        valid_idx = ~np.isnan(column)
        valid_data = column[valid_idx]

        # Compute differences and identify jumps
        diffs = np.diff(valid_data, prepend=valid_data[0])
        jumps = -np.round(diffs / period) * period

        # Apply jumps
        arr_copy[valid_idx, i] = valid_data + np.cumsum(jumps)

    # Restore the original shape and axis order
    arr_copy = arr_copy.reshape(original_shape)
    arr_unwrapped = np.moveaxis(arr_copy, 0, axis)

    return arr_unwrapped


def merge_with_offset(arr_1: np.array, arr_2: np.array) -> np.array:
    """
    Merge two arrays while handling NaN values and calculating offsets.

    Parameters
    ----------
    arr_1 : np.ndarray
        First input array.

    arr_2 : np.ndarray
        Second input array.

    Returns
    -------
    np.ndarray
        Merged array with NaN values handled and offsets calculated.

    Notes
    -----
    This function merges two arrays while handling NaN values and calculating offsets to adjust for differences between the arrays.
    When both arrays have NaN values at the same position, indicating missing or undefined values, the resulting merged array will also have a NaN at that position.

    Examples
    --------
    >>> arr1 = np.array([1.0, 2.0, np.nan, 4.0])
    >>> arr2 = np.array([2.5, np.nan, 3.5, 4.5])
    >>> merged_arr = merge_with_offset(arr1, arr2)
    >>> print(merged_arr)
    [1.  2. 2.5 4.]

    """
    nan_mask_arr_1 = np.isnan(arr_1)
    nan_mask_arr_2 = np.isnan(arr_2)
    not_nan_mask = (~nan_mask_arr_1) & (~nan_mask_arr_2)

    merger = arr_1.copy()
    if not_nan_mask.any():
        offset = np.mean(arr_2[not_nan_mask] - arr_1[not_nan_mask])
        merger[nan_mask_arr_1 & (~nan_mask_arr_2)] = arr_2[nan_mask_arr_1 & (
            ~nan_mask_arr_2)] - offset
    return merger


def interpolate_nan_2d(arr):
    """
    Interpolate NaN values in a 2D numpy array along each row and column.

    Parameters
    ----------
    arr : np.ndarray
        Input 2D array with NaN values.

    Returns
    -------
    np.ndarray
        Array with NaN values interpolated along each row and column.

    Notes
    -----
    This function interpolates NaN values in a 2D numpy array along each row and column using linear interpolation.

    Examples
    --------
    >>> arr = np.array([[1.0, np.nan, 2.0],
    ...                 [np.nan, 3.0, np.nan],
    ...                 [4.0, 5.0, np.nan]])
    >>> interpolated_arr = interpolate_nan_2d(arr)
    >>> print(interpolated_arr)
    [[1.  1.5 2. ]
     [2.5 3.  2.5]
     [4.  5.  5. ]]

    """
    # Interpoler sur les lignes
    interpolated_arr = interpolate_rows(arr)
    
    # Interpoler sur les colonnes
    interpolated_arr = interpolate_rows(interpolated_arr.T).T
    
    return interpolated_arr

def interpolate_rows(arr):
    """
    Interpolate NaN values in a 2D numpy array along each row.

    Parameters
    ----------
    arr : np.ndarray
        Input 2D array with NaN values.

    Returns
    -------
    np.ndarray
        Array with NaN values interpolated along each row.

    """
    interpolated_arr = np.copy(arr)
    
    for i in range(arr.shape[0]):
        not_nan_mask = ~np.isnan(arr[i])
        if np.sum(not_nan_mask) > 1:
            indices = np.arange(arr.shape[1])
            f = interp1d(indices[not_nan_mask], arr[i, not_nan_mask], kind='linear', fill_value='extrapolate')
            interpolated_arr[i] = f(indices)
    
    return interpolated_arr

def unwrap2D(arr: np.array, period: float = 2 * np.pi) -> Tuple[np.array, bool, list[float]]:
    """
    Perform 2D phase unwrapping on a given 2D array.

    The function unwraps the phase of a 2D array by first unwrapping along the columns and then along the rows.
    It combines these results and handles discrepancies to produce a final unwrapped array.
    """
    arr_unwrapped_axis_0 = unwrap1D(arr, period, axis=0)
    arr_unwrapped_axis_1 = unwrap1D(arr, period, axis=1)

    arr_unwrapped = merge_with_offset(arr_unwrapped_axis_0, arr_unwrapped_axis_1)
    arr_unwrapped = interpolate_nan_2d(arr_unwrapped)
    return arr_unwrapped

if __name__ == '__main__':
    import matplotlib.pyplot as plt
    from mpl_toolkits import mplot3d

    # unwrap1D test
    # -------------
    x = np.linspace(-10, 10, 500)
    real_y = 40 - x**2
    y_wrapped = (real_y % np.pi) - np.pi/2
    y_unwrapped = unwrap1D(y_wrapped, period=np.pi)

    plt.figure()
    plt.plot(x, real_y, label='Real')
    plt.plot(x, y_wrapped, label='Wrapped')
    plt.plot(x, y_unwrapped, label='Unwrapped')
    plt.plot(x, y_unwrapped-real_y, ':', label='Constant difference')
    plt.legend()
    plt.show()

    # Test interpolation NaN
    # ----------------------
    # Exemple d'utilisation
    arr = np.array([[1.0, np.nan, 2.0],
                    [np.nan, 3.0, np.nan],
                    [4.0, 5.0, np.nan]])
    interpolated_arr = interpolate_nan_2d(arr)
    print(interpolated_arr)

    # unwrap2D test
    # -------------
    import matplotlib.pyplot as plt
    from mpl_toolkits import mplot3d

    y = np.linspace(-10, 10, 500)
    _x, _y = np.meshgrid(x,y)

    real_z = 40-(_x**2+_y**2)
    z_wrapped = (real_z % np.pi) - np.pi/2
    z_unwrapped = unwrap2D(z_wrapped)
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(_x, _y, real_z)
    ax.plot_surface(_x, _y, z_wrapped)
    ax.plot_surface(_x, _y, z_unwrapped)
    plt.show()

    plt.figure()
    plt.plot(x, z_unwrapped[0, :])
    plt.show()

