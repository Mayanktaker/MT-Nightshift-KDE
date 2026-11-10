/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 */
#include "mtnightshiftstyleplugin.h"

#include "mtnightshiftstyle.h"

// Creates the style for our key; any other key is not ours to answer.
QStyle *MTNightshiftStylePlugin::create(const QString &key)
{
    if (key.compare(QStringLiteral("MTNightshift"), Qt::CaseInsensitive) != 0) {
        return nullptr;
    }
    return new MTNightshiftStyle;
}
