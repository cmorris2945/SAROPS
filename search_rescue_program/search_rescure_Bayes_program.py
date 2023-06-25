import sys
import random
import itertools
import numpy as np
import cv2 as cv
import matplotlib.pyplot as plt
import sys
from PIL import Image

MAP_FILE = "C:\\Users\\chris' pc\\PycharmProjects\\pythonProject2\\pythonProject\\SAR_project\\search_rescue_program\\site_4.png"

#img = Image.open(MAP_FILE)
#img.save("search_rescue_program/site_4.png", "jpeg")

SA1_CORNERS = (130, 265, 180, 315)
SA2_CORNERS = (80, 255, 130, 305)
SA3_CORNERS = (105, 205, 155, 255)


class Search():
    def __init__(self, name):
        self.name = name
        self.img = cv.imread(MAP_FILE, cv.IMREAD_COLOR)
        if self.img is None:
            print("Could not load map file {}".format(MAP_FILE), file=sys.stderr)
            sys.exit(1)

        self.area_actual = 0
        self.sailor_actual = [0, 0]

        self.sa1 = self.img[SA1_CORNERS[1]:SA1_CORNERS[3], SA1_CORNERS[0]:SA1_CORNERS[2]]
        self.sa2 = self.img[SA2_CORNERS[1]:SA2_CORNERS[3], SA2_CORNERS[0]:SA2_CORNERS[2]]
        self.sa3 = self.img[SA3_CORNERS[1]:SA3_CORNERS[3], SA3_CORNERS[0]:SA3_CORNERS[2]]

        self.p1 = 0.2
        self.p2 = 0.5
        self.p3 = 0.3

        self.sep1 = 0
        self.sep2 = 0
        self.sep3 = 0

    def draw_map(self, last_known, search_coords, scale_factor=0.5):
        img_copy = self.img.copy()

        # Draw search areas
        cv.rectangle(img_copy, (SA1_CORNERS[0], SA1_CORNERS[1]),
                    (SA1_CORNERS[2], SA1_CORNERS[3]), (0, 0, 0), 1)
        cv.rectangle(img_copy, (SA2_CORNERS[0], SA2_CORNERS[1]),
                    (SA2_CORNERS[2], SA2_CORNERS[3]), (0, 0, 0), 1)
        cv.rectangle(img_copy, (SA3_CORNERS[0], SA3_CORNERS[1]),
                    (SA3_CORNERS[2], SA3_CORNERS[3]), (0, 0, 0), 1)

        # Draw last known position as a cross
        scaled_last_known = (int(last_known[0] * scale_factor), int(last_known[1] * scale_factor))
        cv.drawMarker(img_copy, scaled_last_known, (0, 0, 255), cv.MARKER_CROSS, 5)

        # Draw search coordinates
        for coord in search_coords:
            x = coord[0]
            y = coord[1]
            if coord[0] < self.sa1.shape[1]:
                x += SA1_CORNERS[0]
                y += SA1_CORNERS[1]
            elif coord[0] < self.sa1.shape[1] + self.sa2.shape[1]:
                x += SA2_CORNERS[0] - self.sa1.shape[1]
                y += SA2_CORNERS[1]
            else:
                x += SA3_CORNERS[0] - self.sa1.shape[1] - self.sa2.shape[1]
                y += SA3_CORNERS[1]

            scaled_coord = (int(x * scale_factor), int(y * scale_factor))
            cv.putText(img_copy, f"({coord[0]},{coord[1]})", scaled_coord,
                    cv.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
            cv.circle(img_copy, scaled_coord, 1, (0, 255, 0), -1)  # Smallest circle size

        scaled_img = cv.resize(img_copy, None, fx=scale_factor, fy=scale_factor)
        plt.imshow(cv.cvtColor(scaled_img, cv.COLOR_BGR2RGB))
        plt.show(block=False)

    def sailor_final_location(self):
    # Define the range of coordinates near the Titanic wreck site
        x_range = range(4100, 4200)
        y_range = range(-5000, -4900)


        # Generate random coordinates within the defined range
        x = np.random.choice(x_range, 1)
        y = np.random.choice(y_range, 1)

        # Set the sailor's actual location
        self.sailor_actual = [x, y]

        return x, y


    def calc_search_effectiveness(self):
        self.sep1 = random.uniform(0.2, 0.9)
        self.sep2 = random.uniform(0.2, 0.9)
        self.sep3 = random.uniform(0.2, 0.9)

    def conduct_search(self, area_num, area_array, effectiveness_prob):
        local_y_range = range(area_array.shape[0])
        local_x_range = range(area_array.shape[1])
        coords = list(itertools.product(local_x_range, local_y_range))
        random.shuffle(coords)
        coords = coords[:int((len(coords) * effectiveness_prob))]
        loc_actual = (self.sailor_actual[0], self.sailor_actual[1])
        if area_num == self.area_actual and loc_actual in coords:
            return "WARNING! FOUND IN AREA {}!".format(area_num), coords, self.area_actual, loc_actual
        else:
            return "Negative Contact...", coords, self.area_actual, loc_actual

    def revise_target_probs(self):
        denom = self.p1 * (1 - self.sep1) + self.p2 * (1 - self.sep2) + self.p3 * (1 - self.sep3)
        if denom != 0:
            self.p1 = self.p1 * (1 - self.sep1) / denom
            self.p2 = self.p2 * (1 - self.sep2) / denom
            self.p3 = self.p3 * (1 - self.sep3) / denom


def draw_menu(search_num):
    print('\nSearch {}'.format(search_num))
    print(
        """ Welcome to 'SAROPS' choose the areas to search: 

        0 - QUIT  
        1 - Search Area 1 twice
        2 - Search Area 2 twice
        3 - Search Area 3 twice
        4 - Search Area 1 & 2
        5 - Search Area 2 & 3
        6 - Search Area 2 & 3
        7 - START OVER 

                        """
    )


def main():
    app = Search('Titanic Wreck')
    search_num = 1

    while True:
        app.calc_search_effectiveness()
        draw_menu(search_num)
        choice = input("Choice: ")

        if choice == "0":
            sys.exit()

        elif choice == "1":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2, _, _ = app.conduct_search(1, app.sa1, app.sep1)
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa1) ** 2)
            app.sep2 = 0
            app.sep3 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "2":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2, _, _ = app.conduct_search(2, app.sa2, app.sep2)
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa2) ** 2)
            app.sep2 = 0
            app.sep3 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "3":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(3, app.sa3, app.sep3)
            results_2, coords_2, _, _ = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa3) ** 2)
            app.sep2 = 0
            app.sep3 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "4":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2, _, _ = app.conduct_search(2, app.sa2, app.sep2)
            app.sep3 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "5":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(1, app.sa1, app.sep1)
            results_2, coords_2, _, _ = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "6":
            results_1, coords_1, actual_area, actual_coords = app.conduct_search(2, app.sa2, app.sep2)
            results_2, coords_2, _, _ = app.conduct_search(3, app.sa3, app.sep3)
            app.sep1 = (len(set(coords_1 + coords_2))) / (len(app.sa1) ** 2)
            app.sep2 = 0
            app.sep3 = 0
            search_coords = coords_1 + coords_2
            app.sailor_actual = actual_coords
            app.area_actual = actual_area
            app.draw_map((160, 290), search_coords)
            app.revise_target_probs()
            print("Search {} Results 2 = {}\n".format(search_num, results_2), file=sys.stderr)
            print("Updated Probabilities: P1 = {}, P2 = {}, P3 = {}\n".format(app.p1, app.p2, app.p3), file=sys.stderr)
            search_num += 1

        elif choice == "7":
            app.__init__('Titanic Wreck')
            search_num = 1
            continue

        else:
            print("\nSorry...invalid choice. Please choose again.", file=sys.stderr)
            continue


if __name__ == '__main__':
    main()








