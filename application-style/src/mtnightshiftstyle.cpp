/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#include "mtnightshiftstyle.h"

#include <QAbstractScrollArea>
#include <QAbstractSpinBox>
#include <QComboBox>
#include <QCoreApplication>
#include <QDialog>
#include <QDockWidget>
#include <QLatin1StringView>
#include <QLineEdit>
#include <QMainWindow>
#include <QMetaObject>
#include <QPainter>
#include <QPainterPath>
#include <QScrollBar>
#include <QStyleFactory>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionFrame>

#include <cmath>

namespace
{
// Sculpted control radius in logical pixels, clamped per control.
constexpr qreal kControlRadius = 15.0;
// WCAG non-text contrast for state outlines; focus must read brighter than hover.
constexpr qreal kOutlineContrast = 3.0;
constexpr qreal kFocusContrast = 5.0;
// Share of the surface tone mixed in when a disabled control must look muted.
constexpr qreal kDisabledMute = 0.65;
// Frame-line strength: design.md section 6/8 frameContrast token.
constexpr qreal kFrameContrast = 0.2;
// State outline thickness in logical pixels; keyboard focus doubles it.
constexpr qreal kOutlineWidth = 1.0;
constexpr qreal kFocusOutlineWidth = 2.0;
// Scroll bar gutter in logical pixels. Breeze spends 21px on a gutter its 8px
// handle never fills, so a 12px gutter keeps the same handle, hover states and
// drag length while reading considerably slimmer.
constexpr int kSlimScrollBarExtent = 12;
// Application name Dolphin reports for its own windows; the zero scroll bar
// extent is scoped to this name so no other application loses a scroll bar.
constexpr QLatin1StringView kDolphinApplicationName = QLatin1StringView("dolphin");
// Public class name of the Places sidebar view (KIO::KFilePlacesView), matched
// from the QObject meta-object so no KIO or Dolphin headers are linked here.
constexpr QLatin1StringView kPlacesViewClassName = QLatin1StringView("KFilePlacesView");
// Public class name of KIO's URL path bar (KIO::KUrlNavigator). Dolphin's own
// path bar is a subclass of it, so one name covers both.
constexpr QLatin1StringView kUrlNavigatorClassName = QLatin1StringView("KUrlNavigator");

// Compares one meta-object class name with an expected class name, ignoring any
// namespace prefix.
bool matchesClassName(const char *className, QLatin1StringView expected)
{
    const QLatin1StringView name(className);
    const qsizetype separator = name.lastIndexOf(QLatin1StringView("::"));
    const QLatin1StringView shortName = separator < 0 ? name : name.mid(separator + 2);
    return shortName.compare(expected) == 0;
}

// Compares one meta-object class name with the public Places view class name.
bool isPlacesViewClassName(const char *className)
{
    return matchesClassName(className, kPlacesViewClassName);
}

// True when the widget is a KIO URL path bar, including Dolphin's own subclass.
bool isUrlNavigator(const QWidget *widget)
{
    if (!widget) {
        return false;
    }
    for (const QMetaObject *meta = widget->metaObject(); meta; meta = meta->superClass()) {
        if (matchesClassName(meta->className(), kUrlNavigatorClassName)) {
            return true;
        }
    }
    return false;
}

// Finds the scroll area that owns a scroll bar; Qt nests scroll bars in an
// internal container widget directly below their QAbstractScrollArea.
const QWidget *scrollAreaOf(const QWidget *widget)
{
    if (!widget) {
        return nullptr;
    }
    if (!qobject_cast<const QScrollBar *>(widget)) {
        // Style metrics are also asked about the scroll area itself.
        return qobject_cast<const QAbstractScrollArea *>(widget);
    }
    for (const QWidget *ancestor = widget->parentWidget(); ancestor;
         ancestor = ancestor->parentWidget()) {
        if (qobject_cast<const QAbstractScrollArea *>(ancestor)) {
            return ancestor;
        }
        if (ancestor->isWindow()) {
            break;
        }
    }
    return nullptr;
}

// True when the view is Dolphin's own Places sidebar: the process must be
// Dolphin, the view must inherit the public KFilePlacesView, and a view hosted
// in a dialog (Dolphin's own file dialog) keeps its scroll bar.
bool isDolphinPlacesView(const QWidget *view)
{
    if (!view || QCoreApplication::applicationName() != kDolphinApplicationName) {
        return false;
    }
    // Walk the inheritance chain so a Dolphin wrapper class still matches.
    bool isPlacesView = false;
    for (const QMetaObject *meta = view->metaObject(); meta; meta = meta->superClass()) {
        if (isPlacesViewClassName(meta->className())) {
            isPlacesView = true;
            break;
        }
    }
    if (!isPlacesView) {
        return false;
    }
    for (const QWidget *ancestor = view->parentWidget(); ancestor;
         ancestor = ancestor->parentWidget()) {
        if (qobject_cast<const QDialog *>(ancestor)) {
            return false;
        }
    }
    return true;
}

// True when the widget is Dolphin's Places sidebar scroll bar or its scroll area.
bool isDolphinPlacesScrollBar(const QWidget *widget)
{
    return isDolphinPlacesView(scrollAreaOf(widget));
}

// True when the widget is Dolphin's own main window hosting the Places sidebar.
// Only that window loses its dock separator; every other application, and every
// dialog, keeps Breeze's separator line.
bool isDolphinShellWindow(const QWidget *widget)
{
    if (!widget || QCoreApplication::applicationName() != kDolphinApplicationName) {
        return false;
    }
    const auto *mainWindow = qobject_cast<const QMainWindow *>(widget);
    if (!mainWindow) {
        return false;
    }
    const auto docks = mainWindow->findChildren<QDockWidget *>(QString(), Qt::FindDirectChildrenOnly);
    for (const QDockWidget *dock : docks) {
        const auto views = dock->findChildren<QWidget *>();
        for (const QWidget *view : views) {
            if (isDolphinPlacesView(view)) {
                return true;
            }
        }
    }
    return false;
}

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
    const auto mix = [t](qreal a, qreal b) { return a + (b - a) * t; };
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
    return option->state.testFlag(QStyle::State_Active) ? QPalette::Active : QPalette::Inactive;
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
} // namespace

