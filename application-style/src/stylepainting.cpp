/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#include "stylepainting.h"

#include <QAbstractSpinBox>
#include <QComboBox>
#include <QLineEdit>
#include <QPainterPath>

#include <cmath>

namespace mtstyle
{
// WCAG 2.1 relative luminance of an opaque colour.
qreal relativeLuminance(const QColor &color)
{
    const auto linear = [](qreal channel) {
        return channel <= 0.03928 ? channel / 12.92 : std::pow((channel + 0.055) / 1.055, 2.4);
    };
    return 0.2126 * linear(color.redF()) + 0.7152 * linear(color.greenF())
        + 0.0722 * linear(color.blueF());
}

// WCAG 2.1 contrast ratio between two opaque colours.
qreal contrastRatio(const QColor &first, const QColor &second)
{
    const qreal a = relativeLuminance(first), b = relativeLuminance(second);
    return (qMax(a, b) + 0.05) / (qMin(a, b) + 0.05);
}

// Blends two colours; t = 0 keeps the first, t = 1 returns the second.
QColor blend(const QColor &first, const QColor &second, qreal t)
{
    // Clamp before mixing: QColor::fromRgbF rejects channels outside [0, 1] and
    // an invalid colour would silently paint nothing.
    const qreal weight = qBound<qreal>(0.0, t, 1.0);
    const auto mix = [weight](qreal a, qreal b) { return a + (b - a) * weight; };
    return QColor::fromRgbF(mix(first.redF(), second.redF()), mix(first.greenF(), second.greenF()),
                            mix(first.blueF(), second.blueF()));
}

// Moves an accent towards white or black until it clears the contrast target.
QColor readableAccent(const QColor &accent, const QColor &surface, qreal target)
{
    QColor current = accent;
    for (int step = 0; step < 8 && contrastRatio(current, surface) < target; ++step) {
        const QColor lighter = blend(current, Qt::white, 0.2);
        const QColor darker = blend(current, Qt::black, 0.2);
        current = contrastRatio(lighter, surface) >= contrastRatio(darker, surface) ? lighter : darker;
    }
    return current;
}

// Returns the palette group a control state should read its colours from.
QPalette::ColorGroup colorGroup(const QStyleOption *option)
{
    if (!option->state.testFlag(QStyle::State_Enabled)) {
        return QPalette::Disabled;
    }
    // KDE delegates (e.g. Dolphin's Places view) often omit State_Active on
    // selected items even in an active window; the palette's current group is
    // the reliable signal in that case.
    return option->state.testFlag(QStyle::State_Active)
        || option->palette.currentColorGroup() == QPalette::Active
        ? QPalette::Active : QPalette::Inactive;
}

// Fills a rounded Sculpted surface and keeps its state outline inside the rect.
void paintSurface(QPainter *painter, const QRectF &rect, qreal radius, qreal outlineWidth,
                  const QColor &fill, const QColor &outline)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    painter->setPen(Qt::NoPen);
    QPainterPath shape;
    shape.addRoundedRect(rect, radius, radius);
    painter->fillPath(shape, outline);
    const QRectF inner = rect.adjusted(outlineWidth, outlineWidth, -outlineWidth, -outlineWidth);
    shape.clear();
    const qreal innerRadius = qMax<qreal>(0.0, radius - outlineWidth);
    shape.addRoundedRect(inner, innerRadius, innerRadius);
    painter->fillPath(shape, fill);
    painter->restore();
}

// Fills a rounded Sculpted surface with no outline, the resting input look.
void fillSurface(QPainter *painter, const QRectF &rect, qreal radius, const QColor &fill)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    painter->setPen(Qt::NoPen);
    QPainterPath shape;
    shape.addRoundedRect(rect, radius, radius);
    painter->fillPath(shape, fill);
    painter->restore();
}

// True when a combo box or spin box reads as focused: either the container holds
// focus, or the widget in its focus chain does — editable containers put focus
// on their embedded editor, so the option state alone would miss it.
bool fieldContainerFocused(const QStyleOption *option, const QWidget *widget)
{
    if (option && option->state.testFlag(QStyle::State_HasFocus)) {
        return true;
    }
    if (!widget || !option || !option->state.testFlag(QStyle::State_Enabled)) {
        return false;
    }
    const QWidget *focused = widget->focusWidget();
    // focusWidget can be stale after focus moved out of the subtree, so the real
    // keyboard focus must be confirmed before the editor counts.
    return focused && focused != widget && focused->hasFocus()
        && qobject_cast<const QLineEdit *>(focused);
}

