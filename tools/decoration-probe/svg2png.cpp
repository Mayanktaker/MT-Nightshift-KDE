// © Mayanktaker Computers & Web Development | https://mayanktaker.com
// SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development
// SPDX-License-Identifier: LGPL-2.0-or-later
//
// Rasterises one SVG to PNG with alpha through Qt's own qsvg image plugin, so
// decoration checks use the same renderer KWin's FrameSvg uses. Built by
// check-decoration.py; Qt6Svg development headers are not required.
#include <QGuiApplication>
#include <QImage>
#include <QImageReader>

int main(int argc, char **argv)
{
    if (argc < 3) {
        fprintf(stderr, "usage: %s <in.svg> <out.png>\n", argv[0]);
        return 2;
    }
    QGuiApplication app(argc, argv);
    QImageReader reader(QString::fromLocal8Bit(argv[1]));
    QImage image = reader.read();
    if (image.isNull()) {
        fprintf(stderr, "cannot render %s: %s\n", argv[1], qPrintable(reader.errorString()));
        return 1;
    }
    return image.save(QString::fromLocal8Bit(argv[2])) ? 0 : 1;
}
