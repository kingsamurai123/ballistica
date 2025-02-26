// Released under the MIT License. See LICENSE for details.

#ifndef BALLISTICA_CORE_PLATFORM_CORE_PLATFORM_H_
#define BALLISTICA_CORE_PLATFORM_CORE_PLATFORM_H_

#include <sys/stat.h>

#include <list>
#include <optional>
#include <string>
#include <vector>

#include "ballistica/shared/ballistica.h"

namespace ballistica::core {

/// For capturing and printing stack-traces and related errors. Platforms
/// should subclass this and return instances in GetStackTrace(). Stack
/// trace classes should capture the stack state immediately upon
/// construction but should do the bare minimum amount of work to store it.
/// Any expensive operations such as symbolification should be deferred
/// until GetDescription().
class PlatformStackTrace {
 public:
  virtual ~PlatformStackTrace() = default;

  // Return a human readable version of the trace (with symbolification if
  // available).
  virtual auto GetDescription() noexcept -> std::string = 0;

  // Should return a copy of itself allocated via new() (or nullptr if not
  // possible).
  virtual auto copy() const noexcept -> PlatformStackTrace* = 0;
};

/// This class attempts to abstract away most platform-specific
/// functionality. Ideally we should need to pull in no platform-specific
/// system headers outside of the platform*.cc files and can just go through
/// this.
class CorePlatform {
 public:
  /// Create the proper CorePlatform subclass for the current platform.
  static auto Create() -> CorePlatform*;

#pragma mark LIFECYCLE/SETTINGS ------------------------------------------------

  /// Called after our singleton has been instantiated. Any construction
  /// functionality requiring virtual functions resolving to their final
  /// class versions can go here.
  virtual void PostInit();

  virtual void WillExitMain(bool errored);

  /// Inform the platform that all subsystems are up and running and it can
  /// start talking to them.
  virtual void OnMainThreadStartApp();

  virtual void OnAppStart();
  virtual void OnAppPause();
  virtual void OnAppResume();
  virtual void OnAppShutdown();
  virtual void ApplyAppConfig();
  virtual void OnScreenSizeChange();
  virtual void StepDisplayTime();

  // Get/set values before standard game settings are available (for values
  // needed before SDL init/etc). FIXME: We should have some sort of
  // 'bootconfig.json' file for these. (or simply read the regular config in
  // via c++ immediately)
  auto GetLowLevelConfigValue(const char* key, int default_value) -> int;
  void SetLowLevelConfigValue(const char* key, int value);

#pragma mark FILES -------------------------------------------------------------

  /// remove() supporting UTF8 strings.
  virtual auto Remove(const char* path) -> int;

  /// stat() supporting UTF8 strings.
  virtual auto Stat(const char* path, struct BA_STAT* buffer) -> int;

  /// fopen() supporting UTF8 strings.
  virtual auto FOpen(const char* path, const char* mode) -> FILE*;

  /// rename() supporting UTF8 strings.
  /// For cross-platform consistency, this should also remove any file that
  /// exists at the target location first.
  virtual auto Rename(const char* oldname, const char* newname) -> int;

  /// Simple cross-platform check for existence of a file.
  auto FilePathExists(const std::string& name) -> bool;

  /// Attempt to make a directory. Raise an Exception if unable, unless
  /// quiet is true. Succeeds if the directory already exists.
  void MakeDir(const std::string& dir, bool quiet = false);

  /// Return the current working directory.
  virtual auto GetCWD() -> std::string;

  /// Unlink a file.
  virtual void Unlink(const char* path);

  /// Return the absolute path for the provided path. Note that this
  /// requires the path to already exist.
  auto AbsPath(const std::string& path, std::string* outpath) -> bool;

#pragma mark CLIPBOARD ---------------------------------------------------------

  /// Return whether clipboard operations are supported at all. This gets
  /// called when determining whether to display clipboard related UI
  /// elements/etc.
  auto ClipboardIsSupported() -> bool;

  /// Return whether there is currently text on the clipboard.
  auto ClipboardHasText() -> bool;

  /// Set current clipboard text. Raises an Exception if clipboard is
  /// unsupported.
  void ClipboardSetText(const std::string& text);

  /// Return current text from the clipboard. Raises an Exception if
  /// clipboard is unsupported or if there's no text on the clipboard.
  auto ClipboardGetText() -> std::string;

#pragma mark PRINTING/LOGGING --------------------------------------------------

