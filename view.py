# coding: utf-8

from types import SimpleNamespace

import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Atk, GdkPixbuf, Gdk
import gettext

class View:
	def set_transl(self,transl):
		_=transl.gettext

	def fill_store(self,data):
		for row in data:
			self.store.append(row)

	def build_view(self):
		self.width = 800
		self.height = 600
		store = Gtk.ListStore(str, str, GdkPixbuf.Pixbuf, str)
		self.store = store
		filter = store.filter_new()
		self.filter = filter
		self.filter_prefix = ""
		self.entries = self.build_entries()
		explore_lbl_str = _("_Explore")
		self.explore = Gtk.Button(label=explore_lbl_str, use_underline=True)
		self.spinner = Gtk.Spinner()
		delete_lbl_str = _("_Remove")
		self.delete = Gtk.Button(label=delete_lbl_str, use_underline=True)
		self.delete.get_style_context().add_class(Gtk.STYLE_CLASS_DESTRUCTIVE_ACTION)
		boxButtons = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin=8)
		boxButtons.pack_start(self.explore, False, False, 0)
		boxButtons.pack_start(self.delete, False, False, 0)
		boxButtons.pack_start(self.spinner, False,False,0)
		scrolled_window = Gtk.ScrolledWindow(expand=True)
		self.scrolled_window=scrolled_window
		scrolled_window.set_size_request(self.width, self.height)
		self.spinner.start()
		grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
		grid.attach(scrolled_window, 0, 1, 1, 1)
		grid.attach(boxButtons, 0, 2, 3, 1)
		win = Gtk.Window(title="IPM P1")
		win.connect('delete-event', Gtk.main_quit)
		win.add(grid)
		self.win = win

	def build_entries(self):
		entries = Gtk.TreeView(self.filter, headers_visible=False)
		renderer0 = Gtk.CellRendererText()
		lbl_0 = _("Name")
		column0 = Gtk.TreeViewColumn(lbl_0, renderer0, text=0)
		renderer1 = Gtk.CellRendererText()
		lbl_1 = _('Date')
		column1 = Gtk.TreeViewColumn(lbl_1, renderer1, text=1)
		renderer2 = Gtk.CellRendererPixbuf()
		lbl_2 = _("Image")
		column2 = Gtk.TreeViewColumn(lbl_2, renderer2, pixbuf = 2)
		delete_lbl_str = _("_Delete")
		self.delete = Gtk.Button(label=delete_lbl_str, use_underline=True)
		entries.append_column(column0)
		entries.append_column(column1)
		entries.append_column(column2)
		return entries

	def connect_explore_clicked(self, callback):
		self.explore.connect('clicked', callback)

	def connect_row_activated(self, callback):
		self.entries.connect('row-activated', callback)

	def connect_entries_selection_changed(self, callback):
		self.entries.get_selection().connect("changed", callback)

	def connect_delete_clicked(self, callback):
		self.delete.connect('clicked', callback)

	def _get_selected(self):
		filtermodel, filteriter = self.entries.get_selection().get_selected()
		if filteriter == None:
			return (None, None)
		treeiter = filtermodel.convert_iter_to_child_iter(filteriter)
		treemodel = filtermodel.get_model()
		return (treemodel, treeiter)

	def get_selection_info(self):
		treemodel, treeiter = self._get_selected()
		if treeiter is None:
			return None
		row = treemodel[treeiter]
		[position] = treemodel.get_path(treeiter).get_indices()
		return (position, row)

	def confirm_load(self):
		self.scrolled_window.add(self.entries)
		self.entries.grab_focus()
		self.show_all()
		self.spinner.stop()
		self.update_sensitive(explore_btn= False,delete_btn=False,deleting=False)


	def update_sensitive(self, explore_btn, delete_btn, deleting):
		if deleting:
			return
		else:
			self.explore.set_sensitive(explore_btn)
			self.delete.set_sensitive(delete_btn)

	def update_on_deletion(self):
		treemodel, treeiter = self._get_selected()
		treemodel.remove(treeiter)

	def tap_spinner(self,toggle):
		if toggle:
			self.spinner.start()
		else:
			self.spinner.stop()

	def tap_dialog_spinner(self,toggle):
		if toggle:
			self.dialog.spinner.start()
		else:
			self.dialog.spinner.stop()

	def show_all(self):
		self.win.show_all()

	def _run_workout_details_dialog(self, workout_data,workout_id,workout_name,on_up_clicked,on_down_clicked):
		self.spinner.stop()     
		dialog_label =_("Workout details")
		self.dialog=WorkoutDetailsDialog(self.win, dialog_label, workout_data,workout_id,workout_name)
		self.dialog.connect_up_clicked(on_up_clicked)
		self.dialog.connect_down_clicked(on_down_clicked)
		self.dialog.run()
	def _run_error_dialog(self,title,desc):
		self.err_dialog=ErrorDialog(self.win, title,desc)
		self.err_dialog.run()

	def get_dialog_selection_info(self):
		selection_info = self.dialog.get_selection_info()
		return selection_info

	def refresh_dialog(self,workout_data,new_idx):
		liststore = self.dialog.fill_store(workout_data)
		self.dialog.store.clear()
		self.dialog.entries.set_model(liststore)
		self.dialog.entries.get_selection().select_path(new_idx)
		self.dialog.spinner.stop()

