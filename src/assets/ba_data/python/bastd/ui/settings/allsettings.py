# Released under the MIT License. See LICENSE for details.
#
"""UI for top level settings categories."""

from __future__ import annotations

from typing import TYPE_CHECKING
from threading import Thread
import logging

import bauiv1 as bui

if TYPE_CHECKING:
    pass


class AllSettingsWindow(bui.Window):
    """Window for selecting a settings category."""

    def __init__(
        self,
        transition: str = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals

        # Preload some modules we use in a background thread so we won't
        # have a visual hitch when the user taps them.
        Thread(target=self._preload_modules).start()

        bui.set_analytics_screen('Settings Window')
        scale_origin: tuple[float, float] | None
        if origin_widget is not None:
            self._transition_out = 'out_scale'
            scale_origin = origin_widget.get_screen_space_center()
            transition = 'in_scale'
        else:
            self._transition_out = 'out_right'
            scale_origin = None
        assert bui.app.classic is not None
        uiscale = bui.app.classic.ui.uiscale
        width = 900 if uiscale is bui.UIScale.SMALL else 580
        x_inset = 75 if uiscale is bui.UIScale.SMALL else 0
        height = 435
        self._r = 'settingsWindow'
        top_extra = 20 if uiscale is bui.UIScale.SMALL else 0

        uiscale = bui.app.classic.ui.uiscale
        super().__init__(
            root_widget=bui.containerwidget(
                size=(width, height + top_extra),
                transition=transition,
                toolbar_visibility='menu_minimal',
                scale_origin_stack_offset=scale_origin,
                scale=(
                    1.75
                    if uiscale is bui.UIScale.SMALL
                    else 1.35
                    if uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
                stack_offset=(0, -8)
                if uiscale is bui.UIScale.SMALL
                else (0, 0),
            )
        )

        if bui.app.classic.ui.use_toolbars and uiscale is bui.UIScale.SMALL:
            self._back_button = None
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self._do_back
            )
        else:
            self._back_button = btn = bui.buttonwidget(
                parent=self._root_widget,
                autoselect=True,
                position=(40 + x_inset, height - 55),
                size=(130, 60),
                scale=0.8,
                text_scale=1.2,
                label=bui.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._do_back,
            )
            bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        bui.textwidget(
            parent=self._root_widget,
            position=(0, height - 44),
            size=(width, 25),
            text=bui.Lstr(resource=self._r + '.titleText'),
            color=bui.app.classic.ui.title_color,
            h_align='center',
            v_align='center',
            maxwidth=130,
        )

        if self._back_button is not None:
            bui.buttonwidget(
                edit=self._back_button,
                button_type='backSmall',
                size=(60, 60),
                label=bui.charstr(bui.SpecialChar.BACK),
            )

        v = height - 80
        v -= 145

        basew = 280 if uiscale is bui.UIScale.SMALL else 230
        baseh = 170
        x_offs = (
            x_inset + (105 if uiscale is bui.UIScale.SMALL else 72) - basew
        )  # now unused
        x_offs2 = x_offs + basew - 7
        x_offs3 = x_offs + 2 * (basew - 7)
        x_offs4 = x_offs2
        x_offs5 = x_offs3

        def _b_title(
            x: float, y: float, button: bui.Widget, text: str | bui.Lstr
        ) -> None:
            bui.textwidget(
                parent=self._root_widget,
                text=text,
                position=(x + basew * 0.47, y + baseh * 0.22),
                maxwidth=basew * 0.7,
                size=(0, 0),
                h_align='center',
                v_align='center',
                draw_controller=button,
                color=(0.7, 0.9, 0.7, 1.0),
            )

        ctb = self._controllers_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs2, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_controllers,
        )
        if bui.app.classic.ui.use_toolbars and self._back_button is None:
            bbtn = bui.get_special_widget('back_button')
            bui.widget(edit=ctb, left_widget=bbtn)
        _b_title(
            x_offs2, v, ctb, bui.Lstr(resource=self._r + '.controllersText')
        )
        imgw = imgh = 130
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs2 + basew * 0.49 - imgw * 0.5, v + 35),
            size=(imgw, imgh),
            texture=bui.gettexture('controllerIcon'),
            draw_controller=ctb,
        )

        gfxb = self._graphics_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs3, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_graphics,
        )
        if bui.app.classic.ui.use_toolbars:
            pbtn = bui.get_special_widget('party_button')
            bui.widget(edit=gfxb, up_widget=pbtn, right_widget=pbtn)
        _b_title(x_offs3, v, gfxb, bui.Lstr(resource=self._r + '.graphicsText'))
        imgw = imgh = 110
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs3 + basew * 0.49 - imgw * 0.5, v + 42),
            size=(imgw, imgh),
            texture=bui.gettexture('graphicsIcon'),
            draw_controller=gfxb,
        )

        v -= baseh - 5

        abtn = self._audio_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs4, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_audio,
        )
        _b_title(x_offs4, v, abtn, bui.Lstr(resource=self._r + '.audioText'))
        imgw = imgh = 120
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs4 + basew * 0.49 - imgw * 0.5 + 5, v + 35),
            size=(imgw, imgh),
            color=(1, 1, 0),
            texture=bui.gettexture('audioIcon'),
            draw_controller=abtn,
        )

        avb = self._advanced_button = bui.buttonwidget(
            parent=self._root_widget,
            autoselect=True,
            position=(x_offs5, v),
            size=(basew, baseh),
            button_type='square',
            label='',
            on_activate_call=self._do_advanced,
        )
        _b_title(x_offs5, v, avb, bui.Lstr(resource=self._r + '.advancedText'))
        imgw = imgh = 120
        bui.imagewidget(
            parent=self._root_widget,
            position=(x_offs5 + basew * 0.49 - imgw * 0.5 + 5, v + 35),
            size=(imgw, imgh),
            color=(0.8, 0.95, 1),
            texture=bui.gettexture('advancedIcon'),
            draw_controller=avb,
        )
        self._restore_state()

    # noinspection PyUnresolvedReferences
    @staticmethod
    def _preload_modules() -> None:
        """Preload modules we use (called in bg thread)."""
        import bastd.ui.mainmenu as _unused1
        import bastd.ui.settings.controls as _unused2
        import bastd.ui.settings.graphics as _unused3
        import bastd.ui.settings.audio as _unused4
        import bastd.ui.settings.advanced as _unused5

    def _do_back(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.mainmenu import MainMenuWindow

        self._save_state()
        bui.containerwidget(
            edit=self._root_widget, transition=self._transition_out
        )
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            MainMenuWindow(transition='in_left').get_root_widget()
        )

    def _do_controllers(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.controls import ControlsSettingsWindow

        self._save_state()
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            ControlsSettingsWindow(
                origin_widget=self._controllers_button
            ).get_root_widget()
        )

    def _do_graphics(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.graphics import GraphicsSettingsWindow

        self._save_state()
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            GraphicsSettingsWindow(
                origin_widget=self._graphics_button
            ).get_root_widget()
        )

    def _do_audio(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.audio import AudioSettingsWindow

        self._save_state()
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            AudioSettingsWindow(
                origin_widget=self._audio_button
            ).get_root_widget()
        )

    def _do_advanced(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.advanced import AdvancedSettingsWindow

        self._save_state()
        bui.containerwidget(edit=self._root_widget, transition='out_left')
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            AdvancedSettingsWindow(
                origin_widget=self._advanced_button
            ).get_root_widget()
        )

    def _save_state(self) -> None:
        try:
            sel = self._root_widget.get_selected_child()
            if sel == self._controllers_button:
                sel_name = 'Controllers'
            elif sel == self._graphics_button:
                sel_name = 'Graphics'
            elif sel == self._audio_button:
                sel_name = 'Audio'
            elif sel == self._advanced_button:
                sel_name = 'Advanced'
            elif sel == self._back_button:
                sel_name = 'Back'
            else:
                raise ValueError(f'unrecognized selection \'{sel}\'')
            assert bui.app.classic is not None
            bui.app.classic.ui.window_states[type(self)] = {
                'sel_name': sel_name
            }
        except Exception:
            logging.exception('Error saving state for %s.', self)

    def _restore_state(self) -> None:
        try:
            assert bui.app.classic is not None
            sel_name = bui.app.classic.ui.window_states.get(type(self), {}).get(
                'sel_name'
            )
            sel: bui.Widget | None
            if sel_name == 'Controllers':
                sel = self._controllers_button
            elif sel_name == 'Graphics':
                sel = self._graphics_button
            elif sel_name == 'Audio':
                sel = self._audio_button
            elif sel_name == 'Advanced':
                sel = self._advanced_button
            elif sel_name == 'Back':
                sel = self._back_button
            else:
                sel = self._controllers_button
            if sel is not None:
                bui.containerwidget(edit=self._root_widget, selected_child=sel)
        except Exception:
            logging.exception('Error restoring state for %s.', self)