  /// Display a message to any default log for the platform (android log,
  /// etc.) Note that this can be called from any thread.
  virtual void DisplayLog(const std::string& name, LogLevel level,
                          const std::string& msg);

#pragma mark ENVIRONMENT -------------------------------------------------------

  // Return a simple name for the platform: 'mac', 'windows', 'linux', etc.
  virtual auto GetPlatformName() -> std::string;

  // Return a simple name for the subplatform: 'amazon', 'google', etc.
  virtual auto GetSubplatformName() -> std::string;

  // Are we running in event-push-mode? With this on, we return from Main()
  // and the system handles the event loop. With it off, we loop in Main()
  // ourself.
  virtual auto IsEventPushMode() -> bool;

  /// Return the interface type based on the environment (phone, tablet,
  /// etc).
  virtual auto GetUIScale() -> UIScale;

  /// Get the data directory. This dir contains ba_data and possibly other
  /// platform-specific bits needed for the app to function.
  auto GetDataDirectory() -> std::string;

  /// Return default DataDirectory value for monolithic builds.
  auto GetDataDirectoryMonolithicDefault() -> std::string;

  /// Get the root config directory. This dir contains the app config file
  /// and other data considered essential to the app install. This directory
  /// should be included in OS backups.
  auto GetConfigDirectory() -> std::string;
  auto GetConfigDirectoryMonolithicDefault() -> std::optional<std::string>;

  /// Get the path of the app config file.
  auto GetConfigFilePath() -> std::string;

  /// Return a directory where the local user can manually place Python
  /// files where they will be accessible by the app. When possible, this
  /// directory should be in a place easily accessible to the user.
  auto GetUserPythonDirectory() -> std::optional<std::string>;
  auto GetUserPythonDirectoryMonolithicDefault() -> std::optional<std::string>;

  /// Return the directory where the app expects to find its bundled Python
  /// files.
  auto GetAppPythonDirectory() -> std::optional<std::string>;

  /// Return the directory where bundled 3rd party Python files live.
  auto GetSitePythonDirectory() -> std::optional<std::string>;

  /// Get a directory where the app can store internal generated data. This
  /// directory should not be included in backups and the app should remain
  /// functional if this directory is completely cleared between runs
  /// (though it is expected that things stay intact here *while* the app is
  /// running).
  auto GetVolatileDataDirectory() -> std::string;

  /// Return the directory where game replay files live.
  auto GetReplaysDir() -> std::string;

  /// Return en_US or whatnot.
  virtual auto GetLocale() -> std::string;

  virtual auto GetUserAgentString() -> std::string;
  virtual auto GetOSVersionString() -> std::string;

  /// Set an environment variable as utf8, overwriting if it already exists.
  /// Raises an exception on errors.
  virtual void SetEnv(const std::string& name, const std::string& value);

  virtual auto GetEnv(const std::string& name) -> std::optional<std::string>;

  /// Return hostname or other id suitable for displaying in network search
  /// results, etc.
  auto GetDeviceName() -> std::string;

  /// Get a UUID for use with things like device-accounts. This function
  /// should not be used for other purposes, should not be modified, and
  /// eventually should go away after device accounts are phased out. Also,
  /// this value should never be shared beyond the local device.
  auto GetLegacyDeviceUUID() -> const std::string&;

  /// Return values which can be hashed to create a public device uuid.
  /// Ideally these values should come from an OS-provided guid. They should
  /// not include anything that is easily user-changeable. IMPORTANT: Only
  /// hashed/transformed versions of these values should ever be shared
  /// beyond the local device.
  virtual auto GetDeviceUUIDInputs() -> std::list<std::string>;

  /// Return whether there is an actual legacy-device-uuid value for
  /// this platform, and also return it if so.
  virtual auto GetRealLegacyDeviceUUID(std::string* uuid) -> bool;

  /// Are we running on a tv?
  virtual auto IsRunningOnTV() -> bool;

  /// Are we on a daydream-enabled Android device?
  virtual auto IsRunningOnDaydream() -> bool;

  /// Do we have touchscreen hardware?
  auto HasTouchScreen() -> bool;

  /// Are we running on a desktop setup in general?
  virtual auto IsRunningOnDesktop() -> bool;

  /// Are we running on fireTV hardware?
  virtual auto IsRunningOnFireTV() -> bool;

  // For enabling some special hardware optimizations for nvidia.
  auto is_tegra_k1() const -> bool { return is_tegra_k1_; }
  void set_is_tegra_k1(bool val) { is_tegra_k1_ = val; }

