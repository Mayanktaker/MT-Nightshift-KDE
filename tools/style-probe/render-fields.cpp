/*
 * © Mayanktaker Computers & Web Development | https://mayanktaker.com
 * SPDX-FileCopyrightText: 2026 Mayanktaker Computers & Web Development <https://mayanktaker.com>
 * SPDX-License-Identifier: LGPL-2.0-or-later
 *
 * Offscreen style probe: renders one widget of every field-like control under a
 * chosen QStyle with the MT Nightshift palette and saves a PNG, so corner
 * radius and frame ownership can be verified without a live session.
 *
 * Usage: render-fields <StyleKey> <outdir> [scheme.colors] [plugin.so]
 */
#include <QApplication>
#include <QAbstractSpinBox>
#include <QComboBox>
#include <QColor>
#include <QDir>
#include <QFile>
#include <QHash>
#include <QImage>
#include <QPainter>
#include <QPainterPath>

#include "status-card-widget.h"
#include <QLineEdit>
#include <QMenu>
#include <QListView>
#include <QStringListModel>
#include <QPalette>
#include <QPluginLoader>
#include <QProxyStyle>
#include <QScrollArea>
#include <QScrollBar>
#include <QSpinBox>
#include <QString>
#include <QStringList>
#include <QStyleFactory>
#include <QStylePlugin>
#include <cstdio>

namespace
{
// Reads every "Group/Role=value" pair of a KDE .colors file. QSettings cannot
// be used here: its INI parser stops at the "[Colors:Header][Inactive]"
// subgroup header, which silently drops every group stored after it.
QHash<QString, QString> readScheme(const QString &path)
{
    QHash<QString, QString> entries;
    QFile file(path);
    if (!file.open(QIODevice::ReadOnly | QIODevice::Text)) {
        return entries;
    }
    QString group;
    while (!file.atEnd()) {
        const QString line = QString::fromUtf8(file.readLine()).trimmed();
        if (line.startsWith(u'[')) {
            group = line.mid(1, line.lastIndexOf(u']') - 1);
        } else if (!group.isEmpty() && line.contains(u'=')) {
            const int equals = line.indexOf(u'=');
            entries.insert(QStringLiteral("%1/%2").arg(group, line.left(equals)),
                           line.mid(equals + 1));
        }
    }
    return entries;
}

// Reads one KDE colour role ("BackgroundNormal") from one scheme group.
QColor schemeColor(const QHash<QString, QString> &scheme, const QString &group, const QString &role)
{
    const QStringList parts = scheme.value(QStringLiteral("%1/%2").arg(group, role)).split(u',');
    return parts.size() == 3 ? QColor(parts.at(0).toInt(), parts.at(1).toInt(), parts.at(2).toInt())
                             : QColor();
}

// Builds a QPalette from a KDE .colors file; missing roles keep Qt's defaults.
QPalette loadPalette(const QString &path)
{
    QPalette palette;
    const QHash<QString, QString> scheme = readScheme(path);
    const auto assign = [&scheme, &palette](const QString &group, QPalette::ColorRole background,
                                            QPalette::ColorRole foreground) {
        const QColor bg = schemeColor(scheme, group, QStringLiteral("BackgroundNormal"));
        const QColor fg = schemeColor(scheme, group, QStringLiteral("ForegroundNormal"));
        if (bg.isValid()) {
            palette.setColor(background, bg);
        }
        if (fg.isValid()) {
            palette.setColor(foreground, fg);
        }
    };
    assign(QStringLiteral("Colors:Window"), QPalette::Window, QPalette::WindowText);
    assign(QStringLiteral("Colors:Button"), QPalette::Button, QPalette::ButtonText);
    assign(QStringLiteral("Colors:View"), QPalette::Base, QPalette::Text);
    palette.setColor(QPalette::AlternateBase,
                     schemeColor(scheme, QStringLiteral("Colors:View"), QStringLiteral("BackgroundAlternate")));
    assign(QStringLiteral("Colors:Selection"), QPalette::Highlight, QPalette::HighlightedText);
    assign(QStringLiteral("Colors:Tooltip"), QPalette::ToolTipBase, QPalette::ToolTipText);
    palette.setColor(QPalette::Link,
                     schemeColor(scheme, QStringLiteral("Colors:View"), QStringLiteral("ForegroundLink")));
    // KDE derives its disabled tones from the scheme's colour effects; an
    // approximation keeps muted glyphs distinct, as the real session shows them.
    const auto assignDisabled = [&scheme, &palette](QPalette::ColorRole role, const QString &group) {
        const QColor fg = schemeColor(scheme, group, QStringLiteral("ForegroundNormal"));
        const QColor bg = schemeColor(scheme, group, QStringLiteral("BackgroundNormal"));
        if (!fg.isValid() || !bg.isValid()) {
            return;
        }
        const QColor muted(fg.red() + qRound((bg.red() - fg.red()) * 0.55),
                           fg.green() + qRound((bg.green() - fg.green()) * 0.55),
                           fg.blue() + qRound((bg.blue() - fg.blue()) * 0.55));
        palette.setBrush(QPalette::Disabled, role, muted);
    };
    assignDisabled(QPalette::WindowText, QStringLiteral("Colors:Window"));
    assignDisabled(QPalette::ButtonText, QStringLiteral("Colors:Button"));
    assignDisabled(QPalette::Text, QStringLiteral("Colors:View"));
    return palette;
}
} // namespace

