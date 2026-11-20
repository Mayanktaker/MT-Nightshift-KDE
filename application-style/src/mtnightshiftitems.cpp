/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */

// Item views: selection and hover pills, content and frames.
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
#include <QStyleOptionViewItem>

using namespace mtstyle;

// Paints an item-view selection or hover highlight as an inset rounded pill:
// Highlight while the window is active, muted grey when inactive, faint tone
// on hover. Returns false for unselected idle items so views keep painting
// their own backgrounds.
bool MTNightshiftStyle::paintItemPill(const QStyleOption *option, QPainter *painter) const
{
    const auto *item = qstyleoption_cast<const QStyleOptionViewItem *>(option);
    if (!item || !painter) {
        return false;
    }
    const bool selected = option->state.testFlag(QStyle::State_Selected);
    const bool hovered = option->state.testFlag(QStyle::State_MouseOver);
    if (!selected && !hovered) {
        return false;
    }
    const QColor fill = stateFill(option);
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    painter->setPen(Qt::NoPen);
    painter->setBrush(fill);
    const QRectF pill = QRectF(option->rect).adjusted(kItemInsetX, kItemInsetY,
                                                      -kItemInsetX, -kItemInsetY);
    painter->drawRoundedRect(pill, qMin(kControlRadius, pill.height() / 2.0),
                             qMin(kControlRadius, pill.height() / 2.0));
    painter->restore();
    return true;
}

// Paints the item-view keyboard-focus indicator as a pill ring that follows the
// selection pill's geometry; suppressed while the item is selected, which
// already announces it. Returns true so Breeze's squarish outline never draws.

// Paints the item-view keyboard-focus indicator as a pill ring that follows the
// selection pill's geometry; suppressed while the item is selected, which
// already announces it. Returns true so Breeze's squarish outline never draws.
bool MTNightshiftStyle::paintFocusPill(const QStyleOption *option, QPainter *painter,
                                       const QWidget *widget) const
{
    const auto *focus = qstyleoption_cast<const QStyleOptionFocusRect *>(option);
    if (!focus || !painter) {
        return false;
    }
    // The pill follows an item's selection geometry. Every other focused widget
    // (a check box label, a push button) keeps its own focus indication, or the
    // ring would wrap text in a rounded capsule that matches nothing.
    const bool itemView = qobject_cast<const QAbstractItemView *>(widget)
        || (widget && qobject_cast<const QAbstractItemView *>(widget->parentWidget()));
    if (!itemView) {
        return false;
    }
    if (option->state.testFlag(QStyle::State_Selected)) {
        return true;
    }
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    const QColor accent = quietAccent(option->palette.color(QPalette::Active, QPalette::Highlight),
                                      option->palette.color(QPalette::Window));
    painter->setPen(QPen(accent, kOutlineWidth));
    painter->setBrush(Qt::NoBrush);
    const QRectF ring = QRectF(option->rect).adjusted(kItemInsetX, kItemInsetY,
                                                      -kItemInsetX, -kItemInsetY);
    painter->drawRoundedRect(ring, qMin(kControlRadius, ring.height() / 2.0),
                             qMin(kControlRadius, ring.height() / 2.0));
    painter->restore();
    return true;
}

// Paints CE_ItemViewItem content on top of our selection pill: strips the
// selected/hovered band from Breeze's rendering so only its icon and text
// remain, with the text recoloured for contrast on the accent fill.

// Paints CE_ItemViewItem content on top of our selection pill: strips the
// selected/hovered band from Breeze's rendering so only its icon and text
// remain, with the text recoloured for contrast on the accent fill.
void MTNightshiftStyle::paintItemViewContent(const QStyleOptionViewItem *option, QPainter *painter,
                                             const QWidget *widget) const
{
    QStyleOptionViewItem stripped(*option);
    stripped.state &= ~(QStyle::State_Selected | QStyle::State_MouseOver | QStyle::State_HasFocus);
    if (option->state.testFlag(QStyle::State_Selected)) {
        const auto group = colorGroup(option);
        const QColor onPill = option->palette.color(group, QPalette::HighlightedText);
        stripped.palette.setColor(QPalette::Active, QPalette::Text, onPill);
        stripped.palette.setColor(QPalette::Inactive, QPalette::Text, onPill);
    }
    baseStyle()->drawControl(QStyle::CE_ItemViewItem, &stripped, painter, widget);
}

// Paints item-view panel frames (boxed lists like Kate's sessions view) as
// dimmed rounded hairlines; Breeze frames them square and switches to a loud
// Highlight outline when focused.

// Paints item-view panel frames (boxed lists like Kate's sessions view) as
// dimmed rounded hairlines; Breeze frames them square and switches to a loud
// Highlight outline when focused.
bool MTNightshiftStyle::paintItemViewFrame(const QStyleOption *option, QPainter *painter) const
{
    const auto *frame = qstyleoption_cast<const QStyleOptionFrame *>(option);
    if (!frame || !painter) {
        return false;
    }
    if (qEnvironmentVariableIsSet("MTNS_DEBUG")) {
        std::fprintf(stderr, "MTNS-DBG item frame: shape=%d lw=%d rect=%dx%d\n", int(frame->frameShape),
                     frame->lineWidth, frame->rect.width(), frame->rect.height());
        std::fflush(stderr);
    }
    if (frame->frameShape != QFrame::StyledPanel && frame->frameShape != QFrame::Panel) {
        return false;
    }
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    const QColor windowTone = option->palette.color(QPalette::Window);
    const QColor line = blend(windowTone, option->palette.color(QPalette::WindowText), kFrameContrast);
    painter->setPen(QPen(line, kOutlineWidth));
    painter->setBrush(Qt::NoBrush);
    painter->drawRoundedRect(QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5), kTipRadius, kTipRadius);
    painter->restore();
    return true;
}