  /// Run system() command on OSs which support it. Throws exception
  /// elsewhere.
  static auto System(const char* cmd) -> int;

#pragma mark ANDROID -----------------------------------------------------------

  virtual auto GetAndroidExecArg() -> std::string;
  virtual void AndroidSetResString(const std::string& res);
  virtual void AndroidSynthesizeBackPress();
  virtual void AndroidQuitActivity();
  virtual void AndroidShowAppInvite(const std::string& title,
                                    const std::string& message,
                                    const std::string& code);
  virtual void AndroidShowWifiSettings();
  virtual auto AndroidGetExternalFilesDir() -> std::string;

#pragma mark PERMISSIONS -------------------------------------------------------

  /// Request the permission asynchronously. If the permission cannot be
  /// requested (due to having been denied, etc) then this may also present
  /// a message or pop-up instructing the user how to manually grant the
  /// permission (up to individual platforms to implement).
  virtual void RequestPermission(Permission p);

  /// Returns true if this permission has been granted (or if asking is not
  /// required for it).
  virtual auto HavePermission(Permission p) -> bool;

#pragma mark ANALYTICS ---------------------------------------------------------

  virtual void SetAnalyticsScreen(const std::string& screen);
  virtual void IncrementAnalyticsCount(const std::string& name, int increment);
  virtual void IncrementAnalyticsCountRaw(const std::string& name,
                                          int increment);
  virtual void IncrementAnalyticsCountRaw2(const std::string& name,
                                           int uses_increment, int increment);
  virtual void SubmitAnalyticsCounts();

#pragma mark APPLE -------------------------------------------------------------

  virtual auto NewAutoReleasePool() -> void*;
  virtual void DrainAutoReleasePool(void* pool);
  // FIXME: Can we consolidate these with the general music playback calls?
  virtual void MacMusicAppInit();
  virtual auto MacMusicAppGetVolume() -> int;
  virtual void MacMusicAppSetVolume(int volume);
  virtual void MacMusicAppGetLibrarySource();
  virtual void MacMusicAppStop();
  virtual auto MacMusicAppPlayPlaylist(const std::string& playlist) -> bool;
  virtual auto MacMusicAppGetPlaylists() -> std::list<std::string>;

#pragma mark TEXT RENDERING ----------------------------------------------------

  // Set bounds/width info for a bit of text. (will only be called in
  // BA_ENABLE_OS_FONT_RENDERING is set)
  virtual void GetTextBoundsAndWidth(const std::string& text, Rect* r,
                                     float* width);
  virtual void FreeTextTexture(void* tex);
  virtual auto CreateTextTexture(int width, int height,
                                 const std::vector<std::string>& strings,
                                 const std::vector<float>& positions,
                                 const std::vector<float>& widths, float scale)
      -> void*;
  virtual auto GetTextTextureData(void* tex) -> uint8_t*;

#pragma mark ACCOUNTS ----------------------------------------------------------

  virtual void SignInV1(const std::string& account_type);
  virtual void SignOutV1();

  virtual void GameCenterLogin();
  virtual void V1LoginDidChange();

  /// Returns the ID to use for the device account.
  auto GetDeviceV1AccountID() -> std::string;

  /// Return the prefix to use for device-account ids on this platform.
  virtual auto GetDeviceV1AccountUUIDPrefix() -> std::string;

#pragma mark MUSIC PLAYBACK ----------------------------------------------------

  // FIXME: currently these are wired up on Android; need to generalize
  //  to support mac/itunes or other music player types.
  virtual void MusicPlayerPlay(PyObject* target);
  virtual void MusicPlayerStop();
  virtual void MusicPlayerShutdown();
  virtual void MusicPlayerSetVolume(float volume);

#pragma mark ADS ---------------------------------------------------------------

  virtual void ShowAd(const std::string& purpose);

  // Return whether we have the ability to show *any* ads.
  virtual auto GetHasAds() -> bool;

  // Return whether we have the ability to show longer-form video ads (suitable
  // for rewards).
  virtual auto GetHasVideoAds() -> bool;

#pragma mark GAME SERVICES -----------------------------------------------------

  // Given a raw leaderboard score, convert it to what the game uses.
  // For instance, platforms may return times as milliseconds while we require
  // hundredths of a second, etc.
  virtual auto ConvertIncomingLeaderboardScore(
      const std::string& leaderboard_id, int score) -> int;

  virtual void SubmitScore(const std::string& game, const std::string& version,
                           int64_t score);
  virtual void ReportAchievement(const std::string& achievement);
  virtual auto HaveLeaderboard(const std::string& game,
                               const std::string& config) -> bool;

