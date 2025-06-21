import json
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import os
import math


def draw_objects_on_axes(ax, data, title=None):
    box_width = data['box_width']
    box_height = data['box_height']

    ax.set_xlim(0, box_width)
    ax.set_ylim(0, box_height)
    ax.set_aspect('equal')
    ax.set_xticks([])
    ax.set_yticks([])

    for obj in data['objects']:
        rect = patches.Rectangle(
            (obj['x'], box_height - obj['y'] - obj['h']),  # инверсия Y
            obj['w'],
            obj['h'],
            linewidth=0.8,
            edgecolor='black',
            facecolor='skyblue',
            alpha=0.5
        )
        ax.add_patch(rect)

    if title:
        ax.set_title(title, fontsize=8)


def load_and_draw_grid(dir_path):
    files = sorted([f for f in os.listdir(dir_path) if f.endswith(".json")])
    num_files = len(files)
    cols = math.ceil(math.sqrt(num_files))
    rows = math.ceil(num_files / cols)

    fig, axes = plt.subplots(rows, cols, figsize=(cols * 4, rows * 4))
    axes = axes.flatten() if num_files > 1 else [axes]

    for i, filename in enumerate(files):
        full_path = os.path.join(dir_path, filename)
        with open(full_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        draw_objects_on_axes(axes[i], data, title=filename)

    # Отключаем пустые ячейки, если они есть
    for j in range(len(files), len(axes)):
        axes[j].axis('off')

    plt.tight_layout()
    plt.show()


# Запуск
if __name__ == "__main__":
    load_and_draw_grid("../out/bench/dataset_test/greedy")


# Список использованных источников

Data Insight. Российский рынок онлайн-торговли 2023. Статистика и тренды [Электронный ресурс] // Data Insight. — 2024. — URL: https://datainsight.ru/eCommerce_2023 (дата обращения: 03.12.2024)
Малый бизнес стал главным драйвером e-commerce: исследование [Электронный ресурс] // SberBusiness.live. — 2025. — URL: https://sberbusiness.live/publications/malii-biznes-stal-glavnim-draiverom-e-commerce-issledovanie (дата обращения: 03.12.2024)
Nils Boysen, René de Koster, Felix Weidinger Warehousing in the e-commerce era: A survey // European Journal of Operational Research. – 2019. – Т. 277, № 2. – С. 396–411. (дата обращения: 07.12.2024)
Eliiyi U., Eliiyi D. T. Applications of Bin Packing Models Through The Supply Chain // International Journal of Business and Management. – 2009. – Vol. 1, No. 1. – P. 11-19. (дата обращения: 09.12.2024)
Kumaraswamy S., Nair M. K. Bin packing algorithms for virtual machine placement in cloud computing: a review // International Journal of Electrical and Computer Engineering. – 2019. – Vol. 9, No. 1. – P. 512-524. (дата обращения: 15.12.2024)
Dyckhoff H. A typology of cutting and packing problems // European Journal of Operational Research. – 1990. – Vol. 44, No. 2. – P. 145-159. (дата обращения: 16.12.2024)
Wäscher G., Haußner H., Schumann H. An improved typology of cutting and packing problems // European Journal of Operational Research. – 2007. – Vol. 183, No. 3. – P. 1109-1130. (дата обращения: 16.12.2024)
Про двумерную упаковку: offline алгоритмы [Электронный ресурс] // Хабр 2012. URL: https://habr.com/ru/articles/136225/ (дата обращения: 22.12.2024)
Про двумерную упаковку: online алгоритмы [Электронный ресурс] // Хабр 2012. URL: https://habr.com/ru/articles/160869/ (дата обращения: 22.12.2024)
Martello S., Toth P. Knapsack Problems: Algorithms and Computer Implementations. – Chichester: John Wiley & Sons, 1990. – 296 p. (дата обращения: 10.01.2025)
Garey M. R., Johnson D. S. Computers and Intractability: A Guide to the Theory of NP-Completeness. – New York: W. H. Freeman and Company, 1979. – 340 p. (дата обращения: 10.01.2025)
Guo B., Zhang Y., Hu J., Li J., Wu F., Peng Q., Zhang Q. Two-dimensional irregular packing problems: A review // Frontiers in Mechanical Engineering. – 2022. – Vol. 8. (дата обращения: 14.01.2025)
Ntene N. An Algorithmic Approach to the 2D Oriented Strip Packing Problem : PhD thesis / N. Ntene. – Stellenbosch : University of Stellenbosch, 2007. (дата обращения: 18.01.2025)
Iori M., de Lima V. L., Martello S., Miyazawa F. K., Monaci M. Exact Solution Techniques for Two-dimensional Cutting and Packing // European Journal of Operational Research. – 2020. – Vol. 294, No. 3. – P. 369-406. (дата обращения: 18.01.2025)
Delorme M., Iori M., Martello S. Bin packing and cutting stock problems: Mathematical models and exact algorithms // European Journal of Operational Research. – 2016. – Vol. 255, No. 1. – P. 1-20. (дата обращения: 19.01.2025)
Dell'Amico M., Furini F., Iori M. A branch-and-price algorithm for the temporal bin packing problem // Computers and Operations Research. – 2020. – Vol. 114. – P. 104825. (дата обращения: 28.01.2025)
IBM ILOG CPLEX Optimization Studio: IBM ILOG CPLEX Optimization Studio [Электронный ресурс] // IBM. — URL: https://www.ibm.com/products/ilog-cplex-optimization-studio (дата обращения: 06.01.2025)
Gurobi Optimizer: Gurobi Optimizer [Электронный ресурс] // AMPL. — URL: https://dev.ampl.com/solvers/gurobi/index.html (дата обращения: 06.01.2025)
Almufti S. M., Shaban A. A., Ali R. I., Dela Fuente J. A. Overview of Metaheuristic Algorithms // Polaris Global Journal of Scholarly Research and Trends. – 2023. – Vol. 2, No. 2. – P. 10–32. (дата обращения: 02.02.2025)
Gonçalves J.F., Resende M.G.C. A biased random-key genetic algorithm for 2D and 3D bin packing problems // International Journal of Production Economics. – 2013. – Vol. 145, No. 2. – P. 500–510. (дата обращения: 02.02.2025)
Liu D.S., Tan K.C., Huang S.Y., Goh C.K., Ho W.K. On solving multiobjective bin packing problems using evolutionary particle swarm optimization // European Journal of Operational Research. – 2008. – Vol. 190, No. 2. – P. 357–382 (дата обращения: 04.02.2025)
Yuan Y., Li Y.-j., Wang Y.-q. An improved ACO algorithm for the bin packing problem with conflicts based on graph coloring model // Proceedings of the 21st International Conference on Management Science & Engineering. – Helsinki, Finland: IEEE, 2014. – P. 3–10. (дата обращения: 04.02.2025)
Rao R.L., Iyengar S.S. Bin-packing by simulated annealing // Computers & Mathematics with Applications. – 1994. – Vol. 27, No. 5. – P. 71–82. (дата обращения: 05.02.2025)
Xiong H., Guo C., Peng J., Ding K., Chen W., Qiu X., Bai L., Xu J. GOPT: Generalizable online 3D bin packing via transformer-based deep reinforcement learning // IEEE Robotics and Automation Letters. – 2024. – Vol. 9, No. 11. (дата обращения: 25.02.2025)
Jia X., Williams R.A. A packing algorithm for particles of arbitrary shapes // Powder Technology. – 2001. – Vol. 120, No. 3. – P. 175–186. (дата обращения: 26.02.2025)
Saakes D., Cambazard T., Mitani J., Igarashi T. PacCAM: Material Capture and Interactive 2D Packing for Efficient Material Usage on CNC Cutting Machines // Proceedings of the 26th Annual ACM Symposium on User Interface Software and Technology (UIST'13). – St. Andrews, UK: ACM, 2013. – P. 441–450. (дата обращения: 08.03.2025)
Martinez F., Murillo-Suarez A. Packing algorithm inspired by gravitational and electromagnetic effects // Wireless Networks. – 2020. – Vol. 26. – P. 4395–4406. DOI: 10.1007/s11276-019-02011-9 (дата обращения: 12.03.2025)
Zhuang Q., Chen Z., He K., Cao J., Wang W. Dynamics simulation-based packing of irregular 3D objects // Computers & Graphics. – 2024. – Vol. 123. (дата обращения: 12.03.2025)
Картак В. М. Задача упаковки прямоугольников: точный алгоритм на базе матричного представления // Вестник УГАТУ = Vestnik UGATU. 2007. №4. URL: https://cyberleninka.ru/article/n/zadacha-upakovki-pryamougolnikov-tochnyy-algoritm-na-baze-matrichnogo-predstavleniya (дата обращения: 23.03.2025)
Луцан М. В., Нужнов Е. В. Решение задачи трехмерной упаковки с палетированием контейнеров // Известия ЮФУ. Технические науки. 2014. №7 (156). URL: https://cyberleninka.ru/article/n/reshenie-zadachi-trehmernoy-upakovki-s-paletirovaniem-konteynerov (дата обращения: 23.03.2025)
Чеканин В. А., Чеканин А. В. Оптимизация решения задачи ортогональной упаковки объектов // Прикладная информатика. 2012. №4 (40). URL: https://cyberleninka.ru/article/n/optimizatsiya-resheniya-zadachi-ortogonalnoy-upakovki-obektov (дата обращения: 01.04.2025)
Гиля-Зетинов А. А., Панкратов К. К., Хельвас А. В. Разработка алгоритма укладки паллет на полностью автоматизированном складе // Труды МФТИ. 2019. №1 (41). URL: https://cyberleninka.ru/article/n/razrabotka-algoritma-ukladki-pallet-na-polnostyu-avtomatizirovannom-sklade (дата обращения: 01.04.2025)
Lodi A., Martello S., Vigo D. Recent advances on two-dimensional bin packing problems // Discrete Applied Mathematics. – 2002. – Vol. 123, No. 1–3. – P. 379–396. (дата обращения: 03.04.2025)
Google Developers. Решатель CP-SAT [Электронный ресурс] // Google Developers. — 2024. — URL: https://developers.google.com/optimization/cp/cp_solver?hl=ru (дата обращения: 27.01.2025)
Pymunk: Easy 2D physics in Python [Электронный ресурс]. – Pymunk: https://www.pymunk.org/en/latest/ (дата обращения: 09.02.2025)
Chipmunk2D Documentation [Электронный ресурс]. – Chipmunk Game Dynamics: https://chipmunk-physics.net/documentation.php (дата обращения: 09.02.2025)
Romero S. V., Osaba E., Villar-Rodriguez E., Oregi I., Ban Y. Hybrid approach for solving real-world bin packing problem instances using quantum annealers // Scientific Reports. – 2023. – Vol. 13. (дата обращения: 17.04.2025)
Ultralytics YOLO. Официальная документация [Электронный ресурс] // Ultralytics. URL: https://docs.ultralytics.com/ (дата обращения: 11.03.2025)
YOLO: Real-Time Object Detection [Электронный ресурс] // YOLO. URL: https://pjreddie.com/darknet/yolo/ (дата обращения: 11.03.2025)
Fast SAM. Segment Anything Model (Fast SAM) [Электронный ресурс] // GitHub. URL: https://github.com/CASIA-IVA-Lab/FastSAM (дата обращения: 15.03.2025)
Segment Anything. Research by Meta AI. [Электронный ресурс]. Segment Anything. URL: https://segment-anything.com/ (дата обращения: 15.03.2025)
Pygame Front Page [Электронный ресурс]. – Pygame documentation: https://www.pygame.org/docs/ (дата обращения: 20.03.2025)
Documentation - Home Page [Электронный ресурс]. – Pygame GUI documentation: https://pygame-gui.readthedocs.io/en/latest/ (дата обращения: 20.03.2025)
DroidCam. Phone as Webcam[Электронный ресурс] // DroidCam. — 2025. — URL: https://droidcam.app/ (дата обращения: 18.04.2025)
Universal Robots UR3: Universal Robots UR3 [Электронный ресурс] // RoboDK. — URL: https://robodk.com/robot/Universal-Robots/UR3 (дата обращения: 10.05.2025)
Robot Operating System (ROS): Robot Operating System (ROS) [Электронный ресурс] // ROS.org. — URL: https://www.ros.org/ (дата обращения: 10.05.2025)
MoveIt Motion Planning Framework: MoveIt Motion Planning Framework [Электронный ресурс] // MoveIt. — URL: https://moveit.ai/ (дата обращения: 14.05.2025