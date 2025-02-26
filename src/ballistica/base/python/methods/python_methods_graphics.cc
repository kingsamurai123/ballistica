// Released under the MIT License. See LICENSE for details.

#include "ballistica/base/python/methods/python_methods_graphics.h"

#include "ballistica/base/assets/assets.h"
#include "ballistica/base/graphics/graphics.h"
#include "ballistica/base/graphics/support/camera.h"
#include "ballistica/base/graphics/text/text_graphics.h"
#include "ballistica/base/logic/logic.h"
#include "ballistica/base/python/base_python.h"
#include "ballistica/base/python/support/python_context_call_runnable.h"
#include "ballistica/core/core.h"
#include "ballistica/core/platform/core_platform.h"
#include "ballistica/shared/generic/utils.h"
#include "ballistica/shared/python/python.h"
#include "ballistica/shared/python/python_sys.h"

namespace ballistica::base {

// Ignore signed bitwise stuff; python macros do it quite a bit.
#pragma clang diagnostic push
#pragma ide diagnostic ignored "hicpp-signed-bitwise"

// ---------------------------- screenmessage ----------------------------------

static auto PyScreenMessage(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  PyObject* color_obj = Py_None;
  PyObject* message_obj;
  int log{};
  static const char* kwlist[] = {"message", "color", "log", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|Op",
                                   const_cast<char**>(kwlist), &message_obj,
                                   &color_obj, &log)) {
    return nullptr;
  }
  std::string message_str = g_base->python->GetPyLString(message_obj);
  Vector3f color{1, 1, 1};
  if (color_obj != Py_None) {
    color = BasePython::GetPyVector3f(color_obj);
  }
  if (log) {
    Log(LogLevel::kInfo, message_str);
  }

