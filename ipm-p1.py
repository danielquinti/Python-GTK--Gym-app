#!/usr/bin/env python3
# coding: utf-8

from controller import Controller
from view import View
from model import Model
import gettext
import locale
from pathlib import Path

if __name__ == '__main__':
	#
	# Workarround para que funcione el CTRL+C
	import signal
	signal.signal(signal.SIGINT, signal.SIG_DFL)
	LOCALE_DIR = Path(__file__).parent / "locale"
	locale.bindtextdomain('IPM P1', LOCALE_DIR)
	gettext.bindtextdomain('IPM P1', LOCALE_DIR)
	gettext.textdomain('IPM P1')
	locale_tuple=locale.getdefaultlocale()
	locale_string=locale_tuple[0]+'.'+locale_tuple[1]
	language = gettext.translation('base', localedir = 'locales', languages= [locale_string])
	language.install()
	_= language.gettext
	controller = Controller()
	controller.set_model(Model(),language)
	controller.set_view(View(),language)
	controller.main(language)

