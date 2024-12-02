import math


ladder_score_table_m = {
    # fmt: off
    10: [3.70, 3.65, 3.60, 3.55, 3.50, 3.45, 3.40, 3.35, 3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75],
    11: [3.62, 3.57, 3.52, 3.47, 3.42, 3.37, 3.32, 3.27, 3.22, 3.17, 3.12, 3.07, 3.02, 2.97, 2.92, 2.87, 2.82, 2.77, 2.72, 2.67],
    12: [3.54, 3.49, 3.44, 3.39, 3.34, 3.29, 3.24, 3.19, 3.14, 3.09, 3.04, 2.99, 2.94, 2.89, 2.84, 2.79, 2.74, 2.69, 2.64, 2.59],
    13: [3.46, 3.41, 3.36, 3.31, 3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66, 2.61, 2.56, 2.51],
    14: [3.40, 3.35, 3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.45],
    15: [3.36, 3.31, 3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66, 2.61, 2.56, 2.51, 2.46, 2.41],
    16: [3.33, 3.28, 3.23, 3.18, 3.13, 3.08, 3.03, 2.98, 2.93, 2.88, 2.83, 2.78, 2.73, 2.68, 2.63, 2.58, 2.53, 2.48, 2.43, 2.38],
    17: [3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.45, 2.40, 2.35],
    18: [3.28, 3.23, 3.18, 3.13, 3.08, 3.03, 2.98, 2.93, 2.88, 2.83, 2.78, 2.73, 2.68, 2.63, 2.58, 2.53, 2.48, 2.43, 2.38, 2.33],
    19: [3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66, 2.61, 2.56, 2.51, 2.46, 2.41, 2.36, 2.31],
    20: [3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.45, 2.40, 2.35, 2.30],
    # fmt: on
}

ladder_score_table_f = {
    # fmt: off
    10: [3.70, 3.65, 3.60, 3.55, 3.50, 3.45, 3.40, 3.35, 3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75],
    11: [3.61, 3.56, 3.51, 3.46, 3.41, 3.36, 3.31, 3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66],
    12: [3.53, 3.48, 3.43, 3.38, 3.33, 3.28, 3.23, 3.18, 3.13, 3.08, 3.03, 2.98, 2.93, 2.88, 2.83, 2.78, 2.73, 2.68, 2.63, 2.58],
    13: [3.47, 3.42, 3.37, 3.32, 3.27, 3.22, 3.17, 3.12, 3.07, 3.02, 2.97, 2.92, 2.87, 2.82, 2.77, 2.72, 2.67, 2.62, 2.57, 2.52],
    14: [3.43, 3.38, 3.33, 3.28, 3.23, 3.18, 3.13, 3.08, 3.03, 2.98, 2.93, 2.88, 2.83, 2.78, 2.73, 2.68, 2.63, 2.58, 2.53, 2.48],
    15: [3.40, 3.35, 3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.45],
    16: [3.38, 3.33, 3.28, 3.23, 3.18, 3.13, 3.08, 3.03, 2.98, 2.93, 2.88, 2.83, 2.78, 2.73, 2.68, 2.63, 2.58, 2.53, 2.48, 2.43],
    17: [3.37, 3.32, 3.27, 3.22, 3.17, 3.12, 3.07, 3.02, 2.97, 2.92, 2.87, 2.82, 2.77, 2.72, 2.67, 2.62, 2.57, 2.52, 2.47, 2.42],
    18: [3.36, 3.31, 3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66, 2.61, 2.56, 2.51, 2.46, 2.41],
    19: [3.36, 3.31, 3.26, 3.21, 3.16, 3.11, 3.06, 3.01, 2.96, 2.91, 2.86, 2.81, 2.76, 2.71, 2.66, 2.61, 2.56, 2.51, 2.46, 2.41],
    20: [3.35, 3.30, 3.25, 3.20, 3.15, 3.10, 3.05, 3.00, 2.95, 2.90, 2.85, 2.80, 2.75, 2.70, 2.65, 2.60, 2.55, 2.50, 2.45, 2.40],
    # fmt: on
}

hexagon_score_table_m = {
    # fmt: off
    10: [9.80, 9.60, 9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00 ],
    11: [9.60, 9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80 ],
    12: [9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60 ],
    13: [9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60, 5.40 ],
    14: [9.10, 8.90, 8.70, 8.50, 8.30, 8.10, 7.90, 7.70, 7.50, 7.30, 7.10, 6.90, 6.70, 6.50, 6.30, 6.10, 5.90, 5.70, 5.50, 5.30 ],
    15: [8.90, 8.70, 8.50, 8.30, 8.10, 7.90, 7.70, 7.50, 7.30, 7.10, 6.90, 6.70, 6.50, 6.30, 6.10, 5.90, 5.70, 5.50, 5.30, 5.10 ],
    16: [8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60, 5.40, 5.20, 5.00 ],
    17: [8.70, 8.50, 8.30, 8.10, 7.90, 7.70, 7.50, 7.30, 7.10, 6.90, 6.70, 6.50, 6.30, 6.10, 5.90, 5.70, 5.50, 5.30, 5.10, 4.90 ],
    18: [8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60, 5.40, 5.20, 5.00, 4.80 ],
    19: [8.50, 8.30, 8.10, 7.90, 7.70, 7.50, 7.30, 7.10, 6.90, 6.70, 6.50, 6.30, 6.10, 5.90, 5.70, 5.50, 5.30, 5.10, 4.90, 4.70 ],
    20: [8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60, 5.40, 5.20, 5.00, 4.80, 4.60 ],
    # fmt: on
}