  // This version simply displays it locally.
  g_base->graphics->AddScreenMessage(message_str, color);

  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PyScreenMessageDef = {
    "screenmessage",               // name
    (PyCFunction)PyScreenMessage,  // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "screenmessage(message: str | babase.Lstr,\n"
    "  color: Sequence[float] | None = None,\n"
    "  log: bool = False)\n"
    " -> None\n"
    "\n"
    "Print a message to the local client's screen, in a given color.\n"
    "\n"
    "Category: **General Utility Functions**\n"
    "\n"
    "Note that this version of the function is purely for local display.\n"
    "To broadcast screen messages in network play, see the versions of\n"
    "this call provided by the scene-version packages.",
};

// -------------------------- get_camera_position ------------------------------

static auto PyGetCameraPosition(PyObject* self, PyObject* args,
                                PyObject* keywds) -> PyObject* {
  BA_PYTHON_TRY;
  float x = 0.0f;
  float y = 0.0f;
  float z = 0.0f;
  Camera* cam = g_base->graphics->camera();
  cam->get_position(&x, &y, &z);
  return Py_BuildValue("(fff)", x, y, z);
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetCameraPositionDef = {
    "get_camera_position",             // name
    (PyCFunction)PyGetCameraPosition,  // method
    METH_VARARGS | METH_KEYWORDS,      // flags

    "get_camera_position() -> tuple[float, ...]\n"
    "\n"
    "(internal)\n"
    "\n"
    "WARNING: these camera controls will not apply to network clients\n"
    "and may behave unpredictably in other ways. Use them only for\n"
    "tinkering.",
};

// --------------------------- get_camera_target -------------------------------

static auto PyGetCameraTarget(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  float x = 0.0f;
  float y = 0.0f;
  float z = 0.0f;
  Camera* cam = g_base->graphics->camera();
  cam->target_smoothed(&x, &y, &z);
  return Py_BuildValue("(fff)", x, y, z);
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetCameraTargetDef = {
    "get_camera_target",             // name
    (PyCFunction)PyGetCameraTarget,  // method
    METH_VARARGS | METH_KEYWORDS,    // flags

    "get_camera_target() -> tuple[float, ...]\n"
    "\n"
    "(internal)\n"
    "\n"
    "WARNING: these camera controls will not apply to network clients\n"
    "and may behave unpredictably in other ways. Use them only for\n"
    "tinkering.",
};

// --------------------------- set_camera_position -----------------------------

static auto PySetCameraPosition(PyObject* self, PyObject* args,
                                PyObject* keywds) -> PyObject* {
  BA_PYTHON_TRY;
  float x = 0.0f;
  float y = 0.0f;
  float z = 0.0f;
  static const char* kwlist[] = {"x", "y", "z", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "fff",
                                   const_cast<char**>(kwlist), &x, &y, &z)) {
    return nullptr;
  }
  assert(g_base->logic);
  g_base->graphics->camera()->SetPosition(x, y, z);
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PySetCameraPositionDef = {
    "set_camera_position",             // name
    (PyCFunction)PySetCameraPosition,  // method
    METH_VARARGS | METH_KEYWORDS,      // flags

    "set_camera_position(x: float, y: float, z: float) -> None\n"
    "\n"
    "(internal)\n"
    "\n"
    "WARNING: these camera controls will not apply to network clients\n"
    "and may behave unpredictably in other ways. Use them only for\n"
    "tinkering.",
};

// ---------------------------- set_camera_target ------------------------------

static auto PySetCameraTarget(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  float x = 0.0f;
  float y = 0.0f;
  float z = 0.0f;
  static const char* kwlist[] = {"x", "y", "z", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "fff",
                                   const_cast<char**>(kwlist), &x, &y, &z)) {
    return nullptr;
  }
  assert(g_base->logic);
  g_base->graphics->camera()->SetTarget(x, y, z);
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PySetCameraTargetDef = {
    "set_camera_target",             // name
    (PyCFunction)PySetCameraTarget,  // method
    METH_VARARGS | METH_KEYWORDS,    // flags

    "set_camera_target(x: float, y: float, z: float) -> None\n"
    "\n"
    "(internal)\n"
    "\n"
    "WARNING: these camera controls will not apply to network clients\n"
    "and may behave unpredictably in other ways. Use them only for\n"
    "tinkering.",
};

// ---------------------------- set_camera_manual ------------------------------

static auto PySetCameraManual(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  bool value = false;
  static const char* kwlist[] = {"value", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "b",
                                   const_cast<char**>(kwlist), &value)) {
    return nullptr;
  }
  assert(g_base->logic);
  g_base->graphics->camera()->SetManual(value);
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PySetCameraManualDef = {
    "set_camera_manual",             // name
    (PyCFunction)PySetCameraManual,  // method
    METH_VARARGS | METH_KEYWORDS,    // flags

    "set_camera_manual(value: bool) -> None\n"
    "\n"
    "(internal)\n"
    "\n"
    "WARNING: these camera controls will not apply to network clients\n"
    "and may behave unpredictably in other ways. Use them only for\n"
    "tinkering.",
};

// -------------------------------- charstr ------------------------------------

static auto PyCharStr(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  PyObject* name_obj;
  static const char* kwlist[] = {"name", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O",
                                   const_cast<char**>(kwlist), &name_obj)) {
    return nullptr;
  }
  assert(g_base->logic);
  auto id(BasePython::GetPyEnum_SpecialChar(name_obj));
  assert(Utils::IsValidUTF8(g_base->assets->CharStr(id)));
  return PyUnicode_FromString(g_base->assets->CharStr(id).c_str());
  BA_PYTHON_CATCH;
}

static PyMethodDef PyCharStrDef = {
    "charstr",                     // name
    (PyCFunction)PyCharStr,        // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "charstr(char_id: babase.SpecialChar) -> str\n"
    "\n"
    "Get a unicode string representing a special character.\n"
    "\n"
    "Category: **General Utility Functions**\n"
    "\n"
    "Note that these utilize the private-use block of unicode characters\n"
    "(U+E000-U+F8FF) and are specific to the game; exporting or rendering\n"
    "them elsewhere will be meaningless.\n"
    "\n"
    "See babase.SpecialChar for the list of available characters.",
};

// ------------------------------- safecolor -----------------------------------

static auto PySafeColor(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  PyObject* color_obj;
  float red, green, blue;
  float target_intensity = 0.6f;
  static const char* kwlist[] = {"color", "target_intensity", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|f",
                                   const_cast<char**>(kwlist), &color_obj,
                                   &target_intensity)) {
    return nullptr;
  }
  if (!PySequence_Check(color_obj)) {
    throw Exception("Expected a sequence.", PyExcType::kType);
  }
  int len = static_cast<int>(PySequence_Length(color_obj));
  if (len != 3 && len != 4) {
    throw Exception("Expected a 3 or 4 length sequence; got "
                        + Python::ObjToString(color_obj) + ".",
                    PyExcType::kValue);
  }
  PythonRef red_obj(PySequence_GetItem(color_obj, 0), PythonRef::kSteal);
  PythonRef green_obj(PySequence_GetItem(color_obj, 1), PythonRef::kSteal);
  PythonRef blue_obj(PySequence_GetItem(color_obj, 2), PythonRef::kSteal);
  red = Python::GetPyFloat(red_obj.Get());
  green = Python::GetPyFloat(green_obj.Get());
  blue = Python::GetPyFloat(blue_obj.Get());
  Graphics::GetSafeColor(&red, &green, &blue, target_intensity);
  if (len == 3) {
    return Py_BuildValue("(fff)", red, green, blue);
  } else {
    PythonRef alpha_obj(PySequence_GetItem(color_obj, 3), PythonRef::kSteal);
    float alpha = Python::GetPyFloat(alpha_obj.Get());
    return Py_BuildValue("(ffff)", red, green, blue, alpha);
  }
  BA_PYTHON_CATCH;
}

static PyMethodDef PySafeColorDef = {
    "safecolor",                   // name
    (PyCFunction)PySafeColor,      // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "safecolor(color: Sequence[float], target_intensity: float = 0.6)\n"
    "  -> tuple[float, ...]\n"
    "\n"
    "Given a color tuple, return a color safe to display as text.\n"
    "\n"
    "Category: **General Utility Functions**\n"
    "\n"
    "Accepts tuples of length 3 or 4. This will slightly brighten very\n"
    "dark colors, etc.",
};

// ------------------------ get_max_graphics_quality ---------------------------

static auto PyGetMaxGraphicsQuality(PyObject* self, PyObject* args)
    -> PyObject* {
  BA_PYTHON_TRY;
  if (g_base->graphics
      && g_base->graphics->has_supports_high_quality_graphics_value()
      && g_base->graphics->supports_high_quality_graphics()) {
    return Py_BuildValue("s", "High");
  } else {
    return Py_BuildValue("s", "Medium");
  }
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetMaxGraphicsQualityDef = {
    "get_max_graphics_quality",  // name
    PyGetMaxGraphicsQuality,     // method
    METH_VARARGS,                // flags

    "get_max_graphics_quality() -> str\n"
    "\n"
    "(internal)\n"
    "\n"
    "Return the max graphics-quality supported on the current hardware.",
};

// ------------------------------ evaluate_lstr --------------------------------

static auto PyEvaluateLstr(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  const char* value;
  static const char* kwlist[] = {"value", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "s",
                                   const_cast<char**>(kwlist), &value)) {
    return nullptr;
  }
  return PyUnicode_FromString(
      g_base->assets->CompileResourceString(value, "evaluate_lstr").c_str());
  BA_PYTHON_CATCH;
}

static PyMethodDef PyEvaluateLstrDef = {
    "evaluate_lstr",               // name
    (PyCFunction)PyEvaluateLstr,   // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "evaluate_lstr(value: str) -> str\n"
    "\n"
    "(internal)",
};

// --------------------------- get_string_height -------------------------------

static auto PyGetStringHeight(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  std::string s;
  int suppress_warning = 0;
  PyObject* s_obj;
  static const char* kwlist[] = {"string", "suppress_warning", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|i",
                                   const_cast<char**>(kwlist), &s_obj,
                                   &suppress_warning)) {
    return nullptr;
  }
  if (!suppress_warning) {
    BA_LOG_PYTHON_TRACE(
        "get_string_height() use is heavily discouraged as it reduces "
        "language-independence; pass suppress_warning=True if you must use "
        "it.");
  }
  s = g_base->python->GetPyLString(s_obj);
#if BA_DEBUG_BUILD
  if (g_base->assets->CompileResourceString(s, "get_string_height test") != s) {
    BA_LOG_PYTHON_TRACE(
        "resource-string passed to get_string_height; this should be avoided");
  }
#endif
  assert(g_base->graphics);
  return Py_BuildValue("f", g_base->text_graphics->GetStringHeight(s));
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetStringHeightDef = {
    "get_string_height",             // name
    (PyCFunction)PyGetStringHeight,  // method
    METH_VARARGS | METH_KEYWORDS,    // flags

    "get_string_height(string: str, suppress_warning: bool = False) -> "
    "float\n"
    "\n"
    "(internal)\n"
    "\n"
    "Given a string, returns its height using the standard small app\n"
    "font.",
};

// ---------------------------- get_string_width -------------------------------

static auto PyGetStringWidth(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  std::string s;
  PyObject* s_obj;
  int suppress_warning = 0;
  static const char* kwlist[] = {"string", "suppress_warning", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O|i",
                                   const_cast<char**>(kwlist), &s_obj,
                                   &suppress_warning)) {
    return nullptr;
  }
  if (!suppress_warning) {
    BA_LOG_PYTHON_TRACE(
        "get_string_width() use is heavily discouraged as it reduces "
        "language-independence; pass suppress_warning=True if you must use "
        "it.");
  }
  s = g_base->python->GetPyLString(s_obj);
#if BA_DEBUG_BUILD
  if (g_base->assets->CompileResourceString(s, "get_string_width debug test")
      != s) {
    BA_LOG_PYTHON_TRACE(
        "resource-string passed to get_string_width; this should be avoided");
  }
#endif
  assert(g_base->graphics);
  return Py_BuildValue("f", g_base->text_graphics->GetStringWidth(s));
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetStringWidthDef = {
    "get_string_width",             // name
    (PyCFunction)PyGetStringWidth,  // method
    METH_VARARGS | METH_KEYWORDS,   // flags

    "get_string_width(string: str, suppress_warning: bool = False) -> "
    "float\n"
    "\n"
    "(internal)\n"
    "\n"
    "Given a string, returns its width using the standard small app\n"
    "font.",
};

// ------------------------------ have_chars -----------------------------------

static auto PyHaveChars(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  std::string text;
  PyObject* text_obj;
  static const char* kwlist[] = {"text", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O",
                                   const_cast<char**>(kwlist), &text_obj)) {
    return nullptr;
  }
  text = g_base->python->GetPyLString(text_obj);
  if (TextGraphics::HaveChars(text)) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
  BA_PYTHON_CATCH;
}

