/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */

// Control surfaces: tool buttons, tabs, menus, push buttons and meters.
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
#include <QMenu>
#include <QStyleOptionMenuItem>
#include <QStyleOptionProgressBar>
#include <QStyleOptionTab>

using namespace mtstyle;

// Paints a rounded surface for tool-button interaction states; idle delegates.
bool MTNightshiftStyle::paintToolButton(const QStyleOption *option, QPainter *painter) const
{
    if (!option || !painter || option->rect.isEmpty()) {
        return false;
    }
    const bool hovered = option->state.testFlag(QStyle::State_MouseOver);
    const bool pressed = option->state.testFlag(QStyle::State_Sunken);
    const bool checked = option->state.testFlag(QStyle::State_On);
    if (!hovered && !pressed && !checked) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const QColor windowTone = palette.color(group, QPalette::Window);
    QColor fill;
    if (pressed || checked) {
        fill = palette.color(group, QPalette::Highlight);
    } else {
        fill = blend(windowTone, palette.color(group, QPalette::WindowText), kItemHoverContrast);
    }
    const QRectF rect = QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5);
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    fillSurface(painter, rect, radius, fill);
    return true;
}

// Rounds a tab surface while leaving its label and icon to Breeze.

// Rounds a tab surface while leaving its label and icon to Breeze.
bool MTNightshiftStyle::paintTabShape(const QStyleOption *option, QPainter *painter) const
{
    const auto *tab = qstyleoption_cast<const QStyleOptionTab *>(option);
    if (!tab || !painter || tab->rect.isEmpty()) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QColor fill = option->state.testFlag(QStyle::State_Selected)
        ? stateFill(option)
        : blend(palette.color(QPalette::Window),
                palette.color(QPalette::WindowText), kItemHoverContrast);
    const QRectF rect = QRectF(tab->rect).adjusted(0.5, 0.5, -0.5, -0.5);
    const qreal radius = qMin(kControlRadius, rect.height() / 2.0);
    fillSurface(painter, rect, radius, fill);
    return true;
}

// Paints the hover/selection pill for one menu item, in the item-view tone.

// Paints the hover/selection pill for one menu item, in the item-view tone.
bool MTNightshiftStyle::paintMenuPill(const QStyleOption *option, QPainter *painter) const
{
    const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
    if (!item || !painter || item->rect.isEmpty()) {
        return false;
    }
    const QColor fill = stateFill(option);
    const QRectF rect = QRectF(item->rect).adjusted(kItemInsetX, kItemInsetY,
                                                   -kItemInsetX, -kItemInsetY);
    if (rect.isEmpty()) {
        return false;
    }
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    painter->setPen(Qt::NoPen);
    painter->setBrush(fill);
    const qreal radius = qMin(kControlRadius, rect.height() / 2.0);
    painter->drawRoundedRect(rect, radius, radius);
    painter->restore();
    return true;
}

// Owns the QMenu surface; Window fill and hairline follow the control language.

// Owns the QMenu surface; Window fill and hairline follow the control language.
bool MTNightshiftStyle::paintMenuPanel(const QStyleOption *option, QPainter *painter) const
{
    if (!option || !painter || option->rect.isEmpty()) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const QColor fill = palette.color(group, QPalette::Window);
    const QColor outline = blend(fill, palette.color(group, QPalette::WindowText), kFrameContrast);
    const QRectF rect = QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5);
    paintSurface(painter, rect, kPopupRadius, kOutlineWidth, fill, outline);
    return true;
}

// The panel's hairline is the menu edge; Breeze's square frame would undo its corners.

// The panel's hairline is the menu edge; Breeze's square frame would undo its corners.
bool MTNightshiftStyle::paintMenuFrame(const QStyleOption *option, QPainter *painter) const
{
    Q_UNUSED(option)
    Q_UNUSED(painter)
    return true;
}

// Draws our own line edit and check indicators, delegating all other primitives.