hexagon_score_table_f = {
    # fmt: off
    10: [9.80, 9.60, 9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00 ],
    11: [9.60, 9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80 ],
    12: [9.40, 9.20, 9.00, 8.80, 8.60, 8.40, 8.20, 8.00, 7.80, 7.60, 7.40, 7.20, 7.00, 6.80, 6.60, 6.40, 6.20, 6.00, 5.80, 5.60 ],
    13: [8.00, 7.90, 7.80, 7.70, 7.60, 7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10 ],
    14: [7.90, 7.80, 7.70, 7.60, 7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00 ],
    15: [7.80, 7.70, 7.60, 7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90 ],
    16: [7.70, 7.60, 7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90, 5.80 ],
    17: [7.60, 7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90, 5.80, 5.70 ],
    18: [7.50, 7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90, 5.80, 5.70, 5.60 ],
    19: [7.40, 7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90, 5.80, 5.70, 5.60, 5.50 ],
    20: [7.30, 7.20, 7.10, 7.00, 6.90, 6.80, 6.70, 6.60, 6.50, 6.40, 6.30, 6.20, 6.10, 6.00, 5.90, 5.80, 5.70, 5.60, 5.50, 5.40 ],
    # fmt: on
}

y_test_score_table_m = {
    # fmt: off
    10: [ 0.41, 0.41, 0.42, 0.42, 0.43, 0.44, 0.44, 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52 ],
    11: [ 0.42, 0.43, 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54 ],
    12: [ 0.43, 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54 ],
    13: [ 0.43, 0.44, 0.44, 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55 ],
    14: [ 0.44, 0.44, 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55 ],
    15: [ 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54, 0.55, 0.55 ],
    16: [ 0.44, 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55, 0.56 ],
    17: [ 0.44, 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55, 0.55, 0.56 ],
    18: [ 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55, 0.56, 0.56 ],
    19: [ 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55, 0.55, 0.56, 0.56 ],
    20: [ 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54, 0.55, 0.55, 0.56, 0.57 ],
    # fmt: on
}

y_test_score_table_f = {
    # fmt: off
    10: [ 0.41, 0.41, 0.42, 0.42, 0.43, 0.44, 0.44, 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52 ],
    11: [ 0.42, 0.42, 0.43, 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53 ],
    12: [ 0.42, 0.43, 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54 ],
    13: [ 0.43, 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54 ],
    14: [ 0.43, 0.44, 0.44, 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55 ],
    15: [ 0.43, 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54, 0.55 ],
    16: [ 0.44, 0.44, 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55, 0.55 ],
    17: [ 0.44, 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54, 0.55, 0.55 ],
    18: [ 0.44, 0.45, 0.45, 0.46, 0.47, 0.47, 0.48, 0.48, 0.49, 0.50, 0.50, 0.51, 0.51, 0.52, 0.53, 0.53, 0.54, 0.54, 0.55, 0.56 ],
    19: [ 0.44, 0.45, 0.46, 0.46, 0.47, 0.47, 0.48, 0.49, 0.49, 0.50, 0.50, 0.51, 0.52, 0.52, 0.53, 0.53, 0.54, 0.55, 0.55, 0.56 ],
    20: [ 0.45, 0.45, 0.46, 0.46, 0.47, 0.48, 0.48, 0.49, 0.49, 0.50, 0.51, 0.51, 0.52, 0.52, 0.53, 0.54, 0.54, 0.55, 0.55, 0.56 ],
    # fmt: on
}

