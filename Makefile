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
VARIANTS := nightshift dayshift nord-night nord-day one-dark-pro
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
one-dark-pro_STYLE := mt-one-dark-pro
one-dark-pro_SCHEME := MT-One-Dark-Pro
one-dark-pro_DECORATION := __aurorae__svg__MTOneDarkPro

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
QT_PLUGIN_DIR := $(shell qtpaths6 --query QT_INSTALL_PLUGINS 2>/dev/null)
QT_INSTALL_PREFIX := $(shell qtpaths6 --query QT_INSTALL_PREFIX 2>/dev/null)
KSTYLE_THEME_DIR := $(QT_INSTALL_PREFIX)/share/kstyle/themes

.PHONY: all decoration check check-style check-dpr2 check-kpackages check-math style style-preview wallpapers package release-check apply apply-dayshift apply-nord-night apply-nord-day apply-one-dark-pro apply-install uninstall style-install style-uninstall verify-live clean

all: check

# Regenerate all five registered variants from PARAMS (the SVGs are build artefacts).
decoration:
	python3 tools/decoration-probe/build-decoration.py --all
	@for f in themes/aurorae/*/decoration.svg; do xmllint --noout "$$f" || exit 1; done

# Generate all wallpapers across the five variants from source masters.
wallpapers:
	./tools/wallpapers/build-wallpapers.py

# Build distributable tarballs for KDE Store and user releases in dist/
package:
	./tools/packaging/build-packages.py
	./tools/packaging/build-packages.py --check

# Pre-tag gate: everything `package` proves, plus the checks a release must not
# skip. Run this before `git tag`, so version drift is caught locally instead of
# in the release workflow, which only learns about it after the tag is public.
release-check: check
	@./tools/theme-audit/check-theme.py >/dev/null
	@$(MAKE) --no-print-directory package
	@echo
	@echo "release-check passed. Version: $$(./tools/packaging/build-packages.py --version)"
	@echo "Next: git tag -a v$$(./tools/packaging/build-packages.py --version) -m '...'"
	@echo "      git push && git push origin v$$(./tools/packaging/build-packages.py --version)"

# Fail if the committed SVG drifted from its generator, the raster invariants
# broke, or the rendered field family regressed.
check:
	python3 tools/decoration-probe/build-decoration.py --check
	python3 tools/decoration-probe/check-buttons.py
	./tools/decoration-probe/check-decoration.py
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTDayshift/decoration.svg
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTNordNight/decoration.svg
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTNordDay/decoration.svg
	./tools/decoration-probe/check-decoration.py themes/aurorae/MTOneDarkPro/decoration.svg
	@for f in themes/aurorae/*/*.svg; do xmllint --noout "$$f" || exit 1; done
	./tools/theme-audit/check-theme.py
	./tools/plasma-theme/dialog-frame.py --check
	./tools/plasma-theme/applet-background.py --check
	./tools/wallpapers/build-wallpapers.py --check
	$(MAKE) check-kpackages
	$(MAKE) check-math
	$(MAKE) check-style
	@echo "all theme checks passed"

# Install every Look-and-Feel package into a throwaway XDG_DATA_HOME, which is
# the check kpackagetool6 performs on a real system. The skip is explicit so CI
# on an image without kpackagetool6 cannot look like a pass.
check-kpackages:
	@if ! command -v kpackagetool6 >/dev/null 2>&1; then \
		echo "kpackagetool6 not installed; Look-and-Feel validation skipped"; \
		exit 0; \
	fi; \
	tmp=$$(mktemp -d); trap 'rm -rf "$$tmp"' EXIT; \
	for package in mt-nightshift-global mt-dayshift-global mt-nord-night-global \
			mt-nord-day-global mt-one-dark-pro-global; do \
		XDG_DATA_HOME="$$tmp" kpackagetool6 --type Plasma/LookAndFeel \
			-i "themes/$$package" >/dev/null || { \
			echo "FAIL: kpackagetool6 rejected $$package"; exit 1; }; \
	done; \
	for id in com.mayanktaker.mt-nightshift.desktop com.mayanktaker.mt-dayshift.desktop \
			com.mayanktaker.mt-nord-night.desktop com.mayanktaker.mt-nord-day.desktop \
			com.mayanktaker.mt-one-dark-pro.desktop; do \
		test -f "$$tmp/plasma/look-and-feel/$$id/metadata.json" || { \
			echo "FAIL: $$id not installed"; exit 1; }; \
	done; \
	echo "5 Look-and-Feel packages install cleanly"

# Colour-math unit checks over the shared helpers, independent of rendering.
check-math:
	@mkdir -p build/style-probe
	g++ -fPIC -std=c++17 -O2 $(QT_CFLAGS) -Iapplication-style/src \
		tools/style-probe/check-math.cpp application-style/src/stylepainting.cpp \
		-o build/style-probe/check-math $(QT_LIBS)
	QT_QPA_PLATFORM=offscreen ./build/style-probe/check-math

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
STYLE_SCHEMES := MT-Nightshift MT-Dayshift MT-Nord-Night MT-Nord-Day MT-One-Dark-Pro

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

