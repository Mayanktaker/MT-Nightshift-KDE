# © Mayanktaker Computers & Web Development | https://mayanktaker.com
# SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
# SPDX-License-Identifier: LGPL-2.0-or-later
#
# Entry points for the theme. `make check` is what CI and the pre-commit hook run;
# `make apply` is the full user-local install-and-select sequence, including the
# two steps Plasma does not persist for us (frameContrast and the decoration
# borders KWin caches until it restarts).

SHELL := /bin/bash

# Named variants: one row per look. `make apply VARIANT=nord-day` selects it,
# `make apply-dayshift` and friends are aliases over the same variable.
VARIANT ?= nightshift
VARIANTS := nightshift dayshift nord-night nord-day
nightshift_STYLE := mt-nightshift
nightshift_SCHEME := MT-Nightshift
nightshift_DECORATION := __aurorae__svg__MTNightshift
dayshift_STYLE := mt-dayshift
dayshift_SCHEME := MT-Dayshift
dayshift_DECORATION := __aurorae__svg__MTDayshift
nord-night_STYLE := mt-nord-night
nord-night_SCHEME := MT-Nord-Night
nord-night_DECORATION := __aurorae__svg__MTNordNight
nord-day_STYLE := mt-nord-day
nord-day_SCHEME := MT-Nord-Day
nord-day_DECORATION := __aurorae__svg__MTNordDay

ifeq ($(filter $(VARIANT),$(VARIANTS)),)
  $(error unknown VARIANT '$(VARIANT)'; use one of: $(VARIANTS))
endif

LIVE_STYLE := $($(VARIANT)_STYLE)
LIVE_SCHEME := $($(VARIANT)_SCHEME)
LIVE_DECORATION := $($(VARIANT)_DECORATION)
# The LAF package id is derived, so a style rename cannot leave it behind.
LIVE_LAF := com.mayanktaker.$(LIVE_STYLE).desktop

AURORAE_DIR := $(HOME)/.local/share/aurorae/themes
DESKTHEME_DIR := $(HOME)/.local/share/plasma/desktoptheme
LF_DIR := $(HOME)/.local/share/plasma/look-and-feel
PROBE_CACHE := $(or $(XDG_CACHE_HOME),$(HOME)/.cache)/mt-nightshift-probe
MOC := $(shell pkg-config --variable=libexecdir Qt6Core)/moc
QT_CFLAGS := $(shell pkg-config --cflags Qt6Widgets)
QT_LIBS := $(shell pkg-config --libs Qt6Widgets)

.PHONY: all decoration check check-style check-dpr2 style style-preview apply apply-dayshift apply-nord-night apply-nord-day apply-install style-install verify-live clean

all: check

# Regenerate all four registered variants from PARAMS (the SVGs are build artefacts).
decoration:
	python3 tools/decoration-probe/build-decoration.py --all
	@for f in themes/aurorae/*/decoration.svg; do xmllint --noout "$$f" || exit 1; done

# Fail if the committed SVG drifted from its generator, the raster invariants
# broke, or the rendered field family regressed.
check:
	python3 tools/decoration-probe/build-decoration.py --check
	python3 tools/decoration-probe/check-buttons.py
	./tools/decoration-probe/check-decoration.py
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTDayshift/decoration.svg
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTNordNight/decoration.svg
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTNordDay/decoration.svg
	@for f in themes/aurorae/*/*.svg; do xmllint --noout "$$f" || exit 1; done
	./tools/theme-audit/check-theme.py
	./tools/plasma-theme/dialog-frame.py --check
	./tools/plasma-theme/applet-background.py --check
	$(MAKE) check-style
	@echo "all theme checks passed"

# Render the field family under the built style offscreen once per scheme and
# assert the pill language, the 1px ring, the free-space meter and the 12px
# scroll-bar gutter against that scheme's reference tones (SCHEMES in
# tools/style-probe/check-style.py). GitHub Actions sets GITHUB_ACTIONS=true,
# which passes --ci and skips the two Breeze-dependent assertions; a local run
# keeps them, whatever CI the shell happens to export.
# The active scheme file is not refreshed by plasma-apply-lookandfeel once it
# exists, so apply reinstalls it explicitly before selecting the theme.
SCHEME_DIR := $(HOME)/.local/share/color-schemes
STYLE_CHECK_ARGS := $(if $(GITHUB_ACTIONS),--ci,)
STYLE_SCHEMES := MT-Nightshift MT-Dayshift MT-Nord-Night MT-Nord-Day

check-style: style
	@mkdir -p build/style-probe
	$(MOC) tools/style-probe/status-card-widget.h -o build/style-probe/moc-status-card.cpp
	g++ -fPIC -std=c++17 -O2 $(QT_CFLAGS) -Itools/style-probe \
		tools/style-probe/render-fields.cpp build/style-probe/moc-status-card.cpp \
		-o build/style-probe/render-fields $(QT_LIBS)
	@set -e; for scheme in $(STYLE_SCHEMES); do \
		mkdir -p build/style-probe/out-$$scheme; \
		QT_QPA_PLATFORM=offscreen ./build/style-probe/render-fields MTNightshift \
			build/style-probe/out-$$scheme color-schemes/$$scheme.colors \
			$(CURDIR)/build/style/mtnightshiftstyle.so >/dev/null; \
		python3 tools/style-probe/check-style.py build/style-probe/out-$$scheme \
			$(STYLE_CHECK_ARGS) --scheme $$scheme; \
	done

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

