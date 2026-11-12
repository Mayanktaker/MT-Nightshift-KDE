/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#include "mtnightshiftstyle.h"

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
#include <QMainWindow>
#include <QMetaObject>
#include <QPainter>
#include <QPainterPath>
#include <QScrollBar>
#include <QStyleFactory>
#include <QStyleOptionButton>
#include <QStyleOptionComboBox>
#include <QStyleOptionFrame>
#include <QStyleOptionSpinBox>

#include <cmath>

namespace
{
// Sculpted control radius in logical pixels, clamped per control.
constexpr qreal kControlRadius = 15.0;
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
// State outline thickness in logical pixels; the focus ring stays 1px and reads
// crisp, with its visibility carried by the contrast token instead of weight.
constexpr qreal kOutlineWidth = 1.0;
constexpr qreal kFocusOutlineWidth = 1.0;
// Scroll bar gutter in logical pixels. Breeze spends 21px on a gutter its 8px
// handle never fills, so a 12px gutter keeps the same handle, hover states and
// drag length while reading considerably slimmer.
constexpr int kSlimScrollBarExtent = 12;
// Corner radius Dolphin hardcodes for its compact status card
// ("drawRoundedRect(opt.rect, 5, 5)" in DolphinStatusBar::paintEvent); the card
// frame must follow it or the border squares off the rounded fill.
constexpr qreal kStatusCardRadius = 5.0;
// Application name Dolphin reports for its own windows; the zero scroll bar
// extent is scoped to this name so no other application loses a scroll bar.
constexpr QLatin1StringView kDolphinApplicationName = QLatin1StringView("dolphin");
// Public class name of the Places sidebar view (KIO::KFilePlacesView), matched
// from the QObject meta-object so no KIO or Dolphin headers are linked here.
constexpr QLatin1StringView kPlacesViewClassName = QLatin1StringView("KFilePlacesView");
// Public class name of KIO's URL path bar (KIO::KUrlNavigator). Dolphin's own
// path bar is a subclass of it, so one name covers both.
constexpr QLatin1StringView kUrlNavigatorClassName = QLatin1StringView("KUrlNavigator");
// Public class name of Dolphin's status bar, which paints its compact card
// through PE_Frame; matched from the meta-object like the other KDE classes.
constexpr QLatin1StringView kStatusCardClassName = QLatin1StringView("DolphinStatusBar");

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

// True when the widget is Dolphin's own status bar, whose compact card asks the
// style for a square frame over its rounded fill.
bool isStatusCard(const QWidget *widget)
{
    return widget && matchesClassName(widget->metaObject()->className(), kStatusCardClassName);
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

// True when any ancestor is a KUrlNavigator: the breadcrumb and the editable path
// are one control in two states, so the child edit needs the same field surface.
bool isInsideUrlNavigator(const QWidget *widget)
{
    for (const QWidget *parent = widget ? widget->parentWidget() : nullptr; parent;
         parent = parent->parentWidget()) {
        if (isUrlNavigator(parent)) {
            return true;
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

// Fills one field surface under the shared rule: borderless tone-step fill at
// rest, readable accent ring only while focused.
void paintFieldSurface(QPainter *painter, const QRectF &rect, const QColor &fill, bool focused,
                       const QPalette &palette, QPalette::ColorGroup group)
{
    const qreal radius = qMin(kControlRadius, qMin(rect.width(), rect.height()) / 2.0);
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
    } else {
        fillSurface(painter, rect, radius, fill);
    }
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
        // Qt itself never asks a QLineEdit for this frame, but app-initiated
        // draws that pass a QLineEdit widget must not stamp Breeze's tight
        // radius over the pill PE_PanelLineEdit painted.
        if (widget && qobject_cast<const QLineEdit *>(widget)) {
            return;
        }
        break;
    case PE_Frame:
        // Dolphin's compact status card draws its own rounded Window-tone fill
        // and asks the style only for a square frame; answer with a hairline
        // that follows the card's rounding instead of squaring it off.
        if (option && painter && isStatusCard(widget)) {
            paintStatusCardFrame(option, painter);
            return;
        }
        break;
    case PE_IndicatorCheckBox:
        paintIndicator(option, painter, false);
        return;
    case PE_IndicatorRadioButton:
        paintIndicator(option, painter, true);
        return;
    case PE_PanelTipLabel:
        // Breeze's default app tooltip is a square-cornered frame; that surfaced as a
        // stray bordered box over the view. Give it the theme's tooltip surface instead.
        if (option && painter) {
            const QPalette &tipPalette = option->palette;
            const QPalette::ColorGroup tipGroup = colorGroup(option);
            const QRectF tipRect = QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5);
            const QColor tipFill = tipPalette.color(tipGroup, QPalette::ToolTipBase);
            const QColor tipLine = blend(tipFill, tipPalette.color(tipGroup, QPalette::ToolTipText),
                                         kFrameContrast);
            paintSurface(painter, tipRect, kTipRadius, kOutlineWidth, tipFill, tipLine);
            return;
        }
        break;
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
        fillSurface(painter, fillRect, qMin(radius, fillRect.width() / 2.0),
                    palette.color(group, QPalette::Highlight));
    }
    if (option->textVisible && !option->text.isEmpty()) {
        painter->save();
        painter->setPen(palette.color(group, QPalette::Text));
        painter->drawText(rect, Qt::AlignCenter, option->text);
        painter->restore();
    }
    return true;
}

// KDE's custom-element protocol: the widget temporarily carries the element name
// in its objectName and queries 0xff000001; remember the id Breeze assigns to
// CE_CapacityBar so its draws can be taken over in drawControl.
int MTNightshiftStyle::styleHint(StyleHint hint, const QStyleOption *option,
                                 const QWidget *widget, QStyleHintReturn *hintReturn) const
{
    constexpr StyleHint kKdeCustomStyleElement = static_cast<StyleHint>(0xff000001);
    constexpr int kOwnCapacityBarElement = static_cast<int>(QStyle::CE_CustomBase) + 1;
    if (hint == kKdeCustomStyleElement && widget
        && widget->objectName() == QLatin1StringView("CE_CapacityBar")) {
        // Neither Qt nor Breeze supports CE_CapacityBar here — Breeze leaves the
        // query unanswered, so KCapacityBar falls back to its near-black
        // QPainter shape. Hand out our own element id and paint the pill.
        m_capacityBarElement = kOwnCapacityBarElement;
        return kOwnCapacityBarElement;
    }
    return QProxyStyle::styleHint(hint, option, widget, hintReturn);
}

// Draws our own push buttons, delegating every other control element.
void MTNightshiftStyle::drawControl(ControlElement element, const QStyleOption *option, QPainter *painter,
                                    const QWidget *widget) const
{
    if (element == CE_PushButton && paintPushButton(option, painter, widget)) {
        return;
    }
    // KDE capacity meters (Dolphin's free-space meter and KCapacityBar users)
    // fall back to this primitive through our proxy, where Breeze's groove
    // reads as a black slab.
    // KDE capacity meters (Dolphin's free-space meter and other KCapacityBar
    // users) arrive under Breeze's custom element id; the generic progress bars
    // arrive as CE_ProgressBar. Both render as the same Sculpted pill.
    if (element == m_capacityBarElement || element == CE_ProgressBar) {
        const auto *bar = qstyleoption_cast<const QStyleOptionProgressBar *>(option);
        if (bar && paintProgressBar(bar, painter, widget)) {
            return;
        }
    }
    QProxyStyle::drawControl(element, option, painter, widget);
}

// Draws our own combo boxes and spin boxes, delegating every other complex control.
void MTNightshiftStyle::drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                                           QPainter *painter, const QWidget *widget) const
{
    if (control == CC_ComboBox) {
        const auto *combo = qstyleoption_cast<const QStyleOptionComboBox *>(option);
        if (combo && paintComboBox(combo, painter, widget)) {
            return;
        }
    }
    if (control == CC_SpinBox) {
        const auto *spin = qstyleoption_cast<const QStyleOptionSpinBox *>(option);
        if (spin && paintSpinBox(spin, painter, widget)) {
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
    // Frameless fields stay exactly as Breeze draws them — except the path edit
    // inside a URL navigator, which replaces the rounded breadcrumb field when
    // clicked and must keep the same pill in both states.
    const auto *edit = qobject_cast<const QLineEdit *>(widget);
    const bool navigatorField = isInsideUrlNavigator(widget);
    if (edit && !edit->hasFrame() && !navigatorField) {
        return false;
    }
    // Editors inside combos and spin boxes sit on the container's own rounded
    // surface: paint nothing, or a square panel would cover the pill's corners.
    if (edit && widget && (qobject_cast<const QComboBox *>(widget->parentWidget())
                           || qobject_cast<const QAbstractSpinBox *>(widget->parentWidget()))) {
        return true;
    }
    const QPalette &palette = panel->palette;
    const QPalette::ColorGroup group = colorGroup(panel);
    const bool focused = panel->state.testFlag(State_HasFocus)
        && panel->state.testFlag(State_Enabled);
    const QRectF rect = QRectF(panel->rect);
    // The field reads as a tone step, not a frame: the theme's Base colour. KIO tints
    // a navigator's own Base to the toolbar shade, so both states of the path bar take
    // the input tone from the application palette and match each other.
    const QColor fill = (navigatorField || !widget) && qApp
        ? qApp->palette().color(group, QPalette::Base)
        : widget->palette().color(group, QPalette::Base);
    paintFieldSurface(painter, rect, fill, focused, palette, group);
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
    // The theme's input tone, taken from the application palette. KIO tints the
    // navigator's own Base to the toolbar shade, which left the field with no
    // contrast at all: the rounded fill was invisible and only the corner
    // antialiasing showed, so the path bar read as "no proper roundness".
    const QColor fill = qApp ? qApp->palette().color(group, QPalette::Base)
                             : palette.color(group, QPalette::Base);
    if (focused) {
        const QColor ring = readableAccent(palette.color(group, QPalette::Highlight), fill, kFocusContrast);
        paintSurface(painter, rect, radius, kFocusOutlineWidth, fill, ring);
    } else {
        fillSurface(painter, rect, radius, fill);
    }
    return true;
}

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
    const QRectF rect = QRectF(option->rect);
    // Combos that take typed text use the input tone (Base); menu-style combos
    // keep the button tone, which keeps the file dialog's two rows distinct.
    const QColor fill = option->editable ? palette.color(group, QPalette::Base)
                                         : palette.color(group, QPalette::Button);
    paintFieldSurface(painter, rect, fill, focused, palette, group);
    QStyleOption arrowOption(*option);
    arrowOption.rect = subControlRect(CC_ComboBox, option, SC_ComboBoxArrow, widget);
    baseStyle()->drawPrimitive(PE_IndicatorArrowDown, &arrowOption, painter, widget);
    baseStyle()->drawControl(CE_ComboBoxLabel, option, painter, widget);
    return true;
}

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
    const QRectF rect = QRectF(option->rect);
    // A spin box edits typed text, so it takes the input tone like line edits;
    // a frameless editor delegate opts out, mirroring the line edit rule.
    const QColor fill = palette.color(group, QPalette::Base);
    if (option->frame) {
        paintFieldSurface(painter, rect, fill, focused, palette, group);
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
