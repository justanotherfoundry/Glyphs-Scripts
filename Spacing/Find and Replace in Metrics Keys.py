# MenuTitle: Find and Replace in Metrics Keys
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Finds and replaces text in the metrics keys of selected glyphs. Leave the Find string blank to hang the replace string at the end of the metrics keys.
"""

import vanilla
import traceback
from GlyphsApp import Glyphs
from mekkablue import mekkaObject


class MetricKeyReplacer(mekkaObject):
	prefDict = {
		"leftSearchFor": "=a",
		"leftReplaceBy": "=a.ss01",
		"rightSearchFor": "=|a",
		"rightReplaceBy": "=|a.ss01",
	}

	def __init__(self):
		self.w = vanilla.FloatingWindow((335, 125), "Find and Replace in Metrics Keys", autosaveName=self.domain("mainwindow"))

		self.w.text_Find = vanilla.TextBox((10, 30 + 3, 55, 20), "Find", sizeStyle='small')
		self.w.text_Replace = vanilla.TextBox((10, 55 + 3, 55, 20), "Replace", sizeStyle='small')

		self.w.text_left = vanilla.TextBox((70, 12, 120, 14), "Left Key", sizeStyle='small')
		self.w.leftSearchFor = vanilla.EditText((70, 30, 120, 20), "=a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.leftReplaceBy = vanilla.EditText((70, 55, 120, 20), "=a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')

		self.w.text_right = vanilla.TextBox((200, 12, 120, 14), "Right Key", sizeStyle='small')
		self.w.rightSearchFor = vanilla.EditText((200, 30, 120, 20), "=|a", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')
		self.w.rightReplaceBy = vanilla.EditText((200, 55, 120, 20), "=|a.ss01", callback=self.SavePreferences, sizeStyle='small', placeholder='(empty)')

		self.w.runButton = vanilla.Button((-110, -20 - 15, -15, -15), "Replace", sizeStyle='regular', callback=self.MetricKeyReplaceMain)
		self.w.setDefaultButton(self.w.runButton)

		try:
			self.LoadPreferences()
		except:
			print("Warning: Could not load preferences.\n%s" % traceback.format_exc())

		self.w.open()
		self.w.makeKey()

	def MetricKeyReplaceMain(self, sender):
		Glyphs.font.disableUpdateInterface()
		try:
			self.SavePreferences()

			Font = Glyphs.font
			selectedLayers = Font.selectedLayers
			currentLayers = [layer for layer in selectedLayers if layer.parent.name is not None]

			LsearchFor = self.w.leftSearchFor.get()
			LreplaceBy = self.w.leftReplaceBy.get()
			RsearchFor = self.w.rightSearchFor.get()
			RreplaceBy = self.w.rightReplaceBy.get()

			for layer in currentLayers:
				try:
					g = layer.parent
					# g.beginUndo()  # undo grouping causes crashes

					# Left Metrics Key:
					try:
						for glyphOrLayer in (g, layer):
							leftKey = glyphOrLayer.leftMetricsKey
							if leftKey:
								if LsearchFor == "":
									glyphOrLayer.leftMetricsKey = leftKey + LreplaceBy
								else:
									glyphOrLayer.leftMetricsKey = leftKey.replace(LsearchFor, LreplaceBy)

								print("%s: new left metrics key: '%s'" % (g.name, glyphOrLayer.leftMetricsKey))

					except Exception as e:
						print("\nError while trying to set left key for: %s" % g.name)
						print(e)
						print(traceback.format_exc())

					# Right Metrics Key:
					try:
						for glyphOrLayer in (g, layer):
							rightKey = glyphOrLayer.rightMetricsKey
							if rightKey:
								if LsearchFor == "":
									glyphOrLayer.rightMetricsKey = rightKey + RreplaceBy
								else:
									glyphOrLayer.rightMetricsKey = rightKey.replace(RsearchFor, RreplaceBy)

								print("%s: new right metrics key: '%s'" % (g.name, glyphOrLayer.rightMetricsKey))

					except Exception as e:
						print("\nError while trying to set right key for: %s" % g.name)
						print(e)
						print(traceback.format_exc())

					# g.endUndo()  # undo grouping causes crashes

				except Exception as e:
					print("\nError while processing glyph %s" % g.name)
					print(e)
					print(traceback.format_exc())

					# g.endUndo()  # undo grouping causes crashes

			self.w.close()

		except Exception as e:
			Glyphs.showMacroWindow()
			print("\n⚠️ Script Error:\n")
			import traceback
			print(traceback.format_exc())
			print()
			raise e

		finally:
			Glyphs.font.enableUpdateInterface()


Glyphs.clearLog()
MetricKeyReplacer()
