import cv2
from time import time
import numpy as np
from camera import camera_instantiator
from timers import timers
from triangulation import LSLocalizer
from predict import RecursivePolynomialFit
from visualization import PointInSpace
# from motor_control import controller_stat, move_motors_to_world_position
from lsrl_predict import solve_zeroes, quadratic_regression, linear_regression



# a lacrosse goal is a square with sidelength 6 feet (182.9 cm)
GOALDIMS = 182.9
CAM1_TO_GOAL = 0 # TODO: measure actual distance to this


def calculate_points(lsl, rays, calculated_pts):
    ray_vals = np.array(list(rays.values()))
    calculated_pt = lsl.predict(ray_vals)
    calculated_pts.append(calculated_pt)
    print(f"Calculated point: {calculated_pt}")
    return calculated_pt


def main_loop(cameras, lsl, static):
    calculated_pts = []
     
    lim_x = [-1, 1]
    lim_y = [0, 2]
    lim_z = [-0.5, 0.5]
    plotter = PointInSpace(lim_x, lim_y, lim_z)
    detection_start_time = time()   
    t = time() - detection_start_time

    detected_frames = 0
    detected_frames_cap = 30
    detected_frame_threshold = 5
    detected = False
    x_rpf = RecursivePolynomialFit(2)
    y_rpf = RecursivePolynomialFit(2)
    z_rpf = RecursivePolynomialFit(2)


    reset_time = 1
    start = time()

    # during profiling I saw that appending to a normal list is faster than
    # appending to a numpy array
    observations = {'x' : [], 'y': [], 'z': [], 'time' : []}

    # some paramenters


    
    

    while True:
        with timers.timers["Main Loop"]:
            if cv2.waitKey(1) == ord("q"):
                for camera in cameras.values():
                    camera.release_camera()
                break

            rays = {
                camera: result
                for camera in cameras.values()
                if (result := camera.run()) is not None
            }


            # reset the arrays every once in a while
            if time() - start > 0.5:
                observations = {'x' : [], 'y': [], 'z': [], 'time' : []}
                start = time()



            if rays:
                calculated_point = calculate_points(lsl, rays, calculated_pts)

                # print("Calculated point", calculated_point)


                observations['time'].append(time() - start)
                observations['x'].append(calculated_point[0])
                observations['y'].append(calculated_point[1])
                observations['z'].append(calculated_point[2])



                plotter.draw_point(calculated_point)

                # print(f"Predicted ball position: {predicted_point}")

                detected_frames += 1
            else:
                detected_frames -= 1


            
            if len(observations['y']) > 4: # have at least 4 observations to test
                # do a regression
                """
                on my computer:
                quadratic regression takes 10.199s / 100000 calls = 0.00010199s = 0.102 ms per call
                poly_predict_with_coeffs takes 19.781s / 5000000 calls = 0.0000039562 per call = 0.0039562 ms per call
                should be ok to just run a whole regression every few frames
                
                """


                time_stamps = np.array(observations['time'])
                # seems like it uses a z up coordinate system, so that one should be quadratic
                y_func, y_coeffs = linear_regression(time_stamps, np.array(observations['y']))
                x_func, x_coeffs = linear_regression(time_stamps, np.array(observations['x']))
                z_func, z_coeffs = quadratic_regression(time_stamps, np.array(observations['z']))
                print("Current functions")
                print(y_func, x_func, z_func)
                print()
                print()
                intersection_time = solve_zeroes(y_coeffs)
                if intersection_time:
                    x_predicted = x_func(intersection_time)
                    z_predicted = z_func(intersection_time)
                    print(f"Anthony x_coord prediction = {x_predicted}")
                    print(f"Anthony z_coord prediction = {z_predicted}")
                else:
                    print("Anthony Could't predict")
                print()
                print()



            
            

            detected_frames = min(max(0, detected_frames), detected_frames_cap)

            if detected_frames > detected_frame_threshold:
                detected = True
                t = time() - detection_start_time
                x_rpf.add_point(t, calculated_point[0])
                y_rpf.add_point(t, calculated_point[1])
                z_rpf.add_point(t, calculated_point[2])

                intersection_time = y_rpf.solve(0).round(3)
                x_predicted = x_rpf.plug_in(intersection_time)
                z_predicted = z_rpf.plug_in(intersection_time)

                print(f"x_coord prediction = {x_predicted}")
                print(f"z_coord prediction = {z_predicted}")



                # camera 1 is defined at origin so  the ball "in" range should be
                # dist_from_cam1_to_goal <= x <= dist_from_cam1_to_goal + 6 feet

                # check that ball is actually in frame of goal
                if CAM1_TO_GOAL <= x_predicted <= GOALDIMS + CAM1_TO_GOAL and z_predicted <= GOALDIMS:
                    move_motors_to_world_position(x_predicted, z_predicted)






            else:
                if detected:
                    detected = False
                    print(f"Detection that started at {detection_start_time}")
                    print(f"{x_rpf.get_coef().round(3) = }")
                    print(f"{y_rpf.get_coef().round(3) = }")
                    print(f"{z_rpf.get_coef().round(3) = }")
                x_rpf.reset()
                y_rpf.reset()
                z_rpf.reset()
                detection_start_time = time()


        timers.record_time("Main Loop")


def main(camera_transforms, cam_ids=None):
    static_hsv = input('Use static hsv values? (y/n): ').lower().strip() == 'y'
    cameras = camera_instantiator(cam_ids, static_hsv)
    print("Press q to release cameras and exit.\n")
    lam = 0.98
    lsl = LSLocalizer(camera_transforms)
    main_loop(cameras, lsl, static_hsv)

    cv2.destroyAllWindows()
    timers.display_averages()


if __name__ == "__main__":
    # first camera at origin
    T_cam1 = np.array(
        [
            [1, 0, 0, 0],
            [0, 1, 0, 0],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    # second camera rotated pi/2 about Z at (1, 1, 0)
    T_cam2 = np.array(
        [
            [0, -1, 0, 1],
            [1, 0, 0, 1],
            [0, 0, 1, 0],
            [0, 0, 0, 1],
        ]
    )
    camera_transforms = [T_cam1, T_cam2]

    main(camera_transforms)
