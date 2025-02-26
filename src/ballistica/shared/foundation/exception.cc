// Released under the MIT License. See LICENSE for details.

#include "ballistica/shared/foundation/exception.h"

#include "ballistica/core/core.h"
#include "ballistica/core/platform/core_platform.h"

namespace ballistica {

auto GetShortExceptionDescription(const std::exception& exc) -> const char* {
  if (auto b_exc = dynamic_cast<const Exception*>(&exc)) {
    return b_exc->message();
  }
  return exc.what();
}

Exception::Exception(std::string message_in, PyExcType python_type)
    : message_(std::move(message_in)), python_type_(python_type) {
  thread_name_ = CurrentThreadName();

  // If core has been inited, attempt to capture a stack-trace here we
  // can print out later if desired.
  if (core::g_core) {
    stack_trace_ = core::g_core->platform->GetStackTrace();
  }
}
Exception::Exception(PyExcType python_type) : python_type_(python_type) {
  thread_name_ = CurrentThreadName();

  // If core has been inited, attempt to capture a stack-trace here we
  // can print out later if desired.
  if (core::g_core) {
    stack_trace_ = core::g_core->platform->GetStackTrace();
  }
}

// Copy constructor.
Exception::Exception(const Exception& other) noexcept {
  try {
    thread_name_ = other.thread_name_;
    message_ = other.message_;
    full_description_ = other.full_description_;
    python_type_ = other.python_type_;
    if (other.stack_trace_) {
      stack_trace_ = other.stack_trace_->copy();
    }
  } catch (const std::exception&) {
    // Hmmm not sure what we should do if this happens;
    // for now we'll just wind up with some parts of our
    // shiny new exception copy potentially missing.
    // Better than crashing I suppose.
  }
}

Exception::~Exception() { delete stack_trace_; }

auto Exception::what() const noexcept -> const char* {
  // Return a nice pretty stack trace and other relevant info.
  try {
    // This call is const so we're technically not supposed to modify ourself,
    // but a one-time flattening of our description into an internal buffer
    // should be fine.
    if (full_description_.empty()) {
      if (stack_trace_ != nullptr) {
        const_cast<Exception*>(this)->full_description_ =
            message_ + "\nThrown from " + thread_name_ + " thread:\n"
            + stack_trace_->GetDescription();
      } else {
        const_cast<Exception*>(this)->full_description_ = message_;
      }
    }
    return full_description_.c_str();
  } catch (const std::exception&) {
    // Welp; we tried.
    return "Error generating ballistica::Exception::what(); oh dear.";
  }
}

}  // namespace ballistica
