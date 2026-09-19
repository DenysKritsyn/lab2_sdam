import tkinter as tk
import collections
import matplotlib.pyplot as plt
import tkinter.messagebox as messagebox
import math
from itertools import accumulate
from tkinter import messagebox
from parameters.average import getAverage
from parameters.median import getMedian
from parameters.mode import getMode, NoModeError
from parameters.scope import getScope
from parameters.math_expectation import getMathExpectation
from parameters.dispersion import getDispersion
from parameters.standard_deviation import getStandardDeviation
from parameters.modified_dispersion import getModifiedDispersion
from parameters.modified_standard_deviation import getModifiedStandardDeviation
from parameters.variation import getVariation
from parameters.initial_statistical_moment import getInitialStatisticalMoment
from parameters.central_statistical_moment import getCentralStatisticalMoment
from parameters.asymmetry import getAsymmetry
from parameters.excess import getExcess


# Variant 15
default_values = [
    [0.36, 0.38, 0.38, 0.37, 0.40, 0.38, 0.36],
    [0.52, 0.19, 0.11, 0.00, 0.57, 0.42, 0.25],
    [0.29, 0.32, 0.34, 0.34, 0.49, 0.52, 0.81]
]

matrix_vars = []

###########################################
# Matrix for entering representing sample
###########################################

def init_matrix():
    for row_i in range(len(default_values)):
        row_vars = []
        for column_j in range(len(default_values[row_i])):
            row_vars.append(tk.StringVar(value=str(default_values[row_i][column_j])))
        matrix_vars.append(row_vars)

def redraw_matrix():
    for widget in matrix_frame.winfo_children():
        widget.destroy()
        
    for row_i, row_vars in enumerate(matrix_vars):
        for column_j, var in enumerate(row_vars):
            ent = tk.Entry(matrix_frame, textvariable=var, width=7,  relief=tk.SOLID, borderwidth=1)
            ent.grid(row=row_i, column=column_j, padx=2, pady=2)

def add_row():
    if not matrix_vars:
        matrix_vars.append([tk.StringVar(value="")])
    else:
        matrix_vars.append([tk.StringVar(value="") for _ in range(len(matrix_vars[0]))])
    redraw_matrix()

def delete_row():
    if len(matrix_vars) > 1:
        matrix_vars.pop()
        redraw_matrix()

def add_column():
    for row in matrix_vars:
        row.append(tk.StringVar(value=""))
    redraw_matrix()

def delete_column():
    if matrix_vars and len(matrix_vars[0]) > 1:
        for row in matrix_vars:
            row.pop()
        redraw_matrix()

# Get matrix data as a single dimention list
def get_matrix_data():
    flat_list = []
    for row in matrix_vars:
        for var in row:
            val = var.get().strip().replace(',', '.')
            if val:
                flat_list.append(float(val))
    return flat_list

#########################################################
# Calculate visualization table of result interval series
#########################################################

def calculate_intervals(num_series):
    """
    Calculates the interval statistical series from a given numeric sample.
    Returns:
        list of tuples: [( (start, end), z_i, m_i ), ...]
    """
    N = len(num_series)
    
    # Handle edge cases for empty or uniform datasets
    if N == 0:
        return []
    if N == 1 or min(num_series) == max(num_series):
        x_val = num_series[0] if N > 0 else 0
        return [((x_val, x_val), x_val, N)]
    
    # Sturges' formula: k = 1 + 3.322 * lg(N)
    k = max(1, round(1 + 3.322 * math.log10(N)))
    
    x_min, x_max = min(num_series), max(num_series)
    h = (x_max - x_min) / k  # Step (width) of each interval
    
    intervals = []
    
    for i in range(k):
        # Calculate interval boundaries
        start = x_min + i * h
        # Ensure the last interval exactly hits the max value
        end = x_max if i == k - 1 else x_min + (i + 1) * h
        
        #  Calculate the middle of interval (z_i)
        z_i = (start + end) / 2
        
        # Count frequencies (m_i) for the current interval
        if i == k - 1:
            # Last interval includes the right boundary: [start, end]
            m_i = sum(1 for x in num_series if start <= x <= end)
        else:
            # Standard intervals exclude the right boundary: [start, end)
            m_i = sum(1 for x in num_series if start <= x < end)
            
        intervals.append(((start, end), z_i, m_i))
        
    return intervals

