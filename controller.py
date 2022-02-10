# coding: utf-8
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk,Gdk,GLib,Atk
import threading
import gettext

class Controller:
	def set_model(self, model,transl):
		self.model = model
		self.model.set_transl(transl)
		self.deleting= False

	def set_view(self, view,transl):
		self.view = view
		self.view.set_transl(transl)
		view.build_view()
		view.connect_explore_clicked(self.on_explore_clicked)
		view.connect_delete_clicked(self.on_delete_clicked)
		view.connect_entries_selection_changed(self.on_entries_selection_changed)
		view.connect_row_activated(self.on_row_activated)

	def launch_error(self,title,desc):
		self.deleting=False
		self.view._run_error_dialog(title,desc)

	def main(self,language):
		_=language.gettext
		self.button_sensitivity = False
		self.view.show_all()
		t3=threading.Thread(target=self.load_data_thread)
		t3.start()
		Gtk.main()

	def confirm_load(self):
			self.view.confirm_load()

	def confirm_error(self):
		self.view.update_sensitive(explore_btn= False,delete_btn=False,deleting=False)
		error_title=_("Workouts")
		error_description=_("Could not access the database")
		self.view.tap_spinner(False)
		self.launch_error(error_title,error_description)

	def load_data_thread(self):
		try:
			data = self.model.get_data()
			self.view.fill_store(data)
			GLib.idle_add(self.confirm_load)
		except:
			GLib.idle_add(self.confirm_error)

	def on_explore_clicked(self, w):
		selection_info = self.view.get_selection_info()
		if selection_info is None:
			return
		position, row = selection_info
		self.workout_id = self.model.workout_id_from_row(row)
		t2=threading.Thread(target=self.on_explore_clicked_thread,args=[self.workout_id])
		t2.start()

	def launch_workout_details_dialog(self,workout_data, workout_id,workout_name):
		self.view._run_workout_details_dialog(workout_data, workout_id,workout_name,self.on_up_clicked,self.on_down_clicked)

	def on_explore_clicked_thread(self,workout_id):
		self.view.tap_spinner(True)
		try:
			workout_data, workout_id,workout_name = self.model.get_workout_data(workout_id)
			GLib.idle_add(self.launch_workout_details_dialog,workout_data, workout_id,workout_name)
		except Exception as e:
			GLib.idle_add(self.view.tap_spinner,False)
			error_title=_("Workout Details")
			error_description=_("Could not access the database")
			GLib.idle_add(self.launch_error,error_title,error_description)
	
	def on_entries_selection_changed(self, selection):
		if self.button_sensitivity:
			sensitive = self.view.get_selection_info() is not None
			self.view.update_sensitive(explore_btn= sensitive,delete_btn=sensitive, deleting=self.deleting)
		else:
			self.button_sensitivity = True

	def on_row_activated(self,a,b,c):
		selection_info = self.view.get_selection_info()
		if selection_info is None:
			return
		position, row = selection_info
		workout_id = self.model.workout_id_from_row(row)
		t6=threading.Thread(target=self.on_explore_clicked_thread,args=[workout_id])
		t6.start()

	def on_row_activated_thread(workout_id):
		self.view.tap_spinner(True)
		try:
			workout_data, workout_id,workout_name = self.model.get_workout_data(workout_id)
			GLib.idle_add(self.launch_workout_details_dialog,workout_data, workout_id,workout_name)
		except Exception as e:
			GLib.idle_add(self.view.tap_dialog_spinner,False)
			error_title=_("Workout Details")
			error_description=_("Could not access the database")
			GLib.idle_add(self.launch_error,error_title,error_description)	

	def on_delete_clicked(self, w):
		self.view.tap_spinner(True)
		self.view.update_sensitive(False,False,self.deleting)
		self.deleting=True
		selection_info = self.view.get_selection_info()
		if selection_info == None:
			return
		position, row = selection_info
		object_id=self.model.workout_id_from_row(row)
		t1=threading.Thread(target=self.on_delete_clicked_thread,args=[object_id])
		t1.start()

	def confirm_deletion(self):
		self.deleting=False
		self.view.tap_spinner(False)
		self.view.update_on_deletion()
	def on_delete_clicked_thread(self,object_id):
		try:
			self.model.delete_workout(object_id)
			GLib.idle_add(self.confirm_deletion)
		except Exception as e:
			GLib.idle_add(self.view.tap_dialog_spinner,False)
			error_title=_("Deletion error")
			error_description=_("Deletion could not be performed")
			GLib.idle_add(self.launch_error, error_title,error_description)

	def on_up_clicked(self, w):
		self.on_switch_places_clicked(-1)

	def on_down_clicked(self, w):
		self.on_switch_places_clicked(1)

	def on_switch_places_clicked(self, target):
		self.view.tap_dialog_spinner(True)
		t4 = threading.Thread(target=self.on_switch_places_clicked_thread, args=[target])
		t4.start()

	def refresh_dialog(self, workout_data,new_idx):
		self.view.refresh_dialog(workout_data,new_idx)

	def on_switch_places_clicked_thread(self, target):
		try:
			doc, idx = self.get_dialog_doc_info()
			new_idx = self.model.switch_places(doc, idx, idx+target)
			workout_data,workout_id,workout_name = self.model.get_workout_data(self.workout_id)
			GLib.idle_add(self.view.refresh_dialog,workout_data, new_idx)
		except:
			GLib.idle_add(self.view.tap_dialog_spinner,False)
			error_title = _("Switching error")
			error_description = _("Switching could not be performed")
			GLib.idle_add(self.launch_error, error_title, error_description)

	def get_dialog_doc_info(self):
		selection_info = self.view.get_dialog_selection_info()
		if selection_info is None:
			return
		idx, row_data, workout, treemodel, treeiter = selection_info
		doc = self.model.get_doc('workouts', '_id', workout)
		return doc, idx