// Fills a field at rest, with a quiet hover outline or a stronger focus ring.
void paintFieldSurface(QPainter *painter, const QRectF &rect, const QColor &fill, bool focused,
                       bool hovered, const QPalette &palette, QPalette::ColorGroup group)
{
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
        return;
    }
    if (hovered) {
        const QColor outline = readableAccent(palette.color(group, QPalette::Highlight), fill, kOutlineContrast);
        paintSurface(painter, rect, radius, kOutlineWidth, fill, outline);
        return;
    }
    if (group == QPalette::Disabled) {
        // A disabled field keeps its shape: one tone step for the whole family
        // (Base-tone and Button-tone disabled fields otherwise vanish or go
        // near-black on settings pages) plus a dimmed hairline. The step comes
        // from the enabled tones so it keeps its direction on a light scheme.
        const QColor lifted = blend(palette.color(QPalette::Active, QPalette::Window),
                                    palette.color(QPalette::Active, QPalette::WindowText),
                                    kDisabledLift);
        const QColor outline = blend(lifted, palette.color(QPalette::Disabled, QPalette::WindowText),
                                     kDisabledOutlineContrast);
        paintSurface(painter, rect, radius, kOutlineWidth, lifted, outline);
        return;
    }
    fillSurface(painter, rect, radius, fill);
}

// Draws the compact status card's border as a hairline that follows its own
// rounding; Dolphin's clip path keeps the left and bottom border off exactly as
// it clips the card fill, so the border can never square the corners off again.
void paintStatusCardFrame(const QStyleOption *option, QPainter *painter)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    const QColor fill = option->palette.color(QPalette::Window);
    const QColor line = blend(fill, option->palette.color(QPalette::WindowText), kFrameContrast);
    painter->setPen(QPen(line, kOutlineWidth));
    painter->setBrush(Qt::NoBrush);
    painter->drawRoundedRect(QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5), kStatusCardRadius,
                             kStatusCardRadius);
    painter->restore();
}

// Draws a chevron arrow centred in the given rect, pointing up or down; used for
// spin buttons so a hit step limit can mute its glyph, which the base style's
// generic arrow primitives cannot express.
void paintChevron(QPainter *painter, const QRectF &rect, const QColor &color, bool up)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    const QPointF centre = rect.center();
    const qreal reach = qMin(rect.width(), rect.height()) * 0.26;
    const qreal apex = up ? -reach * 0.7 : reach * 0.7;
    painter->setPen(QPen(color, qMax(1.5, rect.height() / 7.0), Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));
    QPainterPath chevron;
    chevron.moveTo(centre.x() - reach, centre.y() - apex);
    chevron.lineTo(centre.x(), centre.y() + apex);
    chevron.lineTo(centre.x() + reach, centre.y() - apex);
    painter->drawPath(chevron);
    painter->restore();
}

// Draws a plus or minus centred in the given rect, the plus/minus spin symbol.
void paintPlusGlyph(QPainter *painter, const QRectF &rect, const QColor &color, bool plus)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    const QPointF centre = rect.center();
    const qreal reach = qMin(rect.width(), rect.height()) * 0.28;
    painter->setPen(QPen(color, qMax<qreal>(1.5, rect.height() / 7.0), Qt::SolidLine, Qt::RoundCap));
    painter->drawLine(centre + QPointF(-reach, 0), centre + QPointF(reach, 0));
    if (plus) {
        painter->drawLine(centre + QPointF(0, -reach), centre + QPointF(0, reach));
    }
    painter->restore();
}

// Draws the check, dash or dot mark inside an indicator rect.
void paintMark(QPainter *painter, const QRectF &rect, const QColor &color, bool radio, bool partial)
{
    painter->save();
    painter->setRenderHint(QPainter::Antialiasing, true);
    if (radio) {
        const qreal dot = qMin(rect.width(), rect.height()) * 0.24;
        painter->setPen(Qt::NoPen);
        painter->setBrush(color);
        painter->drawEllipse(rect.center(), dot, dot);
    } else if (partial) {
        painter->setPen(QPen(color, qMax(1.5, rect.height() / 7.0), Qt::SolidLine, Qt::RoundCap));
        painter->drawLine(QPointF(rect.left() + rect.width() * 0.28, rect.center().y()),
                          QPointF(rect.right() - rect.width() * 0.28, rect.center().y()));
    } else {
        painter->setPen(QPen(color, qMax(1.5, rect.height() / 7.0), Qt::SolidLine, Qt::RoundCap, Qt::RoundJoin));
        painter->setBrush(Qt::NoBrush);
        QPainterPath check;
        check.moveTo(rect.left() + rect.width() * 0.26, rect.top() + rect.height() * 0.52);
        check.lineTo(rect.left() + rect.width() * 0.44, rect.top() + rect.height() * 0.72);
        check.lineTo(rect.left() + rect.width() * 0.76, rect.top() + rect.height() * 0.30);
        painter->drawPath(check);
    }
    painter->restore();
}

// Shared hover/selection fill for pill-shaped states in menus and item views.
QColor stateFill(const QStyleOption *option)
{
    const QPalette &palette = option->palette;
    const QColor windowTone = palette.color(QPalette::Window);
    if (!option->state.testFlag(QStyle::State_Selected)) {
        return blend(windowTone, palette.color(QPalette::WindowText), kItemHoverContrast);
    }
    const bool active = option->state.testFlag(QStyle::State_Active)
        || palette.currentColorGroup() == QPalette::Active;
    if (active) {
        return palette.color(QPalette::Active, QPalette::Highlight);
    }
    return blend(windowTone, palette.color(QPalette::WindowText), kItemInactiveContrast);
}
} // namespace mtstyle
