# Released under the MIT License. See LICENSE for details.
#
"""Snippets of code for use by the c++ layer."""
# (most of these are self-explanatory)
# pylint: disable=missing-function-docstring
from __future__ import annotations

from typing import TYPE_CHECKING

import _babase
import _bascenev1

if TYPE_CHECKING:
    from typing import Any

    import bascenev1


def launch_main_menu_session() -> None:
    from bastd.mainmenu import MainMenuSession

    _bascenev1.new_host_session(MainMenuSession)


def get_player_icon(sessionplayer: bascenev1.SessionPlayer) -> dict[str, Any]:
    info = sessionplayer.get_icon_info()
    return {
        'texture': _bascenev1.gettexture(info['texture']),
        'tint_texture': _bascenev1.gettexture(info['tint_texture']),
        'tint_color': info['tint_color'],
        'tint2_color': info['tint2_color'],
    }


def filter_chat_message(msg: str, client_id: int) -> str | None:
    """Intercept/filter chat messages.

    Called for all chat messages while hosting.
    Messages originating from the host will have clientID -1.
    Should filter and return the string to be displayed, or return None
    to ignore the message.
    """
    del client_id  # Unused by default.
    return msg


def local_chat_message(msg: str) -> None:
    assert _babase.app.classic is not None
    if (
        _babase.app.classic.ui.party_window is not None
        and _babase.app.classic.ui.party_window() is not None
    ):
        _babase.app.classic.ui.party_window().on_chat_message(msg)
