import math


def init_space(heigh, width):
	return [[0 for x in range(width)] for x in range(heigh)]

def detect_circles(image):
	# PUT YOUR CODE HERE
	# access the image using "image[y][x]"
	# where 0 <= y < common.constants.WIDTH and 0 <= x < common.constants.HEIGHT 
	# to create an auxiliar bidimentional structure 
	# you can use "space=common.init_space(heigh, width)"
	DIMS = 200
	space=init_space(DIMS + 1, DIMS + 1)
	radius = 30**2
	threshold = 50

	for y in range(DIMS):
		for x in range(DIMS):
			if image[y][x] == 0:
				# (x - a)^2 + (y - b)^2 = r^2
				# b =  y +/- sqrt(r^2 - (x-a)^2)
				for a in range(DIMS):
					discri = radius - math.pow(x-a, 2)
					if discri >= 0:
						# square root can have positive and negative result but
						# this just doubles vote counts and doesn't change results
						b = y - math.sqrt(discri)
						if b < DIMS:
							space[a][int(b)] += 1
						


	res = 0
	# beegs = []
	for a in range(DIMS):
		for b in range(DIMS):
			# if space[a][b] > 30:
			# 	beegs.append([(a, b), space[a][b]])
			if space[a][b] >= threshold:
				res += 1
	# print(beegs)
	return res