// Builds the style on the installed Breeze style, or the native style when absent.
MTNightshiftStyle::MTNightshiftStyle() : QProxyStyle(QStyleFactory::create(QStringLiteral("Breeze"))) {}

// Draws our own line edit and check indicators, delegating all other primitives.
void MTNightshiftStyle::drawPrimitive(PrimitiveElement element, const QStyleOption *option, QPainter *painter,
                                      const QWidget *widget) const
{
    switch (element) {
    case PE_PanelLineEdit:
        if (paintLineEdit(option, painter, widget)) {
            return;
        }
        break;
    case PE_FrameLineEdit:
        // KIO's URL navigator paints its path bar through this frame primitive.
        if (paintUrlNavigatorField(option, painter, widget)) {
            return;
        }
        break;
    case PE_IndicatorCheckBox:
        paintIndicator(option, painter, false);
        return;
    case PE_IndicatorRadioButton:
        paintIndicator(option, painter, true);
        return;
    case PE_IndicatorDockWidgetResizeHandle:
        // Dolphin's Places sidebar edge: keep the grab strip, drop the printed line.
        if (option && painter && isDolphinShellWindow(widget)) {
            painter->fillRect(option->rect, option->palette.color(QPalette::Window));
            return;
        }
        break;
    default:
        break;
    }
    QProxyStyle::drawPrimitive(element, option, painter, widget);
}

// Draws our own push buttons, delegating every other control element.
void MTNightshiftStyle::drawControl(ControlElement element, const QStyleOption *option, QPainter *painter,
                                    const QWidget *widget) const
{
    if (element == CE_PushButton && paintPushButton(option, painter, widget)) {
        return;
    }
    QProxyStyle::drawControl(element, option, painter, widget);
}

// Draws our own non-editable combo boxes, delegating every other complex control.
void MTNightshiftStyle::drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                                           QPainter *painter, const QWidget *widget) const
{
    if (control == CC_ComboBox) {
        const auto *combo = qstyleoption_cast<const QStyleOptionComboBox *>(option);
        if (combo && paintComboBox(combo, painter, widget)) {
            return;
        }
    }
    QProxyStyle::drawComplexControl(control, option, painter, widget);
}