// Renders one widget into <outdir>/<name>.png on a transparent background,
// forcing a minimum width so single-line content never scrolls inside the grab.
// grab() itself is avoided: it renders the widget as a window root and fills the
// whole rect with the background role first, which would square off any rounded
// corners the style paints.
static void grab(QWidget &widget, const QString &name, const QString &outdir)
{
    const QSize hint = widget.sizeHint();
    widget.resize(QSize(qMax(hint.width(), 260), hint.height() ? hint.height() : 32));
    QImage image(widget.size(), QImage::Format_ARGB32);
    image.fill(Qt::transparent);
    QPainter painter(&image);
    widget.render(&painter, QPoint(0, 0), QRegion(), QWidget::DrawChildren);
    painter.end();
    image.save(QStringLiteral("%1/%2.png").arg(outdir, name));
    // Report the background attributes a live session would also see.
    std::fprintf(stderr, "%s: autofill=%d styledBg=%d focused=%d Base=%s size=%dx%d\n", qPrintable(name),
                 int(widget.autoFillBackground()), int(widget.testAttribute(Qt::WA_StyledBackground)),
                 int(widget.hasFocus()), qPrintable(widget.palette().color(QPalette::Base).name()),
                 image.width(), image.height());
    std::fflush(stderr);
}

// Saves one transparent canvas rendered by a caller-supplied style call; focus
// states that offscreen widgets cannot reach through real events are forced by
// the caller through the style option state.
template<typename Render>
static void saveRendered(const QSize &size, const QString &name, const QString &outdir,
                         const QString &label, Render render)
{
    QImage canvas(size, QImage::Format_ARGB32);
    canvas.fill(Qt::transparent);
    QPainter painter(&canvas);
    render(&painter);
    painter.end();
    canvas.save(QStringLiteral("%1/%2.png").arg(outdir, name));
    std::fprintf(stderr, "%s: forced-state render saved\n", qPrintable(label));
    std::fflush(stderr);
}

