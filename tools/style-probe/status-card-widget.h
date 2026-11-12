/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 */
#pragma once

#include <QWidget>

// Stand-in for Dolphin's status bar widget: the style matches it by meta-object
// class name, which only exists with Q_OBJECT, so moc must run on this header.
class DolphinStatusBar : public QWidget
{
    Q_OBJECT
public:
    explicit DolphinStatusBar(QWidget *parent = nullptr)
        : QWidget(parent)
    {
    }
};
