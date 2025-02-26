# Released under the MIT License. See LICENSE for details.
#
"""Defines AppDelegate class for handling high level app functionality."""
from __future__ import annotations

from typing import TYPE_CHECKING

import _babase

if TYPE_CHECKING:
    from typing import Callable
    import babase
    import bascenev1 as bs


class AppDelegate:
    """Defines handlers for high level app functionality.

    Category: App Classes
    """

    def create_default_game_settings_ui(
        self,
        gameclass: type[bs.GameActivity],
        sessiontype: type[bs.Session],
        settings: dict | None,
        completion_call: Callable[[dict | None], None],
    ) -> None:
        """Launch a UI to configure the given game config.

        It should manipulate the contents of config and call completion_call
        when done.
        """
        # Replace the main window once we come up successfully.
        from bastd.ui.playlist.editgame import PlaylistEditGameWindow

        assert _babase.app.classic is not None
        _babase.app.classic.ui.clear_main_menu_window(transition='out_left')
        _babase.app.classic.ui.set_main_menu_window(
            PlaylistEditGameWindow(
                gameclass,
                sessiontype,
                settings,
                completion_call=completion_call,
            ).get_root_widget()
        )