# Helper function to create a table cell
def create_cell(text_val, row, col, is_header=False):
    font_weight = "bold" if is_header else "normal"
    lbl = tk.Label(
        table_frame, 
        text=text_val, 
        bg="white", 
        fg="black", 
        font=("Arial", 10, font_weight), 
        relief=tk.SOLID, 
        borderwidth=1, 
        padx=5, 
        pady=5
    )
    lbl.grid(row=row, column=col, sticky="nsew")

def draw_interval_table(table_frame, intervals=None):

    # Clear table
    for widget in table_frame.winfo_children():
        widget.destroy()
          
    # Draw row headers
    headers = ["Intervals", "z_i", "m_i"]
    for row_idx, header in enumerate(headers):
        create_cell(header, row_idx, 0, is_header=True)
        
    # Draw placeholder table if no data is provided
    if not intervals:
        for col_idx in range(1, 7):
            for row_idx in range(3):
                create_cell("null", row_idx, col_idx)
        
        # Configure columns to stretch evenly
        for c in range(7):
            table_frame.grid_columnconfigure(c, weight=1)
        return
        
    # Draw data if provided
    for col_idx, (interval, z_i, m_i) in enumerate(intervals, start=1):
        start, end = interval
        
        # Format interval string (last interval has an inclusive right bracket)
        bracket = "]" if col_idx == len(intervals) else ")"
        interval_str = f"[{start:.3f}; {end:.3f}{bracket}"
        
        # Format midpoint to max 4 decimal
        z_i_str = f"{z_i:.4f}".rstrip('0').rstrip('.')
        
        # Fill the column with data
        create_cell(interval_str, 0, col_idx)
        create_cell(z_i_str, 1, col_idx)
        create_cell(str(m_i), 2, col_idx)
        
    # Configure columns to stretch evenly
    for c in range(len(intervals) + 1):
        table_frame.grid_columnconfigure(c, weight=1)

