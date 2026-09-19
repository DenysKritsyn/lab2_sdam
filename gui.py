import tkinter as tk
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

def estimate_parameters():
    raw_data = entry_series.get()
    try:
        # Allow numbers to be separated by spaces or commas
        clean_data = raw_data.replace(',', ' ')
        num_series = [float(x) for x in clean_data.split()]
        
        if not num_series:
            messagebox.showwarning("Warning", "Please enter at least one number.")
            return

        # Computations
        avg = getAverage(num_series)
        med = getMedian(num_series)
        
        try:
            mod = getMode(num_series)
        except NoModeError:
            mod = "No Mode (all numbers are unique)"
            
        scope = getScope(num_series)
        m_exp = getMathExpectation(num_series)
        disp = getDispersion(num_series)
        std_dev = getStandardDeviation(num_series)
        mod_disp = getModifiedDispersion(num_series)
        mod_std_dev = getModifiedStandardDeviation(num_series)
        
        # Handle potential division by zero
        try: var = round(getVariation(num_series), 4)
        except ZeroDivisionError: var = "Error (Math Expectation = 0)"

        init_moment_2 = getInitialStatisticalMoment(2, num_series)
        cent_moment_2 = getCentralStatisticalMoment(2, num_series)
        
        try: asym = round(getAsymmetry(num_series), 4)
        except ZeroDivisionError: asym = "Error (Standard Deviation = 0)"
        
        try: exc = round(getExcess(num_series), 4)
        except ZeroDivisionError: exc = "Error (Standard Deviation = 0)"

        # Display results
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
        messagebox.showerror("Error", "Invalid input. Please use only numbers separated by spaces or commas.")
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {str(e)}")

def plot_graphs():
    raw_data = entry_series.get()
    try:
        clean_data = raw_data.replace(',', ' ')
        num_series = [float(x) for x in clean_data.split()]
        if not num_series:
            messagebox.showwarning("Warning", "Please enter at least one number.")
            return

        import matplotlib.pyplot as plt
        import collections

        n = len(num_series)
        counts = collections.Counter(num_series)
        sorted_unique = sorted(counts.keys())
        
        freqs = [counts[val] for val in sorted_unique]
        rel_freqs = [f / n for f in freqs]
        
        cum_freqs = []
        c = 0
        for f in freqs:
            c += f
            cum_freqs.append(c)
            
        cum_rel_freqs = []
        cr = 0
        for rf in rel_freqs:
            cr += rf
            cum_rel_freqs.append(cr)
        
        fig, axs = plt.subplots(2, 3, figsize=(15, 10))
        fig.canvas.manager.set_window_title('Statistical Graphs')

        # Frequency Polygon
        axs[0, 0].plot(sorted_unique, freqs, marker='o', linestyle='-', color='b')
        axs[0, 0].set_title('Frequency Polygon')
        axs[0, 0].set_xlabel('X')
        axs[0, 0].set_ylabel('Absolute Frequency (n_i)')
        axs[0, 0].grid(True)

        # Relative Frequency Polygon
        axs[0, 1].plot(sorted_unique, rel_freqs, marker='o', linestyle='-', color='g')
        axs[0, 1].set_title('Relative Frequency Polygon')
        axs[0, 1].set_xlabel('X')
        axs[0, 1].set_ylabel('Relative Frequency (w_i)')
        axs[0, 1].grid(True)

        # Cumulative Frequency Curve (Absolute)
        axs[0, 2].plot(sorted_unique, cum_freqs, marker='o', linestyle='-', color='r')
        axs[0, 2].set_title('Cumulative Frequency Curve')
        axs[0, 2].set_xlabel('X')
        axs[0, 2].set_ylabel('Cumulative Frequency')
        axs[0, 2].grid(True)

        # Cumulative Relative Frequency Curve
        axs[1, 0].plot(sorted_unique, cum_rel_freqs, marker='o', linestyle='-', color='orange')
        axs[1, 0].set_title('Cumulative Relative Freq. Curve')
        axs[1, 0].set_xlabel('X')
        axs[1, 0].set_ylabel('Cumulative Rel. Frequency')
        axs[1, 0].grid(True)

        # Empirical CDF (Step function)
        x_step = [sorted_unique[0] - 1] + sorted_unique + [sorted_unique[-1] + 1]
        y_step = [0] + list(cum_rel_freqs) + [1]
        
        axs[1, 1].step(x_step, y_step, where='post', color='purple')
        axs[1, 1].plot(sorted_unique, cum_rel_freqs, 'o', color='purple', alpha=0.5)
        axs[1, 1].set_title('Empirical Distribution Function (ECDF)')
        axs[1, 1].set_xlabel('X')
        axs[1, 1].set_ylabel('F*(x)')
        axs[1, 1].grid(True)

        # Hide the 6th empty subplot
        axs[1, 2].axis('off')

        plt.tight_layout()
        plt.show()

    except Exception as e:
        messagebox.showerror("Error", f"An error occurred while plotting: {str(e)}")

# Create main window
root = tk.Tk()
root.title("Statistical Parameters Estimator (Lab 2)")
root.geometry("600x700")
root.configure(padx=20, pady=20, bg="#f5f5f5")

# Header
tk.Label(root, text="Interval Series Characteristics Calculation", font=("Helvetica", 16, "bold"), bg="#f5f5f5").pack(pady=(0, 20))

# Input field
tk.Label(root, text="Enter numerical values (separated by space or comma):", font=("Arial", 11), bg="#f5f5f5").pack(anchor="w")
input_frame = tk.Frame(root, bg="#f5f5f5")
input_frame.pack(fill=tk.X, pady=5)

tk.Label(input_frame, text="X:", font=("Arial", 14), bg="#f5f5f5").pack(side=tk.LEFT, padx=(0, 5))

entry_series = tk.Entry(input_frame, font=("Arial", 14), width=50)
entry_series.pack(side=tk.LEFT, fill=tk.X, expand=True)
entry_series.insert(0, "0.14 0.25 0.31 0.57 0.65 0.78 0.42 0.47 0.60 0.91") # Default test data (my variant from laboratory task)

# Buttons Frame
buttons_frame = tk.Frame(root, bg="#f5f5f5")
buttons_frame.pack(pady=20)

btn_estimate = tk.Button(buttons_frame, text="Estimate", font=("Arial", 13, "bold"), bg="#4CAF50", fg="white", cursor="hand2", command=estimate_parameters)
btn_estimate.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

btn_plot = tk.Button(buttons_frame, text="Show Graphs", font=("Arial", 13, "bold"), bg="#2196F3", fg="white", cursor="hand2", command=plot_graphs)
btn_plot.pack(side=tk.LEFT, padx=10, ipadx=10, ipady=5)

# Text area for results
tk.Label(root, text="Results:", font=("Arial", 12, "bold"), bg="#f5f5f5").pack(anchor="w")
result_text = tk.Text(root, font=("Consolas", 12), height=20, state=tk.DISABLED, bg="#ffffff", relief=tk.GROOVE, borderwidth=2)
result_text.pack(fill=tk.BOTH, expand=True, pady=5)

root.mainloop()
