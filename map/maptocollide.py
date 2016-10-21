from pygame import *

name = input("Please enter a map name to convert: ")
infile = image.load(name + "collision.png")
outfile = open(name + ".txt", "w")

for y in range(infile.get_height()):
    for x in range(infile.get_width()):
        if infile.get_at((x, y)) == (0, 0, 0):
            outfile.write("1")
        else:
            outfile.write("0")
        if x == infile.get_width()-1:
            outfile.write("\n")

outfile.close()

            