brace_score_table_m = {
    # fmt: off
    10: [ 27.2, 26.4, 25.6, 24.8, 24.0, 23.2, 22.4, 21.6, 20.8, 20.0, 19.2, 18.4, 17.6, 16.8, 16.0, 15.2, 14.4, 13.6, 12.8, 12.0 ],
    11: [ 26.8, 26.0, 25.2, 24.4, 23.6, 22.8, 22.0, 21.2, 20.4, 19.6, 18.8, 18.0, 17.2, 16.4, 15.6, 14.8, 14.0, 13.2, 12.4, 11.6 ],
    12: [ 26.3, 25.5, 24.7, 23.9, 23.1, 22.3, 21.5, 20.7, 19.9, 19.1, 18.3, 17.5, 16.7, 15.9, 15.1, 14.3, 13.5, 12.7, 11.9, 11.1 ],
    13: [ 26.0, 25.2, 24.4, 23.6, 22.8, 22.0, 21.2, 20.4, 19.6, 18.8, 18.0, 17.2, 16.4, 15.6, 14.8, 14.0, 13.2, 12.4, 11.6, 10.8 ],
    14: [ 25.8, 25.0, 24.2, 23.4, 22.6, 21.8, 21.0, 20.2, 19.4, 18.6, 17.8, 17.0, 16.2, 15.4, 14.6, 13.8, 13.0, 12.2, 11.4, 10.6 ],
    15: [ 25.7, 24.9, 24.1, 23.3, 22.5, 21.7, 20.9, 20.1, 19.3, 18.5, 17.7, 16.9, 16.1, 15.3, 14.5, 13.7, 12.9, 12.1, 11.3, 10.5 ],
    16: [ 25.7, 24.9, 24.1, 23.3, 22.5, 21.7, 20.9, 20.1, 19.3, 18.5, 17.7, 16.9, 16.1, 15.3, 14.5, 13.7, 12.9, 12.1, 11.3, 10.5 ],
    17: [ 25.9, 25.1, 24.3, 23.5, 22.7, 21.9, 21.1, 20.3, 19.5, 18.7, 17.9, 17.1, 16.3, 15.5, 14.7, 13.9, 13.1, 12.3, 11.5, 10.7 ],
    18: [ 26.3, 25.5, 24.7, 23.9, 23.1, 22.3, 21.5, 20.7, 19.9, 19.1, 18.3, 17.5, 16.7, 15.9, 15.1, 14.3, 13.5, 12.7, 11.9, 11.1 ],
    19: [ 26.6, 25.8, 25.0, 24.2, 23.4, 22.6, 21.8, 21.0, 20.2, 19.4, 18.6, 17.8, 17.0, 16.2, 15.4, 14.6, 13.8, 13.0, 12.2, 11.4 ],
    20: [ 27.0, 26.2, 25.4, 24.6, 23.8, 23.0, 22.2, 21.4, 20.6, 19.8, 19.0, 18.2, 17.4, 16.6, 15.8, 15.0, 14.2, 13.4, 12.6, 11.8 ],
    # fmt: on
}

brace_score_table_f = {
    # fmt: off
    10: [ 27.2, 26.4, 25.6, 24.8, 24.0, 23.2, 22.4, 21.6, 20.8, 20.0, 19.2, 18.4, 17.6, 16.8, 16.0, 15.2, 14.4, 13.6, 12.8, 12.0 ],
    11: [ 26.8, 26.0, 25.2, 24.4, 23.6, 22.8, 22.0, 21.2, 20.4, 19.6, 18.8, 18.0, 17.2, 16.4, 15.6, 14.8, 14.0, 13.2, 12.4, 11.6 ],
    12: [ 26.4, 25.6, 24.8, 24.0, 23.2, 22.4, 21.6, 20.8, 20.0, 19.2, 18.4, 17.6, 16.8, 16.0, 15.2, 14.4, 13.6, 12.8, 12.0, 11.2 ],
    13: [ 26.2, 25.4, 24.6, 23.8, 23.0, 22.2, 21.4, 20.6, 19.8, 19.0, 18.2, 17.4, 16.6, 15.8, 15.0, 14.2, 13.4, 12.6, 11.8, 11.0 ],
    14: [ 26.1, 25.3, 24.5, 23.7, 22.9, 22.1, 21.3, 20.5, 19.7, 18.9, 18.1, 17.3, 16.5, 15.7, 14.9, 14.1, 13.3, 12.5, 11.7, 10.9 ],
    15: [ 26.1, 25.3, 24.5, 23.7, 22.9, 22.1, 21.3, 20.5, 19.7, 18.9, 18.1, 17.3, 16.5, 15.7, 14.9, 14.1, 13.3, 12.5, 11.7, 10.9 ],
    16: [ 26.2, 25.4, 24.6, 23.8, 23.0, 22.2, 21.4, 20.6, 19.8, 19.0, 18.2, 17.4, 16.6, 15.8, 15.0, 14.2, 13.4, 12.6, 11.8, 11.0 ],
    17: [ 26.5, 25.7, 24.9, 24.1, 23.3, 22.5, 21.7, 20.9, 20.1, 19.3, 18.5, 17.7, 16.9, 16.1, 15.3, 14.5, 13.7, 12.9, 12.1, 11.3 ],
    18: [ 26.8, 26.0, 25.2, 24.4, 23.6, 22.8, 22.0, 21.2, 20.4, 19.6, 18.8, 18.0, 17.2, 16.4, 15.6, 14.8, 14.0, 13.2, 12.4, 11.6 ],
    19: [ 27.0, 26.2, 25.4, 24.6, 23.8, 23.0, 22.2, 21.4, 20.6, 19.8, 19.0, 18.2, 17.4, 16.6, 15.8, 15.0, 14.2, 13.4, 12.6, 11.8 ],
    20: [ 27.2, 26.4, 25.6, 24.8, 24.0, 23.2, 22.4, 21.6, 20.8, 20.0, 19.2, 18.4, 17.6, 16.8, 16.0, 15.2, 14.4, 13.6, 12.8, 12.0 ],
    # fmt: on
}

