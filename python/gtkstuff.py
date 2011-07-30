"""Generally useful gtk based widgets."""

#   Copyright (C) 2011 Stephen Fairchild (s-fairchild@users.sourceforge.net)
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program in the file entitled COPYING.
#   If not, see <http://www.gnu.org/licenses/>.


import os
from abc import ABCMeta, abstractmethod

import gobject
import gtk
import pango

from idjc import FGlobs, PGlobs



class LEDDict(dict):
   """Dictionary of pixbufs of LEDs."""
   
   
   def __init__(self, size=10):
      names = "clear", "red", "green", "yellow"
      filenames = ("led_unlit_clear_border_64x64.png",
                   "led_lit_red_black_border_64x64.png",
                   "led_lit_green_black_border_64x64.png",
                   "led_lit_amber_black_border_64x64.png")
      for name, filename in zip(names, filenames):
         self[name] = gtk.gdk.pixbuf_new_from_file_at_size(
            FGlobs.pkgdatadir / filename, size, size)



class CellRendererLED(gtk.CellRendererPixbuf):
   """A cell renderer that displays LEDs."""
   
   
   __gproperties__ = {
         "active" : (gobject.TYPE_INT, "active", "active",
                     0, 1, 0, gobject.PARAM_WRITABLE),
         "color" :  (gobject.TYPE_STRING, "color", "color",
                     "clear", gobject.PARAM_WRITABLE)
   }

                     
   def __init__(self, size=10, actives=("clear", "green")):
      gtk.CellRendererPixbuf.__init__(self)
      self._led = LEDDict(size)
      self._index = [self._led[key] for key in actives] 

        
   def do_set_property(self, prop, value):
      if prop.name == "active":
         item = self._index[value]
      elif prop.name == "color":
         item = self._led[value]
      else:
         raise AttributeError("unknown property %s" % prop.name)
         
      gtk.CellRendererPixbuf.set_property(self, "pixbuf", item)



class CellRendererTime(gtk.CellRendererText):
   """Displays time in days, hours, minutes."""
   
   
   __gproperties__ = {
         "time" : (gobject.TYPE_INT, "time", "time",
                   0, 1000000000, 0, gobject.PARAM_WRITABLE)
   }
   
   
   def do_set_property(self, prop, value):
      if prop.name == "time":
         m, s = divmod(value, 60)
         h, m = divmod(m, 60)
         d, h = divmod(h, 24)
         if d:
            text = "%dd.%02d:%02d" % (d, h, m)
         else:
            text = "%02d:%02d:%02d" % (h, m, s)
      else:
         raise AttributeError("unknown property %s" % prop.name)
         
      gtk.CellRendererText.set_property(self, "text", text)



class StandardDialog(gtk.Dialog):
   def __init__(self, title, message, stock_item, label_width, modal, markup):
      gtk.Dialog.__init__(self)
      self.set_border_width(6)
      self.get_child().set_spacing(12)
      self.set_modal(modal)
      self.set_destroy_with_parent(True)
      self.set_title(title)
      
      hbox = gtk.HBox()
      hbox.set_spacing(12)
      hbox.set_border_width(6)
      image = gtk.image_new_from_stock(stock_item,
                                          gtk.ICON_SIZE_DIALOG)
      image.set_alignment(0.0, 0.0)
      hbox.pack_start(image, False)
      vbox = gtk.VBox()
      hbox.pack_start(vbox)
      for each in message.split("\n"):
         label = gtk.Label(each)
         label.set_use_markup(markup)
         label.set_alignment(0.0, 0.0)
         label.set_size_request(label_width, -1)
         label.set_line_wrap(True)
         vbox.pack_start(label)
      ca = self.get_content_area()
      ca.add(hbox)
      aa = self.get_action_area()
      aa.set_spacing(6)



class ConfirmationDialog(StandardDialog):
   """This needs to be pulled out since it's generic."""
   
   def __init__(self, title, message, label_width=300, modal=True, markup=False):
      StandardDialog.__init__(self, title, message,
                     gtk.STOCK_DIALOG_WARNING, label_width, modal, markup)
      aa = self.get_action_area()
      cancel = gtk.Button(stock=gtk.STOCK_CANCEL)
      cancel.connect("clicked", lambda w: self.destroy())
      aa.pack_start(cancel)
      self.ok = gtk.Button(stock=gtk.STOCK_DELETE)
      self.ok.connect_after("clicked", lambda w: self.destroy())
      aa.pack_start(self.ok)



class ErrorMessageDialog(StandardDialog):
   """This needs to be pulled out since it's generic."""
   
   def __init__(self, title, message, label_width=300, modal=True, markup=False):
      StandardDialog.__init__(self, title, message,
                     gtk.STOCK_DIALOG_ERROR, label_width, modal, markup)
      b = gtk.Button(stock=gtk.STOCK_CLOSE)
      b.connect("clicked", lambda w: self.destroy())
      self.get_action_area().add(b)



def threadslock(f):
   """Function decorator for thread locking timeout callbacks."""
   
   
   def newf(*args, **kwargs):
      gtk.gdk.threads_enter()
      try:
         r = f(*args, **kwargs)
      finally:
         gtk.gdk.threads_leave()
      return r
   return newf



