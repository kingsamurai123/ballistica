// Released under the MIT License. See LICENSE for details.

#include "ballistica/scene_v1/support/session.h"

#include "ballistica/scene_v1/support/scene_v1_app_mode.h"

namespace ballistica::scene_v1 {

Session::Session() {
  g_core->session_count++;

  auto* appmode = SceneV1AppMode::GetActiveOrThrow();

  // New sessions immediately become foreground.
  appmode->SetForegroundSession(this);
}

Session::~Session() { g_core->session_count--; }

void Session::Update(int time_advance_millisecs, double time_advance) {}

auto Session::GetForegroundContext() -> base::ContextRef { return {}; }

void Session::Draw(base::FrameDef*) {}

void Session::ScreenSizeChanged() {}

void Session::LanguageChanged() {}

void Session::GraphicsQualityChanged(base::GraphicsQuality q) {}

void Session::DebugSpeedMultChanged() {}

void Session::DumpFullState(SessionStream* out) {
  Log(LogLevel::kError,
      "Session::DumpFullState() being called; shouldn't happen.");
}

}  // namespace ballistica::scene_v1