medicimbal_score_table_m = {
    # fmt: off
    10: [ 2.00, 2.20, 2.40, 2.60, 2.80, 3.00, 3.20, 3.40, 3.60, 3.80, 4.20, 4.60, 5.00, 5.40, 5.80, 6.20, 6.60, 7.00, 7.40, 7.80 ],
    11: [ 3.50, 3.70, 3.90, 4.10, 4.30, 4.50, 4.70, 4.90, 5.10, 5.30, 5.70, 6.10, 6.50, 6.90, 7.30, 7.70, 8.10, 8.50, 8.90, 9.30 ],
    12: [ 5.10, 5.30, 5.50, 5.70, 5.90, 6.10, 6.30, 6.50, 6.70, 6.90, 7.30, 7.70, 8.10, 8.50, 8.90, 9.30, 9.70, 10.10, 10.50, 10.90 ],
    13: [ 6.20, 6.40, 6.60, 6.80, 7.00, 7.20, 7.40, 7.60, 7.80, 8.00, 8.40, 8.80, 9.20, 9.60, 10.00, 10.40, 10.80, 11.20, 11.60, 12.00 ],
    14: [ 6.90, 7.10, 7.30, 7.50, 7.70, 7.90, 8.10, 8.30, 8.50, 8.70, 9.10, 9.50, 9.90, 10.30, 10.70, 11.10, 11.50, 11.90, 12.30, 12.70 ],
    15: [ 7.40, 7.60, 7.80, 8.00, 8.20, 8.40, 8.60, 8.80, 9.00, 9.20, 9.60, 10.00, 10.40, 10.80, 11.20, 11.60, 12.00, 12.40, 12.80, 13.20 ],
    16: [ 7.80, 8.00, 8.20, 8.40, 8.60, 8.80, 9.00, 9.20, 9.40, 9.60, 10.00, 10.40, 10.80, 11.20, 11.60, 12.00, 12.40, 12.80, 13.20, 13.60 ],
    17: [ 8.15, 8.35, 8.55, 8.75, 8.95, 9.15, 9.35, 9.55, 9.75, 9.95, 10.35, 10.75, 11.15, 11.55, 11.95, 12.35, 12.75, 13.15, 13.55, 13.95 ],
    18: [ 8.40, 8.60, 8.80, 9.00, 9.20, 9.40, 9.60, 9.80, 10.00, 10.20, 10.60, 11.00, 11.40, 11.80, 12.20, 12.60, 13.00, 13.40, 13.80, 14.20 ],
    19: [ 8.55, 8.75, 8.95, 9.15, 9.35, 9.55, 9.75, 9.95, 10.15, 10.35, 10.75, 11.15, 11.55, 11.95, 12.35, 12.75, 13.15, 13.55, 13.95, 14.35 ],
    20: [ 8.70, 8.90, 9.10, 9.30, 9.50, 9.70, 9.90, 10.10, 10.30, 10.50, 10.90, 11.30, 11.70, 12.10, 12.50, 12.90, 13.30, 13.70, 14.10, 14.50 ],
    # fmt: on
}

medicimbal_score_table_f = {
    # fmt: off
    10: [ 2.00, 2.20, 2.40, 2.60, 2.80, 3.00, 3.20, 3.40, 3.60, 3.80, 4.20, 4.60, 5.00, 5.40, 5.80, 6.20, 6.60, 7.00, 7.40, 7.80 ],
    11: [ 3.20, 3.40, 3.60, 3.80, 4.00, 4.20, 4.40, 4.60, 4.80, 5.00, 5.40, 5.80, 6.20, 6.60, 7.00, 7.40, 7.80, 8.20, 8.60, 9.00 ],
    12: [ 4.20, 4.40, 4.60, 4.80, 5.00, 5.20, 5.40, 5.60, 5.80, 6.00, 6.40, 6.80, 7.20, 7.60, 8.00, 8.40, 8.80, 9.20, 9.60, 10.00 ],
    13: [ 5.00, 5.20, 5.40, 5.60, 5.80, 6.00, 6.20, 6.40, 6.60, 6.80, 7.20, 7.60, 8.00, 8.40, 8.80, 9.20, 9.60, 10.00, 10.40, 10.80 ],
    14: [ 5.40, 5.60, 5.80, 6.00, 6.20, 6.40, 6.60, 6.80, 7.00, 7.20, 7.60, 8.00, 8.40, 8.80, 9.20, 9.60, 10.00, 10.40, 10.80, 11.20 ],
    15: [ 5.70, 5.90, 6.10, 6.30, 6.50, 6.70, 6.90, 7.10, 7.30, 7.50, 7.90, 8.30, 8.70, 9.10, 9.50, 9.90, 10.30, 10.70, 11.10, 11.50 ],
    16: [ 5.95, 6.15, 6.35, 6.55, 6.75, 6.95, 7.15, 7.35, 7.55, 7.75, 8.15, 8.55, 8.95, 9.35, 9.75, 10.15, 10.55, 10.95, 11.35, 11.75 ],
    17: [ 6.15, 6.35, 6.55, 6.75, 6.95, 7.15, 7.35, 7.55, 7.75, 7.95, 8.35, 8.75, 9.15, 9.55, 9.95, 10.35, 10.75, 11.15, 11.55, 11.95 ],
    18: [ 6.30, 6.50, 6.70, 6.90, 7.10, 7.30, 7.50, 7.70, 7.90, 8.10, 8.50, 8.90, 9.30, 9.70, 10.10, 10.50, 10.90, 11.30, 11.70, 12.10 ],
    19: [ 6.35, 6.55, 6.75, 6.95, 7.15, 7.35, 7.55, 7.75, 7.95, 8.15, 8.55, 8.95, 9.35, 9.75, 10.15, 10.55, 10.95, 11.35, 11.75, 12.15 ],
    20: [ 6.40, 6.60, 6.80, 7.00, 7.20, 7.40, 7.60, 7.80, 8.00, 8.20, 8.60, 9.00, 9.40, 9.80, 10.20, 10.60, 11.00, 11.40, 11.80, 12.20 ],
    # fmt: on
}