static PyMethodDef PyHaveCharsDef = {
    "have_chars",                  // name
    (PyCFunction)PyHaveChars,      // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "have_chars(text: str) -> bool\n"
    "\n"
    "(internal)",
};

// ----------------------------- fade_screen -----------------------------------

static auto PyFadeScreen(PyObject* self, PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;

  // This can only be called in the UI context.
  int fade{0};
  float time{0.25f};
  PyObject* endcall = nullptr;
  static const char* kwlist[] = {"to", "time", "endcall", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "|pfO",
                                   const_cast<char**>(kwlist), &fade, &time,
                                   &endcall)) {
    return nullptr;
  }
  g_base->graphics->FadeScreen(static_cast<bool>(fade),
                               static_cast<int>(1000.0f * time), endcall);
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PyFadeScreenDef = {
    "fade_screen",                 // name
    (PyCFunction)PyFadeScreen,     // method
    METH_VARARGS | METH_KEYWORDS,  // flags

    "fade_screen(to: int = 0, time: float = 0.25,\n"
    "  endcall: Callable[[], None] | None = None) -> None\n"
    "\n"
    "(internal)\n"
    "\n"
    "Fade the local game screen in our out from black over a duration of\n"
    "time. if \"to\" is 0, the screen will fade out to black.  Otherwise "
    "it\n"
    "will fade in from black. If endcall is provided, it will be run after "
    "a\n"
    "completely faded frame is drawn.",
};

