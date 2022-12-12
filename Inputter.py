import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import numpy as np
import os
import sys
from os.path import isfile, join
import re

#TODO:
#Allow user to edit parameters - done
#Allow user to edit existing data - done
#Allow user to delete existing data
#Fix saving
#Make buttons and fields dynamic depending on the number of parameters - done!

#TODO: Pretty sure that if more or less parameters are specified in Labels.txt than .csv, upon loading, it will shit itself

#TODO: Only store new values and modified values in memory

#URGENT:
#Create a functioning scrollbar for this abomination - not urgent anymore
#Make nice padding and stretching and shit

class widget:
    def __init__(self, mainFrame:ttk.Frame, type:str, row:int, column:int, curval, rowID:int, paramID:int, makeempty:bool=False, defvals=[],
                        stylename="Untouched", label="", staticstyle=False, commander=None):
        """Initialise a widget object in a cool way that lets you simultaneously hide or change styles of the entry and label associated with it"""
        self.type = type
        self.row = row
        self.column = column
        self.defvals = defvals
        self.rowID = rowID
        self.paramID = paramID
        self.isdefault = makeempty
        self.stylename = stylename
        self.staticstyle = staticstyle
        self.var = tk.StringVar()
        self.var.set((lambda x: x if not makeempty else "0")(curval))
        self.isHidden:bool = False
        if type == "Label":
            self.label = ttk.Label(mainFrame, textvariable=self.var, style=stylename + ".TLabel")
            self.label.grid(row=row, column=column, sticky=tk.NE)
            self.widget = self.label
            return
        if makeempty and len(defvals) > 0:
            self.var.set(defvals[0])
        if label != "" and type != "Checkbutton":
            self.label = ttk.Label(mainFrame, text=label, style=stylename + ".TLabel")
            self.label.grid(row=row, column=column, sticky=tk.NW)
        elif label == "" or type == "Checkbutton":
            self.label = None
            self.row += row + 1
        if type == "Button":
            self.widget = ttk.Button(mainFrame, text=curval, command=commander, style=stylename + ".TButton")
            self.widget.grid(row=row, column=column, sticky=tk.NW)
            if curval == "X":
                self.widget.configure(command=self.destroya)
        if type == "Entry":
            self.widget = ttk.Entry(mainFrame, width=12, textvariable=self.var, style=self.stylename + ".TEntry")
            self.widget.grid(row=row + 1, column=column, sticky=tk.NW)
            if not staticstyle:
                self.widget.bind("<KeyRelease>", self.checkchangeOnValue)
        elif type == "Combobox":
            self.widget = ttk.Combobox(mainFrame, values=defvals, textvariable=self.var, style=self.stylename + ".TCombobox")
            self.widget['state'] = 'readonly'
            self.widget['values'] = defvals
            self.widget.grid(row=row + 1, column=column, sticky=tk.NW)
            if not staticstyle:
                self.widget.bind('<<ComboboxSelected>>', self.checkchangeOnValue)
        elif type == "Checkbutton":
            if not staticstyle:
                self.widget = ttk.Checkbutton(mainFrame, text=label, variable=self.var, style=self.stylename + ".TCheckbutton", command=self.checkchangeOnClick)
            else:
                self.widget = ttk.Checkbutton(mainFrame, text=label, variable=self.var, style=self.stylename + ".TCheckbutton")
            self.widget.grid(row=row + 1, column=column, sticky=tk.NW)

    def __repr__(self):
        return f"""
        Type: {self.type}
        Row: {self.row}
        Column: {self.column}
        Default Values: {self.defvals}
        Row ID: {self.rowID}
        Parameter ID: {self.paramID}
        Is Default: {self.isdefault}
        Style Name: {self.stylename}
        Static Style: {self.staticstyle}
        Variable: {self.var}
        Is Hidden: {self.isHidden}
        Current value: {self.getVarVal()}
        """
    
    def checkchangeOnValue(self, event):
        global modguestdata
        global guestdata
        global dynamic_UIelems
        global labelz
        global pageref
        global rowstodisplay
        global weekdayz

        widgetindexref = getwidgetindex(dynamic_UIelems, self.getWidget())
        widgetref = dynamic_UIelems[widgetindexref]
        dataindex = pageref * rowstodisplay + widgetindexref // len(labelz)
        
        modguestdata[dataindex][widgetref.getParamID()] = widgetref.getVarVal()

        if dataindex >= len(guestdata):
            """Always return unchanged (Edited)"""
            return True
        elif len(guestdata[dataindex]) <= widgetref.getParamID():
            """Always return unchanged (Edited)"""
            return True
        if guestdata[dataindex][widgetref.getParamID()] != modguestdata[dataindex][widgetref.getParamID()]:
            widgetref.setStyle("Edited")
        else:
            widgetref.setStyle("Untouched")

    def checkchangeOnClick(self):
        global modguestdata
        global guestdata
        global dynamic_UIelems
        global labelz
        global pageref
        global rowstodisplay

        widgetindexref = getwidgetindex(dynamic_UIelems, self.getWidget())
        widgetref = dynamic_UIelems[widgetindexref]
        dataindex = pageref * rowstodisplay + widgetindexref // len(labelz)

        modguestdata[dataindex][widgetref.getParamID()] = widgetref.getVarVal()

        if dataindex >= len(guestdata):
            """Always return unchanged (Edited)"""
            return True
        elif len(guestdata[dataindex]) <= widgetref.getParamID():
            """Always return unchanged (Edited)"""
            return True
        if guestdata[dataindex][widgetref.getParamID()] != modguestdata[dataindex][widgetref.getParamID()]:
            widgetref.setStyle("Edited")
        else:
            widgetref.setStyle("Untouched")

    def destroya(self):
        """Removes selected row from the list"""
        global modguestdata
        global pageref
        global rowstodisplay
        global mainFrame
        global guestdata
        global maxpageStr
        global weekdayz

        #Calculate index to pop from modguestdata
        popindex = pageref * rowstodisplay + self.rowID
        #Store in variable to return data for potential future usecases
        deletedelem = modguestdata.pop(popindex)
        #If not user-created, also delete from guestdata
        if len(guestdata) > popindex:
            guestdata.pop(popindex)

        #If deleting this row would cause the page to be empty, delete last page
        if int(maxpageStr.get().split(' / ')[-1]) - 1 > (len(modguestdata) - 1) // rowstodisplay:
            maxpageStr.set(" / " + str((len(modguestdata) - 1) // rowstodisplay + 1))
            #If user is on last page, go back one page
            if pageref > (len(modguestdata) - 1) // rowstodisplay:
                pageref -= 1

        #Refresh UI
        flipPages(mainFrame, pageref, None)

        return deletedelem

    def setToDefault(self, newStyle="Edited"):
        if len(self.defvals) > 0:
            self.var.set(self.defvals[0])
        elif self['values'] != weekdayz:
            self.var.set("0")
        else:
            self.var.set("Friday")
        self.setStyle(newStyle)
        return self.var.get()

    def getVarVal(self):
        return self.var.get()

    def setVarVal(self, val):
        self.var.set(val)
    
    def getStyle(self):
        return self.stylename
    
    def setStyle(self, stylename):
        self.stylename = stylename
        self.widget.configure(style=self.stylename + ".T" + self.type)
        if self.label is not None:
            self.label.configure(style=stylename + ".TLabel")
    
    def getRow(self):
        return self.row
    
    def getColumn(self):
        return self.column
    
    def setRow(self, row):
        self.row = row
        self.widget.grid(row=row + 1, column=self.column, sticky="w")
        self.label.grid(row=row, column=self.column, sticky="w")
    
    def setColumn(self, column):
        self.column = column
        self.widget.grid(row=self.row + 1, column=column, sticky="w")
        self.label.grid(row=self.row, column=column, sticky="w")
    
    def getLabel(self):
        return self.label
    
    def getWidget(self):
        return self.widget
    
    def getType(self):
        return self.type
    
    def getDefVals(self):
        return self.defvals
    
    def setDefVals(self, defvals):
        self.defvals = defvals
        self.widget['values'] = defvals
    
    def getRowID(self):
        return self.rowID
    
    def getParamID(self):
        return self.paramID

    def hide(self):
        self.widget.grid_remove()
        if self.label is not None:
            self.label.grid_remove()
        self.isHidden = True
    
    def show(self):
        self.widget.grid()
        if self.label is not None:
            self.label.grid()
        self.isHidden = False

    def getisHidden(self):
        return self.isHidden

    def annihilate(self):
        if self.label is not None:
            self.label.destroy()
        self.getWidget().destroy()

class LimitedEntryWidget(widget):
    def __init__(self, mainFrame:ttk.Frame, type:str, row:int, column:int, curval, rowID:int, paramID:int, minrange:int = 0, maxrange:int = float("inf"), allowfloat:bool = False,
                    makeempty:bool=False, defvals=[], stylename="Untouched", label="", staticstyle=False, bindto=""):
        super().__init__(mainFrame, type, row - 1, column, curval, rowID, paramID, makeempty, defvals, stylename, label, staticstyle)
        self.minrange = minrange
        self.maxrange = maxrange
        self.allowfloat = allowfloat
        self.lastval = curval
        self.mainFrameref = mainFrame
        validationcommand = (self.getWidget().register(self.validate), '%P')
        invalidationcommand = (self.getWidget().register(self.on_invalid), '%s')
        self.getWidget().configure(validate='key', validatecommand=validationcommand, invalidcommand=invalidationcommand)
        #I imagine I could just take the function name as parameter but hey, this works
        if (bindto == "pageswitcher"):
            self.getWidget().bind('<KeyRelease>', self.pageswitcher)

    def pageswitcher(self, event):
        global pageref
        global dynamic_UIelems

        pageref = int(self.getVarVal()) - 1
        flipPages(self.mainFrameref, int(self.getVarVal()) - 1, self.getWidget())

    def validate(self, value):
        if len(value) == 0:
            self.lastval = self.getVarVal()
            return True
        if (value[0] == "0" or (not self.allowfloat and not value.isnumeric())):
            return False
        else:
            return int(value) >= self.minrange and int(value) <= self.maxrange

    def on_invalid(self, value):
        self.setVarVal(value)
        return value

    def getVarVal(self):
        if self.var.get() == "":
            return self.lastval
        return self.var.get()

def armageddon(mainFrame:ttk.Frame):
    """Hacker voice: I'm in the mainframe"""
    global dynamic_UIelems
    global labelz
    global rowstodisplay
    global pageref
    global guestdata
    global modguestdata
    global dynamic_buttons

    for i in mainFrame.winfo_children():
        if isinstance(i, ttk.Separator):
            i.destroy()
    for elem in dynamic_UIelems:
        elem.annihilate()

    for possibleplus in dynamic_buttons:
        if possibleplus.getParamID() == -2:
            possibleplus.annihilate()

    guestdata = []
    modguestdata = []
    labelz = []
    dynamic_UIelems = []
    pageref = 0

def appendlabelz():
    """Initialises two more labelz of rowID and the delete button"""
    global labelz

    labelz.append(["entryID", "#", [], "Label"])
    labelz.append(["Delbtn", "X", [], "Button"])

    return 2

def getxtralabelz():
    global labelz

    return labelz[-2:]

def getallwidgetsinrow(row:int):
    global dynamic_UIelems
    global labelz

    return dynamic_UIelems[row * len(labelz) : (row + 1) * len(labelz)]

def retrievevalueatrowandindex(row:int, index:int):
    """New method of value retrieval. Returns a tuple of (value, bool) where the bool indicates whether retrieved value is original or modified during runtime"""
    global guestdata
    global modguestdata

def flipPages(mainFrame, pageindex, instigator):
    global pageref
    global dynamic_UIelems
    global labelz
    global rowstodisplay
    global modguestdata
    global guestdata
    global weekdayz

    if pageindex < 0 or pageindex > len(modguestdata) // rowstodisplay:
        return False

    #If called by pressing buttons, update value held by entry widget
    if instigator is None:
        for widgetelem in defaultBtns:
            if isinstance(widgetelem, LimitedEntryWidget):
                widgetelem.setVarVal(str(pageindex + 1))
        pageref = pageindex


    upper = (pageindex + 1) * rowstodisplay + 1
    if upper > len(modguestdata):
        upper = len(modguestdata)
    rangeref = range(pageindex * rowstodisplay, upper)

    for guestindex in rangeref:
        for widgetref in getallwidgetsinrow(guestindex - pageindex * rowstodisplay):
            if int(widgetref.getParamID()) < 0 and widgetref.getType() == "Label":
                widgetref.setVarVal(f'#{guestindex + 1}')
                continue

            widgetref.setVarVal(modguestdata[guestindex][widgetref.getParamID()])
            #Check if value is part of original guestdata
            if len(guestdata) <= guestindex:
                widgetref.setStyle("Edited")
                continue

            #Check for discrepancy between actual and declared amount of labels
            if len(guestdata[guestindex]) <= widgetref.getParamID():
                widgetref.setStyle("Edited")
                continue

            #Finally check if value has been modified from original
            if guestdata[guestindex][widgetref.getParamID()] != modguestdata[guestindex][widgetref.getParamID()]:
                widgetref.setStyle("Edited")
            else:
                widgetref.setStyle("Untouched")
                
            widgetref.show()

    if (pageindex + 1) * rowstodisplay <= len(modguestdata):
        return True

    for i in range(len(modguestdata) % rowstodisplay, rowstodisplay):
        for widgetref in getallwidgetsinrow(i):
            widgetref.hide()
    return True

def getwidgetbyrowID(rowID:int, widgetlist):
    for i in widgetlist:
        if isinstance(i, widget):
            if i.getRowID() == rowID:
                return i

def addPageSwitches(mainFrame):
    global defaultBtns
    global pageref
    global maxpageStr
    global modguestdata
    global maxcolumns

    maxpageStr.set(" / " + str(len(modguestdata) // rowstodisplay + 1))
    #TODO: Update upper index if more pages are added
    print(mainFrame.grid_size())
    if not any(isinstance(elem, LimitedEntryWidget) for elem in defaultBtns):
        defaultBtns.append(ttk.Label(mainFrame, text="Page: ", style="Plain.TLabel").grid(row=1, column=maxcolumns // 2, sticky=tk.NE))
        defaultBtns.append(ttk.Label(mainFrame, textvariable=maxpageStr, style="Plain.TLabel").grid(row=1, column=maxcolumns // 2 + 2, sticky=tk.NW))
        defaultBtns.append(LimitedEntryWidget(mainFrame, "Entry", 1, maxcolumns // 2 + 1, pageref + 1, -1, -1, stylename="Plain", minrange=1, maxrange=pageref + 1, staticstyle=True, bindto="pageswitcher"))
        defaultBtns.append(ttk.Button(mainFrame, text="<", style="Plain.TLabel", command=lambda: flipPages(mainFrame, pageref - 1, None)).grid(row=2, column=maxcolumns // 2 + 1, sticky=tk.NW))
        defaultBtns.append(ttk.Button(mainFrame, text=">", style="Plain.TLabel", command=lambda: flipPages(mainFrame, pageref + 1, None)).grid(row=2, column=maxcolumns // 2 + 2, sticky=tk.NW))
    else:
        getwidgetbyrowID(-1, defaultBtns).setVarVal(str(pageref + 1))

def getwidgetindex(listr, val):
    for i in listr:
        if i.getWidget() == val:
            return listr.index(i)

def guestrowaddr(*args):
    global modguestdata
    global dynamic_UIelems
    global labelz
    global pageref
    global maxpageStr

    for widgetelemindex in range(0, len(dynamic_UIelems), len(labelz)):
        if not dynamic_UIelems[widgetelemindex].getisHidden():
            continue

        tempmodguestentry = []
        for index, singlewidget in enumerate(dynamic_UIelems[widgetelemindex : widgetelemindex + len(labelz)], start=widgetelemindex):
            singlewidget.show()
            singlewidget.setStyle("Edited")
            if index < widgetelemindex + len(labelz) - len(getxtralabelz()):
                tempmodguestentry.append(singlewidget.setToDefault())
            if singlewidget.getType() == "Label":
                singlewidget.setVarVal(f'#{len(modguestdata) + 1}')
        modguestdata.append(tempmodguestentry)
        return True

    tempmodguestentry = []
    for index, singlewidget in enumerate(dynamic_UIelems[widgetelemindex : widgetelemindex + len(labelz)], start=widgetelemindex):
        singlewidget.show()
        singlewidget.setStyle("Edited")
        if index < widgetelemindex + len(labelz) - len(getxtralabelz()):
            tempmodguestentry.append(singlewidget.setToDefault())
        if singlewidget.getType() == "Label":
            singlewidget.setVarVal(f'#{len(modguestdata) + 1}')
    modguestdata.append(tempmodguestentry)

    maxpageStr.set(" / " + str(len(modguestdata) // rowstodisplay + 1))
    flipPages(mainFrame, pageref + 1, None)
    return True
    print("Go fuck yourself")


def spawnPlusButton(mainFrame, lastrow=True):
    global dynamic_buttons

    #TODO: I think I'm done for the day, continue tomorrow. Coming along nicely, the end is in sight
    if lastrow:
        dynamic_buttons.append(widget(mainFrame, "Button", mainFrame.grid_size()[1] + 2, 0, "+", -2, -2, True, stylename="Plain", staticstyle=True, commander=guestrowaddr))
        #dynamic_buttons.append(ttk.Button())
    
    #Tactical error to get attention    
    return True

defaultBtns = []
filenamer = ""
dynamic_vars = []
"""Dynamically appended variables for guet entries. Stores the ttk.String() in the first dimension and row index in the second"""
dynamic_UIelems = []
"""Dynamically appended UI elements for guest entries. Stores the widget in the first dimension and row index in the second"""
pageref = 0
"""Reference to the current page"""
maxcolumns = 15
"""max amount of columns"""
rowstodisplay = 7
"""For now pre-set value for rows to display upon load per page"""
guestdata = []
"""Use this for all except loading and comparison when saving. Stores raw data for each guest based on .csv vals in a list of lists"""
modguestdata = []
"""Stores modified guestdata, use to check for discrepancies and overwrite when saving to .csv"""
fileref:str = ""
"""Stores the file path of the .csv file currently being operated on"""
dynamic_buttons = []
"""Non-entry widgets, such as buttons"""
#TODO: Store rowstodisplay and maxcolumns in Labels.txt file
#Use labels as reference for what widgets to create
labelz = []
"""A list of lists that rn contains values for [rawname, sanitisedname, values, type] pulled from Labels.txt"""
legal_types = set(["check", "contint", "catint", "date", "dropdown"])
weekdayz = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

def spawnbutton(mainFrame:tk.Frame, type:str, i_ndexr:int, indexer:int, rowref:int, makeempty:bool):
    """Spawns and returns a widget given parameters"""
    global maxcolumns
    global guestdata
    global weekdayz
    global dynamic_UIelems
    global labelz

    tempcurval = 1
    if type == "date" and makeempty:
        tempcurval = weekdayz[4]
    if not makeempty:
        tempcurval = guestdata[indexer][i_ndexr]

    propertype = "Combobox"
    if type == "check":
        propertype = "Checkbutton"
    elif type == "contint" or type == "catint":
        propertype = "Entry"
    elif type == "date":
        propertype = "Combobox"
    
    widgeter = widget(mainFrame, propertype, row = rowref + (i_ndexr // maxcolumns) * 2, column = i_ndexr % maxcolumns, curval = tempcurval,
    rowID = len(dynamic_UIelems) // len(labelz), paramID = i_ndexr, makeempty = makeempty, defvals = (lambda x: labelz[i_ndexr][2] if x != "date" else weekdayz)(type),
    stylename = (lambda x: "Edited" if x else "Untouched")(makeempty), label=labelz[i_ndexr][0])

    print(widgeter)

    return widgeter


#TODO: I done fucked up. Rewrite the whole dynamic UI elems and vars into a class LIKE IT SHOULD HAVE BEEN IN THE FIRST PLACE
#DONE!
def dynamicfields(mainFrame, indexr, makeempty=False):
    """Creates dynamic fields for guest entries. Loops as many times as there are labels in the Labels.txt file and outputs a single editable guest entry"""
    global dynamic_vars
    global dynamic_UIelems
    global labelz
    global guestdata
    global defaultBtns
    global rowstodisplay
    global maxcolumns

    lastrow = 0
    rowref = 0
    thisdata = []
    """List of values for current guest entry"""

    # two additional passes for ID reference and the delete button
    rowref = mainFrame.grid_size()[1] + 1
    dynamic_UIelems.append(widget(mainFrame, "Label", rowref, 0, f"#{indexr + 1}", len(dynamic_UIelems) // len(labelz), -3, False,
                                    stylename="Plain", staticstyle=True))
    dynamic_UIelems.append(widget(mainFrame, "Button", rowref, 1, "X", len(dynamic_UIelems) // len(labelz), -4, True, stylename="Plain", staticstyle=True))
    """Could it get fucky due to rowID being suddenly different for actual guest entries? If only I was more clever to know"""

    for i_ndexr in range(len(labelz) - len(getxtralabelz())):
        """Go through all save the extra labelz"""
        if i_ndexr == 0:
            rowref = mainFrame.grid_size()[1] + 1
        elif not makeempty and len(guestdata) > indexr:
            makeempty = i_ndexr >= len(guestdata[indexr])

        dynamic_UIelems.append(spawnbutton(mainFrame, labelz[i_ndexr][3], i_ndexr, indexr, rowref, makeempty))
        
        thisdata.append(dynamic_UIelems[-1].getVarVal())
        lastrow = rowref + (i_ndexr // maxcolumns) * 2 + 1
    ttk.Separator(mainFrame, orient="horizontal").grid(row=lastrow + 1, column=0, ipadx=1000, columnspan=20)
    return thisdata

#TODO: Check for all kinds of errors as human idiocy knows no limits
#Which is funny, given that I am human too
def sanitise(lineval):
    rawname = ""
    typer = lineval.split(' ')[-1].lower().strip()
    defvals = []
    sanitised_name = ' '.join(lineval.split(' ')[:-1])
    if not set([typer]).intersection(legal_types):
        return ["-1", "", "", ""]
    if typer == "dropdown":
        tempdefvals = lineval.split(' ')[-2]
        for i in tempdefvals.split('-'):
            defvals.append(i)
        rawname = ' '.join(lineval.split(' ')[:-2])
    else:
        rawname = ' '.join(lineval.split(' ')[:-1])

    sanitised_name = rawname.replace(" ", "_")
    sanitised_name = re.sub('[\W]+', '', sanitised_name)
    sanitised_name = re.sub('_*$', '', sanitised_name)
    return [rawname, sanitised_name, defvals, typer]

def producename(reviewz:list[str]) -> str:
    """Returns the name for the next dataset file"""
    files = []
    if getattr(sys, 'frozen', False):
        files = [f for f in os.listdir('\\'.join(sys.executable.split('\\')[:-1])) if isfile(join('\\'.join(sys.executable.split('\\')[:-1]), f))]
    else:
        files = [f for f in os.listdir('\\'.join(os.path.abspath(__file__).split('\\')[:-1])) if isfile(join('\\'.join(os.path.abspath(__file__).split('\\')[:-1]), f))]

    reviewz = []
    for f in files:
        if "ReviewData" in f and not "new" in f:
            reviewz.append(f)

    if len(reviewz) == 0:
        return "ReviewData.csv"
    if len(reviewz) == 1:
        return "ReviewData_1.csv"

    highest = 0
    for f in reviewz:
        if not re.search('_[0-9]+', f.split('\\')[-1].split('.')[0]):
            continue

        if int(f.split('\\')[-1].split('_')[1].split('.')[0]) > highest:
            highest = int(f.split('\\')[-1].split('_')[1].split('.')[0])
    #Return a new filename with the highest number + 1
    return "ReviewData_" + str(highest + 1) + ".csv"

def makenewfile(*args):
    #Make a list of filenames in the current directory
    global filenamer
    global modguestdata
    global fileref
    global pageref
    global dynamic_UIelems
    global guestdata
    global rowstodisplay
    global maxcolumns

    armageddon(mainFrame)

    guestdata = []
    
    newfile = producename()

    if getattr(sys, 'frozen', False):
        newfile = '\\'.join(sys.executable.split('\\')[:-1]) + '\\' + newfile
    else:
        newfile = '\\'.join(os.path.abspath(__file__).split('\\')[:-1]) + '\\' + newfile
    fileref = newfile

    with open(newfile, "w+") as file:
        if getattr(sys, 'frozen', False):
            labelspath = '\\'.join(sys.executable.split('\\')[:-1]) + "\\Labels.txt"
        else:
            labelspath = '\\'.join(os.path.abspath(__file__).split('\\')[:-1]) + "\\Labels.txt"
        if not os.path.isfile(labelspath):
            warnlabel.set("Error! Labels.txt not found")
            return

        templabels = ""
        with open(labelspath, "r") as labelfile:
            for line in labelfile:
                if line[0] == "|":
                    continue
                elif line.startswith("Max rows: "):
                    rowstodisplay = int(line.split(" ")[2])
                    continue
                elif line.startswith("Max columns: "):
                    maxcolumns = int(line.split(" ")[2])
                    continue

                #Checks for illegal data types
                rawname, sanitised_name, defvals, typer = sanitise(line)
                if rawname == "-1":
                    warnlabel.set("Error! Labels.txt file is misconfigured or corrupted!")
                    return
                labelz.append([rawname, sanitised_name, defvals, typer])
                templabels += sanitised_name + ","
        file.write(templabels[:-1] + "\n")
            
    appendlabelz()
    plainname = newfile
    newpathname.set(f"Done! File {plainname} created and preloaded.")
    preloadname.set(newfile)
    doner.set("Awaiting input. . .")
    filenamer = newfile
    modguestdata.append(dynamicfields(mainFrame, len(guestdata), True))
    #Not sure if the math checks out, fucking neighbours screaming above me and I can't hear myself think - I think it does
    for i in range(1, rowstodisplay):
        dynamicfields(mainFrame, i, True)
        for hider in dynamic_UIelems[-len(labelz):]:
            hider.hide()
    pageref = len(modguestdata) // rowstodisplay
    addPageSwitches(mainFrame)
    spawnPlusButton(mainFrame)

def getfile(*args):
    global filenamer 
    global dynamic_vars
    global dynamic_UIelems
    global guestdata
    global modguestdata
    global labelz
    global defaultBtns
    global pageref
    global fileref
    global rowstodisplay
    global maxcolumns
    global weekdayz

    labelspath = ""

    print(sys.executable)

    if getattr(sys, 'frozen', False):
        filenamer = askopenfilename(initialdir=sys.executable)
        filenamer = filenamer.replace('/', '\\')
        print(filenamer)
        labelspath = '\\'.join(sys.executable.split('\\')[:-1]) + "\\Labels.txt"
    else:
        filenamer = askopenfilename(initialdir=os.path.abspath(__file__))
        labelspath = '\\'.join(os.path.abspath(__file__).split('\\')[:-1]) + "\\Labels.txt"

    newfirstline = ""
    #Go through data
    if not re.search('ReviewData.*.csv', filenamer) and os.path.isfile(labelspath):
        preloadname.set("Please select a valid ReviewData file and make sure that Labels.txt file exists.")
        return

    fileref = filenamer
    with open(filenamer, "r") as file:

        armageddon(mainFrame)

        lines = file.readlines()
        #Check if file has entries or just the labels
        if len(lines) <= 1:
            preloadname.set(filenamer)
            doner.set("Awaiting input. . .")
            return

        #Get the labels from Labels.txt file
        templabels = ""
        with open(labelspath, "r") as labelfile:
            for line in labelfile:
                if line[0] == "|":
                    continue
                if line.startswith("Max rows: "):
                    rowstodisplay = int(line.split(" ")[2])
                    continue
                if line.startswith("Max columns: "):
                    maxcolumns = int(line.split(" ")[2])
                    continue
                #Checks for illegal data types
                rawname, sanitised_name, defvals, typer = sanitise(line)
                if rawname == "-1":
                    warnlabel.set("Error! Labels.txt file is misconfigured or corrupted!")
                    return
                labelz.append([rawname, sanitised_name, defvals, typer])
                templabels += sanitised_name + ","
        templabels = templabels[:-1]
        #TODO: Allow auto-fill of missing values based on new ones
        if len(templabels.split(',')) > len(lines[0].split(',')):
            warnlabel.set("Warning! Higher amount of labels in the Labels.txt file than the amount of labels in the ReviewData file!\n" +
            "You will need to manually re-enter the values for previous entries.")
        elif len(templabels.split(',')) < len(lines[0].split(',')):
            warnlabel.set("Warning! Higher amount of labels in the ReviewData file than the amount of labels in the Labels.txt file!\n" +
            "Omitting the extra labels. Please remove extra labels from the ReviewData file or add them to the Labels.txt file.")
        if templabels > lines[0]:
            #If more labels in Labels.txt than .csv, overwrite first line in .csv
            newfirstline = templabels
        for line in range(len(lines) - 1):
            #Iterate through each value in the line and append guestdata
            templist = []
            uberlist = []
            #Ugly workaround to transform int to weekdays. When I actually implement calendars, remove this
            for index, elem in enumerate(lines[line + 1].split(',')):
                elem = elem.strip()
                if labelz[index][3] == "date":
                    templist.append(weekdayz[int(elem)])
                    uberlist.append(weekdayz[int(elem)])
                else:
                    templist.append(elem)
                    uberlist.append(elem)
            if len(templist) < len(labelz):
                for i in range(len(labelz) - len(templist[-1])):
                    uberlist.append("0")
            guestdata.append(templist)
            modguestdata.append(uberlist)
        appendlabelz()
        #Calculate the widgets for last page
        #Fuck.
        #The way widgets are created. It creates 20 of the fuckers and then when switching pages
        #FUCK
        #Can I just hide them - YES!
        lastpagefirstindex = ((len(guestdata) + 1) // rowstodisplay) * rowstodisplay
        for i in range(lastpagefirstindex, len(guestdata)):
            #dynamic_UIelems.append(widget(mainFrame, guestdata.index(guestdata[i])))
            dynamicfields(mainFrame, guestdata.index(guestdata[i]))
        modguestdata.append(dynamicfields(mainFrame, len(guestdata), True))
        #Not sure if the math checks out, fucking neighbours screaming above me and I can't hear myself think - I think it does
        for i in range(len(modguestdata) - lastpagefirstindex, rowstodisplay):
            dynamicfields(mainFrame, i, True)
            for hider in dynamic_UIelems[-len(labelz):]:
                hider.hide()
        pageref = len(modguestdata) // rowstodisplay
        preloadname.set(filenamer)
        doner.set("Awaiting input. . .")

    if newfirstline != "":
        with open(filenamer, "r+") as file:
            lines = file.readlines()
            lines[0] = newfirstline + "\n"
            file.seek(0)
            file.writelines(lines)
    addPageSwitches(mainFrame)
    spawnPlusButton(mainFrame)


def saveData(*args):
    global filenamer
    global modguestdata
    global labelz
    global doner
    global weekdayz
    modcopy = modguestdata.copy()
    if re.search('ReviewData.*.csv', filenamer):
        tempnamer = filenamer
        print(tempnamer)
        if not filenamer.endswith("_new.csv"):
            if getattr(sys, 'frozen', False):
                tempnamer = filenamer.split('\\')[-1].split('.')[0] + "_new." + filenamer.split('\\')[-1].split('.')[1]
                print(tempnamer)
            else:
                tempnamer = filenamer.split('\\')[-1].split('.')[0] + "_new." + filenamer.split('\\')[-1].split('.')[1]
        with open(tempnamer, "w+") as newfile:
            firstline = ""
            #More date bodging. I'm so sorry to my future self
            for label in labelz[:-len(getxtralabelz())]:
                firstline += label[1] + ","
            newfile.write(firstline[:-1] + "\n")
            for entry in modcopy:
                fuckingshit = ','.join(entry) + '\n'
                for id, cunt in enumerate(weekdayz):
                    fuckingshit = fuckingshit.replace(cunt, str(id))
                newfile.write(fuckingshit)

        doner.set("Success. Data saved to " + tempnamer)
    else:
        doner.set("Error! Please select a valid file. If you don't have one, click 'Create new file' first.")

MainWindow = tk.Tk()
MainWindow.title("Data Inputter")

PlainFrameStyle = ttk.Style()

plainbgcolour = "#01081A"

PlainFrameStyle.configure("Plain.TFrame", background=plainbgcolour) #01081A

mainFrame = ttk.Frame(MainWindow, padding="3 3 12 12", style="Plain.TFrame")
mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

maxpageStr = tk.StringVar()
"""Stores the max page value for the label"""

toAffectbyStyles = ["TCheckbutton", "TCombobox", "TEntry", "TLabel", "TLabelFrame", "TButton"]
UntouchedStylez:ttk.Style = []
"""Contains unedited styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""
#UntouchedStylez.configure("Untouched", background="#7DFFBB", foreground="#7DFFBB")
EditedStylez:ttk.Style = []
"""Contains edited styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""
PlainStylez:ttk.Style = []
"""Contains plain styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""
#EditedStylez.configure("Edited", background="#7D80FF", foreground="#7D80FF")
temper = ttk.Style()
temper.element_create("plain.field", "from", "default")

def initstyles(stylestoAffect:list[str], uneditedstyles:list[ttk.Style], editedstyles:list[ttk.Style], plainstyles:list[ttk.Style]):
    for i in stylestoAffect:
        tempuntouched = ttk.Style()
        tempedited = ttk.Style()
        tempplain = ttk.Style()
        if i == "TCombobox" or i == "TEntry":
            #"Remakes" the nasty boxes that don't, by default, allow for background colour filling
            #This is terrifying but works. Thanks, Firnagzen at StackOverflow!
            #Note: Could use some tinkering with as the background colour where the modified text is defaults to white lmfao
            tempuntouched.layout(f"Untouched.{i}", 
                                    [(f"{i[1:]}.plain.field", {"children": [(
                                        f"{i[1:]}.background", {"children": [(
                                            f"{i[1:]}.padding", {"children": [(
                                                f"{i[1:]}.textarea", {"sticky": "nwse"})], "sticky": "nswe"})], "sticky": "nswe"})], "border": "2", "sticky": "nswe"})])

            tempedited.layout(f"Edited.{i}", 
                                    [(f"{i[1:]}.plain.field", {"children": [(
                                        f"{i[1:]}.background", {"children": [(
                                            f"{i[1:]}.padding", {"children": [(
                                                f"{i[1:]}.textarea", {"sticky": "nwse"})], "sticky": "nswe"})], "sticky": "nswe"})], "border": "2", "sticky": "nswe"})])
            
            tempplain.layout(f"Plain.{i}", 
                                    [(f"{i[1:]}.plain.field", {"children": [(
                                        f"{i[1:]}.background", {"children": [(
                                            f"{i[1:]}.padding", {"children": [(
                                                f"{i[1:]}.textarea", {"sticky": "nwse"})], "sticky": "nswe"})], "sticky": "nswe"})], "border": "2", "sticky": "nswe"})])
        if i == "TLabel":
            tempuntouched.configure(f"Untouched.{i}", background=plainbgcolour, fieldbackground=plainbgcolour,  foreground="#A1A5A3")
            tempedited.configure(f"Edited.{i}", background=plainbgcolour, fieldbackground=plainbgcolour, foreground="#A2A1A5")
            tempplain.configure(f"Plain.{i}", background=plainbgcolour, fieldbackground=plainbgcolour, foreground="#A1A2A5")
        else:
            tempuntouched.configure(f"Untouched.{i}", background="#054423", fieldbackground="#054423", selectbackground="#054423", foreground="#A1A5A3")
            tempedited.configure(f"Edited.{i}", background="#2E0C7B", fieldbackground="#2E0C7B", selectbackground="#2E0C7B",foreground="#A2A1A5")
            tempplain.configure(f"Plain.{i}", background="#0D1B42", fieldbackground="#0D1B42", selectbackground="#0D1B42",foreground="#A1A2A5")
        uneditedstyles.append(tempuntouched)
        editedstyles.append(tempedited)
        plainstyles.append(tempplain)
    return uneditedstyles, editedstyles, plainstyles

UntouchedStylez, EditedStylez, PlainStylez = initstyles(toAffectbyStyles, UntouchedStylez, EditedStylez, PlainStylez)

MainWindow.columnconfigure(0, weight=1)
MainWindow.rowconfigure(0, weight=1)

#TXDX: Refactor all the buttons - DONE!

defaultBtns.append(ttk.Button(mainFrame, text="Make new file", command=makenewfile, style="Plain.TButton"))
defaultBtns[-1].grid(column=0, row=0, sticky=(tk.SW))

newpathname = tk.StringVar()
defaultBtns.append(ttk.Label(mainFrame, textvariable=newpathname, style="PLain.TLabel").grid(column=1, row=0, sticky=(tk.SW), columnspan=9))

defaultBtns.append(ttk.Button(mainFrame, text="Select file to append", command=getfile, style="Plain.TButton"))
defaultBtns[-1].grid(column=0, row=1, sticky=(tk.SW))

preloadname = tk.StringVar()
defaultBtns.append(ttk.Label(mainFrame, text="Preloaded: ", style="Plain.TLabel").grid(column=1, row=1, sticky=(tk.SW)))
defaultBtns.append(ttk.Label(mainFrame, textvariable=preloadname, style="Plain.TLabel").grid(column=2, row=1, sticky=(tk.SW), columnspan=9))

warnlabel = tk.StringVar()
defaultBtns.append(ttk.Label(mainFrame, textvariable=warnlabel, style="Plain.TLabel").grid(column=2, row=1, sticky=(tk.SW), columnspan=9))

defaultBtns.append(ttk.Button(mainFrame, text="Save", command=saveData, style="Plain.TButton").grid(column=0, row=2, sticky=tk.SW, columnspan=9))
doner = tk.StringVar()
doner.set("Awaiting input. . .")
defaultBtns.append(ttk.Label(mainFrame, textvariable=doner, style="Plain.TLabel").grid(column=0, row=3, sticky=(tk.SW), columnspan=9))

MainWindow.bind('<Return>', saveData)
MainWindow.mainloop()