  virtual void ShowOnlineScoreUI(const std::string& show,
                                 const std::string& game,
                                 const std::string& game_version);
  virtual void ResetAchievements();

#pragma mark NETWORKING --------------------------------------------------------

  virtual void CloseSocket(int socket);
  virtual auto GetBroadcastAddrs() -> std::vector<uint32_t>;
  virtual auto SetSocketNonBlocking(int sd) -> bool;

#pragma mark ERRORS & DEBUGGING ------------------------------------------------

  /// Should return a subclass of PlatformStackTrace allocated via new.
  /// Platforms with no meaningful stack trace functionality can return nullptr.
  virtual auto GetStackTrace() -> PlatformStackTrace*;

  // Called during stress testing.
  virtual auto GetMemUsageInfo() -> std::string;

  /// Optionally override fatal error reporting. If true is returned, default
  /// fatal error reporting will not run.
  virtual auto ReportFatalError(const std::string& message,
                                bool in_top_level_exception_handler) -> bool;

  /// Optionally override fatal error handling. If true is returned, default
  /// fatal error handling will not run.
  virtual auto HandleFatalError(bool exit_cleanly,
                                bool in_top_level_exception_handler) -> bool;

  /// If this platform has the ability to show a blocking dialog on the main
  /// thread for fatal errors, return true here.
  virtual auto CanShowBlockingFatalErrorDialog() -> bool;

  /// Called on the main thread when a fatal error occurs.
  /// Will only be called if CanShowBlockingFatalErrorDialog() is true.
  virtual void BlockingFatalErrorDialog(const std::string& message);

  /// Use this instead of looking at errno (translates winsock errors to errno).
  virtual auto GetSocketError() -> int;

  /// Return a string for the current value of errno.
  virtual auto GetErrnoString() -> std::string;

  /// Return a description of errno (unix) or WSAGetLastError() (windows).
  virtual auto GetSocketErrorString() -> std::string;

  /// Set a key to be included in crash logs or other debug cases.
  /// This is expected to be lightweight as it may be called often.
  virtual void SetDebugKey(const std::string& key, const std::string& value);

  void DebugLog(const std::string& msg);

#pragma mark MISC --------------------------------------------------------------

  /// Return a time measurement in milliseconds since launch.
  /// It *should* be monotonic.
  /// For most purposes, AppTime values are preferable since their progression
  /// pauses during app suspension and they are 100% guaranteed to not go
  /// backwards.
  auto GetTicks() const -> millisecs_t;

  /// Return a raw current milliseconds value. It *should* be monotonic.
  /// It is relative to an undefined start point; only use it for time
  /// differences. Generally the AppTime values are preferable since their
  /// progression pauses during app suspension and they are 100% guaranteed
  /// to not go backwards.
  static auto GetCurrentMillisecs() -> millisecs_t;

  /// Return a raw current microseconds value. It *should* be monotonic.
  /// It is relative to an undefined start point; only use it for time
  /// differences. Generally the AppTime values are preferable since their
  /// progression pauses during app suspension and they are 100% guaranteed
  /// to not go backwards.
  static auto GetCurrentMicrosecs() -> microsecs_t;

  /// Return a raw current seconds integer value. It *should* be monotonic.
  /// It is relative to an undefined start point; only use it for time
  /// differences. Generally the AppTime values are preferable since their
  /// progression pauses during app suspension and they are 100% guaranteed
  /// to not go backwards.
  static auto GetCurrentWholeSeconds() -> int64_t;

  static void SleepMillisecs(millisecs_t ms);

  /// Pop up a text edit dialog.
  virtual void EditText(const std::string& title, const std::string& value,
                        int max_chars);

  /// Given a C++ symbol, attempt to return a pretty one.
  virtual auto DemangleCXXSymbol(const std::string& s) -> std::string;

  /// Called each time through the main event loop;
  /// for custom pumping/handling.
  virtual void RunEvents();

  /// Is the OS currently playing music? (so we can avoid doing so).
  virtual auto IsOSPlayingMusic() -> bool;

  /// Pass platform-specific misc-read-vals along to the OS (as a json string).
  virtual void SetPlatformMiscReadVals(const std::string& vals);

  /// Show/hide the hardware cursor.
  virtual void SetHardwareCursorVisible(bool visible);

  /// Quit the app (can be immediate or via posting some high level event).
  virtual void QuitApp();

