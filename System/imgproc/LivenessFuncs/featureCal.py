import numpy,time

def leftshift(origin, digit):
    #int *LSnumber = new int[digit];
    LSnumber = numpy.zeros(digit)
    for i in range(0,digit):
        LSnumber[(i + digit - 1) % digit] = origin[i]
        pass
    return LSnumber

def dec2bin(num,bit):
    base = [str(x) for x in range(10)] + [chr(x) for x in range(ord('A'), ord('A') + 6)]
    mid = []
    while True:
        if num == 0:
            break
        num,rem = divmod(num, 2)
        mid.append(base[rem])
    if mid == []:
        mid = [0]
    binNum = int(''.join([str(x) for x in mid[::-1]]))
    bins = numpy.zeros(bit)
    for i in range(0,bit):
        bins[bit-i-1] = binNum%10
        binNum = int(binNum/10)
    return bins



def getmapping(samples, mappingtype):
    GetMap = {'table': [], 'sample': 0, 'num': 0}
    tableIndexMax = pow(2, samples)
    GetMap['table'] = numpy.zeros(tableIndexMax)
    newMax = 0  # number of patterns in the resulting LBP code
    index = 0
    if (mappingtype == 1):
        newMax = samples * (samples - 1) + 3
        for i in range(0, tableIndexMax):
            # for (int i = 0; i < tableIndexMax; i++) {
            i_bin = dec2bin(i, samples)
            j_bin = leftshift(i_bin, samples)
            numt = 0
            for j in range(0,samples):
                #for (int j = 0; j < samples; j++)
                if i_bin[j] != j_bin[j]:
                    numt+=1
            if numt <= 2:
                GetMap['table'][i] = index
                index = index + 1
            else:
                GetMap['table'][i] = newMax - 1
            # }

    elif mappingtype == 2:
        pass
    elif mappingtype == 3:
        pass
    GetMap['num'] = newMax
    GetMap['sample'] = samples
    return GetMap;


def LBP_Column(pic, radius, neighbors, map, mode):
    spoints = numpy.zeros([8,2])
    a = 2 * numpy.pi / neighbors
    bins = 512
    for i in range(0, 8):
        spoints[i][0] = -radius * numpy.sin((i) * a)
        spoints[i][1] = radius * numpy.cos((i) * a)
    #miny = maxy = spoints[0][0]
    #minx = maxx = spoints[0][1]
    maxy = max(spoints[:,0])
    miny = min(spoints[:,0])
    maxx = max(spoints[:,1])
    minx = min(spoints[:,1])

    #for i in range(0, 8):
    #    if spoints[i][0] > maxy:
    #        maxy = spoints[i][0]
    #    if spoints[i][0] < miny:
    #        miny = spoints[i][0]
    #    if spoints[i][1] > maxx:
    #        maxx = spoints[i][1]
    #    if spoints[i][1] < miny:
    #        miny = spoints[i][1]
    bsizey = numpy.ceil(max(maxy, 0)) - numpy.floor(min(miny, 0)) + 1
    bsizex = numpy.ceil(max(maxx, 0)) - numpy.floor(min(minx, 0)) + 1
    origy = 1 - numpy.floor(min(miny, 0))
    origx = 1 - numpy.floor(min(minx, 0))
    dx = 32 - bsizex
    dy = 32 - bsizey
    origin=numpy.zeros([30,30])
    result = numpy.zeros([30,30])
    x = 0
    y = 0
    origin[0:30,0:30] = pic[1:31,1:31]

    for t in range (0,8):
        y = int(spoints[t][0] + origy-1)
        x = int(spoints[t][1] + origx-1)
        fy = int(numpy.floor(y))
        cy = int(numpy.ceil(y))
        ry = int(numpy.round(y))
        fx = int(numpy.floor(x))
        cx = int(numpy.ceil(x))
        rx = int(numpy.round(x))
        if (abs(x - rx) < 1e-6) and (abs(y - ry) < 1e-6):
            temp = numpy.array(pic[y:(30+y),x:(30+x)])
            result += numpy.dot(temp>origin,pow(2,t))
        else:
            ty = y - fy
            tx = x - fx
            w1 = (1 - tx) * (1 - ty)
            w2 = tx * (1 - ty)
            w3 = (1 - tx) * ty
            w4 = tx * ty
            temp = w1*pic[fy:(30+fy),fx:(30+fx)]+ w2 * pic[fy:(30+fy),fx:(30+cx)]+ w3 * pic[fy:(30+cy),fx:(30+fx)]+ w4 * pic[fy:(30+cy),fx:(30+cx)]
            result += numpy.dot(temp>origin,pow(2,t))
    ans = numpy.zeros(59)
    bins = map['num']

    #tempRes.

    for i in range (0,30):
        for j in range (0,30):
            tempRes = int(result[i][j])
            result[i][j] = map['table'][tempRes]
            tempRes = int(result[i][j])
            ans[tempRes]+=1;
    return ans;

def LBP_Picture (img,spoints, zero, mode_no_use) :
    neighbour = 8
    mode = 1
    miny = -1
    minx = -1
    maxx = 1
    maxy = 1
    bsizey = 3
    bsizex = 3
    origx = 1
    origy = 1
    dx = 117
    dy = 141
    origin=numpy.zeros([128,144])
    #temp=origin.copy()
    result = numpy.zeros([128,144])
    x = 0
    y = 0
    origin = img[1:129,1:145]
    '''for i in range(0, 142):
		for ii in range(0,118):
			origin[i][ii] = img.at<cv::Vec3b>(i + 1, ii + 1)[2];
			result[i][ii] = 0'''

    for t in range(0, 8):
        y = spoints[t][0] + origy
        x = spoints[t][1] + origx
        temp = numpy.array(img[y:y+128,x:x+144])
        result += numpy.dot(temp > origin, pow(2, t))


        '''for ii in range (0, 144):
            for i in range (0,128):
                temp[i][ii] = img[i + y, ii + x]
                if (temp[i][ii] >= origin[i][ii]):
                    result[i][ii] += pow(2, t)'''
    return result