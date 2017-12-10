import cv2
import numpy as np

def outline_image(image, threshold_range, overdraw_lines=False, lines_thickness=1, lines_color=(255,0,0)[::-1], n_intersections=50, pixels_distance=2, min_line_length=200, max_line_gap=50):
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur_gray = cv2.GaussianBlur(gray,(5, 5),0)
    edges = cv2.Canny(blur_gray, threshold_range[0], threshold_range[1])

    lines = cv2.HoughLinesP(edges, pixels_distance, (np.pi / 180), n_intersections, np.array([]), min_line_length,max_line_gap)
    
    if len(lines) > 0:
        if overdraw_lines:

            blank_image = np.zeros(image.shape, np.uint8)

            for line in lines:
                for x1,y1,x2,y2 in line:
                    cv2.line(blank_image,(x1,y1),(x2,y2),lines_color,lines_thickness)
                    outlined_image = cv2.addWeighted(image, 0.5, blank_image, 0.5, 0)
            return outlined_image, lines

        return image, lines

    else:
        return image, []