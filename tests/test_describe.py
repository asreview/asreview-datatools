import subprocess


def test_describe():
    subprocess.run(["asreview", "data-describe", "benchmark:van_de_schoot2017"])