# Show parameters
def estimate_parameters():
    try:
        num_series = get_matrix_data()
        
        if not num_series:
            messagebox.showwarning("Warning", "Enter at least one number.")
            return

        # Visualize result interval series
        intervals = calculate_intervals(num_series)
        draw_interval_table(table_frame, intervals)

        avg = getAverage(num_series)
        med = getMedian(num_series)
        scope = getScope(num_series)
        m_exp = getMathExpectation(num_series)
        disp = getDispersion(num_series)
        mod_disp = getModifiedDispersion(num_series)
        mod_std_dev = getModifiedStandardDeviation(num_series)
        init_moment_2 = getInitialStatisticalMoment(2, num_series)
        cent_moment_2 = getCentralStatisticalMoment(2, num_series)
        std_dev = getStandardDeviation(num_series)
        
        try:
            mod = getMode(num_series)
        except NoModeError:
            mod = "No Mode (all numbers are unique)"

        if std_dev == 0:
            var = "Error (Math Expectation = 0)"
            asym = "Error (Standard Deviation = 0)"
            exc = "Error (Standard Deviation = 0)"
        else:
            var = round(getVariation(num_series), 4)
            asym = round(getAsymmetry(num_series), 4)
            exc = round(getExcess(num_series), 4)

        result_text.config(state=tk.NORMAL)
        result_text.delete(1.0, tk.END)
        
        results = [
            f"Average: {avg}",
            f"Median: {med}",
            f"Mode: {mod}",
            f"Scope (Range): {scope}",
            f"Math Expectation: {m_exp}",
            f"Dispersion: {disp}",
            f"Standard Deviation: {std_dev}",
            f"Modified Dispersion: {mod_disp}",
            f"Modified Standard Deviation: {mod_std_dev}",
            f"Variation (%): {var}",
            f"Initial Statistical Moment (k=2): {init_moment_2}",
            f"Central Statistical Moment (k=2): {cent_moment_2}",
            f"Asymmetry: {asym}",
            f"Excess: {exc}",
        ]
        
        result_text.insert(tk.END, "\n\n".join(results))
        result_text.config(state=tk.DISABLED)

    except ValueError:
        messagebox.showerror("Error", "Incorrect data. Allowed only integers.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Modify graphic, making him 'step alike'
def make_step_tuple(base_tuple):
    idx, X, F_x, color, title, ylabel = base_tuple
    x_horiz, y_horiz = [], []
    x_vert, y_vert = [], []
    offset = (X[-1] - X[0]) * 0.1 if len(X) > 1 else 1.0
    x_horiz.extend([X[0] - offset, X[0], float('nan')])
    y_horiz.extend([0, 0, float('nan')])
    prev_f_x = 0
    for i in range(len(X)):
        current_x = X[i]
        current_f_x = F_x[i]
        x_vert.extend([current_x, current_x, float('nan')])
        y_vert.extend([prev_f_x, current_f_x, float('nan')])
        next_x = X[i+1] if i < len(X) - 1 else X[-1] + offset
        x_horiz.extend([current_x, next_x, float('nan')])
        y_horiz.extend([current_f_x, current_f_x, float('nan')])
        prev_f_x = current_f_x
    return (idx, (x_horiz, x_vert), (y_horiz, y_vert), color, title, ylabel)

# Draw graphs
def plot_curves():
    try:
        num_series = get_matrix_data()
        if not num_series:
            messagebox.showwarning("Warning", "Enter data.")
            return
            
        N = len(num_series)
        
        # Estimate general characteristics
        counts = collections.Counter(num_series)
        X = sorted(counts.keys())
        n = [counts[x_i] for x_i in X]
        m = list(accumulate(n))
        F_x = [m_i / N for m_i in m]
        
        # Set graphs table (3 rows)
        fig, axs = plt.subplots(3, 1, figsize=(15, 18))
        fig.canvas.manager.set_window_title('Statistical Curves (Discrete)')
        axs = axs.flatten()
        
        plot_configs = [
            (0, X, m, 'red', 'Cumulative Frequency Curve', 'Cumulative Frequency (m_i)'),
            (1, X, F_x, 'orange', 'Cumulative Relative Freq. Curve', 'Cumulative Rel. Frequency (m_i / N)'),
            make_step_tuple((2, X, F_x, 'purple', 'Empirical Distribution Function, F(x)', 'F(x)'))
        ]
        
        for idx, x_data, y_data, color, title, ylabel in plot_configs:
            ax = axs[idx]
            if idx == 2:
                x_h, x_v = x_data
                y_h, y_v = y_data
                ax.plot(x_h, y_h, linestyle='-', color=color)
                ax.plot(x_v, y_v, linestyle='--', color=color, alpha=0.5)
                
                # Filled and hollow dots for ECDF
                ax.plot(X, F_x, 'o', color=color, alpha=0.5)
                hollow_y = [0] + F_x[:-1]
                ax.plot(X, hollow_y, 'o', markerfacecolor='white', markeredgecolor=color, color=color, alpha=0.5)
            else:
                ax.plot(x_data, y_data, marker='o', linestyle='-', color=color)
                
            ax.set_title(title)
            ax.set_xlabel('Variants (X)')
            ax.set_ylabel(ylabel)
            ax.grid(True, linestyle='--', alpha=0.5)
            
            # Show exact coordinate values on axes
            ax.set_xticks(X)
            ax.set_xticklabels([str(round(x, 2)) for x in X], fontsize=8)
            
            if idx == 2:
                y_ticks = sorted(list(set([0] + F_x)))
            else:
                y_ticks = sorted(list(set(y_data)))
            ax.set_yticks(y_ticks)
            ax.set_yticklabels([str(round(y, 3)) for y in y_ticks], fontsize=8)

        plt.tight_layout(pad=3.0, h_pad=8.0)
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while plotting: {str(e)}")

def plot_histograms():
    try:
        num_series = get_matrix_data()
        if not num_series:
            messagebox.showwarning("Warning", "Enter data.")
            return
            
        N = len(num_series)
        intervals = calculate_intervals(num_series)
        if not intervals:
            return
            
        starts = [iv[0][0] for iv in intervals]
        h = intervals[0][0][1] - intervals[0][0][0]
        boundaries = starts + [intervals[-1][0][1]]
        
        m_i = [iv[2] for iv in intervals]
        p_i_hist = [val / N for val in m_i]
        
        # Set graphs table (2 rows, 1 column)
        fig, axs = plt.subplots(2, 1, figsize=(15, 12))
        fig.canvas.manager.set_window_title('Statistical Histograms (Interval)')
        axs = axs.flatten()

        # Absolute Frequency Histogram
        ax0 = axs[0]
        ax0.bar(starts, m_i, width=h, align='edge', color='blue', edgecolor='white', alpha=0.7)
        ax0.set_title('Absolute Frequency Histogram')
        ax0.set_xlabel('Interval Boundaries')
        ax0.set_ylabel('Absolute Frequency (m_i)')
        ax0.set_xticks(boundaries)
        ax0.set_xticklabels([f"{b:.3f}" for b in boundaries], fontsize=9)
        unique_m_i = sorted(list(set(m_i)))
        ax0.set_yticks(unique_m_i)
        ax0.set_yticklabels([str(y) for y in unique_m_i], fontsize=9)
        ax0.grid(True, linestyle='--', alpha=0.5)
        
        # Relative Frequency Histogram
        ax1 = axs[1]
        ax1.bar(starts, p_i_hist, width=h, align='edge', color='green', edgecolor='white', alpha=0.7)
        ax1.set_title('Relative Frequency Histogram')
        ax1.set_xlabel('Interval Boundaries')
        ax1.set_ylabel('Relative Frequency (p_i*)')
        ax1.set_xticks(boundaries)
        ax1.set_xticklabels([f"{b:.3f}" for b in boundaries], fontsize=9)
        unique_p_i = sorted(list(set(p_i_hist)))
        ax1.set_yticks(unique_p_i)
        ax1.set_yticklabels([str(round(y, 3)) for y in unique_p_i], fontsize=9)
        ax1.grid(True, linestyle='--', alpha=0.5)
        
        plt.tight_layout(pad=3.0, h_pad=8.0)
        plt.show()
        
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while plotting: {str(e)}")

# Creating window
root = tk.Tk()
root.title("Statistical Parameters Estimator (Lab 2)")
root.geometry("850x850")
root.configure(bg="#f5f5f5")

tk.Label(root, text="Discrete Series Characteristics Calculation", font=("Arial", 14, "bold"), bg="#f5f5f5", fg="black").pack(pady=(20, 10))

# Fill table
matrix_frame = tk.Frame(root, bg="#f5f5f5")
matrix_frame.pack(pady=10)

init_matrix()
redraw_matrix()

# Fill table buttons
ctrl_frame = tk.Frame(root, bg="#f5f5f5")
ctrl_frame.pack(fill=tk.X, pady=10, padx=20)

col_frame = tk.LabelFrame(ctrl_frame, text="Column operations", bg="#f5f5f5", fg="black", font=("Arial", 10))
col_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

tk.Button(col_frame, text="Add column", bg="#f0f0f0", fg="black", font=("Arial", 10), relief=tk.SOLID, borderwidth=1, command=add_column).pack(fill=tk.X, padx=5, pady=2)
tk.Button(col_frame, text="Delete column", bg="#f0f0f0", fg="black", font=("Arial", 10), relief=tk.SOLID, borderwidth=1, command=delete_column).pack(fill=tk.X, padx=5, pady=2)

row_frame = tk.LabelFrame(ctrl_frame, text="Row operations", bg="#f5f5f5", fg="black", font=("Arial", 10))
row_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5)