# Install into user-local KDE paths and select VARIANT's theme in the running
# session. All four variants stay installed; only the selection moves.
apply: check apply-install
	plasma-apply-lookandfeel -a $(LIVE_LAF)
	kwriteconfig6 --file kdeglobals --group KDE --key frameContrast 0.05
	gdbus call --session --dest org.kde.KWin --object-path /KWin --method org.kde.KWin.reconfigure
	$(MAKE) verify-live VARIANT=$(VARIANT)
	@echo "$(VARIANT) applied; restart the session to pick up any Padding* change"

# Thin aliases: the lookup table above is the only place a mapping is spelled out.
apply-dayshift:
	@$(MAKE) apply VARIANT=dayshift

apply-nord-night:
	@$(MAKE) apply VARIANT=nord-night

apply-nord-day:
	@$(MAKE) apply VARIANT=nord-day

# Values Plasma and KWin keep in user config rather than in the packages, plus the
# deployed copies. `make check` cannot see any of this: plasma-apply-lookandfeel
# resets [KDE] frameContrast on every run, and a stale system plugin or theme
# directory keeps rendering the previous build. Run after apply/apply-install.
verify-live:
	@bad=0; \
	seam=$$(kreadconfig6 --file kdeglobals --group KDE --key frameContrast --default none); \
	[ "$$seam" = "0.05" ] || { echo "FAIL [KDE] frameContrast=$$seam, want 0.05 (make apply)"; bad=1; }; \
	scheme=$$(kreadconfig6 --file kdeglobals --group General --key ColorScheme --default none); \
	[ "$$scheme" = "$(LIVE_SCHEME)" ] || { echo "FAIL active scheme=$$scheme, want $(LIVE_SCHEME)"; bad=1; }; \
	style=$$(kreadconfig6 --file plasmarc --group Theme --key name --default none); \
	[ "$$style" = "$(LIVE_STYLE)" ] || { echo "FAIL Plasma Style=$$style, want $(LIVE_STYLE)"; bad=1; }; \
	decoration=$$(kreadconfig6 --file kwinrc --group org.kde.kdecoration2 --key theme --default none); \
	[ "$$decoration" = "$(LIVE_DECORATION)" ] || { echo "FAIL decoration=$$decoration, want $(LIVE_DECORATION)"; bad=1; }; \
	cmp -s color-schemes/$(LIVE_SCHEME).colors $(SCHEME_DIR)/$(LIVE_SCHEME).colors || { echo "FAIL installed scheme differs from the repo (make apply-install)"; bad=1; }; \
	diff -r themes/$(LIVE_STYLE) $(DESKTHEME_DIR)/$(LIVE_STYLE) >/dev/null || { echo "FAIL installed Plasma Style differs from the repo (make apply-install)"; bad=1; }; \
	if [ -f build/style/mtnightshiftstyle.so ]; then \
		cmp -s build/style/mtnightshiftstyle.so /usr/lib64/qt6/plugins/styles/mtnightshiftstyle.so || { echo "FAIL system plugin differs from build/style (make style-install)"; bad=1; }; \
	fi; \
	[ $$bad -eq 0 ] && echo "live session matches the theme"

# Install every variant package user-locally without changing the selection.
apply-install:
	install -d $(AURORAE_DIR)/MTNightshift $(AURORAE_DIR)/MTDayshift \
		$(AURORAE_DIR)/MTNordNight $(AURORAE_DIR)/MTNordDay
	install -m 644 themes/aurorae/MTNightshift/* $(AURORAE_DIR)/MTNightshift/
	install -m 644 themes/aurorae/MTDayshift/* $(AURORAE_DIR)/MTDayshift/
	install -m 644 themes/aurorae/MTNordNight/* $(AURORAE_DIR)/MTNordNight/
	install -m 644 themes/aurorae/MTNordDay/* $(AURORAE_DIR)/MTNordDay/
	install -m 644 color-schemes/MT-Nightshift.colors color-schemes/MT-Dayshift.colors \
		color-schemes/MT-Nord-Night.colors color-schemes/MT-Nord-Day.colors $(SCHEME_DIR)/
	# Copied whole, never a file list: an explicit list silently missed new slots
	# twice (the palette, then widgets/background).
	@set -e; for style in mt-nightshift mt-dayshift mt-nord-night mt-nord-day; do \
		install -d $(DESKTHEME_DIR)/$$style; \
		cp -r themes/$$style/. $(DESKTHEME_DIR)/$$style/; \
	done
	@set -e; for package in mt-nightshift-global mt-dayshift-global \
			mt-nord-night-global mt-nord-day-global; do \
		kpackagetool6 --type Plasma/LookAndFeel -i themes/$$package || \
			kpackagetool6 --type Plasma/LookAndFeel -u themes/$$package; \
	done

# Drop the cached probe binary so the next check rebuilds from scratch.
clean:
	rm -rf $(PROBE_CACHE)