  /// Open a file using the system default method (in another app, etc.)
  virtual void OpenFileExternally(const std::string& path);

  /// Open a directory using the system default method (Finder, etc.)
  virtual void OpenDirExternally(const std::string& path);

  /// Set the name of the current thread (for debugging).
  virtual void SetCurrentThreadName(const std::string& name);

  // If display-resolution can be directly set on this platform,
  // return true and set the native full res here.  Otherwise return false;
  virtual auto GetDisplayResolution(int* x, int* y) -> bool;

  auto using_custom_app_python_dir() const {
    return using_custom_app_python_dir_;
  }

  /// Are we being run from a terminal? (should we show prompts, etc?).
  auto is_stdin_a_terminal() const { return is_stdin_a_terminal_; }

  void SetBaEnvVals(const PythonRef& ref);

  /// Return true if baenv values have been locked in: python paths, log
  /// handling, etc. Early-running code may wish to explicitly avoid making log
  /// calls until this condition is met to ensure predictable behavior.
  auto HaveBaEnvVals() const { return have_ba_env_vals_; }

 protected:
  /// Are we being run from a terminal? (should we show prompts, etc?).
  virtual auto GetIsStdinATerminal() -> bool;

  /// Called once per platform to determine touchscreen presence.
  virtual auto DoHasTouchScreen() -> bool;

  /// Platforms should override this to provide device name.
  virtual auto DoGetDeviceName() -> std::string;

  /// Attempt to actually create a directory.
  /// Should *not* raise Exceptions if it already exists or if quiet is true.
  virtual void DoMakeDir(const std::string& dir, bool quiet);

  /// Attempt to actually get an abs path. This will only be called if
  /// the path is valid and exists.
  virtual auto DoAbsPath(const std::string& path, std::string* outpath) -> bool;

  /// Calc the user scripts dir path for this platform.
  /// This will be called once and the path cached.
  virtual auto DoGetUserPythonDirectoryMonolithicDefault()
      -> std::optional<std::string>;

  /// Return the default config directory for this platform.
  /// This will be used as the config dir if not overridden via command
  /// line options, etc.
  virtual auto DoGetConfigDirectoryMonolithicDefault()
      -> std::optional<std::string>;

  /// Return the default data directory for this platform.
  /// This will be used as the data dir if not overridden by core-config, etc.
  /// This is the one monolithic-default value that is not optional.
  virtual auto DoGetDataDirectoryMonolithicDefault() -> std::string;

  /// Return the default Volatile data dir for this platform.
  /// This will be used as the volatile-data-dir if not overridden via command
  /// line options/etc.
  virtual auto GetDefaultVolatileDataDirectory() -> std::string;

  /// Generate a random UUID string.
  virtual auto GenerateUUID() -> std::string;

  virtual auto DoClipboardIsSupported() -> bool;
  virtual auto DoClipboardHasText() -> bool;
  virtual void DoClipboardSetText(const std::string& text);
  virtual auto DoClipboardGetText() -> std::string;

  /// Print a log message to be included in crash logs or other debug
  /// mechanisms (example: Crashlytics). V1-cloud-log messages get forwarded
  /// to here as well. It can be useful to call this directly to report extra
  /// details that may help in debugging, as these calls are not considered
  /// 'noteworthy' or presented to the user as standard Log() calls are.
  virtual void HandleDebugLog(const std::string& msg);

 protected:
  CorePlatform();
  virtual ~CorePlatform();

 private:
  bool is_stdin_a_terminal_{};
  bool using_custom_app_python_dir_{};  // FIXME not wired up currently.
  bool have_has_touchscreen_value_{};
  bool have_touchscreen_{};
  bool is_tegra_k1_{};
  bool have_clipboard_is_supported_{};
  bool clipboard_is_supported_{};
  bool made_volatile_data_dir_{};
  bool have_device_uuid_{};
  bool ran_base_post_init_{};
  bool have_ba_env_vals_{};
  millisecs_t start_time_millisecs_{};
  std::string device_name_;
  std::string legacy_device_uuid_;
  std::string volatile_data_dir_;
  std::string replays_dir_;
  std::string ba_env_config_dir_;
  std::string ba_env_data_dir_;
  std::optional<std::string> ba_env_app_python_dir_;
  std::optional<std::string> ba_env_user_python_dir_;
  std::optional<std::string> ba_env_site_python_dir_;
};

}  // namespace ballistica::core

#endif  // BALLISTICA_CORE_PLATFORM_CORE_PLATFORM_H_
