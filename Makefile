# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Entry points for the theme. `make check` is what CI and the pre-commit hook run;
# `make apply` is the full user-local install-and-select sequence, including the
# two steps Plasma does not persist for us (frameContrast and the decoration
# borders KWin caches until it restarts).

SHELL := /bin/bash
DECORATION := themes/aurorae/MTNightshift/decoration.svg
AURORAE_DIR := $(HOME)/.local/share/aurorae/themes/MTNightshift
LF_DIR := $(HOME)/.local/share/plasma/look-and-feel
LOOKANDFEEL := com.mayanktaker.mt-nightshift.desktop
PROBE_CACHE := $(or $(XDG_CACHE_HOME),$(HOME)/.cache)/mt-nightshift-probe
MOC := $(shell pkg-config --variable=libexecdir Qt6Core)/moc
QT_CFLAGS := $(shell pkg-config --cflags Qt6Widgets)
QT_LIBS := $(shell pkg-config --libs Qt6Widgets)

.PHONY: all decoration check check-style check-dpr2 style style-preview apply style-install clean

all: check

# Regenerate decoration.svg from PARAMS (the SVG is a build artefact).
decoration:
	python3 tools/decoration-probe/build-decoration.py
	xmllint --noout $(DECORATION)

# Fail if the committed SVG drifted from its generator, the raster invariants
# broke, or the rendered field family regressed.
check: check-style
	python3 tools/decoration-probe/build-decoration.py --check
	./tools/decoration-probe/check-decoration.py
	@for f in themes/aurorae/MTNightshift/*.svg; do xmllint --noout "$$f" || exit 1; done
	@echo "all theme checks passed"

# Render the field family under the built style offscreen and assert the pill
# language, the 1px ring, the free-space meter and the 12px scroll-bar gutter.
# --ci (set by CI) skips the two Breeze-dependent assertions.
check-style: style
	@mkdir -p build/style-probe
	$(MOC) tools/style-probe/status-card-widget.h -o build/style-probe/moc-status-card.cpp
	g++ -fPIC -std=c++17 -O2 $(QT_CFLAGS) -Itools/style-probe \
		tools/style-probe/render-fields.cpp build/style-probe/moc-status-card.cpp \
		-o build/style-probe/render-fields $(QT_LIBS)
	QT_QPA_PLATFORM=offscreen ./build/style-probe/render-fields MTNightshift build/style-probe/out \
		color-schemes/MT-Nightshift.colors $(CURDIR)/build/style/mtnightshiftstyle.so >/dev/null
	python3 tools/style-probe/check-style.py build/style-probe/out

# The corner border is drawn `frame_line_arc` px thick because a 1px annulus only
# reaches ~half coverage per pixel at 45 degrees on a 1x display. At 2x the same
# line covers nearly every device pixel, so 1px is correct there — this target
# proves the artwork still holds on HiDPI with the 1px arc it should use.
check-dpr2:
	@mkdir -p build
	python3 tools/decoration-probe/build-decoration.py --arc 1.0 build/decoration-dpr2.svg
	./tools/decoration-probe/check-decoration.py --scale 2 build/decoration-dpr2.svg

# Build the Qt Widgets style plugin. Both the plugin and its .themerc need root to
# install (Qt has no user-local style path on this host), hence the separate target.
style:
	cmake -S application-style -B build/style -DCMAKE_BUILD_TYPE=Release
	cmake --build build/style -j4
	@echo "built build/style/mtnightshiftstyle.so"

# Run any app against the freshly built plugin without touching /usr: Qt reads
# plugins from QT_PLUGIN_PATH, and this lays out the <root>/styles/<name>.so tree it
# expects. Usage: make style-preview APP=dolphin
style-preview: style
	@mkdir -p build/style-preview/styles
	@ln -sfn "$(CURDIR)/build/style/mtnightshiftstyle.so" build/style-preview/styles/mtnightshiftstyle.so
	QT_PLUGIN_PATH="$(CURDIR)/build/style-preview" QT_STYLE_OVERRIDE=MTNightshift $(or $(APP),dolphin) &
	@echo "launched $(or $(APP),dolphin) with the freshly built plugin"

# Requires sudo: installs the plugin where QStyleFactory finds it and the display
# name where KStyle reads it. Relaunch apps afterwards; the running ones keep the
# style they started with.
style-install: style
	sudo install -m 755 build/style/mtnightshiftstyle.so /usr/lib64/qt6/plugins/styles/
	sudo install -m 644 application-style/kstyle/themes/mtnightshift.themerc /usr/share/kstyle/themes/
	@echo "installed; start a new app to see the change"

# Install into user-local KDE paths and select the theme in the running session.
apply: check
	install -m 644 themes/aurorae/MTNightshift/* $(AURORAE_DIR)/
	kpackagetool6 --type Plasma/LookAndFeel -u themes/mt-nightshift-global
	plasma-apply-lookandfeel -a $(LOOKANDFEEL)
	kwriteconfig6 --file kdeglobals --group KDE --key frameContrast 0.05
	gdbus call --session --dest org.kde.KWin --object-path /KWin --method org.kde.KWin.reconfigure
	@echo "applied; restart the session to pick up any Padding* change"

# Drop the cached probe binary so the next check rebuilds from scratch.
clean:
	rm -rf $(PROBE_CACHE)
