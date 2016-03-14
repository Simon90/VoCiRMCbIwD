# MoCapDB.py
# Two convenience classes useful for reading and storing data read 
# from a mocap data (.txt) sourced from,
#        http://accad.osu.edu/research/mocap/mocap_data.htm
# Useage:
#    ___________________________________________________
#    from MoCapDB import MoCapDB
#    db = MoCapDB('PATH_TO_MOCAP_DATA_FILE', 0.01)
#    coords = db.getMarkerData(2, 1, 10, 1)
#    # Do something with the coordinates of the marker (index 2)
#     # for frames 1 to 10.
#    ___________________________________________________
# Malcolm Kesson
# October 27 2012
# revised Nov 5 2012 - additional error checking, swapping z/y coords
#----------------------------------------------------------    
# Stores a column of coordinates read from a mocap data (.txt) file.
# Instances of this class are used by the MoCapDB class.
class MoCapMarker:
    SCALE = 1.0
    MIN =  10000000.0
    MAX = -10000000.0
    ERROR = '-9999.99'
    def __init__(self, identifier):
        self.name = identifier
        self.data = [] # a list of lists of xyz values
    def getname(self):
        return self.name
    def append(self, x,y,z):
        if (x == MoCapMarker.ERROR or
            y == MoCapMarker.ERROR or 
            z == MoCapMarker.ERROR):
            self.data.append([])
        else:
            # Note we swap the y and z coordinates
            self.data.append( [float(x) * MoCapMarker.SCALE,
                               float(z) * MoCapMarker.SCALE,
                               float(y) * MoCapMarker.SCALE] )
    def getdata(self, frame):
        if len(self.data) == 0:
            return []
        else:
            return self.data[frame]
    def getBbox(self):
        minx = miny = minz = MoCapMarker.MIN
        maxx = maxy = maxz = MoCapMarker.MAX
        if len(self.data) == 0:
            return []
        for coords in self.data:
            if len(coords) == 0:
                return []
            minx = min(minx, coords[0])
            miny = min(miny, coords[1])
            minz = min(minz, coords[2])
            maxx = max(maxx, coords[0])
            maxy = max(maxy, coords[1])
            maxz = max(maxz, coords[2])
        return [minx,miny,minz,maxx,maxy,maxz]
                
#----------------------------------------------------------    
class MoCapDB:
    def __init__(self, datafile, scaling):
        MoCapMarker.SCALE = scaling
        # Read the mocap date file
        f = open(datafile, 'r')
        data_in = f.readlines()
        f.close()
  
        # Get the names of the markers from the first line of text.
        text = data_in.pop(0)
        items = text.split()[2:]    # 'slice' the first two items
        self.names = []
        for n in range(0, len(items), 3):
            self.names.append(items[n][0:-2]) # Ignore ':X',':Y',':Z'
        self.frames = len(data_in)  # Number of 'Fields'
        self.markers = []           # Instances of MoCapMarker
        self.bbox_width = 0         # x axis
        self.bbox_height = 0        # y axis
        self.bbox_length = 0        # z axis
        self.getdata(data_in)
    
    # The input is a list of rows of data. Each row consists 
    # of list of coordinates - generally 120 values per line.
    def getdata(self, data_in):
        # Get instances of our MoCapMarker.Marker class
        for name in self.names:
            self.markers.append(MoCapMarker(name))
            
        # Process each row of data and add the data to the markers.
        for row in data_in:
            data = row.split()[2:] # Ignore the values of Field & Time
            index = 0
            for n in range(0, len(data), 3):
                self.markers[index].append(data[n], data[n+1], data[n+2])
                index += 1
    # Given a frame number, getFrameData() returns a list of 
    # coordinates of all the markers.
    def getFrameData(self, frame):
        out = []
        for m in self.markers:
            data = m.getdata(frame)
            if len(data) > 0:
                out.append(data)
        return out
	# Given the index of a marker, getMarkerData() returns a list of
    # coordinates for the specified frame range (begin to end).
    def getMarkerData(self, index, begin, end, step):
        out = []
        marker = self.markers[index]
        if begin == end:
            end = begin + step
            step = 1
        for frame in range(begin, end, step):
            data = marker.getdata(frame)
            if len(data) > 0:
                out.extend(data)
        return out
    # Returns a list of the names of the markers.
    def getnames(self):
        return self.names
    # Returns the number of markers.
    def nummarkers(self):
        return len(self.markers)
    # Returns the number of frames (ie. Fields)
    def numframes(self):
        return self.frames
    def getBbox(self):
        minx = miny = minz = MoCapMarker.MIN
        maxx = maxy = maxz = MoCapMarker.MAX
        for m in self.markers:
            bbox = m.getBbox()
            if len(bbox) > 0:
                minx = min(minx, bbox[0])
                miny = min(miny, bbox[1])
                minz = min(minz, bbox[2])
                maxx = max(maxx, bbox[0])
                maxy = max(maxy, bbox[1])
                maxz = max(maxz, bbox[2])
        self.bbox_width =  abs(maxx - minx)
        self.bbox_height = abs(maxy - miny)
        self.bbox_length = abs(maxz - minz)
        return [minx,miny,minz,maxx,maxy,maxz]