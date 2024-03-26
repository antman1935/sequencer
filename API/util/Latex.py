# author: antman1935, anthony.lamont99@yahoo.com

"""
This is a utility file for printing out one or more tables in a latex file.
"""

class LatexTablePrinter:
    def __init__(self, filename):
        self.outfile = open(filename, "w+")
        self._writePreamble()

    def _writePreamble(self):
        self.outfile.writelines(
            [
                "\\documentclass{article}\n",
                "\\usepackage[table]{xcolor}\n"
                "\\begin{document}\n",
            ]
        )

    def writeTable(self, label: str, row_bounds: tuple[int, int], row_dim: str, col_bounds: tuple[int, int], col_dim: str, data: list[list[int]]):
        # table header
        dim_str = f"{row_dim} $\\backslash$ {col_dim}"
        self.outfile.writelines(
            [
                "\\begin{table}[h]\n",
                f"\\caption{{{label}}}\n",
                "\\centering\n",
                f"\\begin{{tabular}}{{|{'|'.join(['c'] * (col_bounds[1] - col_bounds[0] + 2))}|}}\n",
                # first row (column header)
                "\\hline\n",
                f"{dim_str} & {' & '.join([str(c) for c in range(col_bounds[0], col_bounds[1] + 1)])} \\\\\n",
                "\\hline\n",
            ]
        )
        for r, row in zip ([r for r in range(row_bounds[0], row_bounds[1] + 1)], data):
            self.outfile.writelines(
                [
                    # write all data rows
                    f"{r} & {' & '.join([str(v) for v in row])} \\\\\n",
                    "\\hline\n",
                ]
            )
        self.outfile.writelines(
            [
                "\end{tabular}\n",
                "\end{table}\n",
            ]
        )

    def close(self):
        self.outfile.writelines(
            [
                "\end{document}\n"
            ]
        )
        self.outfile.close()
