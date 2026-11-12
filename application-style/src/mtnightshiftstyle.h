/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Original work: no upstream Breeze source is copied. Everything not redrawn
 * here is delegated to the installed Breeze style.
 */
#pragma once

#include <QProxyStyle>

class QPainter;
class QStyleOption;
class QStyleOptionComboBox;
class QStyleOptionComplex;
class QStyleOptionSpinBox;

// Sculpted Qt Widgets style layered over Breeze; only rounded control surfaces are redrawn.
class MTNightshiftStyle : public QProxyStyle
{
public:
    // Uses the installed Breeze style as the base, falling back to the native style.
    MTNightshiftStyle();

    void drawPrimitive(PrimitiveElement element, const QStyleOption *option, QPainter *painter,
                       const QWidget *widget = nullptr) const override;

    // Draws rounded push buttons, delegating labels, icons and focus handling.
    void drawControl(ControlElement element, const QStyleOption *option, QPainter *painter,
                     const QWidget *widget = nullptr) const override;
    // Draws rounded combo boxes and spin boxes, owning the whole field family.
    void drawComplexControl(ComplexControl control, const QStyleOptionComplex *option,
                            QPainter *painter, const QWidget *widget = nullptr) const override;

    // Narrows scroll bars, and removes the one owned by Dolphin's Places sidebar.
    int pixelMetric(PixelMetric metric, const QStyleOption *option = nullptr,
                    const QWidget *widget = nullptr) const override;

private:
    // Paints a rounded push button; returns false when Breeze should handle it.
    bool paintPushButton(const QStyleOption *option, QPainter *painter, const QWidget *widget) const;
    // Paints a borderless rounded text field; returns false when Breeze should handle it.
    bool paintLineEdit(const QStyleOption *option, QPainter *painter, const QWidget *widget) const;
    // Paints a KIO URL path bar as a borderless rounded field; false for anything else.
    bool paintUrlNavigatorField(const QStyleOption *option, QPainter *painter,
                                const QWidget *widget) const;
    // Paints a borderless rounded combo box in both states; false when options are missing.
    bool paintComboBox(const QStyleOptionComboBox *option, QPainter *painter,
                       const QWidget *widget) const;
    // Paints a borderless rounded spin box and its arrows; false when options are missing.
    bool paintSpinBox(const QStyleOptionSpinBox *option, QPainter *painter,
                      const QWidget *widget) const;
    // Paints a check box or radio indicator in the Sculpted shape.
    void paintIndicator(const QStyleOption *option, QPainter *painter, bool radio) const;
};
