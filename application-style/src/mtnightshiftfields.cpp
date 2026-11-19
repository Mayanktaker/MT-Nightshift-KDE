/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */

// Field family: line edits, navigator path bars, combos and spin boxes.
#include "mtnightshiftstyle.h"
#include "stylepainting.h"
#include "stylerecognition.h"

#include <QAbstractItemView>
#include <QAbstractScrollArea>
#include <QApplication>
#include <QAbstractSpinBox>
#include <QComboBox>
#include <QCoreApplication>
#include <QDialog>
#include <QDockWidget>
#include <QLatin1StringView>
#include <QMetaObject>
#include <QLineEdit>
#include <QListView>
#include <QTableView>
#include <QTreeView>
#include <QMainWindow>
#include <QPainter>
#include <QPainterPath>
#include <QScrollBar>
#include <QStyleFactory>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionFrame>
#include <QStyleOptionSpinBox>

#include <cmath>

using namespace mtstyle;

// Paints a borderless rounded text field and lets the widget draw its own text and cursor.
bool MTNightshiftStyle::paintLineEdit(const QStyleOption *option, QPainter *painter, const QWidget *widget) const
{
    const auto *panel = qstyleoption_cast<const QStyleOptionFrame *>(option);
    if (!panel || !painter) {
        return false;
    }
    const auto *edit = qobject_cast<const QLineEdit *>(widget);
    // Editors inside combos and spin boxes sit on the container's own rounded
    // surface: paint nothing, or their square panel — Breeze fills frameless
    // editors with Base even when the container is disabled — would cover the
    // pill's corners and flatten the lifted disabled tone.
    if (edit && widget && (qobject_cast<const QComboBox *>(widget->parentWidget())
                           || qobject_cast<const QAbstractSpinBox *>(widget->parentWidget()))) {
        return true;
    }
    // Frameless fields stay exactly as Breeze draws them — except the path edit
    // inside a URL navigator, which replaces the rounded breadcrumb field when
    // clicked and must keep the same pill in both states.
    const bool navigatorField = isInsideUrlNavigator(widget);
    if (edit && !edit->hasFrame() && !navigatorField) {
        return false;
    }
    const QPalette &palette = panel->palette;
    const QPalette::ColorGroup group = colorGroup(panel);
    const bool enabled = panel->state.testFlag(State_Enabled);
    const bool focused = panel->state.testFlag(State_HasFocus) && enabled;
    const bool hovered = panel->state.testFlag(State_MouseOver) && enabled;
    const QRectF rect = QRectF(panel->rect);
    // The field reads as a tone step, not a frame: the theme's Base colour. KIO tints
    // a navigator's own Base to the toolbar shade, so both states of the path bar take
    // the input tone from the application palette and match each other.
    const QColor fill = (navigatorField || !widget) && qApp
        ? qApp->palette().color(group, QPalette::Base)
        : widget->palette().color(group, QPalette::Base);
    paintFieldSurface(painter, rect, fill, focused, hovered, palette, group);
    return true;
}

// Paints a KIO URL navigator's path bar as a borderless Sculpted field. The
// navigator draws itself through PE_FrameLineEdit, not PE_PanelLineEdit, which is
// why a plain line-edit rule never reached it.

// Paints a KIO URL navigator's path bar as a borderless Sculpted field. The
// navigator draws itself through PE_FrameLineEdit, not PE_PanelLineEdit, which is
// why a plain line-edit rule never reached it.
bool MTNightshiftStyle::paintUrlNavigatorField(const QStyleOption *option, QPainter *painter,
                                               const QWidget *widget) const
{
    if (!option || !painter || !isUrlNavigator(widget)) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const bool enabled = option->state.testFlag(State_Enabled);
    const bool focused = option->state.testFlag(State_HasFocus) && enabled;
    const bool hovered = option->state.testFlag(State_MouseOver) && enabled;
    const QRectF rect = QRectF(option->rect);
    // The theme's input tone, taken from the application palette. KIO tints the
    // navigator's own Base to the toolbar shade, which left the field with no
    // contrast at all: the rounded fill was invisible and only the corner
    // antialiasing showed, so the path bar read as "no proper roundness".
    const QColor fill = qApp ? qApp->palette().color(group, QPalette::Base)
                             : palette.color(group, QPalette::Base);
    paintFieldSurface(painter, rect, fill, focused, hovered, palette, group);
    return true;
}

