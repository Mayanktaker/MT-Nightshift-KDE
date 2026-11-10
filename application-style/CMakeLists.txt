# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
#
# MT Nightshift Qt Application Style plugin (Sculpted control radius over Breeze).

cmake_minimum_required(VERSION 3.16)

project(mtnightshiftstyle VERSION 0.1.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_AUTOMOC ON)

find_package(ECM 6.0 REQUIRED NO_MODULE)
set(CMAKE_MODULE_PATH "${ECM_MODULE_PATH}" ${CMAKE_MODULE_PATH})
include(KDEInstallDirs)

find_package(Qt6 6.11 REQUIRED COMPONENTS Widgets)

add_library(mtnightshiftstyle MODULE
    src/mtnightshiftstyle.cpp
    src/mtnightshiftstyle.h
    src/mtnightshiftstyleplugin.cpp
    src/mtnightshiftstyleplugin.h
    src/mtnightshiftstyleplugin.json
)

target_link_libraries(mtnightshiftstyle PRIVATE Qt6::Widgets)

# Qt style plugins are loaded by metadata, not by library name.
set_target_properties(mtnightshiftstyle PROPERTIES PREFIX "")

install(TARGETS mtnightshiftstyle
    LIBRARY DESTINATION ${KDE_INSTALL_QTPLUGINDIR}/styles
)

# Widget style metadata read by KStyle to fill the application-style list.
install(FILES kstyle/themes/mtnightshift.themerc
    DESTINATION ${KDE_INSTALL_DATADIR}/kstyle/themes
)
