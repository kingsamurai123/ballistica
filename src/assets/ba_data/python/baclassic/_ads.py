# Released under the MIT License. See LICENSE for details.
#
"""Functionality related to ads."""
from __future__ import annotations

import time
from typing import TYPE_CHECKING

import _babase
import _bauiv1
import _bascenev1

if TYPE_CHECKING:
    from typing import Callable, Any


class AdsSubsystem:
    """Subsystem for ads functionality in the app.

    Category: **App Classes**

    Access the single shared instance of this class at 'ba.app.ads'.
    """

    def __init__(self) -> None:
        self.last_ad_network = 'unknown'
        self.last_ad_network_set_time = time.time()
        self.ad_amt: float | None = None
        self.last_ad_purpose = 'invalid'
        self.attempted_first_ad = False
        self.last_in_game_ad_remove_message_show_time: float | None = None
        self.last_ad_completion_time: float | None = None
        self.last_ad_was_short = False

    def do_remove_in_game_ads_message(self) -> None:
        """(internal)"""
        from babase._language import Lstr

        # Print this message once every 10 minutes at most.
        tval = _babase.apptime()
        if self.last_in_game_ad_remove_message_show_time is None or (
            tval - self.last_in_game_ad_remove_message_show_time > 60 * 10
        ):
            self.last_in_game_ad_remove_message_show_time = tval
            with _babase.ContextRef.empty():
                _babase.apptimer(
                    1.0,
                    lambda: _babase.screenmessage(
                        Lstr(
                            resource='removeInGameAdsText',
                            subs=[
                                (
                                    '${PRO}',
                                    Lstr(resource='store.bombSquadProNameText'),
                                ),
                                ('${APP_NAME}', Lstr(resource='titleText')),
                            ],
                        ),
                        color=(1, 1, 0),
                    ),
                )

    def show_ad(
        self, purpose: str, on_completion_call: Callable[[], Any] | None = None
    ) -> None:
        """(internal)"""
        self.last_ad_purpose = purpose
        _bauiv1.show_ad(purpose, on_completion_call)

    def show_ad_2(
        self,
        purpose: str,
        on_completion_call: Callable[[bool], Any] | None = None,
    ) -> None:
        """(internal)"""
        self.last_ad_purpose = purpose
        _bauiv1.show_ad_2(purpose, on_completion_call)

    def call_after_ad(self, call: Callable[[], Any]) -> None:
        """Run a call after potentially showing an ad."""
        # pylint: disable=too-many-statements
        # pylint: disable=too-many-branches
        # pylint: disable=too-many-locals

        app = _babase.app
        plus = app.plus
        classic = app.classic
        assert plus is not None
        assert classic is not None
        show = True

        # No ads without net-connections, etc.
        if not _bauiv1.can_show_ad():
            show = False
        if classic.accounts.have_pro():
            show = False  # Pro disables interstitials.
        try:
            session = _bascenev1.get_foreground_host_session()
            assert session is not None
            is_tournament = session.tournament_id is not None
        except Exception:
            is_tournament = False
        if is_tournament:
            show = False  # Never show ads during tournaments.

        if show:
            interval: float | None
            launch_count = app.config.get('launchCount', 0)

            # If we're seeing short ads we may want to space them differently.
            interval_mult = (
                plus.get_v1_account_misc_read_val('ads.shortIntervalMult', 1.0)
                if self.last_ad_was_short
                else 1.0
            )
            if self.ad_amt is None:
                if launch_count <= 1:
                    self.ad_amt = plus.get_v1_account_misc_read_val(
                        'ads.startVal1', 0.99
                    )
                else:
                    self.ad_amt = plus.get_v1_account_misc_read_val(
                        'ads.startVal2', 1.0
                    )
                interval = None
            else:
                # So far we're cleared to show; now calc our
                # ad-show-threshold and see if we should *actually* show
                # (we reach our threshold faster the longer we've been
                # playing).
                base = 'ads' if _bauiv1.has_video_ads() else 'ads2'
                min_lc = plus.get_v1_account_misc_read_val(base + '.minLC', 0.0)
                max_lc = plus.get_v1_account_misc_read_val(base + '.maxLC', 5.0)
                min_lc_scale = plus.get_v1_account_misc_read_val(
                    base + '.minLCScale', 0.25
                )
                max_lc_scale = plus.get_v1_account_misc_read_val(
                    base + '.maxLCScale', 0.34
                )
                min_lc_interval = plus.get_v1_account_misc_read_val(
                    base + '.minLCInterval', 360
                )
                max_lc_interval = plus.get_v1_account_misc_read_val(
                    base + '.maxLCInterval', 300
                )
                if launch_count < min_lc:
                    lc_amt = 0.0
                elif launch_count > max_lc:
                    lc_amt = 1.0
                else:
                    lc_amt = (float(launch_count) - min_lc) / (max_lc - min_lc)
                incr = (1.0 - lc_amt) * min_lc_scale + lc_amt * max_lc_scale
                interval = (
                    1.0 - lc_amt
                ) * min_lc_interval + lc_amt * max_lc_interval
                self.ad_amt += incr
            assert self.ad_amt is not None
            if self.ad_amt >= 1.0:
                self.ad_amt = self.ad_amt % 1.0
                self.attempted_first_ad = True

            # After we've reached the traditional show-threshold once,
            # try again whenever its been INTERVAL since our last successful
            # show.
            elif self.attempted_first_ad and (
                self.last_ad_completion_time is None
                or (
                    interval is not None
                    and _babase.apptime() - self.last_ad_completion_time
                    > (interval * interval_mult)
                )
            ):
                # Reset our other counter too in this case.
                self.ad_amt = 0.0
            else:
                show = False

        # If we're *still* cleared to show, actually tell the system to show.
        if show:
            # As a safety-check, set up an object that will run
            # the completion callback if we've returned and sat for 10 seconds
            # (in case some random ad network doesn't properly deliver its
            # completion callback).
            class _Payload:
                def __init__(self, pcall: Callable[[], Any]):
                    self._call = pcall
                    self._ran = False

                def run(self, fallback: bool = False) -> None:
                    """Run fallback call (and issue a warning about it)."""
                    assert app.classic is not None
                    if not self._ran:
                        if fallback:
                            lanst = app.classic.ads.last_ad_network_set_time
                            print(
                                'ERROR: relying on fallback ad-callback! '
                                'last network: '
                                + app.classic.ads.last_ad_network
                                + ' (set '
                                + str(int(time.time() - lanst))
                                + 's ago); purpose='
                                + app.classic.ads.last_ad_purpose
                            )
                        _babase.pushcall(self._call)
                        self._ran = True

            payload = _Payload(call)
            with _babase.ContextRef.empty():
                _babase.apptimer(5.0, lambda: payload.run(fallback=True))
            self.show_ad('between_game', on_completion_call=payload.run)
        else:
            _babase.pushcall(call)  # Just run the callback without the ad.
