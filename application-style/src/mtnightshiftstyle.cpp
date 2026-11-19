/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */

// Style entry points: construction and the QStyle dispatch.
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

// Builds the style on the installed Breeze style, or the native style when absent.
MTNightshiftStyle::MTNightshiftStyle() : QProxyStyle(QStyleFactory::create(QStringLiteral("Breeze"))) {}

// Draws our own line edit and check indicators, delegating all other primitives.
void MTNightshiftStyle::drawPrimitive(PrimitiveElement element, const QStyleOption *option, QPainter *painter,
                                      const QWidget *widget) const
{
    switch (element) {
    case PE_PanelStatusBar: {
        if (!option || !painter || option->rect.isEmpty()) {
            break;
        }
        const QPalette &palette = option->palette;
        const auto group = colorGroup(option);
        const QColor fill = palette.color(group, QPalette::Window);
        const QColor line = blend(fill, palette.color(group, QPalette::WindowText), kFrameContrast);
        const QRectF rect = QRectF(option->rect).adjusted(0.5, 0.5, -0.5, -0.5);
        const qreal radius = qMin(kControlRadius, rect.height() / 2.0);
        paintSurface(painter, rect, radius, kOutlineWidth, fill, line);
        return;
    }
    case PE_PanelButtonTool:
        if (paintToolButton(option, painter)) {
            return;
        }
        break;
    case PE_PanelMenu:
        if (paintMenuPanel(option, painter)) {
            return;
        }
        break;
    case PE_FrameMenu:
        if (paintMenuFrame(option, painter)) {
            return;
        }
        break;
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
    case PE_PanelItemViewItem:
    case PE_PanelItemViewRow:
        // Selections and hovers in list, tree and icon views become inset
        // rounded pills instead of Breeze's square bands.
        if (paintItemPill(option, painter)) {
            return;
        }
        break;
    case PE_FrameFocusRect:
        // Item-view keyboard focus becomes a pill ring that follows the
        // selection pill's geometry; Breeze's squarish outline never draws.
        if (paintFocusPill(option, painter, widget)) {
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

// Draws our own push buttons, delegating every other control element.
void MTNightshiftStyle::drawControl(ControlElement element, const QStyleOption *option, QPainter *painter,
                                    const QWidget *widget) const
{
    if (element == CE_PushButton && paintPushButton(option, painter, widget)) {
        return;
    }
    if (element == CE_TabBarTabShape && paintTabShape(option, painter)) {
        return;
    }
    // Hovered/selected menu rows get the pill; Breeze draws icon and text from
    // a state-stripped option so its old flat highlight cannot be painted.
    if (element == CE_MenuItem) {
        const auto *item = qstyleoption_cast<const QStyleOptionMenuItem *>(option);
        if (item && painter
            && (item->state.testFlag(State_MouseOver) || item->state.testFlag(State_Selected))
            && paintMenuPill(option, painter)) {
            QStyleOptionMenuItem stripped(*item);
            stripped.state &= ~(State_MouseOver | State_Selected);
            if (item->state.testFlag(State_Selected)) {
                // QMenu marks its current row Selected; Breeze would paint the
                // label in Text on our Highlight fill, so move it to on-pill ink.
                const auto group = colorGroup(item);
                const QColor onPill = item->palette.color(group, QPalette::HighlightedText);
                stripped.palette.setColor(QPalette::Active, QPalette::Text, onPill);
                stripped.palette.setColor(QPalette::Inactive, QPalette::Text, onPill);
                stripped.palette.setColor(QPalette::Active, QPalette::WindowText, onPill);
                stripped.palette.setColor(QPalette::Inactive, QPalette::WindowText, onPill);
            }
            baseStyle()->drawControl(CE_MenuItem, &stripped, painter, widget);
            return;
        }
    }
    // KDE capacity meters (Dolphin's free-space meter and other KCapacityBar
    // users) arrive under Breeze's custom element id; the generic progress bars
    // arrive as CE_ProgressBar. Both render as the same Sculpted pill.
    // Boxed item-view frames (Kate's sessions list and other item-view
    // panels) become dimmed rounded hairlines; other frames keep Breeze.
    if (element == CE_ShapedFrame && paintItemViewFrame(option, painter)) {
        return;
    }
    // Standard-delegate item views (Kate's welcome lists and every
    // QListView/QTreeWidget routed through CE_ItemViewItem) get the pill under
    // Breeze's content rendering.
    if (element == QStyle::CE_ItemViewItem) {
        const auto *item = qstyleoption_cast<const QStyleOptionViewItem *>(option);
        if (item && painter
            && (item->state.testFlag(State_Selected) || item->state.testFlag(State_MouseOver))) {
            paintItemPill(option, painter);
            paintItemViewContent(item, painter, widget);
            return;
        }
    }
    if (element == m_capacityBarElement || element == CE_ProgressBar) {
        const auto *bar = qstyleoption_cast<const QStyleOptionProgressBar *>(option);
        if (bar && paintProgressBar(bar, painter, widget)) {
            return;
        }
    }
    QProxyStyle::drawControl(element, option, painter, widget);
}

// Draws our own combo boxes and spin boxes, delegating every other complex control.

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

// Narrows every scroll bar gutter and leaves Dolphin's Places sidebar without one.
int MTNightshiftStyle::pixelMetric(PixelMetric metric, const QStyleOption *option,
                                   const QWidget *widget) const
{
    if (metric == PM_DefaultFrameWidth && widget) {
        // Boxed item views (session lists, recent-file lists): keep one pixel
        // so the viewport does not swallow the rounded frame hairline.
        const bool itemView = qobject_cast<const QListView *>(widget)
            || qobject_cast<const QTreeView *>(widget) || qobject_cast<const QTableView *>(widget);
        if (itemView) {
            return qMax(1, QProxyStyle::pixelMetric(metric, option, widget));
        }
    }
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
