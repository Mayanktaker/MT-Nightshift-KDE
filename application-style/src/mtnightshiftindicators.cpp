/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */

// Check and radio chips.
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

// Paints a check box or radio indicator with palette-driven fill, outline and mark.
void MTNightshiftStyle::paintIndicator(const QStyleOption *option, QPainter *painter, bool radio) const
{
    if (!option || !painter) {
        return;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const bool enabled = option->state.testFlag(State_Enabled);
    const bool marked = option->state.testFlag(State_On) || option->state.testFlag(State_NoChange);
    const bool hovered = enabled && option->state.testFlag(State_MouseOver);
    const bool focused = enabled && option->state.testFlag(State_HasFocus);
    const QRectF rect = QRectF(option->rect);
    const qreal shortest = qMin(rect.width(), rect.height());
    const qreal radius = radio ? shortest / 2.0 : qMin(kControlRadius, shortest / 4.0);
    // An indicator is a control surface, not a text well: the Button tone keeps
    // it on the same layer as the fields it sits beside.
    QColor fill = palette.color(group, QPalette::Button);
    QColor outline = blend(fill, palette.color(QPalette::Active, QPalette::WindowText),
                           kIndicatorOutlineContrast);
    if (!enabled) {
        // A disabled chip steps halfway back to the page rather than lifting
        // like a field: the muted fill is the cue, the dim hairline keeps the
        // shape, and both polarities stay distinct from the enabled chip.
        fill = blend(palette.color(QPalette::Active, QPalette::Window),
                     palette.color(QPalette::Active, QPalette::Button), 0.5);
        outline = blend(fill, palette.color(QPalette::Disabled, QPalette::WindowText),
                        kDisabledOutlineContrast);
    }
    if (marked) {
        fill = palette.color(group, QPalette::Highlight);
        outline = fill;
        if (!enabled) {
            fill = outline = blend(fill, palette.color(group, QPalette::Base), kDisabledMute);
        }
    } else if (focused) {
        // Keyboard focus lives on the chip, not in a capsule around the label.
        outline = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
    } else if (hovered) {
        outline = readableAccent(palette.color(group, QPalette::Highlight), fill, kOutlineContrast);
    }
    paintSurface(painter, rect, radius, kOutlineWidth, fill, outline);
    if (marked) {
        const QColor mark = enabled ? palette.color(group, QPalette::HighlightedText)
                                    : palette.color(group, QPalette::Text);
        paintMark(painter, rect, mark, radio, option->state.testFlag(State_NoChange));
    }
}
