# Released under the MIT License. See LICENSE for details.
#
"""UI functionality for purchasing/acquiring currency."""

from __future__ import annotations

from typing import TYPE_CHECKING

import bauiv1 as bui

if TYPE_CHECKING:
    from typing import Any


class GetCurrencyWindow(bui.Window):
    """Window for purchasing/acquiring currency."""

    def __init__(
        self,
        transition: str = 'in_right',
        from_modal_store: bool = False,
        modal: bool = False,
        origin_widget: bui.Widget | None = None,
        store_back_location: str | None = None,
    ):
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-locals

        plus = bui.app.plus
        assert plus is not None

        bui.set_analytics_screen('Get Tickets Window')

        self._transitioning_out = False
        self._store_back_location = store_back_location  # ew.

        self._ad_button_greyed = False
        self._smooth_update_timer: bui.AppTimer | None = None
        self._ad_button = None
        self._ad_label = None
        self._ad_image = None
        self._ad_time_text = None

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
        self._width = 1000.0 if uiscale is bui.UIScale.SMALL else 800.0
        x_inset = 100.0 if uiscale is bui.UIScale.SMALL else 0.0
        self._height = 480.0

        self._modal = modal
        self._from_modal_store = from_modal_store
        self._r = 'getTicketsWindow'

        top_extra = 20 if uiscale is bui.UIScale.SMALL else 0

        super().__init__(
            root_widget=bui.containerwidget(
                size=(self._width, self._height + top_extra),
                transition=transition,
                scale_origin_stack_offset=scale_origin,
                color=(0.4, 0.37, 0.55),
                scale=(
                    1.63
                    if uiscale is bui.UIScale.SMALL
                    else 1.2
                    if uiscale is bui.UIScale.MEDIUM
                    else 1.0
                ),
                stack_offset=(0, -3)
                if uiscale is bui.UIScale.SMALL
                else (0, 0),
            )
        )

        btn = bui.buttonwidget(
            parent=self._root_widget,
            position=(55 + x_inset, self._height - 79),
            size=(140, 60),
            scale=1.0,
            autoselect=True,
            label=bui.Lstr(resource='doneText' if modal else 'backText'),
            button_type='regular' if modal else 'back',
            on_activate_call=self._back,
        )

        bui.containerwidget(edit=self._root_widget, cancel_button=btn)

        bui.textwidget(
            parent=self._root_widget,
            position=(self._width * 0.5, self._height - 55),
            size=(0, 0),
            color=bui.app.classic.ui.title_color,
            scale=1.2,
            h_align='center',
            v_align='center',
            text=bui.Lstr(resource=self._r + '.titleText'),
            maxwidth=290,
        )

        if not modal:
            bui.buttonwidget(
                edit=btn,
                button_type='backSmall',
                size=(60, 60),
                label=bui.charstr(bui.SpecialChar.BACK),
            )

        b_size = (220.0, 180.0)
        v = self._height - b_size[1] - 80
        spacing = 1

        self._ad_button = None

        def _add_button(
            item: str,
            position: tuple[float, float],
            size: tuple[float, float],
            label: bui.Lstr,
            price: str | None = None,
            tex_name: str | None = None,
            tex_opacity: float = 1.0,
            tex_scale: float = 1.0,
            enabled: bool = True,
            text_scale: float = 1.0,
        ) -> bui.Widget:
            btn2 = bui.buttonwidget(
                parent=self._root_widget,
                position=position,
                button_type='square',
                size=size,
                label='',
                autoselect=True,
                color=None if enabled else (0.5, 0.5, 0.5),
                on_activate_call=(
                    bui.Call(self._purchase, item)
                    if enabled
                    else self._disabled_press
                ),
            )
            txt = bui.textwidget(
                parent=self._root_widget,
                text=label,
                position=(
                    position[0] + size[0] * 0.5,
                    position[1] + size[1] * 0.3,
                ),
                scale=text_scale,
                maxwidth=size[0] * 0.75,
                size=(0, 0),
                h_align='center',
                v_align='center',
                draw_controller=btn2,
                color=(0.7, 0.9, 0.7, 1.0 if enabled else 0.2),
            )
            if price is not None and enabled:
                bui.textwidget(
                    parent=self._root_widget,
                    text=price,
                    position=(
                        position[0] + size[0] * 0.5,
                        position[1] + size[1] * 0.17,
                    ),
                    scale=0.7,
                    maxwidth=size[0] * 0.75,
                    size=(0, 0),
                    h_align='center',
                    v_align='center',
                    draw_controller=btn2,
                    color=(0.4, 0.9, 0.4, 1.0),
                )
            i = None
            if tex_name is not None:
                tex_size = 90.0 * tex_scale
                i = bui.imagewidget(
                    parent=self._root_widget,
                    texture=bui.gettexture(tex_name),
                    position=(
                        position[0] + size[0] * 0.5 - tex_size * 0.5,
                        position[1] + size[1] * 0.66 - tex_size * 0.5,
                    ),
                    size=(tex_size, tex_size),
                    draw_controller=btn2,
                    opacity=tex_opacity * (1.0 if enabled else 0.25),
                )
            if item == 'ad':
                self._ad_button = btn2
                self._ad_label = txt
                assert i is not None
                self._ad_image = i
                self._ad_time_text = bui.textwidget(
                    parent=self._root_widget,
                    text='1m 10s',
                    position=(
                        position[0] + size[0] * 0.5,
                        position[1] + size[1] * 0.5,
                    ),
                    scale=text_scale * 1.2,
                    maxwidth=size[0] * 0.85,
                    size=(0, 0),
                    h_align='center',
                    v_align='center',
                    draw_controller=btn2,
                    color=(0.4, 0.9, 0.4, 1.0),
                )
            return btn2

        rsrc = self._r + '.ticketsText'

        c2txt = bui.Lstr(
            resource=rsrc,
            subs=[
                (
                    '${COUNT}',
                    str(
                        plus.get_v1_account_misc_read_val('tickets2Amount', 500)
                    ),
                )
            ],
        )
        c3txt = bui.Lstr(
            resource=rsrc,
            subs=[
                (
                    '${COUNT}',
                    str(
                        plus.get_v1_account_misc_read_val(
                            'tickets3Amount', 1500
                        )
                    ),
                )
            ],
        )
        c4txt = bui.Lstr(
            resource=rsrc,
            subs=[
                (
                    '${COUNT}',
                    str(
                        plus.get_v1_account_misc_read_val(
                            'tickets4Amount', 5000
                        )
                    ),
                )
            ],
        )
        c5txt = bui.Lstr(
            resource=rsrc,
            subs=[
                (
                    '${COUNT}',
                    str(
                        plus.get_v1_account_misc_read_val(
                            'tickets5Amount', 15000
                        )
                    ),
                )
            ],
        )

        h = 110.0

        # Enable buttons if we have prices.
        tickets2_price = plus.get_price('tickets2')
        tickets3_price = plus.get_price('tickets3')
        tickets4_price = plus.get_price('tickets4')
        tickets5_price = plus.get_price('tickets5')

        # TEMP
        # tickets1_price = '$0.99'
        # tickets2_price = '$4.99'
        # tickets3_price = '$9.99'
        # tickets4_price = '$19.99'
        # tickets5_price = '$49.99'

        _add_button(
            'tickets2',
            enabled=(tickets2_price is not None),
            position=(
                self._width * 0.5 - spacing * 1.5 - b_size[0] * 2.0 + h,
                v,
            ),
            size=b_size,
            label=c2txt,
            price=tickets2_price,
            tex_name='ticketsMore',
        )  # 0.99-ish
        _add_button(
            'tickets3',
            enabled=(tickets3_price is not None),
            position=(
                self._width * 0.5 - spacing * 0.5 - b_size[0] * 1.0 + h,
                v,
            ),
            size=b_size,
            label=c3txt,
            price=tickets3_price,
            tex_name='ticketRoll',
        )  # 4.99-ish
        v -= b_size[1] - 5
        _add_button(
            'tickets4',
            enabled=(tickets4_price is not None),
            position=(
                self._width * 0.5 - spacing * 1.5 - b_size[0] * 2.0 + h,
                v,
            ),
            size=b_size,
            label=c4txt,
            price=tickets4_price,
            tex_name='ticketRollBig',
            tex_scale=1.2,
        )  # 9.99-ish
        _add_button(
            'tickets5',
            enabled=(tickets5_price is not None),
            position=(
                self._width * 0.5 - spacing * 0.5 - b_size[0] * 1.0 + h,
                v,
            ),
            size=b_size,
            label=c5txt,
            price=tickets5_price,
            tex_name='ticketRolls',
            tex_scale=1.2,
        )  # 19.99-ish

        self._enable_ad_button = bui.has_video_ads()
        h = self._width * 0.5 + 110.0
        v = self._height - b_size[1] - 115.0

        if self._enable_ad_button:
            h_offs = 35
            b_size_3 = (150, 120)
            cdb = _add_button(
                'ad',
                position=(h + h_offs, v),
                size=b_size_3,
                label=bui.Lstr(
                    resource=self._r + '.ticketsFromASponsorText',
                    subs=[
                        (
                            '${COUNT}',
                            str(
                                plus.get_v1_account_misc_read_val(
                                    'sponsorTickets', 5
                                )
                            ),
                        )
                    ],
                ),
                tex_name='ticketsMore',
                enabled=self._enable_ad_button,
                tex_opacity=0.6,
                tex_scale=0.7,
                text_scale=0.7,
            )
            bui.buttonwidget(edit=cdb, color=(0.65, 0.5, 0.7))

            self._ad_free_text = bui.textwidget(
                parent=self._root_widget,
                text=bui.Lstr(resource=self._r + '.freeText'),
                position=(
                    h + h_offs + b_size_3[0] * 0.5,
                    v + b_size_3[1] * 0.5 + 25,
                ),
                size=(0, 0),
                color=(1, 1, 0, 1.0),
                draw_controller=cdb,
                rotate=15,
                shadow=1.0,
                maxwidth=150,
                h_align='center',
                v_align='center',
                scale=1.0,
            )
            v -= 125
        else:
            v -= 20

        if True:  # pylint: disable=using-constant-test
            h_offs = 35
            b_size_3 = (150, 120)
            cdb = _add_button(
                'app_invite',
                position=(h + h_offs, v),
                size=b_size_3,
                label=bui.Lstr(
                    resource='gatherWindow.earnTicketsForRecommendingText',
                    subs=[
                        (
                            '${COUNT}',
                            str(
                                plus.get_v1_account_misc_read_val(
                                    'sponsorTickets', 5
                                )
                            ),
                        )
                    ],
                ),
                tex_name='ticketsMore',
                enabled=True,
                tex_opacity=0.6,
                tex_scale=0.7,
                text_scale=0.7,
            )
            bui.buttonwidget(edit=cdb, color=(0.65, 0.5, 0.7))

            bui.textwidget(
                parent=self._root_widget,
                text=bui.Lstr(resource=self._r + '.freeText'),
                position=(
                    h + h_offs + b_size_3[0] * 0.5,
                    v + b_size_3[1] * 0.5 + 25,
                ),
                size=(0, 0),
                color=(1, 1, 0, 1.0),
                draw_controller=cdb,
                rotate=15,
                shadow=1.0,
                maxwidth=150,
                h_align='center',
                v_align='center',
                scale=1.0,
            )
            tc_y_offs = 0

        h = self._width - (185 + x_inset)
        v = self._height - 95 + tc_y_offs

        txt1 = (
            bui.Lstr(resource=self._r + '.youHaveText')
            .evaluate()
            .partition('${COUNT}')[0]
            .strip()
        )
        txt2 = (
            bui.Lstr(resource=self._r + '.youHaveText')
            .evaluate()
            .rpartition('${COUNT}')[-1]
            .strip()
        )

        bui.textwidget(
            parent=self._root_widget,
            text=txt1,
            position=(h, v),
            size=(0, 0),
            color=(0.5, 0.5, 0.6),
            maxwidth=200,
            h_align='center',
            v_align='center',
            scale=0.8,
        )
        v -= 30
        self._ticket_count_text = bui.textwidget(
            parent=self._root_widget,
            position=(h, v),
            size=(0, 0),
            color=(0.2, 1.0, 0.2),
            maxwidth=200,
            h_align='center',
            v_align='center',
            scale=1.6,
        )
        v -= 30
        bui.textwidget(
            parent=self._root_widget,
            text=txt2,
            position=(h, v),
            size=(0, 0),
            color=(0.5, 0.5, 0.6),
            maxwidth=200,
            h_align='center',
            v_align='center',
            scale=0.8,
        )

        self._ticking_sound: bui.Sound | None = None
        self._smooth_ticket_count: float | None = None
        self._ticket_count = 0
        self._update()
        self._update_timer = bui.AppTimer(
            1.0, bui.WeakCall(self._update), repeat=True
        )
        self._smooth_increase_speed = 1.0

    def __del__(self) -> None:
        if self._ticking_sound is not None:
            self._ticking_sound.stop()
            self._ticking_sound = None

    def _smooth_update(self) -> None:
        if not self._ticket_count_text:
            self._smooth_update_timer = None
            return

        finished = False

        # If we're going down, do it immediately.
        assert self._smooth_ticket_count is not None
        if int(self._smooth_ticket_count) >= self._ticket_count:
            self._smooth_ticket_count = float(self._ticket_count)
            finished = True
        else:
            # We're going up; start a sound if need be.
            self._smooth_ticket_count = min(
                self._smooth_ticket_count + 1.0 * self._smooth_increase_speed,
                self._ticket_count,
            )
            if int(self._smooth_ticket_count) >= self._ticket_count:
                finished = True
                self._smooth_ticket_count = float(self._ticket_count)
            elif self._ticking_sound is None:
                self._ticking_sound = bui.getsound('scoreIncrease')
                self._ticking_sound.play()

        bui.textwidget(
            edit=self._ticket_count_text,
            text=str(int(self._smooth_ticket_count)),
        )

        # If we've reached the target, kill the timer/sound/etc.
        if finished:
            self._smooth_update_timer = None
            if self._ticking_sound is not None:
                self._ticking_sound.stop()
                self._ticking_sound = None
                bui.getsound('cashRegister2').play()

    def _update(self) -> None:
        import datetime

        plus = bui.app.plus
        assert plus is not None

        # if we somehow get signed out, just die..
        if plus.get_v1_account_state() != 'signed_in':
            self._back()
            return

        self._ticket_count = plus.get_v1_account_ticket_count()

        # update our incentivized ad button depending on whether ads are
        # available
        if self._ad_button is not None:
            next_reward_ad_time = plus.get_v1_account_misc_read_val_2(
                'nextRewardAdTime', None
            )
            if next_reward_ad_time is not None:
                next_reward_ad_time = datetime.datetime.utcfromtimestamp(
                    next_reward_ad_time
                )
            now = datetime.datetime.utcnow()
            if bui.have_incentivized_ad() and (
                next_reward_ad_time is None or next_reward_ad_time <= now
            ):
                self._ad_button_greyed = False
                bui.buttonwidget(edit=self._ad_button, color=(0.65, 0.5, 0.7))
                bui.textwidget(edit=self._ad_label, color=(0.7, 0.9, 0.7, 1.0))
                bui.textwidget(edit=self._ad_free_text, color=(1, 1, 0, 1))
                bui.imagewidget(edit=self._ad_image, opacity=0.6)
                bui.textwidget(edit=self._ad_time_text, text='')
            else:
                self._ad_button_greyed = True
                bui.buttonwidget(edit=self._ad_button, color=(0.5, 0.5, 0.5))
                bui.textwidget(edit=self._ad_label, color=(0.7, 0.9, 0.7, 0.2))
                bui.textwidget(edit=self._ad_free_text, color=(1, 1, 0, 0.2))
                bui.imagewidget(edit=self._ad_image, opacity=0.6 * 0.25)
                sval: str | bui.Lstr
                if (
                    next_reward_ad_time is not None
                    and next_reward_ad_time > now
                ):
                    sval = bui.timestring(
                        (next_reward_ad_time - now).total_seconds(), centi=False
                    )
                else:
                    sval = ''
                bui.textwidget(edit=self._ad_time_text, text=sval)

        # if this is our first update, assign immediately; otherwise kick
        # off a smooth transition if the value has changed
        if self._smooth_ticket_count is None:
            self._smooth_ticket_count = float(self._ticket_count)
            self._smooth_update()  # will set the text widget

        elif (
            self._ticket_count != int(self._smooth_ticket_count)
            and self._smooth_update_timer is None
        ):
            self._smooth_update_timer = bui.AppTimer(
                0.05, bui.WeakCall(self._smooth_update), repeat=True
            )
            diff = abs(float(self._ticket_count) - self._smooth_ticket_count)
            self._smooth_increase_speed = (
                diff / 100.0
                if diff >= 5000
                else diff / 50.0
                if diff >= 1500
                else diff / 30.0
                if diff >= 500
                else diff / 15.0
            )

    def _disabled_press(self) -> None:
        plus = bui.app.plus
        assert plus is not None

        # if we're on a platform without purchases, inform the user they
        # can link their accounts and buy stuff elsewhere
        app = bui.app
        assert app.classic is not None
        if (
            app.test_build
            or (
                app.classic.platform == 'android'
                and app.classic.subplatform in ['oculus', 'cardboard']
            )
        ) and plus.get_v1_account_misc_read_val('allowAccountLinking2', False):
            bui.screenmessage(
                bui.Lstr(resource=self._r + '.unavailableLinkAccountText'),
                color=(1, 0.5, 0),
            )
        else:
            bui.screenmessage(
                bui.Lstr(resource=self._r + '.unavailableText'),
                color=(1, 0.5, 0),
            )
        bui.getsound('error').play()

    def _purchase(self, item: str) -> None:
        from bastd.ui import account
        from bastd.ui import appinvite

        plus = bui.app.plus
        assert plus is not None

        if bui.app.classic is None:
            raise RuntimeError('This requires classic support.')

        if item == 'app_invite':
            if plus.get_v1_account_state() != 'signed_in':
                account.show_sign_in_prompt()
                return
            appinvite.handle_app_invites_press()
            return
        # here we ping the server to ask if it's valid for us to
        # purchase this.. (better to fail now than after we've paid locally)
        app = bui.app
        assert app.classic is not None
        bui.app.classic.master_server_v1_get(
            'bsAccountPurchaseCheck',
            {
                'item': item,
                'platform': app.classic.platform,
                'subplatform': app.classic.subplatform,
                'version': app.version,
                'buildNumber': app.build_number,
            },
            callback=bui.WeakCall(self._purchase_check_result, item),
        )

    def _purchase_check_result(
        self, item: str, result: dict[str, Any] | None
    ) -> None:
        if result is None:
            bui.getsound('error').play()
            bui.screenmessage(
                bui.Lstr(resource='internal.unavailableNoConnectionText'),
                color=(1, 0, 0),
            )
        else:
            if result['allow']:
                self._do_purchase(item)
            else:
                if result['reason'] == 'versionTooOld':
                    bui.getsound('error').play()
                    bui.screenmessage(
                        bui.Lstr(resource='getTicketsWindow.versionTooOldText'),
                        color=(1, 0, 0),
                    )
                else:
                    bui.getsound('error').play()
                    bui.screenmessage(
                        bui.Lstr(resource='getTicketsWindow.unavailableText'),
                        color=(1, 0, 0),
                    )

    # actually start the purchase locally..
    def _do_purchase(self, item: str) -> None:
        plus = bui.app.plus
        assert plus is not None

        if item == 'ad':
            import datetime

            # if ads are disabled until some time, error..
            next_reward_ad_time = plus.get_v1_account_misc_read_val_2(
                'nextRewardAdTime', None
            )
            if next_reward_ad_time is not None:
                next_reward_ad_time = datetime.datetime.utcfromtimestamp(
                    next_reward_ad_time
                )
            now = datetime.datetime.utcnow()
            if (
                next_reward_ad_time is not None and next_reward_ad_time > now
            ) or self._ad_button_greyed:
                bui.getsound('error').play()
                bui.screenmessage(
                    bui.Lstr(
                        resource='getTicketsWindow.unavailableTemporarilyText'
                    ),
                    color=(1, 0, 0),
                )
            elif self._enable_ad_button:
                assert bui.app.classic is not None
                bui.app.classic.ads.show_ad('tickets')
        else:
            plus.purchase(item)

    def _back(self) -> None:
        from bastd.ui.store import browser

        if self._transitioning_out:
            return
        bui.containerwidget(
            edit=self._root_widget, transition=self._transition_out
        )
        if not self._modal:
            window = browser.StoreBrowserWindow(
                transition='in_left',
                modal=self._from_modal_store,
                back_location=self._store_back_location,
            ).get_root_widget()
            if not self._from_modal_store:
                assert bui.app.classic is not None
                bui.app.classic.ui.set_main_menu_window(window)
        self._transitioning_out = True


def show_get_tickets_prompt() -> None:
    """Show a 'not enough tickets' prompt with an option to purchase more.

    Note that the purchase option may not always be available
    depending on the build of the game.
    """
    from bastd.ui.confirm import ConfirmWindow

    assert bui.app.classic is not None
    if bui.app.classic.allow_ticket_purchases:
        ConfirmWindow(
            bui.Lstr(
                translate=(
                    'serverResponses',
                    'You don\'t have enough tickets for this!',
                )
            ),
            lambda: GetCurrencyWindow(modal=True),
            ok_text=bui.Lstr(resource='getTicketsWindow.titleText'),
            width=460,
            height=130,
        )
    else:
        ConfirmWindow(
            bui.Lstr(
                translate=(
                    'serverResponses',
                    'You don\'t have enough tickets for this!',
                )
            ),
            cancel_button=False,
            width=460,
            height=130,
        )
