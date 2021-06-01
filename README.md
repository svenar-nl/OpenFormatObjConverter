# OpenFormatObjConverter
Convert OpenIV (GTA 4 & GTA 5) .odr files to Wavefront OBJ files.

Currently this is a quite crude implementation that works.

Requirements
--------------
- OpenIV
- Python 3

Tested with
--------------
- OpenIV 4.0.1
- Python 3.9.5
- ODR version 110 12 (GTA 4)
- ODR version 165 32 (GTA 5)

Usage
--------------
This script requires 1 argument, the path to the Open Format file.
For each LOD (level of detail) model in the odr file it generates a .obj and .mtl file

    OpenFormatObjConverter.py <file.odr>
    OpenFormatObjConverter.py GTA5Models/cs4_02_stuntcrash.odr

Preview
--------------
![](https://raw.githubusercontent.com/svenar-nl/OpenFormatObjConverter/master/images/preview.png)
