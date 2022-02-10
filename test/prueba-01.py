#!/usr/bin/env python3
# coding: utf-8
import time
import pyatspi
import subprocess
import os
os.chdir("..")
subprocess.Popen('./ipm-p1.py')
import time


def tree(obj):
    yield obj
    for i in range(0, obj.get_child_count()):
        yield from tree(obj.get_child_at_index(i))

time.sleep(3)
desktop = pyatspi.Registry.getDesktop(0)
for i in range(desktop.get_child_count()):
	if desktop[i].get_name()=="ipm-p1.py":
		app = desktop[i]  
		break

for obj in tree(app):
	if obj.get_role_name()== "table":
		table=obj
		
		for obj in tree(table):
			if obj.get_name()=="Achilles":
				achilles=obj
				achilles.grab_focus()
				pyatspi.Registry.generateKeyboardEvent(65293, "", pyatspi.KEY_SYM)
				time.sleep(2)
				updatedwindow=pyatspi.Registry.getDesktop(0)
				for i in range(updatedwindow.get_child_count()):
					if updatedwindow[i].get_name()=="ipm-p1.py":
						app = updatedwindow[i]
						for i in range(app.get_child_count()):
							if app[i].get_role_name()=="dialog":
								dialog=app[i]
								for obj in tree(dialog):
									if obj.get_role_name()=="table":
										dialog_table=obj
										entries=dialog_table.get_child_count()-5
										exercises=entries//5
										if exercises==26:
											print("OK")
										else:
											print("Some exercises are missing")