/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#pragma once

#include <QColor>
#include <QPalette>
#include <QPainter>
#include <QRectF>
#include <QStyle>
#include <QStyleOption>
#include <QWidget>

namespace mtstyle
{
// Shared maximum radius for Qt control surfaces and their interaction states.
constexpr qreal kControlRadius = 10.0;
// Popup containers keep their existing outside corner radius.
constexpr qreal kPopupRadius = 15.0;
// Tooltips follow the Plasma tooltip radius from design.md section 6, not the
// control radius, so app tooltips match the shell's tooltips.
constexpr qreal kTipRadius = 6.0;
// WCAG non-text contrast for state outlines; focus must read brighter than hover.
constexpr qreal kOutlineContrast = 3.0;
constexpr qreal kFocusContrast = 5.0;
// Share of the surface tone mixed in when a disabled control must look muted.
constexpr qreal kDisabledMute = 0.65;
// Frame-line strength: design.md section 6/8 frameContrast token.
constexpr qreal kFrameContrast = 0.2;
// How far a disabled field steps off the page tone. Mixed from the *enabled*
// Window/WindowText pair so the step points away from the surface on both
// variants: a lift on Nightshift, a recess on Dayshift. Blending the two muted
// disabled tones instead collapsed on light (Window and Button differ by only
// 5/255 there), leaving the field indistinguishable from the page.
constexpr qreal kDisabledLift = 0.075;
// Hairline contrast for disabled fields: dimmer than the resting outline so a
// greyed-out group stays quiet, but present enough to keep the shapes legible.
constexpr qreal kDisabledOutlineContrast = 0.25;
// Indicator corners scale with their size; the quiet hairline matches a field edge.
constexpr qreal kIndicatorOutlineContrast = 0.07;
// State outline thickness in logical pixels; the focus ring stays 1px and reads
// crisp, with its visibility carried by the contrast token instead of weight.
constexpr qreal kOutlineWidth = 1.0;
constexpr qreal kFocusOutlineWidth = 1.0;
// Item-view pills are inset from the row edges so selections read as cards
// rather than full-width bands, and hover stays fainter than selection.
constexpr qreal kItemInsetX = 4.0;
constexpr qreal kItemInsetY = 1.0;
constexpr qreal kItemHoverContrast = 0.07;
constexpr qreal kItemInactiveContrast = 0.12;
// Tab strips need three distinguishable steps: an idle surface Breeze's own tab
// shape never provides, a hover step, and the selected accent fill. Idle keeps
// the 7% the flat single tone used, so tabs stay readable as tabs; hover rises
// to 13%, which is a visible step without competing with the selected accent.
constexpr qreal kTabIdleContrast = 0.07;
constexpr qreal kTabHoverContrast = 0.13;
// Tool buttons carry monochrome symbolic icons whose colour follows the theme
// ink, and a QIcon pixmap cannot be recoloured from a style option. Their active
// state is therefore a tint of the accent towards the window tone, deep enough
// to read as "on" and light enough that the theme's own ink — text and icon
// alike — keeps its contrast. A saturated accent fill puts those icons at
// 2.23-2.31:1 on Nord Night, Nord Day and One Dark Pro.
constexpr qreal kToolStateTint = 0.55;
// Menu separators are inset so they do not cut the 15px menu corner; the line
// is quieter than the panel hairline because it sits inside the surface.
constexpr qreal kMenuSeparatorContrast = 0.14;
constexpr qreal kMenuSeparatorInset = 8.0;
// Scroll bar gutter in logical pixels. Breeze spends 21px on a gutter its 8px
// handle never fills, so a 12px gutter keeps the same handle, hover states and
// drag length while reading considerably slimmer.
constexpr int kSlimScrollBarExtent = 12;
// Corner radius Dolphin hardcodes for its compact status card
// ("drawRoundedRect(opt.rect, 5, 5)" in DolphinStatusBar::paintEvent); the card
// frame must follow it or the border squares off the rounded fill.
constexpr qreal kStatusCardRadius = 5.0;
qreal relativeLuminance(const QColor &color);
qreal contrastRatio(const QColor &first, const QColor &second);
QColor blend(const QColor &first, const QColor &second, qreal t);
QColor readableAccent(const QColor &accent, const QColor &surface, qreal target);
QPalette::ColorGroup colorGroup(const QStyleOption *option);
void paintSurface(QPainter *painter, const QRectF &rect, qreal radius, qreal outlineWidth,
                  const QColor &fill, const QColor &outline);
void fillSurface(QPainter *painter, const QRectF &rect, qreal radius, const QColor &fill);
bool fieldContainerFocused(const QStyleOption *option, const QWidget *widget);
void paintFieldSurface(QPainter *painter, const QRectF &rect, const QColor &fill, bool focused,
                       bool hovered, const QPalette &palette, QPalette::ColorGroup group);
void paintStatusCardFrame(const QStyleOption *option, QPainter *painter);
void paintChevron(QPainter *painter, const QRectF &rect, const QColor &color, bool up);
void paintPlusGlyph(QPainter *painter, const QRectF &rect, const QColor &color, bool plus);
void paintMark(QPainter *painter, const QRectF &rect, const QColor &color, bool radio, bool partial);
QColor stateFill(const QStyleOption *option);
bool usesAccentFill(const QStyleOption *option);
} // namespace mtstyle
