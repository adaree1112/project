import numpy as np
from scipy.stats import norm

def make_dataset(mu, sigma):
    xs = np.linspace(mu - 3*sigma, mu + 3*sigma, 50)

    pdf_data = [(round(float(x), 4), round(float(norm.pdf(x, mu, sigma)), 4)) for x in xs]
    cdf_data = [(round(float(x), 4), round(float(norm.cdf(x, mu, sigma)), 4)) for x in xs]

    # intervals: consecutive xs
    interval_data = [
        (round(float(xs[i]), 4), round(float(xs[i+1]), 4),
         round(float(norm.cdf(xs[i+1], mu, sigma) - norm.cdf(xs[i], mu, sigma)), 4))
        for i in range(len(xs)-1)
    ]


    sym_interval_data = []
    for i in range(1, 51):
        a = mu - i * sigma * 0.1
        b = mu + i * sigma * 0.1
        p = norm.cdf(b, mu, sigma) - norm.cdf(a, mu, sigma)
        sym_interval_data.append((round(float(a), 4), round(float(b), 4), round(float(p), 4)))
    return pdf_data, cdf_data, interval_data, sym_interval_data

datasets = [
    (0, 1, *make_dataset(0, 1)),
    (0, 2, *make_dataset(0, 2)),
    (1, 1, *make_dataset(1, 1)),
    (2, 3, *make_dataset(2, 3)),
    (-1, 0.5, *make_dataset(-1, 0.5)),
]

for mu, sigma, pdf_data, cdf_data, interval_data, sym_interval_data in datasets:
    print(f"({mu}, {sigma},")
    print(pdf_data, ",")
    print(cdf_data, ",")
    print(interval_data, ",")
    print(sym_interval_data, "),\n")