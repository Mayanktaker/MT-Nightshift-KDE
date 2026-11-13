# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
# SPDX-License-Identifier: LGPL-2.0-or-later
#
# MT Nightshift Qt Application Style plugin (Sculpted control radius over Breeze).

cmake_minimum_required(VERSION 3.16)

project(mtnightshiftstyle VERSION 1.3.0 LANGUAGES CXX)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)
set(CMAKE_CXX_EXTENSIONS OFF)
set(CMAKE_AUTOMOC ON)

# No ECM dependency: deployment goes through the Makefile's explicit install
# paths, so plain GNUInstallDirs covers the target rules.
include(GNUInstallDirs)

# 6.4 keeps CI (ubuntu-24.04) able to build the plugin; no newer API is used.
find_package(Qt6 6.4 REQUIRED COMPONENTS Widgets)

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
    LIBRARY DESTINATION ${CMAKE_INSTALL_LIBDIR}/qt6/plugins/styles
)

# Widget style metadata read by KStyle to fill the application-style list.
install(FILES kstyle/themes/mtnightshift.themerc
    DESTINATION ${CMAKE_INSTALL_DATADIR}/kstyle/themes
)
