// Released under the MIT License. See LICENSE for details.

#include "ballistica/ui_v1/python/class/python_class_widget.h"

#include "ballistica/base/graphics/graphics.h"
#include "ballistica/base/logic/logic.h"
#include "ballistica/shared/foundation/event_loop.h"
#include "ballistica/shared/generic/utils.h"
#include "ballistica/shared/python/python.h"
#include "ballistica/ui_v1/widget/container_widget.h"

namespace ballistica::ui_v1 {

auto PythonClassWidget::nb_bool(PythonClassWidget* self) -> int {
  return self->widget_->Exists();
}

PyNumberMethods PythonClassWidget::as_number_;

auto PythonClassWidget::type_name() -> const char* { return "Widget"; }

void PythonClassWidget::SetupType(PyTypeObject* cls) {
  PythonClass::SetupType(cls);
  // Fully qualified type path we will be exposed as:
  cls->tp_name = "bauiv1.Widget";
  cls->tp_basicsize = sizeof(PythonClassWidget);
  cls->tp_doc =
      "Internal type for low level UI elements; buttons, windows, etc.\n"
      "\n"
      "Category: **User Interface Classes**\n"
      "\n"
      "This class represents a weak reference to a widget object\n"
      "in the internal C++ layer. Currently, functions such as\n"
      "babase.buttonwidget() must be used to instantiate or edit these.";
  cls->tp_new = tp_new;
  cls->tp_dealloc = (destructor)tp_dealloc;
  cls->tp_repr = (reprfunc)tp_repr;
  cls->tp_methods = tp_methods;

  // we provide number methods only for bool functionality
  memset(&as_number_, 0, sizeof(as_number_));
  as_number_.nb_bool = (inquiry)nb_bool;
  cls->tp_as_number = &as_number_;
}

auto PythonClassWidget::Create(Widget* widget) -> PyObject* {
  // Make sure we only have one python ref per widget.
  if (widget) {
    assert(!widget->has_py_ref());
  }

  assert(TypeIsSetUp(&type_obj));
  auto* py_widget = reinterpret_cast<PythonClassWidget*>(
      PyObject_CallObject(reinterpret_cast<PyObject*>(&type_obj), nullptr));
  if (!py_widget) throw Exception("babase.Widget creation failed");

  *py_widget->widget_ = widget;

  auto* out = reinterpret_cast<PyObject*>(py_widget);
  return out;
}

auto PythonClassWidget::GetWidget() const -> Widget* {
  Widget* w = widget_->Get();
  if (!w) throw Exception("Invalid widget");
  return w;
}

auto PythonClassWidget::tp_repr(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  return Py_BuildValue("s", (std::string("<bauiv1 '")
                             + (w ? w->GetWidgetTypeName() : "<invalid>")
                             + "' widget " + Utils::PtrToString(w) + ">")
                                .c_str());
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::tp_new(PyTypeObject* type, PyObject* args,
                               PyObject* keywds) -> PyObject* {
  auto* self = reinterpret_cast<PythonClassWidget*>(type->tp_alloc(type, 0));
  if (!self) {
    return nullptr;
  }
  BA_PYTHON_TRY;
  if (!g_base->InLogicThread()) {
    throw Exception(
        "ERROR: " + std::string(type_obj.tp_name)
        + " objects must only be created in the logic thread (current is ("
        + CurrentThreadName() + ").");
  }
  self->widget_ = new Object::WeakRef<Widget>();
  return reinterpret_cast<PyObject*>(self);
  BA_PYTHON_NEW_CATCH;
}

void PythonClassWidget::tp_dealloc(PythonClassWidget* self) {
  BA_PYTHON_TRY;
  // these have to be destructed in the logic thread - send them along to it if
  // need be
  if (!g_base->InLogicThread()) {
    Object::WeakRef<Widget>* w = self->widget_;
    g_base->logic->event_loop()->PushCall([w] { delete w; });
  } else {
    delete self->widget_;
  }
  BA_PYTHON_DEALLOC_CATCH;
  Py_TYPE(self)->tp_free(reinterpret_cast<PyObject*>(self));
}

auto PythonClassWidget::Exists(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (w) {
    Py_RETURN_TRUE;
  } else {
    Py_RETURN_FALSE;
  }
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::GetWidgetType(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  return PyUnicode_FromString(w->GetWidgetTypeName().c_str());
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::Activate(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  w->Activate();
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::GetChildren(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  PyObject* py_list = PyList_New(0);
  auto* cw = dynamic_cast<ContainerWidget*>(w);

  // Clion seems to think dynamic_casting a Widget* to a ContainerWidget*
  // will always succeed. Go home Clion; you're drunk.
#pragma clang diagnostic push
#pragma ide diagnostic ignored "ConstantConditionsOC"
  if (cw) {
#pragma clang diagnostic pop
    for (auto&& i : cw->widgets()) {
      assert(i.Exists());
      PyList_Append(py_list, i->BorrowPyRef());
    }
  }
  return py_list;
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::GetSelectedChild(PythonClassWidget* self) -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  auto* cw = dynamic_cast<ContainerWidget*>(w);

  // Clion seems to think dynamic_casting a Widget* to a ContainerWidget*
  // will always succeed. Go home Clion; you're drunk.
#pragma clang diagnostic push
#pragma ide diagnostic ignored "ConstantConditionsOC"
  if (cw) {
#pragma clang diagnostic pop
    Widget* selected_widget = cw->selected_widget();
    if (selected_widget) return selected_widget->NewPyRef();
  }
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::GetScreenSpaceCenter(PythonClassWidget* self)
    -> PyObject* {
  BA_PYTHON_TRY;
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  float x, y;
  w->GetCenter(&x, &y);

  // this gives us coords in the widget's parent's space; translate from that
  // to screen space
  if (ContainerWidget* parent = w->parent_widget()) {
    parent->WidgetPointToScreen(&x, &y);
  }
  // ..but we actually want to return points relative to the center of the
  // screen (so they're useful as stack-offset values)
  float screen_width = g_base->graphics->screen_virtual_width();
  float screen_height = g_base->graphics->screen_virtual_height();
  x -= screen_width * 0.5f;
  y -= screen_height * 0.5f;
  return Py_BuildValue("(ff)", x, y);
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::Delete(PythonClassWidget* self, PyObject* args,
                               PyObject* keywds) -> PyObject* {
  BA_PYTHON_TRY;
  int ignore_missing = true;
  static const char* kwlist[] = {"ignore_missing", nullptr};
  if (!PyArg_ParseTupleAndKeywords(
          args, keywds, "|i", const_cast<char**>(kwlist), &ignore_missing)) {
    return nullptr;
  }
  Widget* w = self->widget_->Get();
  if (!w) {
    if (!ignore_missing) {
      throw Exception(PyExcType::kWidgetNotFound);
    }
  } else {
    ContainerWidget* p = w->parent_widget();
    if (p) {
      p->DeleteWidget(w);
    } else {
      Log(LogLevel::kError, "Can't delete widget: no parent.");
    }
  }
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

auto PythonClassWidget::AddDeleteCallback(PythonClassWidget* self,
                                          PyObject* args, PyObject* keywds)
    -> PyObject* {
  BA_PYTHON_TRY;
  PyObject* call_obj;
  static const char* kwlist[] = {"call", nullptr};
  if (!PyArg_ParseTupleAndKeywords(args, keywds, "O",
                                   const_cast<char**>(kwlist), &call_obj)) {
    return nullptr;
  }
  Widget* w = self->widget_->Get();
  if (!w) {
    throw Exception(PyExcType::kWidgetNotFound);
  }
  w->AddOnDeleteCall(call_obj);
  Py_RETURN_NONE;
  BA_PYTHON_CATCH;
}

PyTypeObject PythonClassWidget::type_obj;
PyMethodDef PythonClassWidget::tp_methods[] = {
    {"exists", (PyCFunction)Exists, METH_NOARGS,
     "exists() -> bool\n"
     "\n"
     "Returns whether the Widget still exists.\n"
     "Most functionality will fail on a nonexistent widget.\n"
     "\n"
     "Note that you can also use the boolean operator for this same\n"
     "functionality, so a statement such as \"if mywidget\" will do\n"
     "the right thing both for Widget objects and values of None."},
    {"get_widget_type", (PyCFunction)GetWidgetType, METH_NOARGS,
     "get_widget_type() -> str\n"
     "\n"
     "Return the internal type of the Widget as a string. Note that this\n"
     "is different from the Python bauiv1.Widget type, which is the same for\n"
     "all widgets."},
    {"activate", (PyCFunction)Activate, METH_NOARGS,
     "activate() -> None\n"
     "\n"
     "Activates a widget; the same as if it had been clicked."},
    {"get_children", (PyCFunction)GetChildren, METH_NOARGS,
     "get_children() -> list[bauiv1.Widget]\n"
     "\n"
     "Returns any child Widgets of this Widget."},
    {"get_screen_space_center", (PyCFunction)GetScreenSpaceCenter, METH_NOARGS,
     "get_screen_space_center() -> tuple[float, float]\n"
     "\n"
     "Returns the coords of the bauiv1.Widget center relative to the center\n"
     "of the screen. This can be useful for placing pop-up windows and other\n"
     "special cases."},
    {"get_selected_child", (PyCFunction)GetSelectedChild, METH_NOARGS,
     "get_selected_child() -> bauiv1.Widget | None\n"
     "\n"
     "Returns the selected child Widget or None if nothing is selected."},
    // NOLINTNEXTLINE (signed bitwise stuff)
    {"delete", (PyCFunction)Delete, METH_VARARGS | METH_KEYWORDS,
     "delete(ignore_missing: bool = True) -> None\n"
     "\n"
     "Delete the Widget. Ignores already-deleted Widgets if ignore_missing\n"
     "is True; otherwise an Exception is thrown."},
    {"add_delete_callback", (PyCFunction)AddDeleteCallback,
     METH_VARARGS | METH_KEYWORDS,  // NOLINT (signed bitwise stuff)
     "add_delete_callback(call: Callable) -> None\n"
     "\n"
     "Add a call to be run immediately after this widget is destroyed."},
    {nullptr}};

}  // namespace ballistica::ui_v1
