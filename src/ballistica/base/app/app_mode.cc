// Released under the MIT License. See LICENSE for details.

#include "ballistica/base/app/app_mode.h"

#include "ballistica/base/input/device/input_device_delegate.h"
#include "ballistica/base/support/context.h"

namespace ballistica::base {

AppMode::AppMode() = default;

void AppMode::OnActivate() {}
void AppMode::OnDeactivate() {}

void AppMode::OnAppStart() {}
void AppMode::OnAppPause() {}
void AppMode::OnAppResume() {}
void AppMode::OnAppShutdown() {}

auto AppMode::CreateInputDeviceDelegate(InputDevice* device)
    -> InputDeviceDelegate* {
  return Object::NewDeferred<InputDeviceDelegate>();
}

auto AppMode::HandleJSONPing(const std::string& data_str) -> std::string {
  return "";
}

void AppMode::HandleIncomingUDPPacket(const std::vector<uint8_t>& data_in,
                                      const SockAddr& addr) {}

void AppMode::HandleGameQuery(const char* buffer, size_t size,
                              sockaddr_storage* from) {}

auto AppMode::DoesWorldFillScreen() -> bool { return false; }

void AppMode::GraphicsQualityChanged(GraphicsQuality quality) {}

void AppMode::DrawWorld(FrameDef* frame_def) {}

void AppMode::ChangeGameSpeed(int offs) {}

void AppMode::StepDisplayTime() {}

auto AppMode::GetPartySize() const -> int { return 0; }

auto AppMode::GetNetworkDebugString() -> std::string { return ""; }

auto AppMode::GetPingString() -> std::string { return ""; }

auto AppMode::HasConnectionToHost() const -> bool { return false; }

auto AppMode::HasConnectionToClients() const -> bool { return false; }

void AppMode::ApplyAppConfig() {}

auto AppMode::GetForegroundContext() -> ContextRef { return {}; }

void AppMode::OnScreenSizeChange() {}

void AppMode::LanguageChanged() {}

auto AppMode::LastClientJoinTime() const -> millisecs_t { return -1; }

auto AppMode::InMainMenu() const -> bool { return false; }

}  // namespace ballistica::base
