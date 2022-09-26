import Pivot_Point
import dict_digger

##nowCandle Data Unlocking##


nowCandle = Pivot_Point.result[1]
##
##Data Open##
nowOpen = float(dict_digger.dig(nowCandle, 'mid', 'o'))
nowHigh = float(dict_digger.dig(nowCandle, 'mid', 'h'))
nowLow = float(dict_digger.dig(nowCandle, 'mid', 'l'))
nowClose = float(dict_digger.dig(nowCandle, 'mid', 'c'))
##

print('-------------------------')
print('NOW OPEN: ', nowOpen)

####DEFINICAO DE GAP DE ABERTURA####
##Entre R1 - PP / S1 - PP##
if Pivot_Point.PP <= nowOpen <= Pivot_Point.R1:
    print("R1 <-> PP")
    Grid_max = Pivot_Point.R1
    Grid_min = Pivot_Point.PP
elif Pivot_Point.S1 <= nowOpen <= Pivot_Point.PP:
    print('S1 <-> PP')
    Grid_max = Pivot_Point.PP
    Grid_min = Pivot_Point.S1
##
##Entre R1 - R2 / S1 - S2##
elif Pivot_Point.R1 <= nowOpen <= Pivot_Point.R2:
    print('R1 <-> R2')
    Grid_max = Pivot_Point.R2
    Grid_min = Pivot_Point.R1
elif Pivot_Point.S2 <= nowOpen <= Pivot_Point.S1:
    print('S1 <-> S2')
    Grid_max = Pivot_Point.S1
    Grid_min = Pivot_Point.S2
##
##Entre R2 - R3 / S2 - S3##
elif Pivot_Point.R2 <= nowOpen <= Pivot_Point.R3:
    print('R2 <-> R3')
    Grid_max = Pivot_Point.R3
    Grid_min = Pivot_Point.R2
elif Pivot_Point.S3 <= nowOpen <= Pivot_Point.S2:
    print('S2 <-> S3')
    Grid_max = Pivot_Point.S2
    Grid_min = Pivot_Point.S3
##
##ERRO##
else:
    print('ERRO COM DEFINIÇÃO DE GAP')
##
####FECHAMENTO DE DEFINICAO DE GAP DE ABERTURA####

print("-------------------------")
print("Grid_max: ", Grid_max)
print("Grid_min: ", Grid_min)

##SET GRID SCALE##
Grid_scale = 5
Grid_distance = round((Grid_max - Grid_min), 3)
Grid_sizebox = round((Grid_distance/Grid_scale),3)
##

print('GRID DISTANCE: ', Grid_distance)
print('GRID SIZEBOX: ', Grid_sizebox)


##GRID PRICES##
Grid_0 = Grid_min
Grid_1 = round(Grid_min + (1*Grid_sizebox),3)
Grid_2_channel_low = round(Grid_min + (2*Grid_sizebox) ,3)
Grid_3_channel_high = round(Grid_min + (3*Grid_sizebox), 3)
Grid_4 = round(Grid_min + (4*Grid_sizebox), 3)
Grid_5 = Grid_max
##

print('*')
print('G5: ', Grid_5)
print('G4: ', Grid_4)
print('G3CH: ', Grid_3_channel_high)
print('G2CL: ', Grid_2_channel_low)
print('G1: ', Grid_1)
print('G0: ', Grid_0)
print('*')