jet_score_table_m = {
    # fmt: off
    10: [ 168, 176, 184, 192, 200, 208, 216, 224, 232, 240, 248, 256, 264, 272, 280, 288, 296, 304, 312, 320 ],
    11: [ 198, 206, 214, 222, 230, 238, 246, 254, 262, 270, 278, 286, 294, 302, 310, 318, 326, 334, 342, 350 ],
    12: [ 228, 236, 244, 252, 260, 268, 276, 284, 292, 300, 308, 316, 324, 332, 340, 348, 356, 364, 372, 380 ],
    13: [ 258, 266, 274, 282, 290, 298, 306, 314, 322, 330, 338, 346, 354, 362, 370, 378, 386, 394, 402, 410 ],
    14: [ 283, 291, 299, 307, 315, 323, 331, 339, 347, 355, 363, 371, 379, 387, 395, 403, 411, 419, 427, 435 ],
    15: [ 303, 311, 319, 327, 335, 343, 351, 359, 367, 375, 383, 391, 399, 407, 415, 423, 431, 439, 447, 455 ],
    16: [ 323, 331, 339, 347, 355, 363, 371, 379, 387, 395, 403, 411, 419, 427, 435, 443, 451, 459, 467, 475 ],
    17: [ 343, 351, 359, 367, 375, 383, 391, 399, 407, 415, 423, 431, 439, 447, 455, 463, 471, 479, 487, 495 ],
    18: [ 358, 366, 374, 382, 390, 398, 406, 414, 422, 430, 438, 446, 454, 462, 470, 478, 486, 494, 502, 510 ],
    19: [ 368, 376, 384, 392, 400, 408, 416, 424, 432, 440, 448, 456, 464, 472, 480, 488, 496, 504, 512, 520 ],
    20: [ 373, 381, 389, 397, 405, 413, 421, 429, 437, 445, 453, 461, 469, 477, 485, 493, 501, 509, 517, 525 ],
    # fmt: on
}

jet_score_table_f = {
    # fmt: off
    10: [ 168, 175, 183, 190, 198, 205, 213, 220, 228, 235, 243, 250, 258, 265, 273, 280, 288, 295, 303, 310 ],
    11: [ 198, 205, 213, 220, 228, 235, 243, 250, 258, 265, 273, 280, 288, 295, 303, 310, 318, 325, 333, 340 ],
    12: [ 226, 233, 241, 248, 256, 263, 271, 278, 286, 293, 301, 308, 316, 323, 331, 338, 346, 353, 361, 368 ],
    13: [ 248, 255, 263, 270, 278, 285, 293, 300, 308, 315, 323, 330, 338, 345, 353, 360, 368, 375, 383, 390 ],
    14: [ 266, 273, 281, 288, 296, 303, 311, 318, 326, 333, 341, 348, 356, 363, 371, 378, 386, 393, 401, 408 ],
    15: [ 280, 287, 295, 302, 310, 317, 325, 332, 340, 347, 355, 362, 370, 377, 385, 392, 400, 407, 415, 422 ],
    16: [ 293, 300, 308, 315, 323, 330, 338, 345, 353, 360, 368, 375, 383, 390, 398, 405, 413, 420, 428, 435 ],
    17: [ 303, 310, 318, 325, 333, 340, 348, 355, 363, 370, 378, 385, 393, 400, 408, 415, 423, 430, 438, 445 ],
    18: [ 311, 318, 326, 333, 341, 348, 356, 363, 371, 378, 386, 393, 401, 408, 416, 423, 431, 438, 446, 453 ],
    19: [ 316, 323, 331, 338, 346, 353, 361, 368, 376, 383, 391, 398, 406, 413, 421, 428, 436, 443, 451, 458 ],
    20: [ 318, 325, 333, 340, 348, 355, 363, 370, 378, 385, 393, 400, 408, 415, 423, 430, 438, 445, 453, 460 ],
    # fmt: on
}

