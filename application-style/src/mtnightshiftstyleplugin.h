/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 */
#pragma once

#include <QStylePlugin>

// Qt style plugin exposing the MTNightshift style key.
class MTNightshiftStylePlugin : public QStylePlugin
{
    Q_OBJECT
    Q_PLUGIN_METADATA(IID "org.qt-project.Qt.QStyleFactoryInterface"
                      FILE "mtnightshiftstyleplugin.json")

public:
    // Creates the MT Nightshift style for our key and declines every other key.
    QStyle *create(const QString &key) override;
};