class WorkoutDetailsDialog:

	def __init__(self, parent, title, workout_data,workout_id,workout_name):
		dialog = Gtk.Dialog(title, parent, Gtk.DialogFlags.DESTROY_WITH_PARENT)
		dialog.set_default_response(Gtk.ResponseType.OK)
		dialog.set_response_sensitive(Gtk.ResponseType.OK, False)
		self.dialog = dialog
		label1 = _("Workout name")
		self.workout_name_label = Gtk.Label(label=workout_name)
		self.workout=workout_id
		self.store=self.fill_store(workout_data)
		filter = self.store.filter_new()
		self.filter = filter
		self.filter_prefix = ""
		self.entries = self.build_entries()
		scrolled_window = Gtk.ScrolledWindow(expand=True)
		scrolled_window.set_size_request(800, 600)
		scrolled_window.add(self.entries)
		self.scrolled_window = scrolled_window
		up_lbl_str = _("UP")
		down_lbl_str = _("DOWN")
		self.up = Gtk.Button(label=up_lbl_str, use_underline=True)
		self.down = Gtk.Button(label=down_lbl_str, use_underline=True)
		self.spinner = Gtk.Spinner()
		boxButtons = Gtk.Box(
			orientation=Gtk.Orientation.HORIZONTAL, spacing=8, margin=8)
		boxButtons.pack_start(self.up, False, False, 0)
		boxButtons.pack_start(self.down, False, False, 0)
		boxButtons.pack_start(self.spinner, False, False, 0)
		grid = Gtk.Grid(margin=20, column_spacing=10, row_spacing=10)
		grid.attach(scrolled_window, 0, 1, 1, 1)
		grid.attach(boxButtons, 0, 2, 3, 1)
		self.box = dialog.get_content_area()
		self.box.pack_start(self.workout_name_label, True, True, 15)
		self.box.pack_start(grid, True, True, 0)
		self.box.show_all()

	def build_entries(self):
		entries = Gtk.TreeView(self.filter, headers_visible=False)
		renderer0 = Gtk.CellRendererText()
		renderer0.props.wrap_width = 300
		column0text=_("Duration")
		column1text=_("Exercise Name")
		column2text=_("Exercise Description")
		column3text=_("Image")
		column4text=_("Video URL")
		column0 = Gtk.TreeViewColumn(column0text, renderer0, text=0)
		renderer1 = Gtk.CellRendererText()
		renderer1.props.wrap_width = 300
		column1 = Gtk.TreeViewColumn(column1text, renderer1, text=1)
		renderer2 = Gtk.CellRendererText()
		renderer2.props.wrap_width = 300
		column2 = Gtk.TreeViewColumn(column2text, renderer2, text=2)
		renderer3 = Gtk.CellRendererPixbuf()
		column3 = Gtk.TreeViewColumn(column3text, renderer3, pixbuf = 3)
		renderer4 = Gtk.CellRendererText()
		renderer4.props.wrap_width = 100
		column4 = Gtk.TreeViewColumn(column4text, renderer4, text = 4)
		entries.append_column(column0)
		entries.append_column(column1)
		entries.append_column(column2)
		entries.append_column(column3)
		entries.append_column(column4)
		return entries

	def connect_up_clicked(self, callback):
		self.up.connect('clicked', callback)

	def connect_down_clicked(self, callback):
		self.down.connect('clicked', callback)

	def run(self):
		self.dialog.run()
		self.dialog.destroy()

	def get_selection_info(self):
		treemodel, treeiter = self._get_selected()
		if treeiter is None:
			return None
		row_data = treemodel[treeiter]
		[idx] = treemodel.get_path(treeiter).get_indices()
		return (idx, row_data, self.workout, treemodel, treeiter)

	def _get_selected(self):
		filtermodel, filteriter = self.entries.get_selection().get_selected()
		if filteriter == None:
			return (None, None)
		return (filtermodel, filteriter)

	def fill_store(self, workout_data):
		tmp_store = Gtk.ListStore(str, str, str, GdkPixbuf.Pixbuf, str)
		for row in workout_data:
			tmp_store.append(row)
		return tmp_store

class ErrorDialog:

	def __init__(self, parent, title,desc):
		dialog = Gtk.Dialog(title, parent, Gtk.DialogFlags.DESTROY_WITH_PARENT)
		dialog.set_default_response(Gtk.ResponseType.OK)
		dialog.set_response_sensitive(Gtk.ResponseType.OK, False)
		self.workout_name_label = Gtk.Label(label= desc)
		self.dialog=dialog
		self.box = dialog.get_content_area()
		self.box.pack_start(self.workout_name_label, True, True, 60)
		self.box.show_all()

	def run(self):
		response = self.dialog.run()
		self.dialog.destroy()