triple_jump_score_table_m = {
    # fmt: off
    10: [ 2.70, 2.86, 3.03, 3.19, 3.35, 3.51, 3.67, 3.84, 4.00, 4.16, 4.32, 4.48, 4.65, 4.81, 4.97, 5.13, 5.29, 5.46, 5.62, 5.78 ],
    11: [ 3.09, 3.25, 3.42, 3.58, 3.74, 3.90, 4.06, 4.23, 4.39, 4.55, 4.71, 4.87, 5.04, 5.20, 5.36, 5.52, 5.68, 5.85, 6.01, 6.17 ],
    12: [ 3.48, 3.64, 3.81, 3.97, 4.13, 4.29, 4.45, 4.62, 4.78, 4.94, 5.10, 5.26, 5.43, 5.59, 5.75, 5.91, 6.07, 6.24, 6.40, 6.56 ],
    13: [ 3.93, 4.09, 4.26, 4.42, 4.58, 4.74, 4.90, 5.07, 5.23, 5.39, 5.55, 5.71, 5.88, 6.04, 6.20, 6.36, 6.52, 6.69, 6.85, 7.01 ],
    14: [ 4.39, 4.55, 4.72, 4.88, 5.04, 5.20, 5.36, 5.53, 5.69, 5.85, 6.01, 6.17, 6.34, 6.50, 6.66, 6.82, 6.98, 7.15, 7.31, 7.47 ],
    15: [ 4.87, 5.03, 5.20, 5.36, 5.52, 5.68, 5.84, 6.01, 6.17, 6.33, 6.49, 6.65, 6.82, 6.98, 7.14, 7.30, 7.46, 7.63, 7.79, 7.95 ],
    16: [ 5.10, 5.26, 5.43, 5.59, 5.75, 5.91, 6.07, 6.24, 6.40, 6.56, 6.72, 6.88, 7.05, 7.21, 7.37, 7.53, 7.69, 7.86, 8.02, 8.18 ],
    17: [ 5.25, 5.41, 5.58, 5.74, 5.90, 6.06, 6.22, 6.39, 6.55, 6.71, 6.87, 7.03, 7.20, 7.36, 7.52, 7.68, 7.84, 8.01, 8.17, 8.33 ],
    18: [ 5.40, 5.56, 5.73, 5.89, 6.05, 6.21, 6.37, 6.54, 6.70, 6.86, 7.02, 7.18, 7.35, 7.51, 7.67, 7.83, 7.99, 8.16, 8.32, 8.48 ],
    19: [ 5.49, 5.65, 5.82, 5.98, 6.14, 6.30, 6.46, 6.63, 6.79, 6.95, 7.11, 7.27, 7.44, 7.60, 7.76, 7.92, 8.08, 8.25, 8.41, 8.57 ],
    20: [ 5.56, 5.72, 5.89, 6.05, 6.21, 6.37, 6.53, 6.70, 6.86, 7.02, 7.18, 7.34, 7.51, 7.67, 7.83, 7.99, 8.15, 8.32, 8.48, 8.64 ],
    # fmt: on
}

triple_jump_score_table_f = {
    # fmt: off
    10: [ 2.50, 2.66, 2.83, 2.99, 3.15, 3.31, 3.47, 3.64, 3.80, 3.96, 4.12, 4.28, 4.45, 4.61, 4.77, 4.93, 5.09, 5.26, 5.42, 5.58 ],
    11: [ 2.74, 2.90, 3.07, 3.23, 3.39, 3.55, 3.71, 3.88, 4.04, 4.20, 4.36, 4.52, 4.69, 4.85, 5.01, 5.17, 5.33, 5.50, 5.66, 5.82 ],
    12: [ 3.02, 3.18, 3.35, 3.51, 3.67, 3.83, 3.99, 4.16, 4.32, 4.48, 4.64, 4.80, 4.97, 5.13, 5.29, 5.45, 5.61, 5.78, 5.94, 6.10 ],
    13: [ 3.28, 3.44, 3.61, 3.77, 3.93, 4.09, 4.25, 4.42, 4.58, 4.74, 4.90, 5.06, 5.23, 5.39, 5.55, 5.71, 5.87, 6.04, 6.20, 6.36 ],
    14: [ 3.51, 3.67, 3.84, 4.00, 4.16, 4.32, 4.48, 4.65, 4.81, 4.97, 5.13, 5.29, 5.46, 5.62, 5.78, 5.94, 6.10, 6.27, 6.43, 6.59 ],
    15: [ 3.74, 3.90, 4.07, 4.23, 4.39, 4.55, 4.71, 4.88, 5.04, 5.20, 5.36, 5.52, 5.69, 5.85, 6.01, 6.17, 6.33, 6.50, 6.66, 6.82 ],
    16: [ 3.97, 4.13, 4.30, 4.46, 4.62, 4.78, 4.94, 5.11, 5.27, 5.43, 5.59, 5.75, 5.92, 6.08, 6.24, 6.40, 6.56, 6.73, 6.89, 7.05 ],
    17: [ 4.10, 4.26, 4.43, 4.59, 4.75, 4.91, 5.07, 5.24, 5.40, 5.56, 5.72, 5.88, 6.05, 6.21, 6.37, 6.53, 6.69, 6.86, 7.02, 7.18 ],
    18: [ 4.17, 4.33, 4.50, 4.66, 4.82, 4.98, 5.14, 5.31, 5.47, 5.63, 5.79, 5.95, 6.12, 6.28, 6.44, 6.60, 6.76, 6.93, 7.09, 7.25 ],
    19: [ 4.19, 4.35, 4.52, 4.68, 4.84, 5.00, 5.16, 5.33, 5.49, 5.65, 5.81, 5.97, 6.14, 6.30, 6.46, 6.62, 6.78, 6.95, 7.11, 7.27 ],
    20: [ 4.19, 4.35, 4.52, 4.68, 4.84, 5.00, 5.16, 5.33, 5.49, 5.65, 5.81, 5.97, 6.14, 6.30, 6.46, 6.62, 6.78, 6.95, 7.11, 7.27 ],
    # fmt: on
}