// Narrows every scroll bar gutter and leaves Dolphin's Places sidebar without one.
int MTNightshiftStyle::pixelMetric(PixelMetric metric, const QStyleOption *option,
                                   const QWidget *widget) const
{
    if (metric == PM_ScrollBarExtent) {
        // A zero extent alone removes the bar: Qt 6.11 sizes scroll bars from
        // QScrollBar::sizeHint(), and a 0-wide bar leaves the layout entirely.
        if (isDolphinPlacesScrollBar(widget)) {
            return 0;
        }
        // Never widen a base style that is already slimmer than the target.
        return qMin(kSlimScrollBarExtent, QProxyStyle::pixelMetric(metric, option, widget));
    }
    return QProxyStyle::pixelMetric(metric, option, widget);
}

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
bool MTNightshiftStyle::paintLineEdit(const QStyleOption *option, QPainter *painter, const QWidget *widget) const
{
    const auto *panel = qstyleoption_cast<const QStyleOptionFrame *>(option);
    if (!panel || !painter) {
        return false;
    }
    // Frameless fields stay exactly as Breeze draws them. The option's line width
    // cannot tell them apart, because Breeze reports a zero PM_DefaultFrameWidth
    // for framed edits too, so the widget's own frame flag is the reliable test.
    const auto *edit = qobject_cast<const QLineEdit *>(widget);
    if (edit && !edit->hasFrame()) {
        return false;
    }
    // Editable combos and spin boxes own a child edit that Breeze already frames.
    if (widget && (qobject_cast<QComboBox *>(widget->parentWidget())
                   || qobject_cast<QAbstractSpinBox *>(widget->parentWidget()))) {
        return false;
    }
    const QPalette &palette = panel->palette;
    const QPalette::ColorGroup group = colorGroup(panel);
    const bool focused = panel->state.testFlag(State_HasFocus)
        && panel->state.testFlag(State_Enabled);
    const QRectF rect = QRectF(panel->rect);
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    // The field reads as a tone step, not a frame: the palette's own Base colour,
    // so a widget that tints its option palette (KUrlNavigator swaps Base for
    // AlternateBase) cannot make the unframed field disappear into its toolbar.
    const QColor fill = widget ? widget->palette().color(group, QPalette::Base)
                               : palette.color(group, QPalette::Base);
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
    } else {
        fillSurface(painter, rect, radius, fill);
    }
    return true;
}

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
    const bool focused = option->state.testFlag(State_HasFocus)
        && option->state.testFlag(State_Enabled);
    const QRectF rect = QRectF(option->rect);
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    // Same input surface as every other field: the widget's own Base tone, not the
    // AlternateBase tint the navigator puts in its frame option.
    const QColor fill = widget->palette().color(group, QPalette::Base);
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
    } else {
        fillSurface(painter, rect, radius, fill);
    }
    return true;
}

// Paints the combo frame and delegates the arrow and the label to Breeze.
bool MTNightshiftStyle::paintComboBox(const QStyleOptionComboBox *option, QPainter *painter,
                                      const QWidget *widget) const
{
    // Editable combos keep Breeze's field and arrow arrangement.
    if (!option || !painter || option->editable) {
        return false;
    }
    const QPalette &palette = option->palette;
    const QPalette::ColorGroup group = colorGroup(option);
    const bool enabled = option->state.testFlag(State_Enabled);
    const bool focused = option->state.testFlag(State_HasFocus) && enabled;
    const QRectF rect = QRectF(option->rect);
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    const QColor fill = palette.color(group, QPalette::Button);
    // Same rule as text fields: filled and rounded, with the outline reserved for focus.
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
    } else {
        fillSurface(painter, rect, radius, fill);
    }
    QStyleOption arrowOption(*option);
    arrowOption.rect = subControlRect(CC_ComboBox, option, SC_ComboBoxArrow, widget);
    baseStyle()->drawPrimitive(PE_IndicatorArrowDown, &arrowOption, painter, widget);
    baseStyle()->drawControl(CE_ComboBoxLabel, option, painter, widget);
    return true;
}

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
    const QRectF rect = QRectF(option->rect);
    const qreal shortest = qMin(rect.width(), rect.height());
    const qreal radius = radio ? shortest / 2.0 : qMin(kControlRadius, shortest / 4.0);
    QColor fill = palette.color(group, QPalette::Base);
    QColor outline = blend(fill, palette.color(group, QPalette::WindowText), kFrameContrast);
    if (marked) {
        fill = palette.color(group, QPalette::Highlight);
        outline = fill;
        if (!enabled) {
            fill = outline = blend(fill, palette.color(group, QPalette::Base), kDisabledMute);
        }
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
