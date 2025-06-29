import os
import statistics

from utils.PackingData import PackingData
from utils.metrics.CenterOfMassShiftCalculator import CenterOfMassShiftCalculator
from utils.metrics.PlacementDensityCalculator import PlacementDensityCalculator
from utils.metrics.ShakeStabilityCalculator import ShakeStabilityCalculator


def print_results(dir):
    density_res = []
    center_res = []
    shake_res = []

    for file in os.listdir(dir):
        fullpath = f"{dir}/{file}"
        data = PackingData.load_from_file(fullpath)

        density = PlacementDensityCalculator(data)
        density_res.append(density.calculate_density())

        center = CenterOfMassShiftCalculator(data)
        center_res.append(center.calculate_shift())

        shake = ShakeStabilityCalculator(data)
        shake_res.append(shake.calculate_average_displacement())

    def print_stat(name, values):
        if not values:
            print(f"{name}: Нет данных")
            return

        mean = statistics.mean(values)
        stdev = statistics.stdev(values) if len(values) > 1 else 0

        print(f"{name}:")
        print(f"  Среднее: {mean:.4f}")
        print(f"  Стандартное отклонение: {stdev:.4f}")

    print_stat("Плотность", density_res)
    print_stat("Смещение центра масс", center_res)
    print_stat("Устойчивость (среднее смещение)", shake_res)


if __name__ == "__main__":
    greedy_dir = "../out/bench/dataset_test/greedy"
    phys_dir = "../out/bench/dataset_test/phys"
    exact = "../out/bench/dataset_test_multi/exactortools"
    print_results(greedy_dir)
    print("================= ")
    print_results(phys_dir)
    print("================= ")
    print_results(exact)