int main(int argc, char **argv)
{
    if (argc < 3) {
        qWarning("usage: render-fields <StyleKey> <outdir> [scheme.colors]");
        return 2;
    }
    qputenv("QT_QPA_PLATFORM", "offscreen");
    QApplication app(argc, argv);
    const QString styleKey = QString::fromLocal8Bit(argv[1]);
    if (argc > 4) {
        // Load an explicit plugin build so the probe can never silently fall back
        // to the system copy when testing a fresh compile.
        QPluginLoader loader(QString::fromLocal8Bit(argv[4]));
        if (!loader.load()) {
            std::fprintf(stderr, "plugin load failed: %s\n", qPrintable(loader.errorString()));
            return 1;
        }
        auto *plugin = qobject_cast<QStylePlugin *>(loader.instance());
        if (!plugin) {
            std::fprintf(stderr, "not a QStylePlugin\n");
            return 1;
        }
        QStyle *style = plugin->create(styleKey);
        if (!style) {
            std::fprintf(stderr, "plugin does not provide %s\n", qPrintable(styleKey));
            return 1;
        }
        app.setStyle(style);
    } else if (!QStyleFactory::keys().contains(styleKey, Qt::CaseInsensitive)) {
        qWarning("style %s not found; keys: %s", qPrintable(styleKey), qPrintable(QStyleFactory::keys().join(u", ")));
        return 1;
    } else {
        app.setStyle(QStyleFactory::create(styleKey));
    }
    if (argc > 3) {
        const QPalette loaded = loadPalette(QString::fromLocal8Bit(argv[3]));
        app.setPalette(loaded);
        std::fprintf(stderr, "palette Window=%s Base=%s Button=%s\n",
                     qPrintable(loaded.color(QPalette::Window).name()),
                     qPrintable(loaded.color(QPalette::Base).name()),
                     qPrintable(loaded.color(QPalette::Button).name()));
    }
    const QString outdir = QString::fromLocal8Bit(argv[2]);
    QDir().mkpath(outdir);

    // Standalone framed line edit: the plain input-field case.
    QLineEdit framed;
    framed.setText(QStringLiteral("framed line edit"));
    grab(framed, QStringLiteral("framed-lineedit"), outdir);

    // Forced-focus line edit: the panel gains the accent ring, and the frame
    // primitive must draw nothing on top of it.
    saveRendered(framed.size(), QStringLiteral("framed-lineedit-focused"), outdir,
                 QStringLiteral("framed-lineedit-focused"), [&](QPainter *p) {
        QStyleOptionFrame option;
        option.initFrom(&framed);
        option.rect = framed.rect();
        option.state |= QStyle::State_Enabled | QStyle::State_HasFocus | QStyle::State_Active;
        app.style()->drawPrimitive(QStyle::PE_PanelLineEdit, &option, p, &framed);
    });
    saveRendered(framed.size(), QStringLiteral("framed-lineedit-framecheck"), outdir,
                 QStringLiteral("framed-lineedit-framecheck"), [&](QPainter *p) {
        QStyleOptionFrame option;
        option.initFrom(&framed);
        option.rect = framed.rect();
        option.state |= QStyle::State_Enabled | QStyle::State_HasFocus | QStyle::State_Active;
        app.style()->drawPrimitive(QStyle::PE_FrameLineEdit, &option, p, &framed);
    });

    // Frameless line edit: what a plain frameless edit must keep from Breeze.
    QLineEdit frameless;
    frameless.setText(QStringLiteral("frameless line edit"));
    frameless.setFrame(false);
    grab(frameless, QStringLiteral("frameless-lineedit"), outdir);

    // Editable combo: the file dialog location bar is one of these.
    QComboBox editable;
    editable.setEditable(true);
    editable.addItems({QStringLiteral("/editable/combo/path")});
    editable.setCurrentText(QStringLiteral("/editable/combo/path"));
    grab(editable, QStringLiteral("editable-combo"), outdir);
    saveRendered(editable.size(), QStringLiteral("editable-combo-focused"), outdir,
                 QStringLiteral("editable-combo-focused"), [&](QPainter *p) {
        QStyleOptionComboBox option;
        option.initFrom(&editable);
        option.rect = editable.rect();
        option.editable = true;
        option.subControls = QStyle::SC_All;
        option.state |= QStyle::State_Enabled | QStyle::State_HasFocus | QStyle::State_Active;
        app.style()->drawComplexControl(QStyle::CC_ComboBox, &option, p, &editable);
    });

    // Non-editable combo: the file-type selector.
    QComboBox selector;
    selector.addItems({QStringLiteral("Folder")});
    grab(selector, QStringLiteral("selector-combo"), outdir);
    saveRendered(selector.size(), QStringLiteral("selector-combo-focused"), outdir,
                 QStringLiteral("selector-combo-focused"), [&](QPainter *p) {
        QStyleOptionComboBox option;
        option.initFrom(&selector);
        option.rect = selector.rect();
        option.subControls = QStyle::SC_All;
        option.state |= QStyle::State_Enabled | QStyle::State_HasFocus | QStyle::State_Active;
        app.style()->drawComplexControl(QStyle::CC_ComboBox, &option, p, &selector);
    });

    // Spin box: another field container in the same family.
    QSpinBox spinner;
    spinner.setValue(42);
    grab(spinner, QStringLiteral("spinbox"), outdir);
    saveRendered(spinner.size(), QStringLiteral("spinbox-focused"), outdir,
                 QStringLiteral("spinbox-focused"), [&](QPainter *p) {
        QStyleOptionSpinBox option;
        option.initFrom(&spinner);
        option.rect = spinner.rect();
        option.frame = true;
        option.subControls = QStyle::SC_All;
        option.state |= QStyle::State_Enabled | QStyle::State_HasFocus | QStyle::State_Active;
        app.style()->drawComplexControl(QStyle::CC_SpinBox, &option, p, &spinner);
    });

    // Spin button modes and step limits: arrows must honour both.
    QSpinBox capped;
    capped.setRange(0, 99);
    grab(capped, QStringLiteral("spinbox-at-min"), outdir);
    QSpinBox silent;
    silent.setButtonSymbols(QAbstractSpinBox::NoButtons);
    grab(silent, QStringLiteral("spinbox-nobuttons"), outdir);
    QSpinBox plus;
    plus.setButtonSymbols(QAbstractSpinBox::PlusMinus);
    plus.setValue(3);
    grab(plus, QStringLiteral("spinbox-plusminus"), outdir);

    // Step limits under otherwise identical options: a hit limit must dim its
    // own arrow and leave the other one alone.
    const auto spinRender = [&](QAbstractSpinBox::StepEnabled steps, const QString &name) {
        saveRendered(spinner.size(), name, outdir, name, [&](QPainter *p) {
            QStyleOptionSpinBox option;
            option.initFrom(&spinner);
            option.rect = spinner.rect();
            option.subControls = QStyle::SC_SpinBoxUp | QStyle::SC_SpinBoxDown;
            option.buttonSymbols = QAbstractSpinBox::UpDownArrows;
            option.stepEnabled = steps;
            option.state |= QStyle::State_Enabled | QStyle::State_Active;
            app.style()->drawComplexControl(QStyle::CC_SpinBox, &option, p, &spinner);
        });
    };
    spinRender(QAbstractSpinBox::StepUpEnabled | QAbstractSpinBox::StepDownEnabled, QStringLiteral("spinbox-steps-both"));
    spinRender(QAbstractSpinBox::StepUpEnabled, QStringLiteral("spinbox-steps-uponly"));

    // Dolphin's compact status card: rounded fill drawn by Dolphin, then the
    // frame primitive — which our style must answer with a matching hairline.
    DolphinStatusBar statusCard;
    statusCard.resize(120, 28);
    saveRendered(statusCard.size(), QStringLiteral("status-card"), outdir,
                 QStringLiteral("status-card"), [&](QPainter *p) {
        // Reproduce Dolphin's clip: left and bottom border cut off.
        QPainterPath clip;
        clip.addRect(4, 0, 116, 24);
        p->setClipPath(clip);
        QStyleOption option;
        option.initFrom(&statusCard);
        // Dolphin expands the rect left and down only; the right edge stays put,
        // which is where the rounding and its hairline remain visible.
        option.rect = QRect(-4, 0, 124, 32);
        option.state |= QStyle::State_Enabled | QStyle::State_Sunken;
        p->setPen(Qt::NoPen);
        p->setBrush(statusCard.palette().color(QPalette::Window));
        p->drawRoundedRect(option.rect, 5, 5);
        app.style()->drawPrimitive(QStyle::PE_Frame, &option, p, &statusCard);
    });

    // Capacity meters and progress bars take the CE_ProgressBar path (KCapacityBar
    // falls back to it under styles without KDE custom elements): 30% meter with
    // and without inline text.
    const auto meterRender = [&](int progress, bool textVisible, const QString &name) {
        saveRendered(QSize(160, 12), name, outdir, name, [&](QPainter *p) {
            QStyleOptionProgressBar option;
            option.initFrom(&statusCard);
            option.rect = QRect(0, 0, 160, 12);
            option.minimum = 0;
            option.maximum = 100;
            option.progress = progress;
            option.text = textVisible ? QStringLiteral("%1%").arg(progress) : QString();
            option.textVisible = textVisible;
            option.state |= QStyle::State_Enabled | QStyle::State_Horizontal;
            app.style()->drawControl(QStyle::CE_ProgressBar, &option, p, &statusCard);
        });
    };
    meterRender(30, false, QStringLiteral("capacity-meter"));
    meterRender(55, true, QStringLiteral("progress-text"));

    // Boxed item-view frame (Kate's sessions list): must render as a dimmed
    // rounded hairline, not Breeze's blue square outline.
    QListView framedList;
    framedList.setFrameShape(QFrame::StyledPanel);
    framedList.resize(220, 200);
    framedList.grab().save(QStringLiteral("%1/itemview-frame.png").arg(outdir));
    std::fprintf(stderr, "framedList frameWidth=%d PM_DefaultFrameWidth=%d\n", framedList.frameWidth(),
                 framedList.style()->pixelMetric(QStyle::PM_DefaultFrameWidth, nullptr, &framedList));
    // Forced primitive: isolates our frame painting from viewport stacking.
    saveRendered(framedList.size(), QStringLiteral("frame-primitive"), outdir,
                 QStringLiteral("frame-primitive"), [&](QPainter *p) {
        QStyleOptionFrame option;
        option.initFrom(&framedList);
        option.rect = framedList.rect();
        option.frameShape = QFrame::StyledPanel;
        option.lineWidth = 1;
        option.state |= QStyle::State_Enabled;
        app.style()->drawControl(QStyle::CE_ShapedFrame, &option, p, &framedList);
    });

    // Item-view pills: a real list with a selection, plus the primitive with
    // forced hover and inactive-selection states.
    QListView listView;
    QStringListModel listModel(QStringList() << QStringLiteral("Mouse & Touchpad")
                                             << QStringLiteral("Accessibility")
                                             << QStringLiteral("Sound")
                                             << QStringLiteral("Display & Monitor"));
    listView.setModel(&listModel);
    listView.setCurrentIndex(listModel.index(1, 0));
    listView.resize(220, 130);
    grab(listView, QStringLiteral("itemview-selected"), outdir);

    const auto pillRender = [&](QStyle::State state, const QString &name) {
        saveRendered(QSize(220, 30), name, outdir, name, [&](QPainter *p) {
            QStyleOptionViewItem option;
            option.initFrom(&listView);
            option.rect = QRect(0, 0, 220, 30);
            option.state |= QStyle::State_Enabled | state;
            app.style()->drawPrimitive(QStyle::PE_PanelItemViewItem, &option, p, &listView);
        });
    };
    pillRender(QStyle::State_MouseOver, QStringLiteral("item-hover"));
    pillRender(QStyle::State_Selected | QStyle::State_Active, QStringLiteral("item-selected"));
    pillRender(QStyle::State_Selected, QStringLiteral("item-selected-inactive"));

    // Keyboard-focus pill: replaces the squarish focus outline; suppressed
    // while the item is selected.
    const auto focusRender = [&](bool selected, const QString &name) {
        saveRendered(QSize(220, 30), name, outdir, name, [&](QPainter *p) {
            QStyleOptionFocusRect option;
            option.initFrom(&listView);
            option.rect = QRect(0, 0, 220, 30);
            option.state |= QStyle::State_Enabled | QStyle::State_Active | QStyle::State_HasFocus;
            if (selected) {
                option.state |= QStyle::State_Selected;
            }
            app.style()->drawPrimitive(QStyle::PE_FrameFocusRect, &option, p, &listView);
        });
    };
    focusRender(false, QStringLiteral("focus-pill"));
    focusRender(true, QStringLiteral("focus-pill-selected"));

    // Context menu: does the frame language reach QMenu corners?
    QMenu menu;
    menu.addAction(QStringLiteral("Open"));
    menu.addAction(QStringLiteral("Save"));
    menu.addSeparator();
    menu.addAction(QStringLiteral("Quit"));
    menu.resize(menu.sizeHint());
    menu.grab().save(QStringLiteral("%1/menu.png").arg(outdir));

    // Disabled field family: the Login Screen settings page greys out whole
    // groups of combos and edits, so their surface must stay legible.
    QComboBox disabledCombo;
    disabledCombo.setEnabled(false);
    disabledCombo.addItems({QStringLiteral("as user:")});
    grab(disabledCombo, QStringLiteral("disabled-combo"), outdir);

    QComboBox disabledEditable;
    disabledEditable.setEditable(true);
    disabledEditable.setEnabled(false);
    disabledEditable.addItems({QStringLiteral("with session:")});
    grab(disabledEditable, QStringLiteral("disabled-editable-combo"), outdir);
    if (auto *child = disabledEditable.findChild<QLineEdit *>()) {
        std::fprintf(stderr, "disabled editable child: autofill=%d Base=%s\n",
                     int(child->autoFillBackground()),
                     qPrintable(child->palette().color(QPalette::Disabled, QPalette::Base).name()));
    }

    QLineEdit disabledEdit;
    disabledEdit.setEnabled(false);
    disabledEdit.setText(QStringLiteral("disabled edit"));
    grab(disabledEdit, QStringLiteral("disabled-lineedit"), outdir);

    // Scroll bar gutter: the 12px clamp is asserted against Breeze's 21px base.
    {
        QScrollBar scrollbar(Qt::Vertical);
        scrollbar.setRange(0, 100);
        scrollbar.setPageStep(10);
        scrollbar.resize(scrollbar.sizeHint());
        scrollbar.grab().save(QStringLiteral("%1/scrollbar.png").arg(outdir));
        const auto *proxy = qobject_cast<const QProxyStyle *>(app.style());
        std::fprintf(stderr, "base style: %s\n",
                     proxy && proxy->baseStyle() ? proxy->baseStyle()->metaObject()->className() : "(none)");
    }

    // Simulate KDE's custom-element protocol exactly as KCapacityBar runs it:
    // the widget temporarily carries the element name in its objectName.
    statusCard.setObjectName(QStringLiteral("CE_CapacityBar"));
    const int classInfoIndex = statusCard.style()->metaObject()->indexOfClassInfo("X-KDE-CustomElements");
    const int customId = statusCard.style()->styleHint(static_cast<QStyle::StyleHint>(0xff000001),
                                                      nullptr, &statusCard);
    std::fprintf(stderr, "protocol: classInfo=%d customId=%d\n", classInfoIndex, customId);
    if (customId) {
        saveRendered(QSize(160, 12), QStringLiteral("capacity-meter-custom"), outdir,
                     QStringLiteral("capacity-meter-custom"), [&](QPainter *p) {
            QStyleOptionProgressBar option;
            option.initFrom(&statusCard);
            option.rect = QRect(0, 0, 160, 12);
            option.minimum = 0;
            option.maximum = 100;
            option.progress = 30;
            option.state |= QStyle::State_Enabled | QStyle::State_Horizontal;
            app.style()->drawControl(static_cast<QStyle::ControlElement>(customId), &option, p, &statusCard);
        });
    }
    statusCard.setObjectName(QString());

    return 0;
}
