from MoCapDB import MoCapDB
import numpy as np

def split_list(alist, wanted_parts=1):
    length = len(alist)
    return [ alist[i*length // wanted_parts: (i+1)*length // wanted_parts] 
             for i in range(wanted_parts) ]

def getTrack(path,mID):
	scene_scale = 1
	track = MoCapDB(path, scene_scale)
  
	markerID = mID
	start = 0
	end = track.numframes()
	step = 1
  
	coords = track.getMarkerData(markerID, start, end, step)
	data = np.array(split_list(coords, wanted_parts=len(coords)/3))

	return data

def DTW(nt, it, num):
    matrix = []    
    
    for i in range (num):
        ntrack = getTrack (nt, i)
        itrack = getTrack (it, i)
       
		# Dynamic Time Warping 
        distances = np.zeros((len(itrack), len(ntrack)))
        
        for i in range(len(itrack)):
            for j in range(len(ntrack)):
                distances[i,j] = np.linalg.norm(ntrack[j]-itrack[i])
        		
        accumulated_cost = np.zeros((len(itrack), len(ntrack)))
        for i in range(1, len(itrack)):
            for j in range(1, len(ntrack)):
                accumulated_cost[i, j] = min(accumulated_cost[i-1, j-1], accumulated_cost[i-1, j], accumulated_cost[i, j-1]) + distances[i, j]
        		
        path = [[len(ntrack)-1, len(itrack)-1]]
        i = len(itrack)-1
        j = len(ntrack)-1
        
        while i>0 and j>0:
            if i==0:
                j = j - 1
            elif j==0:
                i = i - 1
            else:
                if accumulated_cost[i-1, j] == min(accumulated_cost[i-1, j-1], accumulated_cost[i-1, j], accumulated_cost[i, j-1]):
                    i = i - 1
                elif accumulated_cost[i, j-1] == min(accumulated_cost[i-1, j-1], accumulated_cost[i-1, j], accumulated_cost[i, j-1]):
                    j = j-1
                else:
                    i = i - 1
                    j= j- 1
            path.append([j, i])
        path.append([0,0])
        
        dist = []
        for [y, x] in path:
            dist.append(distances[x, y])  
        
        l = list(reversed(dist))
    
        matrix.append(l)
    return zip(*matrix)

# distances table
table = DTW("20150820_Alex0003.txt","20150820_Alex0013.txt", 21)

# example: print distances of frame 383
print (table[383])