tk.Button(row_frame, text="Add row", bg="#f0f0f0", fg="black", font=("Arial", 10), relief=tk.SOLID, borderwidth=1, command=add_row).pack(fill=tk.X, padx=5, pady=2)
tk.Button(row_frame, text="Delete row", bg="#f0f0f0", fg="black", font=("Arial", 10), relief=tk.SOLID, borderwidth=1, command=delete_row).pack(fill=tk.X, padx=5, pady=2)

# Estimation buttons
calc_frame = tk.Frame(root, bg="#f5f5f5")
calc_frame.pack(pady=20)

btn_font = ("Arial", 10, "bold")
tk.Button(calc_frame, text="Estimate", font=btn_font, bg="#4CAF50", fg="white", cursor="hand2", relief=tk.FLAT, padx=15, pady=5, command=estimate_parameters).pack(side=tk.LEFT, padx=10)
tk.Button(calc_frame, text="Show Curves", font=btn_font, bg="#2196F3", fg="white", cursor="hand2", relief=tk.FLAT, padx=15, pady=5, command=plot_curves).pack(side=tk.LEFT, padx=10)
tk.Button(calc_frame, text="Show Histograms", font=btn_font, bg="#FF9800", fg="white", cursor="hand2", relief=tk.FLAT, padx=15, pady=5, command=plot_histograms).pack(side=tk.LEFT, padx=10)

# Results
tk.Label(root, text="Results:", font=("Arial", 10, "bold"), bg="#f5f5f5", fg="black").pack(anchor="w", padx=20)
results_container = tk.Frame(root, bg="#f5f5f5")
results_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(5, 20))

table_frame = tk.Frame(results_container, bg="#f5f5f5")
table_frame.pack(fill=tk.X, pady=(0, 10))

draw_interval_table(table_frame, intervals=calculate_intervals(get_matrix_data()))

result_text = tk.Text(results_container, font=("Consolas", 11), height=15, state=tk.DISABLED, bg="white", fg="black", relief=tk.SOLID, borderwidth=1)
result_text.pack(fill=tk.BOTH, expand=True)

root.mainloop()