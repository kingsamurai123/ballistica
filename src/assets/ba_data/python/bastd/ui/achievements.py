# Released under the MIT License. See LICENSE for details.
#
"""Provides a popup window to view achievements."""

from __future__ import annotations

from bastd.ui.popup import PopupWindow
import bauiv1 as bui


class AchievementsWindow(PopupWindow):
    """Popup window to view achievements."""

    def __init__(
        self, position: tuple[float, float], scale: float | None = None
    ):
        # pylint: disable=too-many-locals
        assert bui.app.classic is not None
        uiscale = bui.app.classic.ui.uiscale
        if scale is None:
            scale = (
                2.3
                if uiscale is bui.UIScale.SMALL
                else 1.65
                if uiscale is bui.UIScale.MEDIUM
                else 1.23
            )
        self._transitioning_out = False
        self._width = 450
        self._height = (
            300
            if uiscale is bui.UIScale.SMALL
            else 370
            if uiscale is bui.UIScale.MEDIUM
            else 450
        )
        bg_color = (0.5, 0.4, 0.6)

        # creates our _root_widget
        super().__init__(
            position=position,
            size=(self._width, self._height),
            scale=scale,
            bg_color=bg_color,
        )

        self._cancel_button = bui.buttonwidget(
            parent=self.root_widget,
            position=(50, self._height - 30),
            size=(50, 50),
            scale=0.5,
            label='',
            color=bg_color,
            on_activate_call=self._on_cancel_press,
            autoselect=True,
            icon=bui.gettexture('crossOut'),
            iconscale=1.2,
        )

        achievements = bui.app.classic.ach.achievements
        num_complete = len([a for a in achievements if a.complete])

        txt_final = bui.Lstr(
            resource='accountSettingsWindow.achievementProgressText',
            subs=[
                ('${COUNT}', str(num_complete)),
                ('${TOTAL}', str(len(achievements))),
            ],
        )
        self._title_text = bui.textwidget(
            parent=self.root_widget,
            position=(self._width * 0.5, self._height - 20),
            size=(0, 0),
            h_align='center',
            v_align='center',
            scale=0.6,
            text=txt_final,
            maxwidth=200,
            color=(1, 1, 1, 0.4),
        )

        self._scrollwidget = bui.scrollwidget(
            parent=self.root_widget,
            size=(self._width - 60, self._height - 70),
            position=(30, 30),
            capture_arrows=True,
            simple_culling_v=10,
        )
        bui.widget(edit=self._scrollwidget, autoselect=True)

        bui.containerwidget(
            edit=self.root_widget, cancel_button=self._cancel_button
        )

        incr = 36
        sub_width = self._width - 90
        sub_height = 40 + len(achievements) * incr

        eq_rsrc = 'coopSelectWindow.powerRankingPointsEqualsText'
        pts_rsrc = 'coopSelectWindow.powerRankingPointsText'

        self._subcontainer = bui.containerwidget(
            parent=self._scrollwidget,
            size=(sub_width, sub_height),
            background=False,
        )

        total_pts = 0
        for i, ach in enumerate(achievements):
            complete = ach.complete
            bui.textwidget(
                parent=self._subcontainer,
                position=(sub_width * 0.08 - 5, sub_height - 20 - incr * i),
                maxwidth=20,
                scale=0.5,
                color=(0.6, 0.6, 0.7) if complete else (0.6, 0.6, 0.7, 0.2),
                flatness=1.0,
                shadow=0.0,
                text=str(i + 1),
                size=(0, 0),
                h_align='right',
                v_align='center',
            )

            bui.imagewidget(
                parent=self._subcontainer,
                position=(sub_width * 0.10 + 1, sub_height - 20 - incr * i - 9)
                if complete
                else (sub_width * 0.10 - 4, sub_height - 20 - incr * i - 14),
                size=(18, 18) if complete else (27, 27),
                opacity=1.0 if complete else 0.3,
                color=ach.get_icon_color(complete)[:3],
                texture=ach.get_icon_ui_texture(complete),
            )
            if complete:
                bui.imagewidget(
                    parent=self._subcontainer,
                    position=(
                        sub_width * 0.10 - 4,
                        sub_height - 25 - incr * i - 9,
                    ),
                    size=(28, 28),
                    color=(2, 1.4, 0),
                    texture=bui.gettexture('achievementOutline'),
                )
            bui.textwidget(
                parent=self._subcontainer,
                position=(sub_width * 0.19, sub_height - 19 - incr * i + 3),
                maxwidth=sub_width * 0.62,
                scale=0.6,
                flatness=1.0,
                shadow=0.0,
                color=(1, 1, 1) if complete else (1, 1, 1, 0.2),
                text=ach.display_name,
                size=(0, 0),
                h_align='left',
                v_align='center',
            )

            bui.textwidget(
                parent=self._subcontainer,
                position=(sub_width * 0.19, sub_height - 19 - incr * i - 10),
                maxwidth=sub_width * 0.62,
                scale=0.4,
                flatness=1.0,
                shadow=0.0,
                color=(0.83, 0.8, 0.85) if complete else (0.8, 0.8, 0.8, 0.2),
                text=ach.description_full_complete
                if complete
                else ach.description_full,
                size=(0, 0),
                h_align='left',
                v_align='center',
            )

            pts = ach.power_ranking_value
            bui.textwidget(
                parent=self._subcontainer,
                position=(sub_width * 0.92, sub_height - 20 - incr * i),
                maxwidth=sub_width * 0.15,
                color=(0.7, 0.8, 1.0) if complete else (0.9, 0.9, 1.0, 0.3),
                flatness=1.0,
                shadow=0.0,
                scale=0.6,
                text=bui.Lstr(
                    resource=pts_rsrc, subs=[('${NUMBER}', str(pts))]
                ),
                size=(0, 0),
                h_align='center',
                v_align='center',
            )
            if complete:
                total_pts += pts

        bui.textwidget(
            parent=self._subcontainer,
            position=(
                sub_width * 1.0,
                sub_height - 20 - incr * len(achievements),
            ),
            maxwidth=sub_width * 0.5,
            scale=0.7,
            color=(0.7, 0.8, 1.0),
            flatness=1.0,
            shadow=0.0,
            text=bui.Lstr(
                value='${A} ${B}',
                subs=[
                    ('${A}', bui.Lstr(resource='coopSelectWindow.totalText')),
                    (
                        '${B}',
                        bui.Lstr(
                            resource=eq_rsrc,
                            subs=[('${NUMBER}', str(total_pts))],
                        ),
                    ),
                ],
            ),
            size=(0, 0),
            h_align='right',
            v_align='center',
        )

    def _on_cancel_press(self) -> None:
        self._transition_out()

    def _transition_out(self) -> None:
        if not self._transitioning_out:
            self._transitioning_out = True
            bui.containerwidget(edit=self.root_widget, transition='out_scale')

    def on_popup_cancel(self) -> None:
        bui.getsound('swish').play()
        self._transition_out()
