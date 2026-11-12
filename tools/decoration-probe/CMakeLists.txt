# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Builds the qsvg raster probe used by check-decoration.py. The check script
# configures and builds this into ~/.cache/mt-nightshift-probe, so repeated runs
# are incremental instead of recompiling in a throwaway directory.
cmake_minimum_required(VERSION 3.20)
project(mt-nightshift-decoration-probe LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

find_package(Qt6 REQUIRED COMPONENTS Gui)

add_executable(svg2png svg2png.cpp)
target_link_libraries(svg2png PRIVATE Qt6::Gui)
