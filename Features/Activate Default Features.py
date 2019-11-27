#MenuTitle: Activate Default Features
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
try:
	from builtins import str
except Exception as e:
	print("Warning: 'future' module not installed. Run 'sudo pip install future' in Terminal.")

__doc__="""
In the current Edit tab, activates all OT features that should be on by default.
"""

defaultFeatures = """
abvf
abvm
abvs
akhn
blwf
blwm
blws
calt
ccmp
cfar
cjct
clig
cpsp
curs
dist
fin2
fin3
fina
half
haln
init
isol
kern
liga
ljmo
locl
lfbd
mark
med2
medi
mkmk
nukt
opbd
pref
pres
pstf
psts
rclt
rlig
rkrf
rphf
stch
tjmo
vjmo
ltra
ltrm
rtla
rtlm
valt
vrt2
dtls
flac
ssty
"""

thisFont = Glyphs.font # frontmost font
defaultFeatures = defaultFeatures.strip().splitlines()
availableDefaultFeatures = [f.name for f in thisFont.features if f.name in defaultFeatures]

editTab = Glyphs.currentDocument.windowController().activeEditViewController()
for featureName in availableDefaultFeatures:
	if not featureName in editTab.selectedFeatures():
		editTab.selectedFeatures().append(featureName)

editTab.graphicView().reflow()
editTab._updateFeaturePopup()
