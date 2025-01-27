# MenuTitle: Straight Stem Cruncher
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Measures in centers of straight segments, and reports deviations in stem thicknesses.
"""

import vanilla
from Foundation import NSPoint
from GlyphsApp import Glyphs, GSAnnotation, PLUS, Message, distance, subtractPoints, scalePoint, addPoints
from mekkablue import mekkaObject


def pointDistance(p1, p2):
	stemThickness = ((p2.x - p1.x)**2.0 + (p2.y - p1.y)**2.0)**0.5
	return stemThickness


def middleBetweenTwoPoints(p1, p2):
	x = (p1.x + p2.x) * 0.5
	y = (p1.y + p2.y) * 0.5
	return NSPoint(x, y)


class StraightStemCruncher(mekkaObject):
	defaultExcludeList = ".sc, .c2sc, .smcp, .sups, .subs, .sinf, superior, inferior, .numr, .dnom"
	prefDict = {
		"stems": "80, 100",
		"deviationMin": 0.6,
		"deviationMax": 4.0,
		"checkSpecialLayers": 1,
		"selectedGlyphsOnly": 0,
		"includeNonExporting": 0,
		"openTab": 1,
		"includeCompounds": 0,
		"minimumSegmentLength": 200,
		"reportNonMeasurements": 0,
		"excludeGlyphs": 0,
		"excludeGlyphNames": defaultExcludeList,
		"checkVStems": 1,
		"checkHStems": 0,
		"checkDStems": 0,
		"markStems": 1,
		"reuseTab": 1,
	}

	marker = "➕"

	def __init__(self):
		# Window 'self.w':
		windowWidth = 355
		windowHeight = 370
		windowWidthResize = 600  # user can resize width by this value
		windowHeightResize = 0  # user can resize height by this value
		self.w = vanilla.FloatingWindow(
			(windowWidth, windowHeight),  # default window size
			"Straight Stem Cruncher",  # window title
			minSize=(windowWidth, windowHeight),  # minimum size (for resizing)
			maxSize=(windowWidth + windowWidthResize, windowHeight + windowHeightResize),  # maximum size (for resizing)
			autosaveName=self.domain("mainwindow")  # stores last window position and size
		)

		# UI elements:
		linePos, inset, lineHeight = 12, 15, 22
		self.w.descriptionText = vanilla.TextBox((inset, linePos + 2, -inset, 14), u"In current master, looks for stems close but not exactly at:", sizeStyle='small', selectable=True)
		linePos += lineHeight

		self.w.stemsText = vanilla.TextBox((inset, linePos + 3, 80, 14), u"Stem Widths:", sizeStyle='small', selectable=True)
		self.w.stems = vanilla.EditText((inset + 80, linePos, -inset - 25, 19), "20, 30, 40", callback=self.SavePreferences, sizeStyle='small')
		self.w.stems.getNSTextField().setToolTip_("Comma-separated list of stem sizes to look for. If the script finds stems deviating from these sizes, within the given min/max deviations, it will report them.")
		self.w.stemUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update)
		self.w.stemUpdate.getNSButton().setToolTip_("Populate the stems with the stems of the current master.")
		linePos += lineHeight

		self.w.stemFindText = vanilla.TextBox((inset, linePos + 3, 175, 14), u"Find deviating stems, min/max:", sizeStyle='small', selectable=True)
		self.w.deviationMin = vanilla.EditText((inset + 175, linePos, 45, 19), "0.4", callback=self.SavePreferences, sizeStyle='small')
		self.w.deviationMin.getNSTextField().setToolTip_("Deviations up to this value will be tolerated. Half a unit is a good idea to avoid false positives from rounding errors.")
		self.w.deviationMax = vanilla.EditText((inset + 175 + 55, linePos, 45, 19), "3.1", callback=self.SavePreferences, sizeStyle='small')
		self.w.deviationMax.getNSTextField().setToolTip_("Deviations up to this value will be reported. Do not exaggerate value, otherwise you get false positives from cases where the opposing segment is not the other side of the stem.")
		linePos += lineHeight

		self.w.minimumSegmentLengthText = vanilla.TextBox((inset, linePos + 2, 145, 14), u"Minimum segment length:", sizeStyle='small', selectable=True)
		self.w.minimumSegmentLength = vanilla.EditText((inset + 145, linePos, -inset - 25, 19), "200", callback=self.SavePreferences, sizeStyle='small')
		self.w.minimumSegmentLength.getNSTextField(
		).setToolTip_("Looks for straight-line segments with at least this length and measures from their center to the opposing segment. Half x-height is a good idea.")
		self.w.segmentLengthUpdate = vanilla.SquareButton((-inset - 20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update)
		self.w.segmentLengthUpdate.getNSButton().setToolTip_("Reset to 40% of x-height.")
		linePos += lineHeight

		self.w.checkStemsText = vanilla.TextBox((inset, linePos + 2, 80, 14), u"Check stems:", sizeStyle='small', selectable=True)
		self.w.checkVStems = vanilla.CheckBox((inset + 90, linePos - 1, 65, 20), u"Vertical", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.checkHStems = vanilla.CheckBox((inset + 90 + 65, linePos - 1, 80, 20), u"Horizontal", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.checkDStems = vanilla.CheckBox((inset + 90 + 65 + 80, linePos - 1, -inset, 20), u"Diagonal", value=False, callback=self.SavePreferences, sizeStyle='small')
		checkStemsTooltip = "Choose which stems to measure: any combination of these three options. At least one must be active to run the script."
		self.w.checkVStems.getNSButton().setToolTip_(checkStemsTooltip)
		self.w.checkHStems.getNSButton().setToolTip_(checkStemsTooltip)
		self.w.checkDStems.getNSButton().setToolTip_(checkStemsTooltip)
		linePos += lineHeight

		self.w.checkSpecialLayers = vanilla.CheckBox((inset, linePos, -inset, 20), u"Also check bracket layers", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.checkSpecialLayers.getNSButton().setToolTip_("If checked, also measures on bracket ayers. Otherwise only on master layers.")
		linePos += lineHeight

		self.w.selectedGlyphsOnly = vanilla.CheckBox((inset, linePos, -inset, 20), u"Measure selected glyphs only (otherwise all glyphs in font)", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.selectedGlyphsOnly.getNSButton().setToolTip_("Uncheck for measuring complete font.")
		linePos += lineHeight

		self.w.includeNonExporting = vanilla.CheckBox((inset, linePos, -inset, 20), u"Include non-exporting glyphs", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeNonExporting.getNSButton().setToolTip_("Usually not necessary because the algorithm decomposes and removes overlap first.")
		linePos += lineHeight

		self.w.includeCompounds = vanilla.CheckBox((inset, linePos, -inset, 20), u"Include components", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.includeCompounds.getNSButton().setToolTip_("If checked, also measures components (after decomposition and removing overlap). If unchecked, only measures outlines.")
		linePos += lineHeight

		self.w.excludeGlyphs = vanilla.CheckBox((inset, linePos, 165, 20), u"Exclude glyphs containing:", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeGlyphNames = vanilla.EditText((inset + 165, linePos, -inset - 25, 19), self.defaultExcludeList, callback=self.SavePreferences, sizeStyle='small')
		self.w.excludeGlyphNames.getNSTextField(
		).setToolTip_("Comma-separated list of glyph name parts (e.g., suffixes). Glyphs containing these will not be measured if checkbox is enabled.")
		self.w.excludeGlyphNamesReset = vanilla.SquareButton((-inset - 20, linePos, -inset, 19), u"↺", sizeStyle='small', callback=self.update)
		self.w.excludeGlyphNamesReset.getNSButton().setToolTip_("Reset to: %s." % self.defaultExcludeList)
		linePos += lineHeight

		self.w.markStems = vanilla.CheckBox((inset, linePos, -inset, 20), u"Mark affected stems with %s annotation" % self.marker, value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.markStems.getNSButton().setToolTip_("If checked, will add a red-plus annotation at the center of the measurement. Will often add two of them because stem will be measured from both sides.\nCAREFUL: May delete existing plus annotations.")
		linePos += lineHeight

		self.w.reportNonMeasurements = vanilla.CheckBox((inset, linePos, -inset, 20), u"Report layers without measurements", value=False, callback=self.SavePreferences, sizeStyle='small')
		self.w.reportNonMeasurements.getNSButton().setToolTip_("In Macro Window, report if a layer does not have any measurements. Most likely causes: no straight stems in the paths, or wrong path direction.")
		linePos += lineHeight

		self.w.openTab = vanilla.CheckBox((inset, linePos, 200, 20), u"Open tab with affected glyphs", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.openTab.getNSButton().setToolTip_("If unchecked, will bring macro window with detailed report to front.")
		self.w.reuseTab = vanilla.CheckBox((inset + 200, linePos, -inset, 20), u"Reuse current tab", value=True, callback=self.SavePreferences, sizeStyle='small')
		self.w.reuseTab.getNSButton().setToolTip_(u"If checked, will reuse the active tab if there is one, otherwise will open a new tab. If unchecked, will always open a new tab.")
		linePos += lineHeight

		self.w.progress = vanilla.ProgressBar((inset, linePos, -inset, 16))
		self.w.progress.set(0)  # set progress indicator to zero
		linePos += lineHeight

		# Status message:
		self.w.status = vanilla.TextBox((inset, -18 - inset, -120 - inset, 16), u"🤖 Ready.", sizeStyle='small', selectable=True)

		# Run Button:
		self.w.runButton = vanilla.Button((-120 - inset, -20 - inset, -inset, -inset), "Measure", sizeStyle='regular', callback=self.StraightStemCruncherMain)
		self.w.setDefaultButton(self.w.runButton)

		# Load Settings:
		self.LoadPreferences()

		# Open window and focus on it:
		self.w.open()
		self.w.makeKey()

	def updateUI(self, sender=None):
		self.w.reuseTab.enable(self.w.openTab.get())

		buttonEnable = (
			self.pref("checkVStems") or self.pref("checkHStems")
			or self.pref("checkDStems")
		)
		self.w.runButton.enable(onOff=buttonEnable)

	def update(self, sender=None):
		if sender == self.w.segmentLengthUpdate:
			xHeight = Glyphs.font.selectedFontMaster.xHeight
			self.w.minimumSegmentLength.set("%i" % round(xHeight / 2.1, -1))

		elif sender == self.w.stemUpdate:
			thisFont = Glyphs.font
			if thisFont:
				master = thisFont.selectedFontMaster
				if master:

					if Glyphs.versionNumber >= 3:
						# Glyphs 3 code
						stems = [stem for stem in master.stems]
					else:
						stems = []
						# Glyphs 2 code
						for stemSet in (master.horizontalStems, master.verticalStems):
							if stemSet:
								for s in stemSet:
									stems.append(s)
					stems = sorted(set(stems))
					stemString = ", ".join([str(s) for s in stems])
					if stemString:
						self.w.stems.set(stemString)
					else:
						Message(title="Stem Error", message="No standard stems defined in the current master. Please add some in Font Info > Masters.", OKButton=None)

		elif sender == self.w.excludeGlyphNamesReset:
			self.w.excludeGlyphNames.set(self.defaultExcludeList)

		self.SavePreferences()

	def stemThicknessAtLine(self, layer, p1, p2, measureLength):
		h = p2.x - p1.x
		v = p2.y - p1.y
		length = (h**2 + v**2)**0.5

		hUnit = h / length
		vUnit = v / length

		h = hUnit * measureLength
		v = vUnit * measureLength

		measurePoint1 = middleBetweenTwoPoints(p1, p2)
		# print "  middle:", measurePoint1, hUnit, vUnit
		# measurePoint1.x += vUnit*2
		# measurePoint1.y -= hUnit*2

		measurePoint2 = NSPoint(measurePoint1.x - v, measurePoint1.y + h)
		intersections = layer.intersectionsBetweenPoints(measurePoint1, measurePoint2)

		if measurePoint1 != intersections[0].pointValue():
			intersections = intersections[::-1]

		if len(intersections) > 2:
			# two measurement points:
			p1 = intersections[0].pointValue()
			p2 = intersections[1].pointValue()

			# calculate stem width:
			stemWidth = distance(p1, p2)

			# calculate center of stem:
			vector = subtractPoints(p2, p1)
			scaledVector = scalePoint(vector, 0.5)
			centerOfStem = addPoints(p1, scaledVector)

			# return results:
			return stemWidth, centerOfStem
		else:
			return None

	def measureStraighStemsInLayer(self, layer, glyphName=""):
		try:
			minLength = self.prefInt("minimumSegmentLength")
		except:
			self.update(self.w.segmentLengthUpdate)
			minLength = self.prefInt("minimumSegmentLength")

		checkVStems = self.pref("checkVStems")
		checkHStems = self.pref("checkHStems")
		checkDStems = self.pref("checkDStems")

		centers = []
		measurements = []
		measureLayer = layer.copyDecomposedLayer()
		measureLayer.parent = layer.parent
		measureLayer.removeOverlap()

		for thisPath in measureLayer.paths:
			nodeCount = len(thisPath.nodes)
			if nodeCount > 2:
				for thisSegment in thisPath.segments:
					if len(thisSegment) == 2:
						p1 = thisSegment[0]
						p2 = thisSegment[1]

						isVertical = (p1.x == p2.x)
						isHorizontal = (p1.y == p2.y)
						check = False

						if isHorizontal and checkHStems:
							check = True

						elif isVertical and checkVStems:
							check = True

						elif checkDStems:
							check = True

						# if p1.x==p2.x or p1.y==p2.y or not self.pref("ignoreDiagonals"):
						if check:
							if pointDistance(p1, p2) >= minLength:
								measureLength = max(100.0, measureLayer.bounds.size.width + measureLayer.bounds.size.height)
								results = self.stemThicknessAtLine(measureLayer, p1, p2, measureLength)
								if results:
									measurement, centerOfStem = results
									measurements.append(measurement)
									centers.append(centerOfStem)
			else:
				print(u"⚠️ Found path with only %i point%s%s." % (
					nodeCount,
					"" if nodeCount == 1 else "s",
					" in %s" % glyphName if glyphName else "",
				))
		return measurements, centers

	def StraightStemCruncherMain(self, sender):
		try:
			Glyphs.clearLog()

			# update settings to the latest user input:
			self.SavePreferences()

			thisFont = Glyphs.font  # frontmost font
			print("Straight Stem Cruncher Report for %s" % thisFont.familyName)
			print(thisFont.filepath)
			print()

			self.w.progress.set(0)
			if self.pref("selectedGlyphsOnly"):
				glyphsToCheck = [layer.parent for layer in thisFont.selectedLayers]
			else:
				glyphsToCheck = thisFont.glyphs

			excludedGlyphNameParts = []
			if self.pref("excludeGlyphs"):
				enteredParts = [x.strip() for x in self.pref("excludeGlyphNames").split(",")]
				if enteredParts:
					excludedGlyphNameParts.extend(set(enteredParts))

			stems = self.pref("stems")  # "80, 100"
			stems = [float(s.strip()) for s in stems.split(",")]

			shouldMark = self.pref("markStems")
			deviationMin = self.prefFloat("deviationMin")  # 0.6
			deviationMax = self.prefFloat("deviationMax")  # 4.0

			affectedLayers = []
			for glyphIndex, thisGlyph in enumerate(glyphsToCheck):
				self.w.progress.set(100 * glyphIndex / len(thisFont.glyphs))

				# see if any exclusion applies:

				glyphNameIsExcluded = False
				for particle in excludedGlyphNameParts:
					if particle in thisGlyph.name:
						glyphNameIsExcluded = True
						break

				glyphExportsOrNonExportingIncluded = thisGlyph.export or self.pref("includeNonExporting")

				if glyphExportsOrNonExportingIncluded and not glyphNameIsExcluded:
					self.w.status.set("Processing: %s" % thisGlyph.name)
					for thisLayer in thisGlyph.layers:
						if thisLayer.master == thisFont.selectedFontMaster:
							if thisLayer.isMasterLayer or (thisLayer.isSpecialLayer and self.pref("checkSpecialLayers")):

								# clean previous markings:
								if shouldMark:
									for i in range(len(thisLayer.annotations) - 1, -1, -1):
										a = thisLayer.annotations[i]
										if a and a.text == self.marker:
											del (thisLayer.annotations[i])

								# decompose components if necessary:
								if self.pref("includeCompounds"):
									checkLayer = thisLayer.copyDecomposedLayer()
									checkLayer.parent = thisLayer.parent
								else:
									checkLayer = thisLayer.copy()
									checkLayer.parent = thisLayer.parent
									if Glyphs.versionNumber >= 3:
										# Glyphs 3 code

										for comp in checkLayer.components:

											del checkLayer.shapes[checkLayer.shapes.index(comp)]

									else:
										# Glyphs 2 code
										checkLayer.components = None

								# go on if there are any paths:
								if checkLayer.paths:
									checkLayer.removeOverlap()
									measurements, centers = self.measureStraighStemsInLayer(checkLayer, glyphName=thisGlyph.name)
									if not measurements:
										if self.pref("reportNonMeasurements"):
											print(u"⚠️ %s, layer '%s': no stem measurements. Wrong path direction or no line segments?" % (
												thisGlyph.name,
												thisLayer.name,
											))
									else:
										deviatingStems = []
										for i, measurement in enumerate(measurements):
											if measurement not in stems:
												for stem in stems:
													if stem - deviationMax < measurement < stem - deviationMin or stem + deviationMin < measurement < stem + deviationMax:
														deviatingStems.append(measurement)
														if shouldMark:
															centerOfStem = centers[i]
															marker = GSAnnotation()
															marker.position = centerOfStem
															marker.type = PLUS
															# marker.type = TEXT
															# marker.text = self.marker
															thisLayer.annotations.append(marker)

										if deviatingStems:
											print(
												u"❌ %s, layer '%s': found %i stem%s off: %s." % (
													thisGlyph.name,
													thisLayer.name,
													len(deviatingStems),
													"" if len(deviatingStems) == 1 else "s",
													", ".join(["%.1f" % s for s in deviatingStems]),
												)
											)
											if thisLayer not in affectedLayers:
												affectedLayers.append(thisLayer)

			self.w.progress.set(100)
			self.w.status.set("✅ Done.")

			if not affectedLayers:
				Message(title="No Deviances Found", message="No point distances deviating from supplied stem widths within the given limits.", OKButton=None)
			elif self.pref("openTab"):
				tab = thisFont.currentTab
				if not tab or not self.pref("reuseTab"):
					tab = thisFont.newTab()
				tab.layers = affectedLayers
			else:
				# brings macro window to front:
				Glyphs.showMacroWindow()

		except Exception as e:
			# brings macro window to front and reports error:
			Glyphs.showMacroWindow()
			print("Straight Stem Cruncher Error: %s" % e)
			import traceback
			print(traceback.format_exc())


StraightStemCruncher()
