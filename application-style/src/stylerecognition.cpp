/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#include "stylerecognition.h"

#include <QAbstractScrollArea>
#include <QCoreApplication>
#include <QDialog>
#include <QDockWidget>
#include <QMainWindow>
#include <QMetaObject>
#include <QScrollBar>

namespace
{
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
} // namespace

namespace mtstyle
{
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
} // namespace mtstyle
