from Hotelprophet import getModel
import tkinter as tk
from tkinter import ttk
from tkinter.filedialog import askopenfilename
import os
import sys
import numpy as np
import pandas as pd
import statistics
import re
from datetime import datetime

legal_types = set(["check", "contint", "catint", "date", "dropdown"])
filenamer = ""
datalists = []
dynamic_vars = []
dynamic_UIelems = []
model = None
correlations = 0
scalar = None

def dynamicfields(mainFrame):
    global dynamic_vars
    global dynamic_UIelems
    global datalists
    for i in range(len(datalists)):
        if datalists[i][3] == "dropdown":
            ttk.Label(mainFrame, text=datalists[i][0], style="Plain.TLabel").grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2, sticky=tk.W)
            dynamic_vars.append(tk.StringVar())
            dynamic_UIelems.append(ttk.Combobox(mainFrame, width=12, textvariable=dynamic_vars[-1], style="Plain.TCombobox"))
            dynamic_UIelems[-1]['values'] = datalists[i][2]
            dynamic_UIelems[-1].grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2 + 1, sticky=tk.W)
            dynamic_vars[-1].set(datalists[i][2][0])
        elif datalists[i][3] == "check":
            dynamic_vars.append(tk.StringVar())
            dynamic_UIelems.append(ttk.Checkbutton(mainFrame, text=datalists[i][0], variable=dynamic_vars[-1], style="Plain.TCheckbutton"))
            dynamic_UIelems[-1].grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2 + 1, sticky=tk.W)
            dynamic_vars[-1].set("0")
        elif datalists[i][3] == "contint":
            dynamic_vars.append(tk.StringVar())
            ttk.Label(mainFrame, text=datalists[i][0], style="Plain.TLabel").grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2, sticky=tk.W)
            dynamic_UIelems.append(ttk.Entry(mainFrame, width=12, textvariable=dynamic_vars[-1], style="Plain.TEntry"))
            dynamic_UIelems[-1].grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2 + 1, sticky=tk.W)
            dynamic_vars[-1].set("0")
        #Cat and cont are the same for now
        elif datalists[i][3] == "catint":
            dynamic_vars.append(tk.StringVar())
            ttk.Label(mainFrame, text=datalists[i][0], style="Plain.TLabel").grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2, sticky=tk.W)
            dynamic_UIelems.append(ttk.Entry(mainFrame, width=12, textvariable=dynamic_vars[-1], style="Plain.TEntry"))
            dynamic_UIelems[-1].grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2 + 1, sticky=tk.W)
            dynamic_vars[-1].set("0")
        #Just a text box for now
        elif datalists[i][3] == "date":
            dynamic_vars.append(tk.StringVar())
            ttk.Label(mainFrame, text=datalists[i][0], style="Plain.TLabel").grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2, sticky=tk.W)
            dynamic_UIelems.append(ttk.Entry(mainFrame, width=12, textvariable=dynamic_vars[-1], style="Plain.TEntry"))
            dynamic_UIelems[-1].grid(row=(i) // 9 + 1, column=((i + 1) % 9) * 2 + 1, sticky=tk.W)
            dynamic_vars[-1].set("dd/mm/yyyy")

def sanitise(lineval):
    global legal_types
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

def getfile(*args):
    global filenamer 
    if getattr(sys, 'frozen', False):
        filenamer = askopenfilename(initialdir=sys.executable)
        filenamer = filenamer.replace("/", "\\")
    else:
        filenamer = askopenfilename(initialdir=os.path.abspath(__file__))
    preloadname.set(filenamer)
    #Find file and check validity
    if not re.search('ReviewData.*.csv', filenamer):
        preloadname.set("Please select a valid ReviewData file by clicking \"Select data to train\"")
        return

    outputText.set("File loaded. Please enter data to predict.")
    labelspath = ""
    if getattr(sys, 'frozen', False):
        labelspath = '\\'.join(sys.executable.split('\\')[:-1]) + "\\LabelsToTrain.txt"
    else:
        labelspath = '\\'.join(os.path.abspath(__file__).split('\\')[:-1]) + "\\LabelsToTrain.txt"
    print(labelspath)
    #Check for existence of labels to train - process if exists
    if not os.path.isfile(labelspath):
        preloadname.set("No label file found. Please create a LabelsToTrain.txt file in the same directory as Predictor.")
        return

    with open(labelspath, "r") as labelsfile:
        lines = labelsfile.readlines()
        for i in range(len(lines)):
            if lines[i][0] != "|":
                rawname, sanitised_name, defvals, typer = sanitise(lines[i])
                if rawname != "-1":
                    datalists.append([rawname, sanitised_name, defvals, typer])
                else:
                    preloadname.set("Invalid labels file. Please check the format.")
                    return
    print("Adding fields")
    dynamicfields(mainFrame)

def predictrating(*args):
    global datalists
    global dynamic_vars
    global model
    global correlations
    global scalar

    try:
        params = []
        paramsnames = []
        for i in range(len(datalists)):
            if datalists[i][3] == "date":
                tempdate = datetime.strptime(dynamic_vars[i].get(), "%d/%m/%Y")
                params.append(int(tempdate.weekday()))
                paramsnames.append(datalists[i][1])
            else:
                params.append(int(dynamic_vars[i].get()))
                paramsnames.append(datalists[i][1])

        data = np.array([i for i in params]).reshape(1, -1)
        reviewz = []

        if not re.search('ReviewData.*.csv', filenamer):
            outputText.set("No prediction made. Please select a valid ReviewData file by clicking \"Select data to train\"")
            return

        """
        correlations = getModel(filenamer, paramsnames)[1]
        for i in range(0, 20):
            tempmodel, _ = getModel(filenamer, paramsnames)
            temprev = tempmodel.predict(data)
            if temprev > 10:
                reviewz.append(10)
            elif temprev < 0:
                reviewz.append(0)
            else:
                reviewz.append(temprev[0])
        """
        if model is None:
            model, correlations, scalar = getModel(filenamer, paramsnames)
        readieddata = scalar.transform(data)
        temprev = model.predict(readieddata)
        print("rev ready")
        print(temprev)
        reviewz = temprev
        revstr = ""
        for i in range(10):
            revstr += f"{i+1}: " + str(round(temprev[0][i] * 100, 2)) + "%\n"
        #outputText.set(f"{round(min(reviewz), 1)} - {round(max(reviewz), 1)}; Mean guess: {round((sum(reviewz) / len(reviewz)), 1)}, Median guess: {round(statistics.median(reviewz), 1)}")
        #outputText.set(f"{np.round(min(reviewz), decimals=1)} - {np.round(max(reviewz), 1)}; Mean guess: {np.round((sum(reviewz) / len(reviewz)), 1)}, Median guess: {np.round(statistics.median(reviewz), 1)}")
        outputText.set(f"{revstr}")
        mini:pd.Series = correlations.iloc[1:4]
        mini = mini.append(correlations.iloc[-3:])
        advisor = ""
        #TODO: Let user specify parameters to ignore when generating advice
        #print(mini)
        for label, value in mini.items():
            value = round(value, 2)
            temper = label.replace("_", " ")
            if value > 0.5:
                advisor += f"There appears to be a noticeable positive correlation ({value}) between \"{temper}\" and rating.\n\n"
            elif value > 0:
                advisor += f"There appears to be a minor positive correlation ({value}) between \"{temper}\" and rating.\n\n"
            elif value < -0.5:
                advisor += f"There appears to be a noticeable negative correlation ({value}) between \"{temper}\" and rating.\n\n"
            elif value < 0:
                advisor += f"There appears to be a minor negative correlation ({value}) between \"{temper}\" and rating.\n\n"
        advisor += "To improve chances of higher score, consider the parameters that have a positive correlation.\n" +\
        "Try to offer these services, or more of them, if you can.\nConsider the parameters with a negative correlation as well: try to minimise the chances of the stated " +\
            "parameters being experienced by the client as that is likely to lower the score.\n"
        advisorText.set(advisor)


    except ValueError as x:
        outputText.set("Please enter a valid number")
        print("Please enter a valid number")
        print(x)
        print(type(x))
        print(x.args)
        argz = x.args
        print(argz[0])

MainWindow = tk.Tk()
MainWindow.title("Rating Predictor")

plainbgcolour = "#01081A"

PlainFrameStyle = ttk.Style()

PlainFrameStyle.configure("Plain.TFrame", background=plainbgcolour)

mainFrame = ttk.Frame(MainWindow, padding="3 3 12 12", style="Plain.TFrame")
mainFrame.grid(column=0, row=0, sticky=(tk.N, tk.W, tk.E, tk.S))

MainWindow.columnconfigure(0, weight=1)
MainWindow.rowconfigure(0, weight=1)

toAffectbyStyles = ["TCheckbutton", "TCombobox", "TEntry", "TLabel", "TLabelFrame", "TButton"]
UntouchedStylez:ttk.Style = []
"""Contains unedited styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""
#UntouchedStylez.configure("Untouched", background="#7DFFBB", foreground="#7DFFBB")
EditedStylez:ttk.Style = []
"""Contains edited styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""
PlainStylez:ttk.Style = []
"""Contains plain styles for (in order): CheckButton, ComboBox, Entry, Label, LabelFrame, Button"""

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
        elif i == "TLabel":
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

outputText = tk.StringVar()
outputText.set("awaiting input. . .")
ttk.Label(mainFrame, textvariable=outputText, style="Plain.TLabel").grid(column=2, row=6, sticky=(tk.W, tk.E), columnspan=9)

pathBtn = ttk.Button(mainFrame, text="Select data to train", command=getfile)
pathBtn.grid(column=1, row=3, sticky=(tk.W, tk.E))

preloadname = tk.StringVar()
ttk.Label(mainFrame, text="Preloaded: ", style="Plain.TLabel").grid(column=2, row=3, sticky=(tk.W))
ttk.Label(mainFrame, textvariable=preloadname, style="Plain.TLabel").grid(column=3, row=3, sticky=(tk.W), columnspan=9)

advisorText = tk.StringVar()
ttk.Label(mainFrame, textvariable=advisorText, style="Plain.TLabel").grid(column=1, row=7, sticky=(tk.W, tk.E), columnspan=9)

"""
ttk.Label(mainFrame, text="Staying nights").grid(column=1, row=2, sticky=(tk.W))
ttk.Label(mainFrame, text="Check-in day").grid(column=2, row=2, sticky=(tk.W))
ttk.Label(mainFrame, text="Rooms booked").grid(column=3, row=2, sticky=(tk.W))
ttk.Label(mainFrame, text="Predicted rating: ").grid(column=1, row=6, sticky=(tk.W))
"""

ttk.Button(mainFrame, text="Predict", command=predictrating, style="Plain.TButton").grid(column=1, row=5, sticky=(tk.W))

MainWindow.bind('<Return>', predictrating)
MainWindow.mainloop()