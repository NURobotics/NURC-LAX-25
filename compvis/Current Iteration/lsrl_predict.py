import numpy as np
import cProfile, pstats
from timers import timers

def solve_zeroes(coeffs: np.array):
    """
    finds a root for a linear equation
    or the largest root for a parabola if it exists

    returns None if it doesn't exist
    """


    if coeffs.shape[0] == 3:
        c = coeffs[2]
        b = coeffs[1]
        a = coeffs[0]

        determinant = b ** 2 - 4 * a * c
        if determinant < 0:
            return None
        
        front = -b / (2 * a)
        other = (determinant ** 0.5) / (2 * a)
        


        return max(front + other, front - other)
    else:
        a = 0
        b = coeffs[0]
        c = coeffs[1]

        # y = bx + c
        # 0 = bx + c
        # -c/b = x
        if abs(b) < 10 ** -7: # since floatin point is finicky I would elect to not do exaclty zero
            return None
        return -c / b

    
    

def linear_regression(times: np.array, values: np.array):
    """
    Arguments
    -----------
    times: series of time stamps
    values: mesurements associated with those timestamps

    Returns
    ----------
    (polynomial, coeffs)

    """


    z = np.polyfit(times, values, 1)
    return np.poly1d(z), z

def quadratic_regression(times: np.array, values: np.array):
    z = np.polyfit(times, values, 2)
    return np.poly1d(z), z


def poly_predict_with_coeffs(coeffs: np.array, time_val: float):

    return np.dot(coeffs, [time_val ** b for b in range(coeffs.shape[0])][::-1]     )



def generate_data(num_entries=50):

    times = np.random.rand(num_entries)

    targets = 9.8 * times ** 2 + 6

    return np.array(times), np.array(targets) 


def main():
    


    errors = [0, 0]

    loops = 100_000
    num_data = 50
    for _ in range(loops):
        times, targets = generate_data(num_data)
        func, coeffs = quadratic_regression(times, targets)

        for i in times:


            prediction = poly_predict_with_coeffs(coeffs, i)
            error = abs(9.8 * i ** 2 + 6 - prediction)
            errors[0] += error
            

            prediction = func(i)
            error = abs(9.8 * i ** 2 + 6 - prediction)
            errors[1] += error
        
    print(errors[0] / (loops * num_data))
    print(errors[1] / (loops * num_data))


if __name__ == '__main__':

    if input('Profile? (y/n) ') in ['yes', 'y', 'YES']:
        profiler = cProfile.Profile()
        profiler.enable()
        # with timers.timers["regression"]:
        #     main()
        # timers.record_time("regression")

        
        main()
        profiler.disable()
        stats = pstats.Stats(profiler).sort_stats('time')
        stats.print_stats()



    times = np.random.rand(500)
    targets = -10 * times + 5
    func, coeffs = linear_regression(times, targets)

    print(solve_zeroes(coeffs))

    times = np.random.rand(500)
    targets = -10 * (times ** 2) + 5
    func, coeffs = quadratic_regression(times, targets)

    print(solve_zeroes(coeffs))
    
# timers.display_averages()