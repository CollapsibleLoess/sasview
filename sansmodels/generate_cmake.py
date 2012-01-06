"""
    Script to generate a CMakeLists.txt file for cmake
    
    python generate_cmake.py
    cd [your build location not in the source tree]
    cmake [path to directory containing CMakeLists.txt]
    make
    
    That will produce a library libModels.a
"""
import os
f = open("CMakeLists.txt", "w")

cmakelist = """# CMakeLists for SANS models
cmake_minimum_required (VERSION 2.6)
project (SansModels)

# Version number
set (SansModels_VERSION_MAJOR 1)
set (SansModels_VERSION_MAJOR 0)

set (SRC_FILES
"""

source_dirs = ["src/c_models",
               "src/libigor"]
excluded_src = ["c_models.cpp",
                "dispersion_visitor.cpp",
                "disperser.c",
                "winFuncs.c"]

for src_dir in source_dirs:
    for item in os.listdir(src_dir):
        if item in excluded_src:
            continue
        ext = os.path.splitext(item)[1]
        if ext in [".c",".cpp"]:
            cmakelist += "    %s\n" % os.path.join(src_dir, item)

cmakelist += "    )\n\n"    

cmakelist += "set ( INC_FILES\n"    

include_dirs = ["src/c_models",
                "src/include",
                "src/libigor"]

for inc_dir in include_dirs:
    for item in os.listdir(inc_dir):
        ext = os.path.splitext(item)[1]
        if ext in [".h",".hh"]:
            cmakelist += "    %s\n" % os.path.join(inc_dir, item)
    
cmakelist += """
)
    
include_directories (src/libigor src/include src/c_models)

# Add the target for this directory
add_library ( Models ${SRC_FILES} ${INC_FILES})
"""

f.write(cmakelist)
f.close()

    