// Paints a combo box — editable or not — as a borderless Sculpted field and
// delegates the arrow and the label to Breeze.

// Paints a combo box — editable or not — as a borderless Sculpted field and
// delegates the arrow and the label to Breeze.
bool MTNightshiftStyle::paintComboBox(const QStyleOptionComboBox *option, QPainter *painter,
                                      const QWidget *widget) const
{
    if (!option || !painter) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const bool focused = option->state.testFlag(State_Enabled)
        && fieldContainerFocused(option, widget);
    const bool hovered = option->state.testFlag(State_MouseOver)
        && option->state.testFlag(State_Enabled);
    const QRectF rect = QRectF(option->rect);
    // Combos that take typed text use the input tone (Base); menu-style combos
    // keep the button tone, which keeps the file dialog's two rows distinct.
    const QColor fill = option->editable ? palette.color(group, QPalette::Base)
                                         : palette.color(group, QPalette::Button);
    paintFieldSurface(painter, rect, fill, focused, hovered, palette, group);
    QStyleOption arrowOption(*option);
    arrowOption.rect = subControlRect(CC_ComboBox, option, SC_ComboBoxArrow, widget);
    baseStyle()->drawPrimitive(PE_IndicatorArrowDown, &arrowOption, painter, widget);
    baseStyle()->drawControl(CE_ComboBoxLabel, option, painter, widget);
    return true;
}

// Paints a spin box as a borderless Sculpted field with the button pair its
// symbol mode and step limits call for.

// Paints a spin box as a borderless Sculpted field with the button pair its
// symbol mode and step limits call for.
bool MTNightshiftStyle::paintSpinBox(const QStyleOptionSpinBox *option, QPainter *painter,
                                     const QWidget *widget) const
{
    if (!option || !painter) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const bool focused = option->state.testFlag(State_Enabled)
        && fieldContainerFocused(option, widget);
    const bool hovered = option->state.testFlag(State_MouseOver)
        && option->state.testFlag(State_Enabled);
    const QRectF rect = QRectF(option->rect);
    // A spin box edits typed text, so it takes the input tone like line edits;
    // a frameless editor delegate opts out, mirroring the line edit rule.
    const QColor fill = palette.color(group, QPalette::Base);
    if (option->frame) {
        paintFieldSurface(painter, rect, fill, focused, hovered, palette, group);
    }
    if (option->buttonSymbols == QAbstractSpinBox::NoButtons) {
        return true;
    }
    // Each button takes its own colour: a hit step limit mutes only its glyph.
    const QColor glyphColor = palette.color(group, QPalette::WindowText);
    const QColor mutedColor = palette.color(QPalette::Disabled, QPalette::WindowText);
    const auto buttonRect = [&](QStyle::SubControl sub) {
        return subControlRect(CC_SpinBox, option, sub, widget);
    };
    const auto buttonColor = [&](QStyle::SubControl sub) {
        const bool enabled = sub == SC_SpinBoxUp
            ? bool(option->stepEnabled & QAbstractSpinBox::StepUpEnabled)
            : bool(option->stepEnabled & QAbstractSpinBox::StepDownEnabled);
        return enabled ? glyphColor : mutedColor;
    };
    if (option->buttonSymbols == QAbstractSpinBox::PlusMinus) {
        // Qt ships no plus/minus primitive, so the glyphs are drawn by hand.
        paintPlusGlyph(painter, buttonRect(SC_SpinBoxUp), buttonColor(SC_SpinBoxUp), true);
        paintPlusGlyph(painter, buttonRect(SC_SpinBoxDown), buttonColor(SC_SpinBoxDown), false);
        return true;
    }
    paintChevron(painter, buttonRect(SC_SpinBoxUp), buttonColor(SC_SpinBoxUp), true);
    paintChevron(painter, buttonRect(SC_SpinBoxDown), buttonColor(SC_SpinBoxDown), false);
    return true;
}