beep_test_score_table_m = {
    # fmt: off
    10: [ 19, 22, 26, 30, 34, 37, 41, 45, 49, 52, 56, 60, 64, 67, 71, 75, 79, 82, 86, 90 ],
    11: [ 22, 26, 30, 33, 37, 41, 45, 49, 52, 56, 60, 64, 67, 71, 75, 79, 83, 86, 90, 94 ],
    12: [ 25, 29, 33, 37, 41, 45, 48, 52, 56, 60, 64, 67, 71, 75, 79, 83, 87, 90, 94, 98 ],
    13: [ 29, 33, 37, 40, 44, 48, 52, 56, 60, 64, 67, 71, 75, 79, 83, 87, 90, 94, 98, 102 ],
    14: [ 35, 39, 43, 47, 51, 55, 59, 63, 67, 71, 74, 78, 82, 86, 90, 94, 98, 102, 106, 110 ],
    15: [ 42, 46, 50, 54, 58, 62, 66, 70, 74, 79, 83, 87, 91, 95, 99, 103, 107, 111, 115, 119 ],
    16: [ 43, 47, 52, 56, 61, 65, 69, 74, 78, 83, 87, 92, 96, 100, 105, 109, 114, 118, 123, 127 ],
    17: [ 46, 51, 55, 60, 65, 70, 75, 79, 84, 89, 94, 99, 103, 108, 113, 118, 123, 127, 132, 137 ],
    18: [ 47, 51, 56, 61, 66, 71, 75, 80, 85, 90, 95, 100, 104, 109, 114, 119, 124, 128, 133, 138 ],
    19: [ 48, 53, 57, 62, 67, 72, 77, 81, 86, 91, 96, 101, 105, 110, 115, 120, 125, 129, 134, 139 ],
    20: [ 51, 55, 60, 65, 70, 74, 79, 84, 88, 93, 98, 102, 107, 112, 117, 121, 126, 131, 135, 140 ],
    # fmt: on
}

beep_test_score_table_f = {
    # fmt: off
    10: [ 12, 15, 18, 20, 23, 26, 29, 32, 34, 37, 40, 43, 45, 48, 51, 54, 57, 59, 62, 65 ],
    11: [ 15, 18, 21, 24, 27, 30, 33, 36, 39, 42, 45, 47, 50, 53, 56, 59, 62, 65, 68, 71 ],
    12: [ 18, 21, 24, 27, 31, 34, 37, 40, 43, 46, 49, 52, 55, 58, 62, 65, 68, 71, 74, 77 ],
    13: [ 23, 27, 30, 33, 36, 40, 43, 46, 49, 53, 56, 59, 62, 66, 69, 72, 75, 79, 82, 85 ],
    14: [ 26, 29, 33, 37, 40, 44, 47, 51, 54, 58, 61, 65, 68, 72, 75, 79, 82, 86, 89, 93 ],
    15: [ 29, 33, 36, 40, 44, 48, 51, 55, 59, 63, 66, 70, 74, 78, 81, 85, 89, 93, 96, 100 ],
    16: [ 33, 37, 41, 46, 50, 54, 58, 62, 66, 70, 75, 79, 83, 87, 91, 95, 100, 104, 108, 112 ],
    17: [ 37, 41, 45, 49, 54, 58, 62, 66, 70, 74, 78, 82, 86, 90, 95, 99, 103, 107, 111, 115 ],
    18: [ 38, 42, 46, 51, 55, 59, 63, 67, 72, 76, 80, 84, 89, 93, 97, 101, 105, 110, 114, 118 ],
    19: [ 39, 43, 48, 52, 56, 61, 65, 69, 73, 78, 82, 86, 91, 95, 99, 104, 108, 112, 117, 121 ],
    20: [ 40, 45, 49, 54, 58, 62, 67, 71, 76, 80, 84, 89, 93, 98, 102, 106, 111, 115, 120, 124 ],
    # fmt: on
}


