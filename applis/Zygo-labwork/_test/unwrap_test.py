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
    [1.75 2.   3.5  4.25]

    """
    # Calculer la moyenne en ignorant les NaN
    result = np.nanmean(np.stack((arr_1, arr_2)), axis=0)
    return result

def remove_nan_groups(arr: np.array) -> np.array:
    """
    Remove consecutive NaN groups from an array, assuming non-NaN values are connected.

    Parameters
    ----------
    arr : np.ndarray
        Input array with NaN values.

    Returns
    -------
    np.ndarray
        Array with consecutive NaN groups removed.

    Notes
    -----
    This function removes consecutive groups of NaNs from the input array.
    It assumes that non-NaN values in the input array are connected.

    See Also
    --------
    np.finfo(float).eps : The smallest representable positive number for the 'float' data type.

    Examples
    --------
    >>> arr = np.array([1.0, np.nan, np.nan, 1.0, 2.0, np.nan, 3.0, np.nan, np.nan, np.nan, 3.0])
    >>> clean_arr = remove_nan_groups(arr)
    >>> print(clean_arr)
    [ 1.  1.  1.  1.  2. nan  3.  3.  3.  3.  3.]
    """
    nan_indices = np.where(np.isnan(arr))[0]  # Find the indices of NaN values
    nan_count = len(nan_indices)

    if nan_count != 0:
        # Calculate the differences between NaN indices
        nan_diff = np.append(np.diff(nan_indices), 0)

        # Create a matrix of indices for consecutive NaNs groups
        nan_groups = np.zeros((0, 2), dtype=int)
        j = 0
        while j < nan_count:
            nan_groups = np.append(
                nan_groups, [[nan_indices[j], nan_indices[j]]], axis=0)
            while j < nan_count and nan_diff[j] == 1:
                j += 1
                # Update the ending index of the group
                nan_groups[-1, 1] = nan_indices[j]
            j += 1

        # Pre-process groups of NaNs at the beginning or end
        if nan_groups[0, 0] == 0:
            nan_groups = nan_groups[1:, :]
        if len(nan_groups) != 0 and nan_groups[-1, 1] == len(arr):
            nan_groups = nan_groups[:-1, :]

        # Remove groups of NaNs intersecting a value plateau
        for group in nan_groups:
            if abs(arr[group[0] - 1] - arr[group[1] + 1]) < np.finfo(float).eps * 2000:
                arr[group[0]:group[1] + 1] = arr[group[0] - 1]
    return arr


def unwrap2D_columns_first(arr: np.array, period: Optional[float] = 6.2831853072, axis: Optional[int] = 0) -> np.array:
    """
    Unwrap phase values of each column independently.

    Parameters
    ----------
    arr : np.ndarray
        Input array containing phase values.

    period : float, optional
        The period of the phase (default is 2π).
        This defines the maximum allowed jump between values before unwrapping occurs.

    axis : int, optional
        The axis along which to unwrap the phase (default is 0).

    Returns
    -------
    np.ndarray
        Unwrapped phase values of each column.

    Notes
    -----
    This function unwraps phase values of each column independently.

    It first unwraps the phase values of each column independently using unwrap1D.
    Then, it identifies a main row with the least NaN values and a secondary row within a certain range from the main row.
    After that, it unwraps the phase values of the main and secondary rows and calculates the jumps.
    Next, it removes consecutive NaN groups from the calculated jumps and adjusts them using merge_with_offset.
    Finally, it applies the adjusted jumps to the entire array to unwrap the phase values.

    See Also
    --------
    unwrap1D : Unwrap phase values of a 1D array while handling NaNs.

    Examples
    --------
    >>> arr = np.array([[0.5, 1.5, np.nan, 2.5],
    ...                 [1.0, np.nan, 2.0, 3.0],
    ...                 [1.5, 2.5, 3.5, 4.5]])
    >>> unwrapped_arr = unwrap2D_columns_first(arr)
    >>> print(unwrapped_arr)
    [[0.5 1.5 nan 2.5]
     [1.  nan 2.  3. ]
     [1.5 2.5 3.5 4.5]]

    """

    # Unwrap phase values of each column independently
    unwrapped_arr = unwrap1D(arr, period=period, axis=axis)

    # Get the number of rows in the array
    number_rows = arr.shape[0]

    # Count the NaN values in each row after unwrapping
    nan_counts_per_row = np.sum(np.isnan(unwrapped_arr), axis=1)

    # Find the row index with the least NaN values (main row)
    min_nan_row_index = np.argmin(nan_counts_per_row)
    main_row = unwrapped_arr[min_nan_row_index]

    # Define the range of rows to consider for finding the secondary row
    coefficient = 0.025
    delta_rows = np.ceil(number_rows * coefficient).astype(int)
    slice_rejected_rows = slice(max(
        1, min_nan_row_index - delta_rows), min(number_rows, min_nan_row_index + delta_rows))
    rejected_rows_indices = ~np.isin(
        np.arange(1, number_rows + 1), slice_rejected_rows)

    # Find the row index with the least NaN values within the defined range (secondary row)
    min_nan_row_index_excluded = np.argmin(
        nan_counts_per_row[rejected_rows_indices])
    if min_nan_row_index_excluded >= min(slice_rejected_rows.stop, number_rows):
        min_nan_row_index_excluded -= len(
            range(min(slice_rejected_rows.stop, number_rows), min_nan_row_index_excluded))
    secondary_row = unwrapped_arr[min_nan_row_index_excluded]

    # Unwrap phase values of the main and secondary rows
    unwrapped_main_row, unwrapped_secondary_row = unwrap1D(
        main_row, period=period), unwrap1D(secondary_row, period=period)

    # Calculate the jumps between unwrapped values of the main and secondary rows
    main_row_jumps, secondary_row_jumps = unwrapped_main_row - \
        main_row, unwrapped_secondary_row - secondary_row

    # Remove consecutive NaN groups from the jumps and adjust them
    clean_main_row_jumps = remove_nan_groups(
        merge_with_offset(main_row_jumps, secondary_row_jumps))
    clean_main_row_jumps_matrix = np.tile(
        clean_main_row_jumps, (number_rows, 1))

    # Apply the adjusted jumps to the entire array to unwrap the phase values
    return unwrapped_arr + clean_main_row_jumps_matrix


def unwrap2D(arr: np.array, period: float = 2 * np.pi) -> Tuple[np.array, bool, list[float]]:
    """
    Perform 2D phase unwrapping on a given 2D array.

    The function unwraps the phase of a 2D array by first unwrapping along the columns and then along the rows.
    It combines these results and handles discrepancies to produce a final unwrapped array.

    Parameters
    ----------
    arr : np.array
        The input 2D array containing phase values.
    period : float, optional
        The period of the phase, by default 2π.

    Returns
    -------
    Tuple[np.array, bool, list[float]]:
        unwrapped_arr : np.array
            The resulting 2D array after phase unwrapping.
        serious_problem : bool
            A boolean flag indicating whether a serious problem was detected during the unwrapping process.
        info : list of float
            A list containing the following three elements:
            - standard_deviation_offset (float): The standard deviation of the phase offset values.
            - initial_offset_error (float): The initial offset error before filtering problematic points.
            - problematic_points_ratio (float): The ratio of problematic points to the total number of points.

    Notes
    -----
    - The function first unwraps the phase along the columns using `unwrap2D_columns_first`.
    - Then it unwraps the phase along the rows by transposing the array, applying `unwrap2D_columns_first`, and transposing back.
    - It identifies common points that are not NaN in both unwrapped arrays and calculates the phase offset.
    - Problematic points are identified where the phase difference exceeds a small threshold.
    - If the proportion of problematic points or the standard deviation of the phase offset is too high, a serious problem is flagged, and divergent points are removed.
    - Otherwise, the unwrapped arrays are combined, resolving discrepancies based on column and row derivatives.

    See Also
    --------
    unwrap1D : Unwrap phase values of a 1D array while handling NaNs.
    unwrap2D_columns_first : Unwrap phase values of each column independently.
    merge_with_offset : Merge two arrays while handling NaN values and calculating offsets.
    remove_nan_groups : Remove consecutive NaN groups from an array, assuming non-NaN values are connected.

    Examples
    --------
    >>> arr = np.array([[0, np.pi/2, np.pi], [np.pi, 3*np.pi/2, 2*np.pi]])
    >>> unwrapped_arr, serious_problem, info = unwrap2D(arr)
    >>> unwrapped_arr
    array([[0.        , 1.57079633, 3.14159265],
           [3.14159265, 4.71238898, 6.28318531]])
    >>> serious_problem
    False
    >>> info
    [0.0, 0.0, 0.0]
    """
    unwrapped_arr_cols_first = unwrap2D_columns_first(
        arr)  # Unwrap 2D by columns
    unwrapped_arr_lines_first = unwrap2D_columns_first(
        arr.T).T  # Unwrap 2D by rows

    nan_unwrapped_arr_by_cols = np.isnan(unwrapped_arr_cols_first)
    nan_unwrapped_arr_by_lines = np.isnan(unwrapped_arr_lines_first)

    common_points = (~nan_unwrapped_arr_by_cols) & (~nan_unwrapped_arr_by_lines)  # Non-NaN common points

    phase_offset_values = unwrapped_arr_cols_first[common_points] - unwrapped_arr_lines_first[common_points]
    mean_phase_offset = np.mean(phase_offset_values)
    wrapped_phase_offset = period * np.round(mean_phase_offset / period)
    initial_offset_error = np.abs(wrapped_phase_offset - mean_phase_offset)

    # Identify problematic points
    problematic_points = np.abs(
        unwrapped_arr_cols_first - unwrapped_arr_lines_first - wrapped_phase_offset) > period / 10000

    # Recalculate phase offset without problematic points
    filtered_phase_offset_values = unwrapped_arr_cols_first[common_points & (~problematic_points)] - unwrapped_arr_lines_first[common_points & (~problematic_points)]
    if len(filtered_phase_offset_values) >= 2:
        mean_phase_offset = np.mean(filtered_phase_offset_values)
        wrapped_phase_offset = period * np.round(mean_phase_offset / period)
        standard_deviation_offset = np.std(filtered_phase_offset_values)
    else:
        standard_deviation_offset = np.inf

    num_problematic_points = np.sum(problematic_points)
    num_common_points = np.sum(common_points)
    problematic_points_ratio = num_problematic_points / num_common_points

    info = [standard_deviation_offset,
            initial_offset_error, problematic_points_ratio]

    max_problematic_points_ratio = 0.05

    if problematic_points_ratio > max_problematic_points_ratio or standard_deviation_offset > period / 10000:  # Serious problem
        serious_problem = True
        # Remove non-common and divergent points
        unwrapped_arr = unwrapped_arr_cols_first.copy()
        unwrapped_arr[~common_points] = np.nan
        unwrapped_arr[problematic_points] = np.nan
    else:
        serious_problem = False
        # Combine data
        unwrapped_arr = unwrapped_arr_cols_first.copy()
        unwrapped_arr[nan_unwrapped_arr_by_cols & (~nan_unwrapped_arr_by_lines)] = unwrapped_arr_lines_first[nan_unwrapped_arr_by_cols & (
            ~nan_unwrapped_arr_by_lines)] + wrapped_phase_offset

        # Handle divergent common points
        problematic_indices_i, problematic_indices_j = np.nonzero(
            problematic_points)
        num_rows, num_columns = arr.shape

        for idx in range(num_problematic_points):
            if problematic_indices_i[idx] in [0, num_rows - 1] or problematic_indices_j[idx] in [0, num_columns - 1]:
                # At the edge of the image
                unwrapped_arr[problematic_indices_i[idx],
                              problematic_indices_j[idx]] = np.nan
            else:
                # Calculate derivatives
                col_diffs = np.diff(
                    unwrapped_arr_cols_first[problematic_indices_i[idx], problematic_indices_j[idx] + np.array([-1, 0, 1])])
                col_diffs = col_diffs[~np.isnan(col_diffs)]
                line_diffs = np.diff(
                    unwrapped_arr_lines_first[problematic_indices_i[idx] + np.array([-1, 0, 1]), problematic_indices_j[idx]])
                line_diffs = line_diffs[~np.isnan(line_diffs)]

                # Check derivatives for issues
                col_problem = np.any(np.abs(col_diffs) >
                                     period) or len(col_diffs) == 0
                line_problem = np.any(
                    np.abs(line_diffs) > period) or len(line_diffs) == 0

                if col_problem and line_problem:
                    # Problem in both directions
                    unwrapped_arr[problematic_indices_i[idx],
                                  problematic_indices_j[idx]] = np.nan
                elif col_problem:
                    # Problem in unwrapped_arr_cols_first
                    unwrapped_arr[problematic_indices_i[idx], problematic_indices_j[idx]
                                  ] = unwrapped_arr_lines_first[problematic_indices_i[idx], problematic_indices_j[idx]] + wrapped_phase_offset
                elif line_problem:
                    # Problem in unwrapped_arr_lines_first
                    pass
                else:
                    # Divergence without column or row problem
                    unwrapped_arr[problematic_indices_i[idx],
                                  problematic_indices_j[idx]] = np.nan

    return unwrapped_arr, serious_problem, info

if __name__ == '__main__':

    arr1 = np.array([1.0, 2.0, np.nan, 4.0])
    arr2 = np.array([2.5, np.nan, 3.5, 4.5])
    merged_arr = merge_with_offset(arr1, arr2)
    print(merged_arr)

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

    # unwrap2D test
    # -------------
    import matplotlib.pyplot as plt
    from mpl_toolkits import mplot3d

    y = np.linspace(-10, 10, 500)
    _x, _y = np.meshgrid(x,y)

    real_z = 40-(_x**2+_y**2)
    z_wrapped = (real_z % np.pi) - np.pi/2
    #z_unwrapped = unwrap1D(unwrap1D(z_wrapped, axis=0, period=np.pi), axis=1, period=np.pi)
    z_unwrapped = unwrap2D(z_wrapped, period=np.pi)[0]

    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.plot_surface(_x, _y, real_z)
    ax.plot_surface(_x, _y, z_wrapped)
    ax.plot_surface(_x, _y, z_unwrapped)
    plt.show()