# The corner border is reinforced by a second pass on the same 1px band because a 1px annulus only
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
	@test -n "$(QT_PLUGIN_DIR)" || { echo "FAIL qtpaths6 did not report QT_INSTALL_PLUGINS"; exit 1; }
	@test -n "$(QT_INSTALL_PREFIX)" || { echo "FAIL qtpaths6 did not report QT_INSTALL_PREFIX"; exit 1; }
	sudo install -d "$(QT_PLUGIN_DIR)/styles" "$(KSTYLE_THEME_DIR)"
	sudo install -m 755 build/style/mtnightshiftstyle.so "$(QT_PLUGIN_DIR)/styles/mtnightshiftstyle.so"
	sudo install -m 644 application-style/kstyle/themes/mtnightshift.themerc "$(KSTYLE_THEME_DIR)/mtnightshift.themerc"
	cmp -s build/style/mtnightshiftstyle.so "$(QT_PLUGIN_DIR)/styles/mtnightshiftstyle.so"
	@echo "installed; Qt plugin: $(QT_PLUGIN_DIR)/styles; KStyle metadata: $(KSTYLE_THEME_DIR)"

# Install into user-local KDE paths and select VARIANT's theme in the running
# session. All five variants stay installed; only the selection moves.
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

apply-one-dark-pro:
	@$(MAKE) apply VARIANT=one-dark-pro

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
		plugin_dir="$$(qtpaths6 --query QT_INSTALL_PLUGINS 2>/dev/null)/styles"; \
		cmp -s build/style/mtnightshiftstyle.so "$$plugin_dir/mtnightshiftstyle.so" || { echo "FAIL system plugin differs from build/style (make style-install)"; bad=1; }; \
	fi; \
	[ $$bad -eq 0 ] && echo "live session matches the theme"

# Install every variant package user-locally without changing the selection.
apply-install:
	install -d $(AURORAE_DIR)/MTNightshift $(AURORAE_DIR)/MTDayshift \
		$(AURORAE_DIR)/MTNordNight $(AURORAE_DIR)/MTNordDay $(AURORAE_DIR)/MTOneDarkPro
	install -m 644 themes/aurorae/MTNightshift/* $(AURORAE_DIR)/MTNightshift/
	install -m 644 themes/aurorae/MTDayshift/* $(AURORAE_DIR)/MTDayshift/
	install -m 644 themes/aurorae/MTNordNight/* $(AURORAE_DIR)/MTNordNight/
	install -m 644 themes/aurorae/MTNordDay/* $(AURORAE_DIR)/MTNordDay/
	install -m 644 themes/aurorae/MTOneDarkPro/* $(AURORAE_DIR)/MTOneDarkPro/
	install -m 644 color-schemes/MT-Nightshift.colors color-schemes/MT-Dayshift.colors \
		color-schemes/MT-Nord-Night.colors color-schemes/MT-Nord-Day.colors \
		color-schemes/MT-One-Dark-Pro.colors $(SCHEME_DIR)/
	# Copied whole, never a file list: an explicit list silently missed new slots
	# twice (the palette, then widgets/background).
	@set -e; for style in mt-nightshift mt-dayshift mt-nord-night mt-nord-day \
			mt-one-dark-pro; do \
		install -d $(DESKTHEME_DIR)/$$style; \
		cp -r themes/$$style/. $(DESKTHEME_DIR)/$$style/; \
	done
	@set -e; for package in mt-nightshift-global mt-dayshift-global \
			mt-nord-night-global mt-nord-day-global mt-one-dark-pro-global; do \
		kpackagetool6 --type Plasma/LookAndFeel -i themes/$$package || \
			kpackagetool6 --type Plasma/LookAndFeel -u themes/$$package; \
	done

# Remove every package apply-install placed in the user's home. The active
# selection is left alone; Plasma falls back to Breeze the next time it starts.
uninstall:
	@test -n "$(HOME)" || { echo "FAIL HOME is not set"; exit 1; }
	@set -e; for style in mt-nightshift mt-dayshift mt-nord-night mt-nord-day \
			mt-one-dark-pro; do rm -rf -- "$(DESKTHEME_DIR)/$$style"; done
	rm -f -- $(SCHEME_DIR)/MT-Nightshift.colors $(SCHEME_DIR)/MT-Dayshift.colors \
		$(SCHEME_DIR)/MT-Nord-Night.colors $(SCHEME_DIR)/MT-Nord-Day.colors \
		$(SCHEME_DIR)/MT-One-Dark-Pro.colors
	@set -e; for theme in MTNightshift MTDayshift MTNordNight MTNordDay \
			MTOneDarkPro; do rm -rf -- "$(AURORAE_DIR)/$$theme"; done
	@set -e; for laf in com.mayanktaker.mt-nightshift.desktop \
			com.mayanktaker.mt-dayshift.desktop \
			com.mayanktaker.mt-nord-night.desktop \
			com.mayanktaker.mt-nord-day.desktop \
			com.mayanktaker.mt-one-dark-pro.desktop; do \
		if command -v kpackagetool6 >/dev/null 2>&1; then \
			kpackagetool6 --type Plasma/LookAndFeel -r "$$laf" >/dev/null 2>&1 || true; \
		fi; \
		rm -rf -- "$(LF_DIR)/$$laf"; \
	done
	@echo "removed the MT user-local packages; select Breeze in System Settings to switch back"

# Remove the system-wide Qt style plugin and its metadata (requires sudo).
style-uninstall:
	@test -n "$(QT_PLUGIN_DIR)" || { echo "FAIL qtpaths6 did not report QT_INSTALL_PLUGINS"; exit 1; }
	@test -n "$(QT_INSTALL_PREFIX)" || { echo "FAIL qtpaths6 did not report QT_INSTALL_PREFIX"; exit 1; }
	sudo rm -f -- "$(QT_PLUGIN_DIR)/styles/mtnightshiftstyle.so" "$(KSTYLE_THEME_DIR)/mtnightshift.themerc"
	@echo "removed the MTNightshift Qt style plugin; restart Qt apps"

# Drop the cached probe binary and built distribution packages.
clean:
	rm -rf $(PROBE_CACHE) dist