// ---------------------- add_clean_frame_callback -----------------------------

static auto PyAddCleanFrameCallback(PyObject* self, PyObject* args,
                                    PyObject* keywds) -> PyObject* {
  BA_PYTHON_TRY;
  PyObject* call_obj;
  static const char* kwlist[] = {"call", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O",
                                   const_cast<char**>(kwlist), &call_obj)) {
    return nullptr;
  }
  g_base->graphics->AddCleanFrameCommand(
      Object::New<PythonContextCall>(call_obj));
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

static PyMethodDef PyAddCleanFrameCallbackDef = {
    "add_clean_frame_callback",            // name
    (PyCFunction)PyAddCleanFrameCallback,  // method
    METH_VARARGS | METH_KEYWORDS,          // flags

    "add_clean_frame_callback(call: Callable) -> None\n"
    "\n"
    "(internal)\n"
    "\n"
    "Provide an object to be called once the next non-progress-bar-frame "
    "has\n"
    "been rendered. Useful for queueing things to load in the background\n"
    "without elongating any current progress-bar-load.",
};

// --------------------------- has_gamma_control -------------------------------

static auto PyHasGammaControl(PyObject* self, PyObject* args) -> PyObject* {
  BA_PYTHON_TRY;
  // phasing this out; our old non-sdl2 mac has gamma controls but nothing newer
  // does...
#if BA_OSTYPE_MACOS && !BA_SDL2_BUILD
  Py_RETURN_TRUE;
#else
  Py_RETURN_FALSE;
#endif
  BA_PYTHON_CATCH;
}