class DefaultEntry(gtk.Entry):
   def __init__(self, default_text, sensitive_override=False):
      gtk.Entry.__init__(self)
      self.connect("focus-in-event", self.on_focus_in)
      self.connect("focus-out-event", self.on_focus_out)
      self.props.primary_icon_activatable = True
      self.connect("icon-press", self.on_icon_press)
      self.connect("realize", self.on_realize)
      self.default_text = default_text
      self.sensitive_override = sensitive_override

   def on_realize(self, entry):
      layout = self.get_layout().copy()
      layout.set_markup("<span foreground='dark gray'>%s</span>" % self.default_text)
      extents = layout.get_pixel_extents()[1]
      drawable = gtk.gdk.Pixmap(self.get_parent_window(), extents[2], extents[3])
      gc = gtk.gdk.GC(drawable)
      gc2 = entry.props.style.base_gc[0]
      drawable.draw_rectangle(gc2, True, *extents)
      drawable.draw_layout(gc, 0, 0, layout)
      pixbuf = gtk.gdk.Pixbuf(gtk.gdk.COLORSPACE_RGB, True, 8, extents[2], extents[3])
      pixbuf.get_from_drawable(drawable, drawable.get_colormap(), 0, 0, *extents)
      self.empty_pixbuf = pixbuf
      if not gtk.Entry.get_text(self):
         self.props.primary_icon_pixbuf = pixbuf

   def on_icon_press(self, entry, icon_pos, event):
      self.grab_focus()
      
   def on_focus_in(self, entry, event):
      self.props.primary_icon_pixbuf = None
      
   def on_focus_out(self, entry, event):
      text = gtk.Entry.get_text(self).strip()
      if not text:
         self.props.primary_icon_pixbuf = self.empty_pixbuf
      
   def get_text(self):
      if (self.flags() & gtk.SENSITIVE) or self.sensitive_override:
         return gtk.Entry.get_text(self).strip() or self.default_text
      else:
         return ""
      
   def set_text(self, newtext):
      newtext = newtext.strip()
      gtk.Entry.set_text(self, newtext)
      if newtext:
         self.props.primary_icon_pixbuf = None
      else:
         try:
            self.props.primary_icon_pixbuf = self.empty_pixbuf
         except AttributeError:
            pass



class HistoryEntry(gtk.ComboBoxEntry):
   """Combobox which performs history function."""
   

   def __init__(self, max_size=6, initial_text=("",), store_blank=True):
      self.max_size = max_size
      self.store_blank = store_blank
      self.ls = gtk.ListStore(str)
      gtk.ComboBoxEntry.__init__(self, self.ls, 0)
      self.connect("notify::popup-shown", self.update_history)
      self.child.connect("activate", self.update_history)
      self.set_history("\x00".join(initial_text))
      geo = self.get_screen().get_root_window().get_geometry()
      cell = self.get_cells()[0]
      cell.props.wrap_width = geo[2] * 2 // 3
      cell.props.wrap_mode = pango.WRAP_CHAR


   def update_history(self, *args):
      text = self.child.get_text().strip()
      if self.store_blank or text:
         # Remove duplicate stored text.
         for i, row in enumerate(self.ls):
            if row[0] == text:
               del self.ls[i]
         # Newly entered text goes at top of history.
         self.ls.prepend((text,))
         # History size is kept trimmed.
         if len(self.ls) > self.max_size:
            del self.ls[-1]

   
   def get_text(self):
      return self.child.get_text()


   def set_text(self, text):
      self.update_history()
      self.child.set_text(text)

      
   def get_history(self):
      self.update_history()
      return "\x00".join([row[0] for row in self.ls])

      
   def set_history(self, hist):
      self.ls.clear()
      for text in reversed(hist.split("\x00")):
         self.set_text(text)



class NamedTreeRowReference(object):
   """Provides named attribute access to gtk.TreeRowReference objects.
   
   This is a virtual base class.
   Virtual method 'get_index_for_name()' must be provided in a subclass.
   """
   
   
   __metaclass__ = ABCMeta


   def __init__(self, tree_row_ref):
      object.__setattr__(self, "_tree_row_ref", tree_row_ref)
      
      
   @abstractmethod
   def get_index_for_name(self, tree_row_ref, name):
      """This method must be subclassed. Note the TreeRowReference
      in question is passed in in case that information is required
      to allocate the names.
      
      When a name is not available an exception must be raised and when
      one is the index into the TreeRowReference must be returned.
      """
      
      pass


   def _index_for_name(self, name):
      try:
         return self.get_index_for_name(self._tree_row_ref, name)
      except Exception:
         raise AttributeError("%s has no attribute: %s" % (repr(self._tree_row_ref), name))


   def __getitem__(self, path):
      return self._tree_row_ref[path]
      
      
   def __setitem__(self, path, data):
      self._tree_row_ref[path] = data


   def __getattr__(self, name):
      return self._tree_row_ref.__getitem__(self._index_for_name(name))


   def __setattr__(self, name, data):
      self._tree_row_ref[self._index_for_name(name)] = data
