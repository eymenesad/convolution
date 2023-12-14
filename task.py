import cache_module
import numpy 

import utils
# Prepare an RGB image containing 3 colour channels.
image = utils.load_image("photom.jpg")
"""image = numpy.array([
    [[10, 20, 30], [40, 50, 60], [70, 80, 90], [100, 110, 120], [130, 140, 150]],
    [[160, 170, 180], [190, 200, 210], [220, 230, 240], [250, 10, 20], [30, 40, 50]],
    [[60, 70, 80], [90, 100, 110], [120, 130, 140], [150, 160, 170], [180, 190, 200]],
    [[210, 220, 230], [240, 250, 10], [20, 30, 40], [50, 60, 70], [80, 90, 100]]
], dtype=numpy.int64)"""

ROW = len(image)#1024
COL = len(image[0])#2048
print(ROW)
print(COL)
print()
print()
Channel = 3
#image = numpy.random.randint(0, 256, size=(ROW, COL, Channel), 
#dtype=numpy.int64)

# Prepare a mask for the convolution operation.
mask_size = 3
up = 10
down = -10
#mask = numpy.random.randint(down, up + 1, size=(mask_size, mask_size), 
#dtype=numpy.int64)
mask = numpy.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]])
# Prepare an empty result image. You will fill this empty array with your 
# code.
result = numpy.zeros([ROW, COL, Channel], dtype=numpy.int64)

# Configuration for the cache simulator module.
l3 = ["L3", 16384, 16, 64, "LRU"]
l2 = ["L2", 4096, 8, 64, "LRU"]
l1 = ["L1", 1024, 4, 64, "LRU"]
m = 256 * 1024 * 1024
cm = cache_module.cache_module(l1, l2, l3, m)

###### WRITE YOUR CODE BELOW. ######

# 1. Load the image into the memory

# Write each 64-bit value from the RGB image array to memory
for row in range(ROW):
    for col in range(COL):
        for channel in range(Channel):
            value = (image[row, col, channel] & 0xFF).astype(numpy.int8)

            
            cm.write((row * COL * Channel + col * Channel + channel), value)

            #if row==1 and col==1 and channel==0:
            #    print(cm.read(row * COL * Channel + col * Channel + channel))            

# Finish the cache operations

# 2. Traverse the image array and apply the mask. Write the results into 
# the memory through the write function. Do not fill the result array in 
# this step.
# Apply convolution by reading image values from memory and writing results back to memory
offset_value = ROW*COL*Channel
for i in range(0, ROW):
    for j in range(0, COL):
        for k in range(Channel):
            # Read values from memory and reconstruct the 64-bit value
            val1=0
            val2=0
            val3=0
            val4=0
            val5= cm.read(i * COL * Channel + j * Channel + k)
            #if (i==1 and j==1 and k ==0):
            #    print("val5:", val5)
            val6=0
            val7=0
            val8=0
            val9=0

            if i!=0 and j!=0:
                val1 = cm.read((i - 1) * COL * Channel + (j - 1) * Channel + k)
            if i !=0:
                val2 = cm.read((i - 1) * COL * Channel + j * Channel + k)
            if i!=0 and j != COL-1:
                val3 = cm.read((i - 1) * COL * Channel + (j + 1) * Channel + k)
            if j!=0:
                val4 = cm.read(i * COL * Channel + (j - 1) * Channel + k)
            if j!= COL-1:
                val6 = cm.read(i * COL * Channel + (j + 1) * Channel + k)
            if i != ROW-1 and j != 0:
                val7 = cm.read((i + 1) * COL * Channel + (j - 1) * Channel + k)
            if i!= ROW-1:
                val8 = cm.read((i + 1) * COL * Channel + j * Channel + k)
            if i!= ROW-1 and j!= COL-1:
                val9 = cm.read((i + 1) * COL * Channel + (j + 1) * Channel + k)

            vals = [[val1,val2,val3],[val4,val5,val6],[val7,val8,val9]]
            


            convolution_result = 0
            for mask1 in range(3):
                for mask2 in range(3):
                    convolution_result += vals[mask1][mask2] * mask[mask1][mask2]
            
            #print(i,j,k,convolution_result)
            

            # Store each byte in the memory (use 8 elements for one 64-bit value)
            for ib in range(8):
                cm.write(offset_value + (i * COL * Channel + j * Channel + k) * 8 + ib, ((convolution_result >> ib*8) & 0xFF))

# Finish the cache operations

# 3. Load the result image from memory through the read function.
for rowi in range(ROW):
    for coli in range(COL):
        for channeli in range(Channel):
            read_value = 0
            for rb in range(8):
                byte_value = cm.read(offset_value + (rowi * COL * Channel + coli * Channel + channeli) * 8 + rb)

                # Construct the 64-bit result by shifting and ORing the bytes
                read_value |= (byte_value << (rb * 8))
                #read_value |= cm.read((rowi * COL * Channel + coli * Channel + channeli)*8 + rb)
                            #read_value |= cm.read((rowi * COL * Channel + coli * Channel + channeli)*8 + rb)
            result[rowi, coli, channeli] = read_value

###### WRITE YOUR CODE ABOVE. ######
#print(result)
utils.save_image(result,"new_image.jpg")

cm.finish()