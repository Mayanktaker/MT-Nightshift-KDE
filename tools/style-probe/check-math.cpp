/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Unit checks for the shared colour maths. The image probe proves what the
 * plugin paints; this proves the helpers behave at the edges the probe never
 * renders (equal tones, extreme targets, inactive palettes).
 */
#include "stylepainting.h"

#include <QApplication>
#include <QPalette>
#include <QStyle>

#include <cmath>
#include <cstdio>

namespace
{
int failures = 0;

void check(const char *name, bool ok, const QString &detail = {})
{
    std::printf("  %-42s %s %s\n", name, ok ? "OK" : "FAIL", qPrintable(detail));
    if (!ok) {
        ++failures;
    }
}

qreal ratio(const QColor &first, const QColor &second)
{
    return mtstyle::contrastRatio(first, second);
}
} // namespace

int main(int argc, char **argv)
{
    QApplication app(argc, argv);

    const QColor black(0, 0, 0);
    const QColor white(255, 255, 255);
    const QColor surface(16, 18, 22);

    const QColor start = mtstyle::blend(black, white, 0.0);
    const QColor middle = mtstyle::blend(black, white, 0.5);
    const QColor end = mtstyle::blend(black, white, 1.0);
    check("blend keeps the first endpoint", start == black, start.name());
    check("blend keeps the second endpoint", end == white, end.name());
    check("blend is linear at the midpoint",
          std::abs(middle.red() - 128) <= 1 && middle.green() == middle.red() && middle.blue() == middle.red(),
          middle.name());
    check("blend clamps below zero", mtstyle::blend(black, white, -1.0) == black);
    check("blend clamps above one", mtstyle::blend(black, white, 2.0) == white);

    check("contrast is symmetric", std::abs(ratio(black, white) - ratio(white, black)) < 0.001);
    check("contrast of a tone with itself is 1", std::abs(ratio(surface, surface) - 1.0) < 0.001);
    check("black on white clears 21:1", ratio(black, white) >= 21.0 - 0.001,
          QString::number(ratio(black, white), 'f', 2));

    const QColor quiet(20, 22, 26);
    const QColor lifted = mtstyle::readableAccent(quiet, surface, 5.0);
    check("readableAccent reaches a 5:1 target", ratio(lifted, surface) >= 5.0 - 0.01,
          QStringLiteral("%1 %2:1").arg(lifted.name(), QString::number(ratio(lifted, surface), 'f', 2)));
    const QColor already(240, 240, 240);
    check("readableAccent leaves a sufficient accent alone",
          mtstyle::readableAccent(already, surface, 3.0) == already);
    const QColor impossible = mtstyle::readableAccent(surface, surface, 21.0);
    check("readableAccent stays finite when the target is unreachable",
          impossible.isValid() && ratio(impossible, surface) > 1.0,
          QString::number(ratio(impossible, surface), 'f', 2));

    QStyleOption option;
    option.state = QStyle::State_Enabled;
    check("enabled option reads as active", mtstyle::colorGroup(&option) == QPalette::Active);
    option.state |= QStyle::State_Active;
    check("explicit active state reads as active", mtstyle::colorGroup(&option) == QPalette::Active);
    option.state = QStyle::State_Enabled;
    option.palette.setCurrentColorGroup(QPalette::Inactive);
    check("inactive palette reads as inactive", mtstyle::colorGroup(&option) == QPalette::Inactive);
    option.state = QStyle::State_None;
    option.palette.setCurrentColorGroup(QPalette::Active);
    check("missing enabled flag wins over the palette group",
          mtstyle::colorGroup(&option) == QPalette::Disabled);

    if (failures) {
        std::printf("%d colour-math check(s) failed\n", failures);
        return 1;
    }
    std::printf("all colour-math checks passed\n");
    return 0;
}