def calculate_score(age, gender, test, *args):
    if age < 10:
        age = 10
    elif age > 20:
        age = 20

    match test:
        case "ladder":
            test_score_table_m = ladder_score_table_m
            test_score_table_f = ladder_score_table_f
        case "brace":
            test_score_table_m = brace_score_table_m
            test_score_table_f = brace_score_table_f
        case "hexagon":
            test_score_table_m = hexagon_score_table_m
            test_score_table_f = hexagon_score_table_f
        case "medicimbal":
            test_score_table_m = medicimbal_score_table_m
            test_score_table_f = medicimbal_score_table_f
        case "triple_jump":
            test_score_table_m = triple_jump_score_table_m
            test_score_table_f = triple_jump_score_table_f
        case "jet":
            test_score_table_m = jet_score_table_m
            test_score_table_f = jet_score_table_f
        case "beep_test":
            test_score_table_m = beep_test_score_table_m
            test_score_table_f = beep_test_score_table_f
        case "y_test":
            test_score_table_m = y_test_score_table_m
            test_score_table_f = y_test_score_table_f
        case _:
            return  # TODO: add exception handling here

    # Get the scores for the given age and test
    if gender == "M":
        age_scores = test_score_table_m.get(age)
    elif gender == "F":
        age_scores = test_score_table_f.get(age)
    else:
        return  # TODO: add exception handling here

    if test == "ladder" or test == "brace" or test == "hexagon":
        if args[0] is None and args[1] is None:
            return 0
        elif args[0] is None:
            time_best = args[1]
        elif args[1] is None:
            time_best = args[0]
        else:
            time_best = min(args[0], args[1])

        for i, score in enumerate(age_scores):
            if time_best >= score:
                return i
        # If score is lower than the lowest score in the table
        return len(age_scores)

    elif test == "medicimbal" or test == "triple_jump":
        if args[0] is None and args[1] is None and args[2] is None:
            return 0
        elif args[0] is None and args[1] is None:
            distance_best = args[2]
        elif args[0] is None and args[2] is None:
            distance_best = args[1]
        elif args[1] is None and args[2] is None:
            distance_best = args[0]
        elif args[0] is None:
            distance_best = max(args[1], args[2])
        elif args[1] is None:
            distance_best = max(args[0], args[2])
        elif args[2] is None:
            distance_best = max(args[0], args[1])
        else:
            distance_best = max(args[0], args[1], args[2])

        for i, score in enumerate(age_scores):
            if distance_best <= score:
                return i
        # If score is higher than the highest score in the table
        return len(age_scores)

    elif test == "jet" or test == "beep_test":
        distance_best = args[0]

        for i, score in enumerate(age_scores):
            if distance_best <= score:
                return i
        # If score is higher than the highest score in the table
        return len(age_scores)

    elif test == "y_test":
        height = args[0]
        sum_reach = 0
        for i in range(1, 13):
            sum_reach += args[i]

        index = math.floor(sum_reach / height / 12 * 100) / 100.0
        for i, score in enumerate(reversed(age_scores)):
            if index > score:
                return len(age_scores) - i
            elif index == score:
                return len(age_scores) - i
        # If score is higher than the highest score in the table
        return len(age_scores)

    return  # TODO: error handling here


# score = calculate_score(12, "M", "y_test", 2, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1)
# print(score)


def quick_calculate(age, gender, test, *args):
    if age < 10:
        age = 10
    elif age > 20:
        age = 20

    match test:
        case "ladder":
            test_score_table_m = ladder_score_table_m
            test_score_table_f = ladder_score_table_f
        case "brace":
            test_score_table_m = brace_score_table_m
            test_score_table_f = brace_score_table_f
        case "hexagon":
            test_score_table_m = hexagon_score_table_m
            test_score_table_f = hexagon_score_table_f
        case "medicimbal":
            test_score_table_m = medicimbal_score_table_m
            test_score_table_f = medicimbal_score_table_f
        case "triple_jump":
            test_score_table_m = triple_jump_score_table_m
            test_score_table_f = triple_jump_score_table_f
        case "jet":
            test_score_table_m = jet_score_table_m
            test_score_table_f = jet_score_table_f
        case "beep_test":
            test_score_table_m = beep_test_score_table_m
            test_score_table_f = beep_test_score_table_f
        case "y_test":
            test_score_table_m = y_test_score_table_m
            test_score_table_f = y_test_score_table_f
        case _:
            return  # TODO: add exception handling here

    # Get the scores for the given age and test
    if gender == "M":
        age_scores = test_score_table_m.get(age)
    elif gender == "F":
        age_scores = test_score_table_f.get(age)
    else:
        return  # TODO: add exception handling here

    if test == "ladder" or test == "brace" or test == "hexagon":
        time = args[0]
        for i, score in enumerate(age_scores):
            if time >= score:
                return i
        # If score is lower than the lowest score in the table
        return len(age_scores)

    elif test == "medicimbal" or test == "triple_jump":
        distance = args[0]

        for i, score in enumerate(age_scores):
            if distance <= score:
                return i
        # If score is higher than the highest score in the table
        return len(age_scores)

    # elif test == "jet" or test == "beep_test":
    #     distance_best = args[0]

    #     for i, score in enumerate(age_scores):
    #         if distance_best <= score:
    #             return i
    #     # If score is higher than the highest score in the table
    #     return len(age_scores)

    elif test == "y_test":
        index = args[0]

        for i, score in enumerate(reversed(age_scores)):
            if index > score:
                return len(age_scores) - i
            elif index == score:
                return len(age_scores) - i
        # If score is higher than the highest score in the table
        return len(age_scores)

    return  # TODO: error handling here


def calculate_y_test_index(height, *args):
    sum_reach = 0
    for i in range(0, 12):
        sum_reach += args[i]

    return math.floor(sum_reach / height / 12 * 100) / 100.0


def calculate_beep_test_total_laps(level, laps):
    match level:
        case 1:
            return laps + 7
        case 2:
            return laps + 15
        case 3:
            return laps + 23
        case 4:
            return laps + 32
        case 5:
            return laps + 41
        case 6:
            return laps + 51
        case 7:
            return laps + 61
        case 8:
            return laps + 72
        case 9:
            return laps + 83
        case 10:
            return laps + 94
        case 11:
            return laps + 106
        case 12:
            return laps + 118
        case 13:
            return laps + 131
        case 14:
            return laps + 144
        case 15:
            return laps + 157
        case _:
            return  # TODO: error handling here