// Paints a rounded push button and lets Breeze draw its label, icon and focus state.
bool MTNightshiftStyle::paintPushButton(const QStyleOption *option, QPainter *painter, const QWidget *widget) const
{
    const auto *button = qstyleoption_cast<const QStyleOptionButton *>(option);
    // Command links keep Breeze's multi-line layout.
    if (!button || !painter || button->features.testFlag(QStyleOptionButton::CommandLinkButton)) {
        return false;
    }
    const QPalette &palette = button->palette;
    const QPalette::ColorGroup group = colorGroup(button);
    const bool enabled = button->state.testFlag(State_Enabled);
    const bool active = button->state.testFlag(State_Sunken) || button->state.testFlag(State_On);
    const bool hovered = button->state.testFlag(State_MouseOver) && enabled && !active;
    const bool focused = button->state.testFlag(State_HasFocus) && enabled;
    const bool flat = button->features.testFlag(QStyleOptionButton::Flat);
    const QRectF rect = QRectF(button->rect);
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    QColor fill = palette.color(group, QPalette::Button);
    QColor outline = blend(fill, palette.color(group, QPalette::WindowText), kFrameContrast);
    if (enabled && active) {
        fill = palette.color(group, QPalette::Highlight);
        // A pressed or checked button still needs a visible focus ring.
        outline = focused ? palette.color(group, QPalette::HighlightedText) : fill;
    } else if (focused) {
        outline = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
    } else if (hovered || button->features.testFlag(QStyleOptionButton::DefaultButton)) {
        outline = readableAccent(palette.color(group, QPalette::Highlight), fill, kOutlineContrast);
    }
    if (!flat || active || hovered || focused) {
        paintSurface(painter, rect, radius, focused ? kFocusOutlineWidth : kOutlineWidth, fill, outline);
    }
    // Keep labels, icons and menu arrows clear of the rounded corners.
    QStyleOptionButton label(*button);
    const int inset = qMin(qMax(4, qRound(radius / 2.0)), qMin(button->rect.width(), button->rect.height()) / 4);
    label.rect = button->rect.adjusted(inset, 0, -inset, 0);
    if (enabled && active) {
        label.palette.setColor(QPalette::ButtonText,
                               palette.color(group, QPalette::HighlightedText));
    }
    baseStyle()->drawControl(CE_PushButtonLabel, &label, painter, widget);
    return true;
}

// Paints a borderless rounded text field and lets the widget draw its own text and cursor.

// Paints a determinate progress meter as a rounded pill; false for busy or
// vertical bars, whose animation and layout stay with Breeze.
bool MTNightshiftStyle::paintProgressBar(const QStyleOptionProgressBar *option, QPainter *painter,
                                         const QWidget *widget) const
{
    if (!option || !painter || option->maximum == 0
        || !option->state.testFlag(QStyle::State_Horizontal)) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const QRectF rect = QRectF(option->rect);
    const qreal radius = qMin(kControlRadius, rect.height() / 2.0);
    // The groove is one tone step below the surroundings — Base against Window —
    // so a capacity meter reads as a soft inset instead of a black slab.
    const QColor groove = blend(palette.color(group, QPalette::Window),
                                palette.color(group, QPalette::Base), 0.5);
    fillSurface(painter, rect, radius, groove);
    const qreal span = option->maximum - option->minimum;
    const qreal done = qBound<qreal>((option->progress - option->minimum) / span, 0.0, 1.0);
    if (done > 0.0) {
        const QRectF fillRect = rect.adjusted(0, 0, -rect.width() * (1.0 - done), 0);
        const qreal fillRadius = qMin(qMin(kControlRadius, fillRect.height() / 4.0),
                                      fillRect.width() / 2.0);
        fillSurface(painter, fillRect, fillRadius, palette.color(group, QPalette::Highlight));
    }
    if (option->textVisible && !option->text.isEmpty()) {
        painter->save();
        painter->setPen(palette.color(group, QPalette::Text));
        painter->drawText(rect, Qt::AlignCenter, option->text);
        painter->restore();
    }
    return true;
}
