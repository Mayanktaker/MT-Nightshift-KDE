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
class QStyleOptionProgressBar;
class QStyleOptionViewItem;
class QStyleOptionSpinBox;
class QStyleHintReturn;

// Sculpted Qt Widgets style layered over Breeze; only rounded control surfaces are redrawn.
class MTNightshiftStyle : public QProxyStyle
{
    Q_OBJECT

    // Opts the proxy into KDE's custom-element protocol so widgets like
    // KCapacityBar ask this style for their element ids (Breeze answers through
    // the delegation) instead of falling back to generic Qt primitives.
    Q_CLASSINFO("X-KDE-CustomElements", "true")

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
    // Paints a determinate progress meter as a rounded pill; false for busy or vertical bars.
    bool paintProgressBar(const QStyleOptionProgressBar *option, QPainter *painter,
                          const QWidget *widget) const;
    // Paints item-view selection and hover as inset rounded pills; true when the
    // primitive must not fall through to Breeze's square highlight.
    bool paintItemPill(const QStyleOption *option, QPainter *painter) const;
    // Paints CE_ItemViewItem content over our pill with the band stripped from
    // Breeze's rendering; keeps icon and readable text.
    void paintItemViewContent(const QStyleOptionViewItem *option, QPainter *painter,
                              const QWidget *widget) const;
    // Paints item-view panel frames as dimmed rounded hairlines; true when the
    // primitive must not fall through to Breeze's square frame.
    bool paintItemViewFrame(const QStyleOption *option, QPainter *painter) const;
    // Paints the item-view keyboard-focus indicator as a pill ring following the
    // selection pill's geometry; true when the primitive must be suppressed
    // (Breeze's squarish outline) or the selection already marks the item.
    bool paintFocusPill(const QStyleOption *option, QPainter *painter) const;

protected:
    // Records the element id Breeze assigns to CE_CapacityBar so the meter can
    // be taken over in drawControl.
    int styleHint(StyleHint hint, const QStyleOption *option, const QWidget *widget,
                  QStyleHintReturn *hintReturn) const override;
    // Paints a check box or radio indicator in the Sculpted shape.
    void paintIndicator(const QStyleOption *option, QPainter *painter, bool radio) const;

    // Element id Breeze handed out for CE_CapacityBar, captured in styleHint;
    // mutable because the protocol queries through a const style.
    mutable int m_capacityBarElement = 0;
};
