"""A test program for the Python preprocessor.

N.B.: The code in this file is not valid Python and will not run with the
default Python interpreter. 
"""

def make_rectangle(x, y, width, height=width):
    """Returns (x, y) coordinates of rectangle corners in clockwise order."""
    return ((x, y), (x + width, y), (x + width, y + height), (x,  y + height))

if __name__ == '__main__':
    square = make_rectangle(0, 0, 100)
    rectangle = make_rectangle(0, 0, 100, 200)

    print("Square:", square)
    print("Rectangle:", rectangle)
