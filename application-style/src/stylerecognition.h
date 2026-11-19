/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work drawn from scratch with QPainter; Breeze is only the proxy base.
 */
#pragma once

#include <QLatin1StringView>
#include <QWidget>

namespace mtstyle
{
bool matchesClassName(const char *className, QLatin1StringView expected);
bool isPlacesViewClassName(const char *className);
bool isUrlNavigator(const QWidget *widget);
bool isStatusCard(const QWidget *widget);
bool isDolphinPlacesView(const QWidget *view);
bool isDolphinPlacesScrollBar(const QWidget *widget);
bool isDolphinShellWindow(const QWidget *widget);
bool isInsideUrlNavigator(const QWidget *widget);
} // namespace mtstyle