static PyMethodDef PyHasGammaControlDef = {
    "has_gamma_control",  // name
    PyHasGammaControl,    // method
    METH_VARARGS,         // flags

    "has_gamma_control() -> bool\n"
    "\n"
    "(internal)\n"
    "\n"
    "Returns whether the system can adjust overall screen gamma)",
};

// ------------------------- get_display_resolution ----------------------------

static auto PyGetDisplayResolution(PyObject* self, PyObject* args)
    -> PyObject* {
  BA_PYTHON_TRY;
  int x = 0;
  int y = 0;
  bool have_res = g_core->platform->GetDisplayResolution(&x, &y);
  if (have_res) {
    return Py_BuildValue("(ii)", x, y);
  } else {
    Py_RETURN_NONE;
  }
  BA_PYTHON_CATCH;
}

static PyMethodDef PyGetDisplayResolutionDef = {
    "get_display_resolution",  // name
    PyGetDisplayResolution,    // method
    METH_VARARGS,              // flags

    "get_display_resolution() -> tuple[int, int] | None\n"
    "\n"
    "(internal)\n"
    "\n"
    "Return the currently selected display resolution for fullscreen\n"
    "display. Returns None if resolutions cannot be directly set.",
};

// -----------------------------------------------------------------------------

auto PythonMethodsGraphics::GetMethods() -> std::vector<PyMethodDef> {
  return {
      PyGetDisplayResolutionDef,
      PyGetCameraPositionDef,
      PyGetCameraTargetDef,
      PySetCameraPositionDef,
      PySetCameraTargetDef,
      PySetCameraManualDef,
      PyHasGammaControlDef,
      PyAddCleanFrameCallbackDef,
      PyHaveCharsDef,
      PyFadeScreenDef,
      PyScreenMessageDef,
      PyGetStringWidthDef,
      PyGetStringHeightDef,
      PyEvaluateLstrDef,
      PyGetMaxGraphicsQualityDef,
      PySafeColorDef,
      PyCharStrDef,
  };
}

#pragma clang diagnostic pop

}  // namespace ballistica::base
