# Released under the MIT License. See LICENSE for details.
#
"""Plugin Window UI."""

from __future__ import annotations

from typing import TYPE_CHECKING

import bauiv1 as bui

if TYPE_CHECKING:
    pass


class PluginWindow(bui.Window):
    """Window for configuring plugins."""

    def __init__(
        self,
        transition: str = 'in_right',
        origin_widget: bui.Widget | None = None,
    ):
        # pylint: disable=too-many-locals
        # pylint: disable=too-many-statements
        app = bui.app

        # If they provided an origin-widget, scale up from that.
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
        self._width = 870.0 if uiscale is bui.UIScale.SMALL else 670.0
        x_inset = 100 if uiscale is bui.UIScale.SMALL else 0
        self._height = (
            390.0
            if uiscale is bui.UIScale.SMALL
            else 450.0
            if uiscale is bui.UIScale.MEDIUM
            else 520.0
        )
        top_extra = 10 if uiscale is bui.UIScale.SMALL else 0
        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height + top_extra),
                transition=transition,
                toolbar_visibility='menu_minimal',
                scale_origin_stack_offset=scale_origin,
                scale=(
                    2.06
                    if uiscale is bui.UIScale.SMALL
                    else 1.4
                    if uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
                stack_offset=(0, -25)
                if uiscale is bui.UIScale.SMALL
                else (0, 0),
            )
        )

        self._scroll_width = self._width - (100 + 2 * x_inset)
        self._scroll_height = self._height - 115.0
        self._sub_width = self._scroll_width * 0.95
        self._sub_height = 724.0

        assert app.classic is not None
        if app.classic.ui.use_toolbars and uiscale is bui.UIScale.SMALL:
            bui.containerwidget(
                edit=self._root_widget, on_cancel_call=self._do_back
            )
            self._back_button = None
        else:
            self._back_button = bui.buttonwidget(
                parent=self._root_widget,
                position=(53 + x_inset, self._height - 60),
                size=(140, 60),
                scale=0.8,
                autoselect=True,
                label=bui.Lstr(resource='backText'),
                button_type='back',
                on_activate_call=self._do_back,
            )
            bui.containerwidget(
                edit=self._root_widget, cancel_button=self._back_button
            )

        self._title_text = bui.textwidget(
            parent=self._root_widget,
            position=(0, self._height - 52),
            size=(self._width, 25),
            text=bui.Lstr(resource='pluginsText'),
            color=app.classic.ui.title_color,
            h_align='center',
            v_align='top',
        )

        if self._back_button is not None:
            bui.buttonwidget(
                edit=self._back_button,
                button_type='backSmall',
                size=(60, 60),
                label=bui.charstr(bui.SpecialChar.BACK),
            )
        settings_button_x = 670 if uiscale is bui.UIScale.SMALL else 570
        self._settings_button = bui.buttonwidget(
            parent=self._root_widget,
            position=(settings_button_x, self._height - 60),
            size=(40, 40),
            label='',
            on_activate_call=self._open_settings,
        )

        bui.imagewidget(
            parent=self._root_widget,
            position=(settings_button_x + 3, self._height - 60),
            size=(35, 35),
            texture=bui.gettexture('settingsIcon'),
        )

        bui.widget(
            edit=self._settings_button,
            up_widget=self._settings_button,
            right_widget=self._settings_button,
        )

        self._scrollwidget = bui.scrollwidget(
            parent=self._root_widget,
            position=(50 + x_inset, 50),
            simple_culling_v=20.0,
            highlight=False,
            size=(self._scroll_width, self._scroll_height),
            selection_loops_to_parent=True,
            claims_left_right=True,
        )
        bui.widget(edit=self._scrollwidget, right_widget=self._scrollwidget)

        if bui.app.meta.scanresults is None:
            bui.screenmessage(
                'Still scanning plugins; please try again.', color=(1, 0, 0)
            )
            bui.getsound('error').play()
        pluglist = bui.app.plugins.potential_plugins
        plugstates: dict[str, dict] = bui.app.config.setdefault('Plugins', {})
        assert isinstance(plugstates, dict)

        plug_line_height = 50
        sub_width = self._scroll_width
        sub_height = len(pluglist) * plug_line_height
        self._subcontainer = bui.containerwidget(
            parent=self._scrollwidget,
            size=(sub_width, sub_height),
            background=False,
        )

        for i, availplug in enumerate(pluglist):
            plugin = bui.app.plugins.active_plugins.get(availplug.class_path)
            active = plugin is not None

            plugstate = plugstates.setdefault(availplug.class_path, {})
            checked = plugstate.get('enabled', False)
            assert isinstance(checked, bool)

            item_y = sub_height - (i + 1) * plug_line_height
            check = bui.checkboxwidget(
                parent=self._subcontainer,
                text=availplug.display_name,
                autoselect=True,
                value=checked,
                maxwidth=self._scroll_width - 200,
                position=(10, item_y),
                size=(self._scroll_width - 40, 50),
                on_value_change_call=bui.Call(
                    self._check_value_changed, availplug
                ),
                textcolor=(
                    (0.8, 0.3, 0.3)
                    if not availplug.available
                    else (0, 1, 0)
                    if active
                    else (0.6, 0.6, 0.6)
                ),
            )
            if plugin is not None and plugin.has_settings_ui():
                button = bui.buttonwidget(
                    parent=self._subcontainer,
                    label=bui.Lstr(resource='mainMenu.settingsText'),
                    autoselect=True,
                    size=(100, 40),
                    position=(sub_width - 130, item_y + 6),
                )
                bui.buttonwidget(
                    edit=button,
                    on_activate_call=bui.Call(plugin.show_settings_ui, button),
                )
            else:
                button = None

            # Allow getting back to back button.
            if i == 0:
                bui.widget(
                    edit=check,
                    up_widget=self._back_button,
                    left_widget=self._back_button,
                    right_widget=self._settings_button,
                )
                if button is not None:
                    bui.widget(edit=button, up_widget=self._back_button)

            # Make sure we scroll all the way to the end when using
            # keyboard/button nav.
            bui.widget(edit=check, show_buffer_top=40, show_buffer_bottom=40)

        bui.containerwidget(
            edit=self._root_widget, selected_child=self._scrollwidget
        )

        self._restore_state()

    def _check_value_changed(
        self, plug: bui.PotentialPlugin, value: bool
    ) -> None:
        bui.screenmessage(
            bui.Lstr(resource='settingsWindowAdvanced.mustRestartText'),
            color=(1.0, 0.5, 0.0),
        )
        plugstates: dict[str, dict] = bui.app.config.setdefault('Plugins', {})
        assert isinstance(plugstates, dict)
        plugstate = plugstates.setdefault(plug.class_path, {})
        plugstate['enabled'] = value
        bui.app.config.commit()

    def _open_settings(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.pluginsettings import PluginSettingsWindow

        bui.getsound('swish').play()

        bui.containerwidget(edit=self._root_widget, transition='out_left')
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            PluginSettingsWindow(transition='in_right').get_root_widget()
        )

    def _save_state(self) -> None:
        pass

    def _restore_state(self) -> None:
        pass

    def _do_back(self) -> None:
        # pylint: disable=cyclic-import
        from bastd.ui.settings.advanced import AdvancedSettingsWindow

        self._save_state()
        bui.containerwidget(
            edit=self._root_widget, transition=self._transition_out
        )
        assert bui.app.classic is not None
        bui.app.classic.ui.set_main_menu_window(
            AdvancedSettingsWindow(transition='in_left').get_root_widget()
        )
