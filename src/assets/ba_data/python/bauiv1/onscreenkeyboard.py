# Released under the MIT License. See LICENSE for details.
#
"""Provides the built-in on screen keyboard UI."""

from __future__ import annotations

import logging
from typing import cast

import bauiv1 as bui


class OnScreenKeyboardWindow(bui.Window):
    """Simple built-in on-screen keyboard."""

    def __init__(self, textwidget: bui.Widget, label: str, max_chars: int):
        self._target_text = textwidget
        self._width = 700
        self._height = 400
        assert bui.app.classic is not None
        uiscale = bui.app.classic.ui.uiscale
        top_extra = 20 if uiscale is bui.UIScale.SMALL else 0
        super().__init__(
            root_widget=bui.containerwidget(
                parent=bui.get_special_widget('overlay_stack'),
                size=(self._width, self._height + top_extra),
                transition='in_scale',
                scale_origin_stack_offset=(
                    self._target_text.get_screen_space_center()
                ),
                scale=(
                    2.0
                    if uiscale is bui.UIScale.SMALL
                    else 1.5
                    if uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
                stack_offset=(0, 0)
                if uiscale is bui.UIScale.SMALL
                else (0, 0)
                if uiscale is bui.UIScale.MEDIUM
                else (0, 0),
            )
        )
        self._done_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(self._width - 200, 44),
            size=(140, 60),
            autoselect=True,
            label=bui.Lstr(resource='doneText'),
            on_activate_call=self._done,
        )
        bui.containerwidget(
            edit=self._root_widget,
            on_cancel_call=self._cancel,
            start_button=self._done_button,
        )

        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 41),
            size=(0, 0),
            scale=0.95,
            text=label,
            maxwidth=self._width - 140,
            color=bui.app.classic.ui.title_color,
            h_align='center',
            v_align='center',
        )

        self._text_field = bui.textwidget(
            parent=self._root_widget,
            position=(70, self._height - 116),
            max_chars=max_chars,
            text=cast(str, bui.textwidget(query=self._target_text)),
            on_return_press_call=self._done,
            autoselect=True,
            size=(self._width - 140, 55),
            v_align='center',
            editable=True,
            maxwidth=self._width - 175,
            force_internal_editing=True,
            always_show_carat=True,
        )

        self._key_color_lit = (1.4, 1.2, 1.4)
        self._key_color = (0.69, 0.6, 0.74)
        self._key_color_dark = (0.55, 0.55, 0.71)

        self._shift_button: bui.Widget | None = None
        self._backspace_button: bui.Widget | None = None
        self._space_button: bui.Widget | None = None
        self._double_press_shift = False
        self._num_mode_button: bui.Widget | None = None
        self._emoji_button: bui.Widget | None = None
        self._char_keys: list[bui.Widget] = []
        self._keyboard_index = 0
        self._last_space_press = 0.0
        self._double_space_interval = 0.3

        self._keyboard: bui.Keyboard
        self._chars: list[str]
        self._modes: list[str]
        self._mode: str
        self._mode_index: int
        self._load_keyboard()

    def _load_keyboard(self) -> None:
        # pylint: disable=too-many-locals
        self._keyboard = self._get_keyboard()
        # We want to get just chars without column data, etc.
        self._chars = [j for i in self._keyboard.chars for j in i]
        self._modes = ['normal'] + list(self._keyboard.pages)
        self._mode_index = 0
        self._mode = self._modes[self._mode_index]

        v = self._height - 180.0
        key_width = 46 * 10 / len(self._keyboard.chars[0])
        key_height = 46 * 3 / len(self._keyboard.chars)
        key_textcolor = (1, 1, 1)
        row_starts = (69.0, 95.0, 151.0)
        key_color = self._key_color
        key_color_dark = self._key_color_dark

        self._click_sound = bui.getsound('click01')

        # kill prev char keys
        for key in self._char_keys:
            key.delete()
        self._char_keys = []

        # dummy data just used for row/column lengths... we don't actually
        # set things until refresh
        chars: list[tuple[str, ...]] = self._keyboard.chars

        for row_num, row in enumerate(chars):
            h = row_starts[row_num]
            # shift key before row 3
            if row_num == 2 and self._shift_button is None:
                self._shift_button = bui.buttonwidget(
                    parent=self._root_widget,
                    position=(h - key_width * 2.0, v),
                    size=(key_width * 1.7, key_height),
                    autoselect=True,
                    textcolor=key_textcolor,
                    color=key_color_dark,
                    label=bui.charstr(bui.SpecialChar.SHIFT),
                    enable_sound=False,
                    extra_touch_border_scale=0.3,
                    button_type='square',
                )

            for _ in row:
                btn = bui.buttonwidget(
                    parent=self._root_widget,
                    position=(h, v),
                    size=(key_width, key_height),
                    autoselect=True,
                    enable_sound=False,
                    textcolor=key_textcolor,
                    color=key_color,
                    label='',
                    button_type='square',
                    extra_touch_border_scale=0.1,
                )
                self._char_keys.append(btn)
                h += key_width + 10

            # Add delete key at end of third row.
            if row_num == 2:
                if self._backspace_button is not None:
                    self._backspace_button.delete()

                self._backspace_button = bui.buttonwidget(
                    parent=self._root_widget,
                    position=(h + 4, v),
                    size=(key_width * 1.8, key_height),
                    autoselect=True,
                    enable_sound=False,
                    repeat=True,
                    textcolor=key_textcolor,
                    color=key_color_dark,
                    label=bui.charstr(bui.SpecialChar.DELETE),
                    button_type='square',
                    on_activate_call=self._del,
                )
            v -= key_height + 9
            # Do space bar and stuff.
            if row_num == 2:
                if self._num_mode_button is None:
                    self._num_mode_button = bui.buttonwidget(
                        parent=self._root_widget,
                        position=(112, v - 8),
                        size=(key_width * 2, key_height + 5),
                        enable_sound=False,
                        button_type='square',
                        extra_touch_border_scale=0.3,
                        autoselect=True,
                        textcolor=key_textcolor,
                        color=key_color_dark,
                        label='',
                    )
                if self._emoji_button is None:
                    self._emoji_button = bui.buttonwidget(
                        parent=self._root_widget,
                        position=(56, v - 8),
                        size=(key_width, key_height + 5),
                        autoselect=True,
                        enable_sound=False,
                        textcolor=key_textcolor,
                        color=key_color_dark,
                        label=bui.charstr(bui.SpecialChar.LOGO_FLAT),
                        extra_touch_border_scale=0.3,
                        button_type='square',
                    )
                btn1 = self._num_mode_button
                if self._space_button is None:
                    self._space_button = bui.buttonwidget(
                        parent=self._root_widget,
                        position=(210, v - 12),
                        size=(key_width * 6.1, key_height + 15),
                        extra_touch_border_scale=0.3,
                        enable_sound=False,
                        autoselect=True,
                        textcolor=key_textcolor,
                        color=key_color_dark,
                        label=bui.Lstr(resource='spaceKeyText'),
                        on_activate_call=bui.Call(self._type_char, ' '),
                    )

                    # Show change instructions only if we have more than one
                    # keyboard option.
                    keyboards = (
                        bui.app.meta.scanresults.exports_of_class(bui.Keyboard)
                        if bui.app.meta.scanresults is not None
                        else []
                    )
                    if len(keyboards) > 1:
                        bui.textwidget(
                            parent=self._root_widget,
                            h_align='center',
                            position=(210, v - 70),
                            size=(key_width * 6.1, key_height + 15),
                            text=bui.Lstr(
                                resource='keyboardChangeInstructionsText'
                            ),
                            scale=0.75,
                        )
                btn2 = self._space_button
                btn3 = self._emoji_button
                bui.widget(edit=btn1, right_widget=btn2, left_widget=btn3)
                bui.widget(
                    edit=btn2, left_widget=btn1, right_widget=self._done_button
                )
                bui.widget(edit=btn3, left_widget=btn1)
                bui.widget(edit=self._done_button, left_widget=btn2)

        bui.containerwidget(
            edit=self._root_widget, selected_child=self._char_keys[14]
        )

        self._refresh()

    def _get_keyboard(self) -> bui.Keyboard:
        assert bui.app.meta.scanresults is not None
        classname = bui.app.meta.scanresults.exports_of_class(bui.Keyboard)[
            self._keyboard_index
        ]
        kbclass = bui.getclass(classname, bui.Keyboard)
        return kbclass()

    def _refresh(self) -> None:
        chars: list[str] | None = None
        if self._mode in ['normal', 'caps']:
            chars = list(self._chars)
            if self._mode == 'caps':
                chars = [c.upper() for c in chars]
            bui.buttonwidget(
                edit=self._shift_button,
                color=self._key_color_lit
                if self._mode == 'caps'
                else self._key_color_dark,
                label=bui.charstr(bui.SpecialChar.SHIFT),
                on_activate_call=self._shift,
            )
            bui.buttonwidget(
                edit=self._num_mode_button,
                label='123#&*',
                on_activate_call=self._num_mode,
            )
            bui.buttonwidget(
                edit=self._emoji_button,
                color=self._key_color_dark,
                label=bui.charstr(bui.SpecialChar.LOGO_FLAT),
                on_activate_call=self._next_mode,
            )
        else:
            if self._mode == 'num':
                chars = list(self._keyboard.nums)
            else:
                chars = list(self._keyboard.pages[self._mode])
            bui.buttonwidget(
                edit=self._shift_button,
                color=self._key_color_dark,
                label='',
                on_activate_call=self._null_press,
            )
            bui.buttonwidget(
                edit=self._num_mode_button,
                label='abc',
                on_activate_call=self._abc_mode,
            )
            bui.buttonwidget(
                edit=self._emoji_button,
                color=self._key_color_dark,
                label=bui.charstr(bui.SpecialChar.LOGO_FLAT),
                on_activate_call=self._next_mode,
            )

        for i, btn in enumerate(self._char_keys):
            assert chars is not None
            have_char = True
            if i >= len(chars):
                # No such char.
                have_char = False
                pagename = self._mode
                if bui.do_once():
                    errstr = (
                        f'Size of page "{pagename}" of keyboard'
                        f' "{self._keyboard.name}" is incorrect:'
                        f' {len(chars)} != {len(self._chars)}'
                        f' (size of default "normal" page)'
                    )
                    logging.error(errstr)
            bui.buttonwidget(
                edit=btn,
                label=chars[i] if have_char else ' ',
                on_activate_call=bui.Call(
                    self._type_char, chars[i] if have_char else ' '
                ),
            )

    def _null_press(self) -> None:
        self._click_sound.play()

    def _abc_mode(self) -> None:
        self._click_sound.play()
        self._mode = 'normal'
        self._refresh()

    def _num_mode(self) -> None:
        self._click_sound.play()
        self._mode = 'num'
        self._refresh()

    def _next_mode(self) -> None:
        self._click_sound.play()
        self._mode_index = (self._mode_index + 1) % len(self._modes)
        self._mode = self._modes[self._mode_index]
        self._refresh()

    def _next_keyboard(self) -> None:
        assert bui.app.meta.scanresults is not None
        kbexports = bui.app.meta.scanresults.exports_of_class(bui.Keyboard)
        self._keyboard_index = (self._keyboard_index + 1) % len(kbexports)

        self._load_keyboard()
        if len(kbexports) < 2:
            bui.getsound('error').play()
            bui.screenmessage(
                bui.Lstr(resource='keyboardNoOthersAvailableText'),
                color=(1, 0, 0),
            )
        else:
            bui.screenmessage(
                bui.Lstr(
                    resource='keyboardSwitchText',
                    subs=[('${NAME}', self._keyboard.name)],
                ),
                color=(0, 1, 0),
            )

    def _shift(self) -> None:
        self._click_sound.play()
        if self._mode == 'normal':
            self._mode = 'caps'
            self._double_press_shift = False
        elif self._mode == 'caps':
            if not self._double_press_shift:
                self._double_press_shift = True
            else:
                self._mode = 'normal'
        self._refresh()

    def _del(self) -> None:
        self._click_sound.play()
        txt = cast(str, bui.textwidget(query=self._text_field))
        # pylint: disable=unsubscriptable-object
        txt = txt[:-1]
        bui.textwidget(edit=self._text_field, text=txt)

    def _type_char(self, char: str) -> None:
        self._click_sound.play()
        if char.isspace():
            if (
                bui.apptime() - self._last_space_press
                < self._double_space_interval
            ):
                self._last_space_press = 0
                self._next_keyboard()
                self._del()  # We typed unneeded space around 1s ago.
                return
            self._last_space_press = bui.apptime()

        # Operate in unicode so we don't do anything funky like chop utf-8
        # chars in half.
        txt = cast(str, bui.textwidget(query=self._text_field))
        txt += char
        bui.textwidget(edit=self._text_field, text=txt)

        # If we were caps, go back only if not Shift is pressed twice.
        if self._mode == 'caps' and not self._double_press_shift:
            self._mode = 'normal'
        self._refresh()

    def _cancel(self) -> None:
        bui.getsound('swish').play()
        bui.containerwidget(edit=self._root_widget, transition='out_scale')

    def _done(self) -> None:
        bui.containerwidget(edit=self._root_widget, transition='out_scale')
        if self._target_text:
            bui.textwidget(
                edit=self._target_text,
                text=cast(str, bui.textwidget(query=self._text_field)),
            )
