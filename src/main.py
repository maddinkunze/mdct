import tkinter as tk
from tkinter.filedialog import askopenfilename, asksaveasfilename, askdirectory
from tkinter.scrolledtext import ScrolledText
import os
import shutil
import json
import copy
from functions import hoverCreateFunctions, buttonsCreate, widgetsPlace, widgetsSetHoverFunctions, widgetsSetStyle, \
    dataStandardGet, dataStandardGetEnvironment, dataStandardGetEnvironmentNames, dataStandardGetEnvironmentTypes, \
    colorCodesCreate, getTkinterImage, dataStandardGetObject, dataStandardGetObjectTypes, dataStandardGetObjectNames,\
    drawRect3D, drawVector3D, drawLine3D, drawCircle3D, getFromObj, getEvalFromObj


class Program:
    def __init__(self, onclose=None):
        self._init_styles()

        # --------------------- #
        # ----- Standards ----- #
        # --------------------- #

        self.environmentsOptionsPasses = ["Combined", "Environment", "Shadow", "Ambient Occlusion", "Specular Light", "Bloom"]
        self.environmentsOptionsCompositorPresets = ["Maddins Compositor v1"]

        # ------------------ #
        # ----- Window ----- #
        # ------------------ #

        self.window = tk.Tk()
        self.window.geometry("1300x700")
        self.window.configure(self.styleWindow)
        self.window.resizable(False, False)
        self.window.iconbitmap('templates/mdct.ico')

        self.window.bind("<Control-n>", lambda _: self.clickStartFile("New"))
        self.window.bind("<Control-o>", lambda _: self.clickStartFile("Open"))
        self.window.bind("<Control-r>", lambda _: self.clickStartFile("Reload"))
        self.window.bind("<Control-s>", lambda _: self.clickStartFile("Save"))
        self.window.bind("<Control-Shift-S>", lambda _: self.clickStartFile("Save As"))
        self.window.bind("<Control-e>", lambda _: self.clickStartFile("Export"))

        # ---------------- #
        # ----- Menu ----- #
        # ---------------- #

        self.frameMenu = tk.Frame(self.window)

        self.buttonsMenu = buttonsCreate(self.frameMenu, ["Start", "Environments", "Objects"], self.clickMenu)
        self.indicatorMenuTab = tk.Frame(self.frameMenu)

        widgetsSetStyle(self.buttonsMenu.values(), self.styleButtonMenu)
        self.indicatorMenuTab.configure(self.styleIndicatorMenu)

        widgetsPlace(self.buttonsMenu.values(), 10, 10, 200, 50, 10)
        widgetsSetHoverFunctions(self.buttonsMenu.values(), self.hoverButtonMenu)

        self.frameMenu.configure(self.styleFrameMenu)
        self.frameMenu.place(x=0, y=0, width=1300, height=70)

        # ----------------- #
        # ----- Start ----- #
        # ----------------- #

        self.frameStart = tk.Frame(self.window)
        self.frameStart.configure(self.styleFrameTab)

        self.frameStartFile = tk.Frame(self.frameStart)
        self.frameStartFile.configure(self.styleFrameOptions)
        self.frameStartFile.place(x=10, y=10, width=110 + 2 * 10, height=6*50+10)

        self.buttonsStart = buttonsCreate(self.frameStartFile, ["New", "Open", "Reload", "Save", "Save As", "Export"], self.clickStartFile)

        widgetsSetStyle(self.buttonsStart.values(), self.styleButtonStd)
        widgetsPlace(self.buttonsStart.values(), 10, 10, 110, 40, 10, "VERTICAL")
        widgetsSetHoverFunctions(self.buttonsStart.values(), self.hoverButtonStd)

        # ------------------------ #
        # ----- Environments ----- #
        # ------------------------ #

        self.frameEnvironments = tk.Frame(self.window)
        self.frameEnvironments.configure(self.styleFrameTab)

        self.frameEnvironmentsElementsContainer = ScrollFrame(self.frameEnvironments)
        self.frameEnvironmentsElementsContainer.configure(self.styleFrameOptions)
        self.frameEnvironmentsElementsContainer.place(x=10, y=10, width=1300-300-3*10, height=630-2*10)
        self.frameEnvironmentsElements = self.frameEnvironmentsElementsContainer.frame

        self.labelEnvironmentsElements = tk.Label(self.frameEnvironmentsElements, text="List of all Environments")
        self.labelEnvironmentsElements.configure(self.styleLabelHeading)
        self.labelEnvironmentsElements.place(x=10, y=10, width=1300-300-5*10-10)

        self.buttonEnvironmentsElementsAdd = tk.Button(self.frameEnvironmentsElements, text="+", command=self.clickAddEnvironment)
        self.buttonEnvironmentsElementsAdd.configure(self.styleButtonEnvAdd)
        widgetsSetHoverFunctions([self.buttonEnvironmentsElementsAdd], self.hoverButtonStd)

        self.buttonsEnvironmentsElements = []

        # ------------------------------------------------ #

        self.frameEnvironmentsOptionsContainer = ScrollFrame(self.frameEnvironments)
        self.frameEnvironmentsOptionsContainer.configure(self.styleFrameOptions)
        self.frameEnvironmentsOptionsContainer.place(x=1300-300-10, y=10, width=300, height=630-2*10)
        self.frameEnvironmentsOptionsContainer.strength = 0.5
        self.frameEnvironmentsOptionsContainer.height(830)

        self.frameEnvironmentsOptions = self.frameEnvironmentsOptionsContainer.frame

        self.labelEnvironmentsOptions = tk.Label(self.frameEnvironmentsOptions, text="General Options")
        self.labelEnvironmentsOptions.configure(self.styleLabelHeading)
        self.labelEnvironmentsOptions.place(x=10, y=10, width=280)

        self.labelEnvironmentsOptionsVariables = tk.Label(self.frameEnvironmentsOptions, text="Variables")
        self.labelEnvironmentsOptionsVariables.configure(self.styleLabelStd)
        self.labelEnvironmentsOptionsVariables.place(x=10, y=50)

        self.labelEnvironmentsOptionsVariablesHelp = tk.Label(self.frameEnvironmentsOptions, text="?")
        self.labelEnvironmentsOptionsVariablesHelp.configure(self.styleLabelHelp)
        self.labelEnvironmentsOptionsVariablesHelp.place(x=130, y=55)

        self.buttonsEnvironmentOpionsVariables = buttonsCreate(self.frameEnvironmentsOptions, ["+", "-", "❏", "✎"], self.clickEnvOptionsVariables)
        widgetsSetStyle(self.buttonsEnvironmentOpionsVariables.values(), self.styleButtonStd)
        widgetsSetHoverFunctions(self.buttonsEnvironmentOpionsVariables.values(), self.hoverButtonStd)
        widgetsPlace(self.buttonsEnvironmentOpionsVariables.values(), 300 - 4 * (24 + 6) - 4, 52, 24, 24, 6)

        self.lboxEnvironmentsOptionsVariables = tk.Listbox(self.frameEnvironmentsOptions)
        self.lboxEnvironmentsOptionsVariables.bind('<<ListboxSelect>>', self.updateEnvVariables)
        self.lboxEnvironmentsOptionsVariables.configure(self.styleListBoxStd)
        self.lboxEnvironmentsOptionsVariables.place(x=10, y=80, width=280, height=160)

        self.labelEnvironmentsOptionsVariableExpression = tk.Label(self.frameEnvironmentsOptions, text="Expression:")
        self.labelEnvironmentsOptionsVariableExpression.configure(self.styleLabelSmall)
        self.labelEnvironmentsOptionsVariableExpression.place(x=10, y=250, height=20)

        self.entryEnvironmentsOptionsVariableExpression = tk.Entry(self.frameEnvironmentsOptions)
        self.entryEnvironmentsOptionsVariableExpression.configure(self.styleEntryDriver)
        self.entryEnvironmentsOptionsVariableExpression.bind("<Return>", self.updateEnvVariableExpression)
        self.entryEnvironmentsOptionsVariableExpression.place(x=85, y=250, width=170, height=20)

        self.buttonEnvironmentsOptionsVariableExpression = tk.Button(self.frameEnvironmentsOptions, text="Ok", command=self.updateEnvVariableExpression)
        self.buttonEnvironmentsOptionsVariableExpression.configure(self.styleButtonSmall)
        self.buttonEnvironmentsOptionsVariableExpression.place(x=260, y=250, width=30, height=20)
        widgetsSetHoverFunctions([self.buttonEnvironmentsOptionsVariableExpression], self.hoverButtonStd)

        # ------------------------------------------------------ #
        self.separatorEnvironmentsOptionsLayers = tk.Frame(self.frameEnvironmentsOptions)
        self.separatorEnvironmentsOptionsLayers.configure(self.styleSeparatorStd)
        self.separatorEnvironmentsOptionsLayers.place(x=5, y=293, width=290, height=2)
        # ------------------------------------------------------ #

        self.labelEnvironmentsOptionsLayers = tk.Label(self.frameEnvironmentsOptions, text="View Layers")
        self.labelEnvironmentsOptionsLayers.configure(self.styleLabelStd)
        self.labelEnvironmentsOptionsLayers.place(x=10, y=300)

        self.labelEnvironmentsOptionsLayersHelp = tk.Label(self.frameEnvironmentsOptions, text="?")
        self.labelEnvironmentsOptionsLayersHelp.configure(self.styleLabelHelp)
        self.labelEnvironmentsOptionsLayersHelp.place(x=130, y=305)

        self.buttonsEnvironmentOpionsLayers = buttonsCreate(self.frameEnvironmentsOptions, ["+", "-", "❏", "✎"], self.clickEnvOptionsLayers)
        widgetsSetStyle(self.buttonsEnvironmentOpionsLayers.values(), self.styleButtonStd)
        widgetsSetHoverFunctions(self.buttonsEnvironmentOpionsLayers.values(), self.hoverButtonStd)
        widgetsPlace(self.buttonsEnvironmentOpionsLayers.values(), 300-4*(24+6)-4, 302, 24, 24, 6)

        self.lboxEnvironmentsOptionsLayers = tk.Listbox(self.frameEnvironmentsOptions)
        self.lboxEnvironmentsOptionsLayers.bind('<<ListboxSelect>>', self.updateEnvLayers)
        self.lboxEnvironmentsOptionsLayers.configure(self.styleListBoxStd)
        self.lboxEnvironmentsOptionsLayers.place(x=10, y=330, width=280, height=160)

        self.menuEnvironmentsOptionsLayerPasses = SelectionMenuCheck(self.frameEnvironmentsOptions, text="View Layer Passes ▼")
        self.menuEnvironmentsOptionsLayerPasses.set_styles(self.styleButtonMenuStd, self.styleMenuStd)
        self.menuEnvironmentsOptionsLayerPasses.place(x=10, y=500)

        # ------------------------------------------------------ #
        self.separatorEnvironmentsOptionsLayers = tk.Frame(self.frameEnvironmentsOptions)
        self.separatorEnvironmentsOptionsLayers.configure(self.styleSeparatorStd)
        self.separatorEnvironmentsOptionsLayers.place(x=5, y=543, width=290, height=2)
        # ------------------------------------------------------ #

        self.labelEnvironmentsOptionsCollections = tk.Label(self.frameEnvironmentsOptions, text="Collections")
        self.labelEnvironmentsOptionsCollections.configure(self.styleLabelStd)
        self.labelEnvironmentsOptionsCollections.place(x=10, y=550)

        self.labelEnvironmentsOptionsCollectionsHelp = tk.Label(self.frameEnvironmentsOptions, text="?")
        self.labelEnvironmentsOptionsCollectionsHelp.configure(self.styleLabelHelp)
        self.labelEnvironmentsOptionsCollectionsHelp.place(x=130, y=555)

        self.buttonsEnvironmentOpionsCollections = buttonsCreate(self.frameEnvironmentsOptions, ["+", "-", "❏", "✎"], self.clickEnvOptionsCollections)
        widgetsSetStyle(self.buttonsEnvironmentOpionsCollections.values(), self.styleButtonStd)
        widgetsSetHoverFunctions(self.buttonsEnvironmentOpionsCollections.values(), self.hoverButtonStd)
        widgetsPlace(self.buttonsEnvironmentOpionsCollections.values(), 300-4*(24+6)-4, 552, 24, 24, 6)

        self.lboxEnvironmentsOptionsCollections = tk.Listbox(self.frameEnvironmentsOptions)
        self.lboxEnvironmentsOptionsCollections.bind('<<ListboxSelect>>', self.updateEnvCollections)
        self.lboxEnvironmentsOptionsCollections.configure(self.styleListBoxStd)
        self.lboxEnvironmentsOptionsCollections.place(x=10, y=580, width=280, height=200)

        self.menuEnvironmentsOptionsCollectionLayers = SelectionMenuCheck(self.frameEnvironmentsOptions, text="Collection View Layers ▼")
        self.menuEnvironmentsOptionsCollectionLayers.set_styles(self.styleButtonMenuStd, self.styleMenuStd)
        self.menuEnvironmentsOptionsCollectionLayers.place(x=10, y=790)

        # ------------------- #
        # ----- Objects ----- #
        # ------------------- #

        self.frameObjects = tk.Frame(self.window)
        self.frameObjects.configure(self.styleFrameTab)

        self.frameObjectsElementsContainer = ScrollFrame(self.frameObjects)
        self.frameObjectsElementsContainer.configure(self.styleFrameOptions)
        self.frameObjectsElementsContainer.place(x=10, y=10, width=1300 - 300 - 3 * 10, height=630 - 2 * 10)
        self.frameObjectsElements = self.frameObjectsElementsContainer.frame

        self.labelObjectsElements = tk.Label(self.frameObjectsElements, text="List of all Objects")
        self.labelObjectsElements.configure(self.styleLabelHeading)
        self.labelObjectsElements.place(x=10, y=10, width=1300 - 300 - 5 * 10 - 10)

        self.buttonObjectsElementsAdd = tk.Button(self.frameObjectsElements, text="+", command=self.clickAddObject)
        self.buttonObjectsElementsAdd.configure(self.styleButtonObjAdd)
        widgetsSetHoverFunctions([self.buttonObjectsElementsAdd], self.hoverButtonStd)

        self.buttonsObjectsElements = []

        self.frameObjectsOptionsContainer = ScrollFrame(self.frameObjects)
        self.frameObjectsOptionsContainer.configure(self.styleFrameOptions)
        self.frameObjectsOptionsContainer.place(x=1300 - 300 - 10, y=10, width=300, height=630 - 2 * 10)
        self.frameObjectsOptionsContainer.strength = 0.5
        self.frameObjectsOptionsContainer.height(830)

        self.frameObjectsOptions = self.frameObjectsOptionsContainer.frame

        self.labelObjectsOptions = tk.Label(self.frameObjectsOptions, text="General Options")
        self.labelObjectsOptions.configure(self.styleLabelHeading)
        self.labelObjectsOptions.place(x=10, y=10, width=280)

        self.labelObjectsOptionsGroups = tk.Label(self.frameObjectsOptions, text="Groups")
        self.labelObjectsOptionsGroups.configure(self.styleLabelStd)
        self.labelObjectsOptionsGroups.place(x=10, y=50)

        self.labelObjectsOptionsGroupsHelp = tk.Label(self.frameObjectsOptions, text="?")
        self.labelObjectsOptionsGroupsHelp.configure(self.styleLabelHelp)
        self.labelObjectsOptionsGroupsHelp.place(x=130, y=55)

        self.buttonsObjectsOptionsGroups = buttonsCreate(self.frameObjectsOptions, ["+", "-", "❏", "✎"], self.clickObjOptionsGroups)
        widgetsSetStyle(self.buttonsObjectsOptionsGroups.values(), self.styleButtonStd)
        widgetsSetHoverFunctions(self.buttonsObjectsOptionsGroups.values(), self.hoverButtonStd)
        widgetsPlace(self.buttonsObjectsOptionsGroups.values(), 300 - 4 * (24 + 6) - 4, 52, 24, 24, 6)

        self.lboxObjectsOptionsGroups = tk.Listbox(self.frameObjectsOptions)
        self.lboxObjectsOptionsGroups.configure(self.styleListBoxStd)
        self.lboxObjectsOptionsGroups.place(x=10, y=80, width=280, height=160)

        # -------------------- #
        # ----- Tooltips ----- #
        # -------------------- #

        self.tooltipEnvironmentsOptionsVariables = Tooltip(self.frameEnvironmentsOptions, "Create custom variables which\ncan be used for materials\nand environments to\nautomate/randomize things")
        self.tooltipEnvironmentsOptionsVariables.configure(self.styleTooltipStd)
        self.tooltipEnvironmentsOptionsVariables.label.configure(self.styleLabelTooltip)

        self.tooltipEnvironmentsOptionsLayers = Tooltip(self.frameEnvironmentsOptions, "All Layers which get created\nin Blender. Only relevant\nif you want to code your\nown Compositor Node.")
        self.tooltipEnvironmentsOptionsLayers.configure(self.styleTooltipStd)
        self.tooltipEnvironmentsOptionsLayers.label.configure(self.styleLabelTooltip)

        self.tooltipEnvironmentsOptionsCollections = Tooltip(self.frameEnvironmentsOptions, "All Collections which get created\nin Blender. Don't change if you\ndon't know, what you're doing :)")
        self.tooltipEnvironmentsOptionsCollections.configure(self.styleTooltipStd)
        self.tooltipEnvironmentsOptionsCollections.label.configure(self.styleLabelTooltip)

        self.tooltipObjectsOptionsGroups = Tooltip(self.frameObjectsOptions, "Create Object Groups (for Object\nor Particle Emitters)")
        self.tooltipObjectsOptionsGroups.configure(self.styleTooltipStd)
        self.tooltipObjectsOptionsGroups.label.configure(self.styleLabelTooltip)

        self.tooltipTriggers = {self.labelEnvironmentsOptionsVariablesHelp: self.tooltipEnvironmentsOptionsVariables,
                                self.labelEnvironmentsOptionsLayersHelp: self.tooltipEnvironmentsOptionsLayers,
                                self.labelEnvironmentsOptionsCollectionsHelp: self.tooltipEnvironmentsOptionsCollections,
                                self.labelObjectsOptionsGroupsHelp: self.tooltipObjectsOptionsGroups}

        self.tooltips = {self.tooltipEnvironmentsOptionsVariables: {"x": 100, "y": 80, "width": 145, "height": 64},
                         self.tooltipEnvironmentsOptionsLayers: {"x": 100, "y": 330, "width": 135, "height": 64},
                         self.tooltipEnvironmentsOptionsCollections: {"x": 90, "y": 580, "width": 150, "height": 52},
                         self.tooltipObjectsOptionsGroups: {"x": 90, "y": 80, "width": 154, "height": 40}}

        widgetsSetHoverFunctions(self.tooltipTriggers, [
            lambda event: self.tooltipTriggers[event.widget].place(self.tooltips[self.tooltipTriggers[event.widget]]),
            lambda event: self.tooltipTriggers[event.widget].place_forget()
        ])

        self.framesMenu = {"Start": self.frameStart, "Environments": self.frameEnvironments, "Objects": self.frameObjects}

        self.window.update()

        self.pathProgram = os.path.abspath(os.curdir)
        self.pathFile = ""
        self.nameFile = ""
        self.data = dataStandardGet()
        self.isSaved = True
        self.openEditors = {"environments": {}, "objects": {}}

        self.setTitle()
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))

    def onclose(self, function=None):
        if not self.isSaved:
            dialog = WarningDialog(self.window, "File not saved!", "Your current file is not saved.\nDo you want to close anyways?", ["Yes", "No"], "No")
            if dialog.value == "No":
                return
        self.window.destroy()
        self.window.quit()
        if function:
            function()

    def run(self):
        self.reloadAll()
        self.clickMenu("Start")
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#121212"
        }

        self.styleFrameMenu = {
            "background": "#303030"
        }

        self.styleButtonMenu = {
            "background": "#121212",
            "foreground": "#808080",
            "activebackground": "#060606",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 20]
        }
        self.hoverButtonMenu = hoverCreateFunctions("#121212", "#202020")

        self.styleButtonStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 17]
        }
        self.hoverButtonStd = hoverCreateFunctions("#303030", "#424242")

        self.styleButtonSmall = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }

        self.styleButtonEnvAdd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 80]
        }

        self.styleButtonEnvStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 12]
        }

        self.styleButtonObjAdd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 80]
        }

        self.styleButtonObjStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 12]
        }

        self.styleIndicatorMenu = {
            "background": "#121212"
        }

        self.styleFrameTab = {
            "background": "#121212"
        }

        self.styleFrameOptions = {
            "background": "#202020"
        }

        self.styleLabelHeading = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 20]
        }

        self.styleLabelStd = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 15]
        }

        self.styleLabelSmall = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleLabelHelp = {
            "background": "#202020",
            "foreground": "#C06060",
            "font": ["Helvetica", 8]
        }

        self.styleOptionMenuStd = {
            "background": "#303030",
            "activebackground": "#404040",
            "foreground": "#808080",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "highlightthickness": 0,
            "font": ["Helvetica", 12]
        }

        self.styleListBoxStd = {
            "background": "#303030",
            "foreground": "#808080",
            "selectbackground": "#505050",
            "selectforeground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#909090",
            "selectborderwidth": 0,
            "relief": "flat",
            "exportselection": False,
            "font": ["Helvetica", 12]
        }

        self.styleButtonMenuStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 12]
        }

        self.styleSeparatorStd = {
            "background": "#505050",
            "relief": "flat"
        }

        self.styleMenuStd = {
            "background": "#202020",
            "foreground": "#808080",
            "selectcolor": "#808080",
            "borderwidth": 0
        }

        self.styleScrollbarStd = {
            "background": "#303030",
            "troughcolor": "#303030",
            "highlightcolor": "black"
        }

        self.styleTooltipStd = {
            "background": "#181818"
        }

        self.styleLabelTooltip = {
            "background": "#181818",
            "foreground": "#808080",
            "font": ["Helvetica", 7]
        }

        self.styleEntryStd = {
            "background": "#181818",
            "foreground": "#808080",
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryFile = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "highlightbackground": "#404018",
            "highlightcolor": "#707020",
            "highlightthickness": 1,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryInteger = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#182050",
            "highlightcolor": "#203890",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryDriver = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#501818",
            "highlightcolor": "#902020",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

    def reloadAll(self):
        self.reloadEnvironments()
        self.updateEnvironmentsElements()
        self.updateEnvironmentsOptions()
        self.reloadObjects()
        self.updateObjectsElements()
        self.updateObjectsOptions()

    def reloadEnvironments(self):
        self.updateEnvironmentsOptions()
        self.updateEnvironmentsElements()

    def updateEnvironmentsElements(self):
        for button in self.buttonsEnvironmentsElements:
            button.place_forget()
            button.destroy()
        self.buttonsEnvironmentsElements = []

        posX = 10
        posY = 70
        width = (self.frameEnvironmentsElements.winfo_width() - 10) / 5 - 10
        height = 130
        for envId in self.data["environments"]:
            name = envId
            button = tk.Button(self.frameEnvironmentsElements, text=name, command=lambda name=name: self.clickEnvironment(name))
            button.configure(self.styleButtonEnvStd)
            widgetsSetHoverFunctions([button], self.hoverButtonStd)
            self.buttonsEnvironmentsElements.append(button)

            menu = tk.Menu(button)
            menu.configure(self.styleMenuStd, tearoff=0)
            menu.add_command(label="Rename", command=lambda _=None, envId=envId: self.clickEnvironmentRename(envId))
            menu.add_command(label="Duplicate", command=lambda _=None, envId=envId: self.clickEnvironmentDuplicate(envId))
            menu.add_command(label="Delete", command=lambda _=None, envId=envId: self.clickEnvironmentRemove(envId))
            button.bind("<Button-3>", lambda event, menu=menu: menu.post(event.x_root, event.y_root))

            button.place(x=posX, y=posY, width=width, height=height)
            posX += width + 10
            if posX > (self.labelEnvironmentsElements.winfo_width() - 3*10):
                posX = 10
                posY += height + 10

        self.buttonEnvironmentsElementsAdd.place(x=posX, y=posY, width=width, height=height)
        self.frameEnvironmentsElementsContainer.height(height=posY+height+10)

    def updateEnvironmentsOptions(self):
        self.lboxEnvironmentsOptionsVariables.delete(0, tk.END)
        self.lboxEnvironmentsOptionsLayers.delete(0, tk.END)
        self.lboxEnvironmentsOptionsCollections.delete(0, tk.END)
        self.entryEnvironmentsOptionsVariableExpression.delete(0, tk.END)
        self.menuEnvironmentsOptionsLayerPasses.delete_all()
        self.menuEnvironmentsOptionsCollectionLayers.delete_all()

        for layer in self.data["options"]["environments"]["layers"]:
            self.lboxEnvironmentsOptionsLayers.insert(tk.END, layer["name"])
            self.menuEnvironmentsOptionsCollectionLayers.add_option(layer["name"], self.updateEnvCollectionLayer)

        for lpass in self.environmentsOptionsPasses:
            self.menuEnvironmentsOptionsLayerPasses.add_option(lpass, self.updateEnvLayerPass)

        for collection in self.data["options"]["environments"]["collections"]:
            self.lboxEnvironmentsOptionsCollections.insert(tk.END, collection["name"])

        for variable in self.data["options"]["environments"]["variables"]:
            self.lboxEnvironmentsOptionsVariables.insert(tk.END, variable)

    def updateEnvVariables(self, _event=None):
        """Update currently selected variable expression (data->entry)"""
        if not self.lboxEnvironmentsOptionsVariables.curselection():
            self.entryEnvironmentsOptionsVariableExpression.delete(0, tk.END)
            return

        curVar = self.lboxEnvironmentsOptionsVariables.get(self.lboxEnvironmentsOptionsVariables.curselection()[0])
        self.entryEnvironmentsOptionsVariableExpression.delete(0, tk.END)
        curExp = self.data["options"]["environments"]["variables"][curVar]
        self.entryEnvironmentsOptionsVariableExpression.insert(0, curExp)

    def updateEnvVariableExpression(self, _event=None):
        """Save currently selected variable expression (entry->data)"""
        if not self.lboxEnvironmentsOptionsVariables.curselection():
            return

        curVar = self.lboxEnvironmentsOptionsVariables.get(self.lboxEnvironmentsOptionsVariables.curselection()[0])
        self.data["options"]["environments"]["variables"][curVar] = self.entryEnvironmentsOptionsVariableExpression.get()

        self.changeSaved(False)

    def updateEnvLayers(self, _event=None):
        if not self.lboxEnvironmentsOptionsLayers.curselection():
            return

        curLayer = self.lboxEnvironmentsOptionsLayers.curselection()[0]
        passes = self.data["options"]["environments"]["layers"][curLayer]["passes"]
        for lpass in self.environmentsOptionsPasses:
            if lpass in passes:
                self.menuEnvironmentsOptionsLayerPasses.values[lpass].set(True)
            else:
                self.menuEnvironmentsOptionsLayerPasses.values[lpass].set(False)

    def updateEnvLayerPasses(self, _event=None):
        if not self.lboxEnvironmentsOptionsLayers.curselection():
            return

        for lpass in self.environmentsOptionsPasses:
            self.updateEnvLayerPass(lpass)

    def updateEnvLayerPass(self, lpass):
        if not self.lboxEnvironmentsOptionsLayers.curselection():
            return

        curLayer = self.lboxEnvironmentsOptionsLayers.curselection()[0]
        passes = self.data["options"]["environments"]["layers"][curLayer]["passes"]
        valPass = self.menuEnvironmentsOptionsLayerPasses.values[lpass].get()
        valExist = lpass in passes

        if valPass and not valExist:
            passes.append(lpass)
        elif valExist and not valPass:
            passes.remove(lpass)

        self.changeSaved(False)

    def updateEnvCollections(self, _event=None):
        if not self.lboxEnvironmentsOptionsCollections.curselection():
            return

        curColl = self.lboxEnvironmentsOptionsCollections.curselection()[0]
        layers = self.data["options"]["environments"]["collections"][curColl]["layers"]
        for layer in self.data["options"]["environments"]["layers"]:
            nameLayer = layer["name"]
            if nameLayer in layers:
                self.menuEnvironmentsOptionsCollectionLayers.values[nameLayer].set(True)
            else:
                self.menuEnvironmentsOptionsCollectionLayers.values[nameLayer].set(False)

    def updateEnvCollectionLayers(self, _event=None):
        if not self.lboxEnvironmentsOptionsCollections.curselection():
            return

        layers = self.data["options"]["environments"]["collections"]
        for layer in layers:
            nameLayer = layer["name"]
            self.updateEnvCollectionLayer(nameLayer)

    def updateEnvCollectionLayer(self, layer):
        if not self.lboxEnvironmentsOptionsCollections.curselection():
            return

        curColl = self.lboxEnvironmentsOptionsCollections.curselection()[0]
        layers = self.data["options"]["environments"]["collections"][curColl]["layers"]
        valLayer = self.menuEnvironmentsOptionsCollectionLayers.values[layer].get()
        valExist = layer in layers

        if valLayer and not valExist:
            layers.append(layer)
        elif valExist and not valLayer:
            layers.remove(layer)

        self.changeSaved(False)

    def reloadObjects(self):
        self.updateObjectsOptions()
        self.updateObjectsElements()

    def updateObjectsElements(self):
        for button in self.buttonsObjectsElements:
            button.place_forget()
            button.destroy()
        self.buttonsObjectsElements = []

        posX = 10
        posY = 70
        width = (self.frameObjectsElements.winfo_width() - 10) / 5 - 10
        height = 130
        for objId in self.data["objects"]:
            name = objId
            button = tk.Button(self.frameObjectsElements, text=name, command=lambda name=name: self.clickObject(name))
            button.configure(self.styleButtonObjStd)
            widgetsSetHoverFunctions([button], self.hoverButtonStd)
            self.buttonsObjectsElements.append(button)

            menu = tk.Menu(button)
            menu.configure(self.styleMenuStd, tearoff=0)
            menu.add_command(label="Rename", command=lambda _=None, objId=objId: self.clickObjectRename(objId))
            menu.add_command(label="Duplicate", command=lambda _=None, objId=objId: self.clickObjectDuplicate(objId))
            menu.add_command(label="Delete", command=lambda _=None, objId=objId: self.clickObjectRemove(objId))
            button.bind("<Button-3>", lambda event, menu=menu: menu.post(event.x_root, event.y_root))

            button.place(x=posX, y=posY, width=width, height=height)
            posX += width + 10
            if posX > (self.labelObjectsElements.winfo_width() - 3 * 10):
                posX = 10
                posY += height + 10

        self.buttonObjectsElementsAdd.place(x=posX, y=posY, width=width, height=height)
        self.frameObjectsElementsContainer.height(height=posY + height + 10)

    def updateObjectsOptions(self):
        self.lboxObjectsOptionsGroups.delete(0, tk.END)

        for group in self.data["options"]["objects"]["groups"]:
            self.lboxObjectsOptionsGroups.insert(tk.END, group["name"])

    def clickMenu(self, name):
        for nameFrame in self.framesMenu:
            if nameFrame == name:
                width = self.window.winfo_width()
                height = self.window.winfo_height() - self.frameMenu.winfo_height()
                self.framesMenu[nameFrame].place(x=0, y=70, width=width, height=height)
            else:
                self.framesMenu[nameFrame].place_forget()

        button = self.buttonsMenu[name]
        posX = button.winfo_x()
        posY = button.winfo_y() + button.winfo_height()
        width = button.winfo_width()
        height = self.frameMenu.winfo_height() - posY

        self.indicatorMenuTab.place(x=posX, y=posY, width=width, height=height)

    def clickStartFile(self, name):
        if name == "New":
            if not self.isSaved:
                dialog = WarningDialog(self.window, "File not saved", "Warning: Current File is not saved!\nAre you sure you want to proceed?", ["Yes", "No"], "No")
                if dialog.value == "No":
                    return
                else:
                    self.nameFile = ""
                    self.isSaved = True
                    self.data = dataStandardGet()
                    self.reloadAll()

        elif name == "Open":
            if not self.isSaved:
                dialog = WarningDialog(self.window, "File not saved", "Warning: Current File is not saved!\nAre you sure you want to proceed?", ["Yes", "No"], "No")
                if dialog.value == "No":
                    return
            self.open()

        elif name == "Save":
            if self.nameFile:
                self.save()
            else:
                self.saveAs()

        elif name == "Save As":
            self.saveAs()

        elif name == "Reload":
            if self.nameFile:
                self.load()
            else:
                self.open()

        elif name == "Export":
            if self.nameFile:
                self.save()
                self.export()
            else:
                dialog = WarningDialog(self.window, "No Filename", "You haven't specified\nany filename. Do you want\nto continue with untitled?", ["Yes", "No"], "No")
                if dialog.value == "Yes":
                    self.export("untitled.madd.json")

    def clickEnvOptionsVariables(self, content):
        variables = self.data["options"]["environments"]["variables"]
        if content == "+":
            name = "Variable"
            nameExt = ""
            nameInt = 0
            while (name + nameExt) in variables:
                nameInt += 1
                nameExt = " " + str(nameInt)
            name += nameExt
            variables[name] = "0"
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsVariables.select_set(tk.END)

        elif content == "-":
            if not self.lboxEnvironmentsOptionsVariables.curselection():
                return

            curVar = self.lboxEnvironmentsOptionsVariables.get(self.lboxEnvironmentsOptionsVariables.curselection()[0])
            variables.pop(curVar)
            self.updateEnvironmentsOptions()

        elif content == "❏":
            if not self.lboxEnvironmentsOptionsVariables.curselection():
                return

            index = self.lboxEnvironmentsOptionsVariables.curselection()[0]
            name = self.lboxEnvironmentsOptionsVariables.get(index)
            variables[name + " Copy"] = variables[name][:]
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsVariables.select_set(index)

        elif content == "✎":
            if not self.lboxEnvironmentsOptionsVariables.curselection():
                return

            index = self.lboxEnvironmentsOptionsVariables.curselection()[0]
            name = self.lboxEnvironmentsOptionsVariables.get(index)
            title = "Rename: " + name
            dialog = RenameDialog(self.window, title, name)
            variables[dialog.value] = variables.pop(name)
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsVariables.select_set(index)

        self.updateEnvVariables()
        self.changeSaved(False)

    def clickEnvOptionsLayers(self, content):
        layers = self.data["options"]["environments"]["layers"]
        if content == "+":
            names = [layer["name"] for layer in layers]
            name = "Layer"
            nameExt = ""
            nameInt = 0
            while (name+nameExt) in names:
                nameInt += 1
                nameExt = " "+str(nameInt)
            name += nameExt
            layers.append({"name": name, "passes": []})
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsLayers.select_set(tk.END)

        elif content == "-":
            if not self.lboxEnvironmentsOptionsLayers.curselection():
                return

            curLayer = self.lboxEnvironmentsOptionsLayers.curselection()[0]
            layers.pop(curLayer)
            self.updateEnvironmentsOptions()

        elif content == "❏":
            if not self.lboxEnvironmentsOptionsLayers.curselection():
                return

            index = self.lboxEnvironmentsOptionsLayers.curselection()[0]
            name = self.lboxEnvironmentsOptionsLayers.get(index)
            layers.append(layers[index].copy())
            layers[len(layers)-1]["name"] = name + " Copy"
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsLayers.select_set(len(layers))

        elif content == "✎":
            if not self.lboxEnvironmentsOptionsLayers.curselection():
                return

            index = self.lboxEnvironmentsOptionsLayers.curselection()[0]
            name = self.lboxEnvironmentsOptionsLayers.get(index)
            title = "Rename: " + name
            dialog = RenameDialog(self.window, title, name)
            layers[index]["name"] = dialog.value
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsLayers.select_set(index)

        self.updateEnvLayerPasses()
        self.changeSaved(False)

    def clickEnvOptionsCollections(self, content):
        collections = self.data["options"]["environments"]["collections"]
        if content == "+":
            names = [collection["name"] for collection in collections]
            name = "Collection"
            nameExt = ""
            nameInt = 0
            while (name+nameExt) in names:
                nameInt += 1
                nameExt = " "+str(nameInt)
            name += nameExt
            collections.append({"name": name, "layers": []})
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsCollections.select_set(tk.END)

        elif content == "-":
            if not self.lboxEnvironmentsOptionsCollections.curselection():
                return

            curColl = self.lboxEnvironmentsOptionsCollections.curselection()[0]
            collections.pop(curColl)
            self.updateEnvironmentsOptions()

        elif content == "❏":
            if not self.lboxEnvironmentsOptionsCollections.curselection():
                return

            index = self.lboxEnvironmentsOptionsCollections.curselection()[0]
            name = self.lboxEnvironmentsOptionsCollections.get(index)
            collections.append(collections[index].copy())
            collections[len(collections)-1]["name"] = name + " Copy"
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsLayers.select_set(len(collections))

        elif content == "✎":
            if not self.lboxEnvironmentsOptionsCollections.curselection():
                return

            index = self.lboxEnvironmentsOptionsCollections.curselection()[0]
            name = self.lboxEnvironmentsOptionsCollections.get(index)
            title = "Rename: " + name
            dialog = RenameDialog(self.window, title, name)
            collections[index]["name"] = dialog.value
            self.updateEnvironmentsOptions()
            self.lboxEnvironmentsOptionsCollections.select_set(index)

        self.updateEnvCollectionLayers()
        self.changeSaved(False)

    def clickEnvironmentRename(self, envId):
        title = "Rename: " + envId
        dialog = RenameDialog(self.window, title, envId)
        self.data["environments"][dialog.value] = self.data["environments"].pop(envId)
        self.updateEnvironmentsElements()
        self.changeSaved(False)

    def clickEnvironmentDuplicate(self, envId):
        self.data["environments"][envId + " Copy"] = copy.deepcopy(self.data["environments"][envId])
        self.updateEnvironmentsElements()
        self.changeSaved(False)

    def clickEnvironmentRemove(self, envId):
        self.data["environments"].pop(envId)
        self.updateEnvironmentsElements()
        self.changeSaved(False)

    def clickAddEnvironment(self):
        name = "Environment"
        index = 0
        while name in self.data["environments"]:
            index += 1
            name = "Environment " + str(index)

        self.data["environments"][name] = dataStandardGetEnvironment()
        self.reloadEnvironments()
        self.clickEnvironment(name)

    def clickEnvironment(self, name):
        self.changeSaved(False)
        if name in self.openEditors["environments"]:
            self.openEditors["environments"][name].window.focus_force()
        else:
            editor = EditorEnvironment(self.window, name, self.data, self.clickEnvironmentClose)
            self.openEditors["environments"][name] = editor
            editor.run()

    def clickEnvironmentClose(self, name):
        self.changeSaved(False)
        self.openEditors["environments"].pop(name)

    def clickObject(self, name):
        self.changeSaved(False)
        if name in self.openEditors["objects"]:
            self.openEditors["objects"][name].window.focus_force()
        else:
            editor = EditorObject(self.window, name, self.data, self.clickObjectClose)
            self.openEditors["objects"][name] = editor
            editor.run()

    def clickObjectClose(self, name):
        self.changeSaved(False)
        self.openEditors["objects"].pop(name)

    def clickObjectRename(self, objId):
        title = "Rename: " + objId
        dialog = RenameDialog(self.window, title, objId)
        self.data["objects"][dialog.value] = self.data["objects"].pop(objId)
        self.updateObjectsElements()
        self.changeSaved(False)

    def clickObjectDuplicate(self, objId):
        self.data["objects"][objId + " Copy"] = copy.deepcopy(self.data["objects"][objId])
        self.updateObjectsElements()
        self.changeSaved(False)

    def clickObjectRemove(self, objId):
        self.data["objects"].pop(objId)
        self.updateObjectsElements()
        self.changeSaved(False)

    def clickAddObject(self):
        name = "Object"
        index = 0
        while name in self.data["objects"]:
            index += 1
            name = "Object " + str(index)

        self.data["objects"][name] = dataStandardGetObject()
        self.reloadObjects()
        self.clickObject(name)

    def clickObjOptionsGroups(self, content):
        groups = self.data["options"]["objects"]["groups"]
        if content == "+":
            names = [group["name"] for group in groups]
            name = "Group"
            nameExt = ""
            nameInt = 0
            while (name + nameExt) in names:
                nameInt += 1
                nameExt = " " + str(nameInt)
            name += nameExt
            groups.append({"name": name})
            self.updateObjectsOptions()
            self.lboxObjectsOptionsGroups.select_set(tk.END)

        elif content == "-":
            if not self.lboxObjectsOptionsGroups.curselection():
                return

            curGroup = self.lboxObjectsOptionsGroups.get(self.lboxObjectsOptionsGroups.curselection()[0])
            groups.remove({"name": curGroup})
            self.updateObjectsOptions()

        elif content == "❏":
            if not self.lboxObjectsOptionsGroups.curselection():
                return

            index = self.lboxObjectsOptionsGroups.curselection()[0]
            name = self.lboxObjectsOptionsGroups.get(index)
            groups.append(groups[index].copy())
            groups[index]["name"] = name + " Copy"
            self.updateObjectsOptions()
            self.lboxObjectsOptionsGroups.select_set(index)

        elif content == "✎":
            if not self.lboxObjectsOptionsGroups.curselection():
                return

            index = self.lboxObjectsOptionsGroups.curselection()[0]
            name = self.lboxObjectsOptionsGroups.get(index)
            title = "Rename: " + name
            dialog = RenameDialog(self.window, title, name)
            groups[index]["name"] = dialog.value
            self.updateObjectsOptions()
            self.lboxObjectsOptionsGroups.select_set(index)

        self.changeSaved(False)

    def changeSaved(self, saved=True):
        self.isSaved = saved
        self.setTitle()

    def setTitle(self):
        if self.nameFile:
            title = self.nameFile
        else:
            title = "Untitled"

        if not self.isSaved:
            title += " *"

        title += " - MDCT"
        self.window.title(title)

    def open(self):
        options = {"parent": self.window, "title": "Open file", "filetypes": [("Maddins files", "*.madd.json"), ("JSON files", ".json"), ("All", "*.*")]}
        if self.pathFile:
            filename = askopenfilename(**options, initialdir=self.pathFile)
        else:
            filename = askopenfilename(**options)

        if not filename:
            return

        self.pathFile, self.nameFile = os.path.split(filename)
        os.chdir(self.pathFile)
        file = open(filename)
        try:
            self.data = json.load(file)
            file.close()
        except Exception as exc:
            err = str(exc)
            errNew = ""
            while err:
                errNew += err[:30] + "\n"
                err = err[30:]
            errNew = errNew[:-1]
            ErrorDialog(self.window, "Error during file read!", "Error while reading JSON file:\n"+errNew)
            file.close()
            return

        self.changeSaved()
        self.reloadAll()

    def load(self):
        pass

    def save(self):
        file = open(os.path.join(self.pathFile, self.nameFile), "w")
        json.dump(self.data, file)
        file.close()
        self.changeSaved()

    def saveAs(self):
        options = {"parent": self.window, "title": "Save file as", "defaultextension": ".madd.json", "filetypes": [("Maddins files", "*.madd.json"), ("JSON files", ".json"), ("All", "*.*")]}
        if self.pathFile:
            filename = asksaveasfilename(**options, initialdir=self.pathFile)
        else:
            filename = asksaveasfilename(**options)

        if not filename:
            return

        self.pathFile, self.nameFile = os.path.split(filename)
        os.chdir(self.pathFile)
        self.save()

    def export(self, filename=""):
        options = {"parent": self.window, "title": "Export to folder"}
        if self.pathFile:
            folder = askdirectory(**options, initialdir=self.pathFile)
        else:
            folder = askdirectory(**options)

        if not filename:
            filename = self.nameFile

        data = copy.deepcopy(self.data)
        errors = []

        try:
            foldername = ".".join(filename.split(".")[:-1])
            directory = os.path.join(folder, foldername)
            os.mkdir(directory)

            dirEnvs = os.path.join(directory, "environments")
            dirObjs = os.path.join(directory, "objects")
            dirRend = os.path.join(directory, "renders")
            dirTemp = os.path.join(directory, "templates")

            os.mkdir(dirEnvs)
            os.mkdir(dirObjs)
            os.mkdir(dirRend)
            os.mkdir(dirTemp)
        except Exception as e:
            dialog = ErrorDialog(self.window, "Errors during export!", "There was an error\nduring the folder creation.", ["Show", "Ok"], "Ok")
            if dialog.value == "Show":
                ErrorShowDialog(self.window, "Error", str(e), ["Ok"], "Ok")
            return

        for envId in data["environments"]:
            env = data["environments"][envId]
            envTemplate = dataStandardGetEnvironmentTypes()[env["type"]]
            dirEnv = os.path.join(dirEnvs, envId)
            os.mkdir(dirEnv)
            os.mkdir(os.path.join(dirRend, envId))
            for optionId in env:
                if not optionId in envTemplate:
                    continue

                if optionId == "path":  # Render path
                    env[optionId] = os.path.relpath(os.path.join(dirRend, envId), directory)
                elif envTemplate[optionId]["type"] in ["image", "file"]:
                    try:
                        newPath = shutil.copy2(env[optionId], dirEnv)
                        env[optionId] = os.path.relpath(newPath, directory)
                    except Exception as e:
                        errors.append([str(e), envId, optionId])
                elif envTemplate[optionId]["type"] in ["directory"]:
                    try:
                        nameDir = os.path.split(env[optionId])[-1]
                        newPath = shutil.copytree(env[optionId], os.path.join(dirEnv, nameDir))
                        env[optionId] = os.path.relpath(newPath, directory)
                    except Exception as e:
                        errors.append([str(e), envId, optionId])

        for objId in data["objects"]:
            obj = data["objects"][objId]
            objTemplate = dataStandardGetObjectTypes("objects")[obj["type"]]
            dirObj = os.path.join(dirObjs, objId)
            os.mkdir(dirObj)
            for optionId in obj:
                if not optionId in objTemplate:
                    continue

                if objTemplate[optionId]["type"] in ["image", "file"]:
                    try:
                        newPath = shutil.copy2(obj[optionId], dirObj)
                        obj[optionId] = os.path.relpath(newPath, directory)
                    except Exception as e:
                        errors.append([str(e), objId, optionId])
                elif objTemplate[optionId]["type"] in ["directory"]:
                    try:
                        nameDir = os.path.split(obj[optionId])[-1]
                        newPath = shutil.copytree(obj[optionId], os.path.join(dirObj, nameDir))
                        obj[optionId] = os.path.relpath(newPath, directory)
                    except Exception as e:
                        errors.append([str(e), objId, optionId])

        shutil.copy2(os.path.join(self.pathProgram, "templates/mdbp.blend"), directory)
        shutil.copy2(os.path.join(self.pathProgram, "templates/template.json"), dirTemp)

        file = open(os.path.join(self.pathProgram, "templates/mdbp.py"))
        plugin = file.read()
        file.close()
        cmd = "read_maddins_data(bpy.context, '{}')".format(os.path.join(directory, filename).replace("\\", "/"))
        plugin = plugin.replace("# [PLACEHOLDER read_maddins_data] #", cmd)
        file = open(os.path.join(dirTemp, "mdbp.py"), "w")
        file.write(plugin)
        file.close()

        file = open(os.path.join(directory, filename), "w")
        json.dump(data, file)
        file.close()

        if errors:
            dialog = ErrorDialog(self.window, "Errors during export!", "There were {} errors\nduring the export process.".format(len(errors)), ["Show", "Ok"], "Ok")
            if dialog.value == "Show":
                texts = []
                for error in errors:
                    texts.append(" - ".join(error))
                ErrorShowDialog(self.window, "Errors", texts, ["Ok"], "Ok")


class EditorEnvironment:
    def __init__(self, root, envId, options, onclose=None):
        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("400x800")
        self.window.configure(self.styleWindow)
        self.window.resizable(False, False)

        self.envId = envId
        self.options = options
        self.optionsEnv = options["environments"][envId]

        self.frameEnvironmentTitle = tk.Frame(self.window)
        self.frameEnvironmentTitle.configure(self.styleFrameOptions)
        self.frameEnvironmentTitle.place(x=10, y=10, width=380, height=50)

        self.labelEnvironmentTitle = tk.Label(self.frameEnvironmentTitle, text=envId)
        self.labelEnvironmentTitle.configure(self.styleLabelHeading)
        self.labelEnvironmentTitle.place(x=10, y=10, width=360, height=30)

        self.frameEnvironmentColorHelp = tk.Frame(self.window)
        self.frameEnvironmentColorHelp.configure(self.styleFrameOptions)
        self.frameEnvironmentColorHelp.place(x=10, y=70, width=380, height=85)

        self.labelEnvironmentColorHelp = tk.Label(self.frameEnvironmentColorHelp, text="Color Codes:")
        self.labelEnvironmentColorHelp.configure(self.styleLabelSmall)
        self.labelEnvironmentColorHelp.place(x=10, y=10)

        colorCodes = colorCodesCreate(self.frameEnvironmentColorHelp, {" - Filepath": "#707020", " - Driver expression": "#902020", " - Integer": "#203890"})
        widgetsSetStyle(colorCodes.keys(), self.styleLabelMicro)
        widgetsPlace(colorCodes.values(), 10, 35, 10, 10, 5, "VERTICAL")
        widgetsPlace(colorCodes.keys(), 20, 35, None, 10, 5, "VERTICAL")

        self.frameEnvironmentOptionsContainer = ScrollFrame(self.window)
        self.frameEnvironmentOptionsContainer.strength = 0.6
        self.frameEnvironmentOptionsContainer.configure(self.styleFrameOptions)
        self.frameEnvironmentOptionsContainer.place(x=10, y=165, width=380, height=625)

        self.frameEnvironmentOptions = self.frameEnvironmentOptionsContainer.frame
        self.frameEnvironmentOptions.configure(self.styleFrameOptions)

        self.environmentTypes = dataStandardGetEnvironmentTypes()
        self.environmentNames = dataStandardGetEnvironmentNames()

        self.labelEnvironmentType = tk.Label(self.frameEnvironmentOptions, text="Environment Type")
        self.labelEnvironmentType.configure(self.styleLabelStd)
        self.labelEnvironmentType.place(x=10, y=10, height=30)

        self.menuEnvironmentType = SelectionMenuRadio(self.frameEnvironmentOptions)
        self.menuEnvironmentType.configure(self.styleButtonMenuStd)
        self.menuEnvironmentType.menu.configure(self.styleMenuStd)
        self.menuEnvironmentType.add_options(self.environmentNames.keys(), self.clickEnvironmentType)
        self.menuEnvironmentType.place(x=10, y=40, width=200)

        self.widgetsEnvironmentOptions = {}

        self.window.update()
        self.updateAll()
        self.setTitle()
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))

    def onclose(self, function=None):
        self.updateData()
        self.window.destroy()
        self.window.quit()
        if function:
            function(self.envId)

    def run(self):
        self.window.focus_force()
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#121212"
        }

        self.styleFrameOptions = {
            "background": "#202020"
        }

        self.styleLabelStd = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 15]
        }

        self.styleLabelSmall = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 12]
        }

        self.styleLabelMicro = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 8]
        }

        self.styleLabelHeading = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 20]
        }

        self.styleButtonMenuStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleButtonMenuHeading = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 15]
        }

        self.styleMenuStd = {
            "background": "#202020",
            "foreground": "#808080",
            "selectcolor": "#808080",
            "borderwidth": 0
        }

        self.styleEntryStd = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryFile = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "highlightbackground": "#404018",
            "highlightcolor": "#707020",
            "highlightthickness": 1,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryInteger = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#182050",
            "highlightcolor": "#203890",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryDriver = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#501818",
            "highlightcolor": "#902020",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleButtonStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 12]
        }
        self.hoverButtonStd = hoverCreateFunctions("#303030", "#424242")

        self.styleButtonBig = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 20]
        }

        self.styleButtonSmall = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }

        self.styleLabelImg = {
            "background": "#181818",
        }

        self.styleListBoxStd = {
            "background": "#303030",
            "foreground": "#808080",
            "selectbackground": "#505050",
            "selectforeground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#909090",
            "selectborderwidth": 0,
            "relief": "flat",
            "exportselection": False,
            "font": ["Helvetica", 12]
        }

    def setTitle(self):
        title = "Untitled"
        if self.envId:
            title = self.envId

        title += " - MEE"
        self.window.title(title)

    def updateAll(self):
        self.updateEnvironmentType()
        # self.updateEnvironmentOptions() No need to call it, 'cause updateEnvironmentType already calls it

    def updateEnvironmentType(self):
        text = self.environmentTypes[self.optionsEnv["type"]]["name"]
        self.menuEnvironmentType.variable.set(text)
        self.menuEnvironmentType.configure(text=text)
        self.updateEnvironmentOptions()

    def updateEnvironmentOptions(self):
        for option in self.widgetsEnvironmentOptions:
            for widget in self.widgetsEnvironmentOptions[option]:
                self.widgetsEnvironmentOptions[option][widget].place_forget()
                self.widgetsEnvironmentOptions[option][widget].destroy()

        self.widgetsEnvironmentOptions = {}

        posY = 90
        envType = self.environmentTypes[self.optionsEnv["type"]]

        for optionId in envType:
            option = envType[optionId]
            if optionId == "name":
                continue

            elif option["type"] == "image":
                path = self.optionsEnv.get(optionId, "")
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryFile)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, path)
                entry.configure(state="readonly")

                buttonReload = tk.Button(self.frameEnvironmentOptions, text="⟳", command=lambda optionId=optionId: self.clickImageReload(optionId))
                buttonReload.configure(self.styleButtonStd)
                buttonReload.place(x=215, y=posY, width=20, height=20)
                buttonOpen = tk.Button(self.frameEnvironmentOptions, text="➟", command=lambda optionId=optionId: self.clickImageBrowse(optionId))
                buttonOpen.configure(self.styleButtonStd)
                buttonOpen.place(x=240, y=posY, width=20, height=20)
                widgetsSetHoverFunctions([buttonReload, buttonOpen], self.hoverButtonStd)
                posY += 25

                labelImg = tk.Label(self.frameEnvironmentOptions)
                labelImg.configure(self.styleLabelImg)
                labelImg.place(x=10, y=posY, width=160, height=90)
                img = getTkinterImage(path, resize=[160, 90])
                self.window.update()
                if img:
                    labelImg.configure(image=img)
                posY += 100

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "labelImg": labelImg, "label": label, "buttonReload": buttonReload, "buttonOpen": buttonOpen}

            elif option["type"] == "directory":
                path = self.optionsEnv.get(optionId, "")

                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryFile)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, path)
                entry.configure(state="readonly")

                buttonOpen = tk.Button(self.frameEnvironmentOptions, text="➟", command=lambda optionId=optionId: self.clickFolderBrowse(optionId))
                buttonOpen.configure(self.styleButtonStd)
                buttonOpen.place(x=215, y=posY, width=20, height=20)
                widgetsSetHoverFunctions([buttonOpen], self.hoverButtonStd)
                posY += 30

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "buttonOpen": buttonOpen, "label": label}

            elif option["type"] == "file":
                path = self.optionsEnv.get(optionId, "")

                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryFile)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, path)
                entry.configure(state="readonly")

                buttonOpen = tk.Button(self.frameEnvironmentOptions, text="➟", command=lambda optionId=optionId: self.clickFileBrowse(optionId))
                buttonOpen.configure(self.styleButtonStd)
                buttonOpen.place(x=215, y=posY, width=20, height=20)
                widgetsSetHoverFunctions([buttonOpen], self.hoverButtonStd)
                posY += 30

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "buttonOpen": buttonOpen, "label": label}

            elif option["type"] == "listmenu":
                text = self.optionsEnv.get(optionId, option["options"][0])
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                menubutton = SelectionMenuRadio(self.frameEnvironmentOptions, text=text)
                menubutton.configure(self.styleButtonMenuStd)
                menubutton.menu.configure(self.styleMenuStd)
                menubutton.add_options(option["options"])
                menubutton.variable.set(text)
                menubutton.place(x=10, y=posY, width=200)
                posY += 35

                self.widgetsEnvironmentOptions[optionId] = {"menubutton": menubutton, "label": label}

            elif option["type"] == "driver":
                text = self.optionsEnv.get(optionId, option["default"])
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryDriver)
                entry.bind("<Return>", self.updateData)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, text)
                buttonChange = tk.Button(self.frameEnvironmentOptions, text="⚙", command=lambda optionId=optionId: self.clickDriverChange(optionId))
                buttonChange.configure(self.styleButtonSmall)
                buttonChange.place(x=215, y=posY, width=20, height=20)
                buttonOk = tk.Button(self.frameEnvironmentOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                buttonOk.place(x=240, y=posY, height=20)
                widgetsSetHoverFunctions([buttonChange, buttonOk], self.hoverButtonStd)
                posY += 35

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "label": label, "buttonChange": buttonChange, "buttonOk": buttonOk}

            elif option["type"] == "boolean":
                pass

            elif option["type"] == "integer":
                text = self.optionsEnv.get(optionId, option["default"])
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = IntEntry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryInteger)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.variable.set(text)
                buttonOk = tk.Button(self.frameEnvironmentOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                widgetsSetHoverFunctions([buttonOk], self.hoverButtonStd)
                buttonOk.place(x=215, y=posY, height=20)
                posY += 35

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "label": label, "buttonOk": buttonOk}

            elif option["type"] == "real":
                text = self.optionsEnv.get(optionId, option["default"])
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = FloatEntry(self.frameEnvironmentOptions)
                entry.configure(self.styleEntryStd)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.variable.set(text)
                buttonOk = tk.Button(self.frameEnvironmentOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                widgetsSetHoverFunctions([buttonOk], self.hoverButtonStd)
                buttonOk.place(x=215, y=posY, height=20)
                posY += 35

                self.widgetsEnvironmentOptions[optionId] = {"entry": entry, "label": label, "buttonOk": buttonOk}

            elif option["type"] == "envobjects":
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                buttonChange = tk.Button(self.frameEnvironmentOptions, text="Edit Environment Objects", command=self.clickEditEnvObjects)
                buttonChange.configure(self.styleButtonSmall)
                widgetsSetHoverFunctions([buttonChange], self.hoverButtonStd)
                buttonChange.place(x=10, y=posY, height=25)
                posY += 35

                self.widgetsEnvironmentOptions[optionId] = {"label": label, "buttonChange": buttonChange}

            elif option["type"][:5] == "array":
                default = option["default"]
                if not isinstance(default, list):
                    default = [default] * option["num"]
                contents = self.optionsEnv.get(optionId, default)
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                names = option.get("names")
                custom = {}

                for i in range(option["num"]):
                    if option["type"][6:] == "integer":
                        entry = IntEntry(self.frameEnvironmentOptions)
                        entry.configure(self.styleEntryInteger)
                        entry.bind("<Return>", self.updateData)
                        entry.bind("<Tab>", self.updateData)
                        if names:
                            entry.place(x=30, y=posY, width=180, height=20)
                            labelName = tk.Label(self.frameEnvironmentOptions, text=names[i])
                            labelName.configure(self.styleLabelMicro)
                            labelName.place(x=10, y=posY, height=20)
                            custom["label" + str(i)] = labelName
                        else:
                            entry.place(x=10, y=posY, width=200, height=20)
                        entry.insert(0, contents[i])
                        buttonOk = tk.Button(self.frameEnvironmentOptions, text="Ok", command=self.updateData)
                        buttonOk.configure(self.styleButtonSmall)
                        widgetsSetHoverFunctions([buttonOk], self.hoverButtonStd)
                        buttonOk.place(x=215, y=posY, height=20)
                        posY += 30
                        custom["entry" + str(i)] = entry
                        custom["buttonOk" + str(i)] = buttonOk

                self.widgetsEnvironmentOptions[optionId] = {"label": label, **custom}

            elif option["type"][:7] == "listbox":
                custom = {}
                label = tk.Label(self.frameEnvironmentOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                if option["type"][8:] == "driver":
                    buttonAdd = tk.Button(self.frameEnvironmentOptions, text="+", command=lambda optionId=optionId: self.clickListBoxAdd(optionId))
                    buttonAdd.configure(self.styleButtonBig)
                    buttonAdd.place(x=285, y=posY, width=25, height=25)
                    buttonDel = tk.Button(self.frameEnvironmentOptions, text="-", command=lambda optionId=optionId: self.clickListBoxRemove(optionId))
                    buttonDel.configure(self.styleButtonBig)
                    buttonDel.place(x=315, y=posY, width=25, height=25)
                    buttonEdit = tk.Button(self.frameEnvironmentOptions, text="✎", command=lambda optionId=optionId: self.clickListBoxRename(optionId))
                    buttonEdit.configure(self.styleButtonBig)
                    buttonEdit.place(x=345, y=posY, width=25, height=25)
                    widgetsSetHoverFunctions([buttonAdd, buttonDel, buttonEdit], self.hoverButtonStd)
                    custom = {"buttonAdd": buttonAdd, "buttonDel": buttonDel, "buttonEdit": buttonEdit, **custom}
                posY += 30

                listbox = tk.Listbox(self.frameEnvironmentOptions)
                listbox.configure(self.styleListBoxStd)
                listbox.bind("<<ListboxSelect>>", lambda _, optionId=optionId: self.clickListBox(optionId))
                listbox.place(x=10, y=posY, width=360, height=150)
                posY += 160

                # wenn type[8:x] listbox -> extra fenster ...
                if option["type"][8:] == "driver":
                    labelExpression = tk.Label(self.frameEnvironmentOptions, text="Expression:")
                    labelExpression.configure(self.styleLabelSmall)
                    labelExpression.place(x=10, y=posY, height=20)
                    entryExpression = tk.Entry(self.frameEnvironmentOptions)
                    entryExpression.configure(self.styleEntryDriver)
                    entryExpression.bind("<Return>", self.updateData)
                    entryExpression.place(x=100, y=posY, height=20, width=215)
                    buttonChange = tk.Button(self.frameEnvironmentOptions, text="⚙", command=lambda optionId=optionId: self.clickDriverChange(optionId))
                    buttonChange.configure(self.styleButtonSmall)
                    buttonChange.place(x=320, y=posY, width=20, height=20)
                    buttonOk = tk.Button(self.frameEnvironmentOptions, text="Ok", command=self.updateData)
                    buttonOk.configure(self.styleButtonSmall)
                    buttonOk.place(x=345, y=posY, width=25, height=20)
                    widgetsSetHoverFunctions([buttonOk, buttonChange], self.hoverButtonStd)
                    for name in self.optionsEnv.get(optionId, {}):
                        listbox.insert(tk.END, name)
                    posY += 35
                    custom = {"labelExpression": labelExpression, "entry": entryExpression, "buttonChange": buttonChange, "buttonOk": buttonOk, **custom}

                self.widgetsEnvironmentOptions[optionId] = {"label": label, "listbox": listbox, **custom}

        self.frameEnvironmentOptionsContainer.height(posY)
        self.updateData()

    def updateData(self, _event=None):
        envType = self.environmentTypes[self.optionsEnv["type"]]
        for optionId in self.widgetsEnvironmentOptions:
            option = envType[optionId]
            widgets = self.widgetsEnvironmentOptions[optionId]
            value = self.optionsEnv.get(optionId, None)
            if option["type"] == "image":
                value = widgets["entry"].get()

            elif option["type"] == "directory":
                value = widgets["entry"].get()

            elif option["type"] == "listmenu":
                value = widgets["menubutton"].variable.get()

            elif option["type"] == "driver":
                value = widgets["entry"].get()
                if not value: value = option["default"]

            elif option["type"] == "integer":
                value = widgets["entry"].get()

            elif option["type"] == "real":
                value = widgets["entry"].get()

            elif option["type"] == "file":
                value = widgets["entry"].get()

            elif option["type"][:5] == "array":
                default = option["default"]
                if not isinstance(default, list):
                    default = [default] * option["num"]
                value = self.optionsEnv.get(optionId, default)
                for i in range(option["num"]):
                    v = widgets["entry" + str(i)].get()
                    if v is None: continue
                    value[i] = v

            elif option["type"][:7] == "listbox":
                if not widgets["listbox"].curselection():
                    continue

                if option["type"][8:] == "driver":
                    value = self.optionsEnv.get(optionId, {})
                    value[widgets["listbox"].get(widgets["listbox"].curselection()[0])] = widgets["entry"].get()
            self.optionsEnv[optionId] = value

    def clickEnvironmentType(self, title):
        self.updateData()
        self.optionsEnv["type"] = self.environmentNames[title]
        self.updateEnvironmentType()

    def clickDriverChange(self, optionId):
        name = "Edit Driver: " + self.environmentTypes[self.optionsEnv["type"]][optionId]["name"]
        varsGlobal = self.options["options"]["environments"]["variables"].keys()
        varsEnv = self.optionsEnv["variables"].keys()
        variables = list(varsEnv) + list(varsGlobal)
        expression = self.widgetsEnvironmentOptions[optionId]["entry"].get()
        editor = EditorDriver(self.window, name, variables, expression, self.exitDriverChange)
        editor.run()

    def exitDriverChange(self, name, value):
        optionId = ""
        options = self.environmentTypes[self.optionsEnv["type"]]
        for optionId in options:
            if optionId == "name":
                continue
            if name[13:] == options[optionId]["name"]:
                break
        self.widgetsEnvironmentOptions[optionId]["entry"].delete(0, tk.END)
        self.widgetsEnvironmentOptions[optionId]["entry"].insert(0, value)
        self.updateData()

    def clickEditEnvObjects(self):
        if (not "objects" in self.optionsEnv) or (not self.optionsEnv["objects"]):
            self.optionsEnv["objects"] = {}
        editor = EditorEnvObjects(self.window, self.options, self.envId, self.optionsEnv["objects"], self.environmentTypes[self.optionsEnv["type"]]["objects"], onclose=self.updateData)
        editor.run()

    def clickListBox(self, optionId):
        widget = self.widgetsEnvironmentOptions[optionId]["listbox"]
        if not widget.curselection():
            return

        name = widget.get(widget.curselection()[0])
        if self.environmentTypes[self.optionsEnv["type"]][optionId]["type"][8:] == "driver":
            value = self.optionsEnv[optionId][name]
            self.widgetsEnvironmentOptions[optionId]["entry"].delete(0, tk.END)
            self.widgetsEnvironmentOptions[optionId]["entry"].insert(0, value)

    def clickListBoxAdd(self, optionId):
        value = self.optionsEnv.get(optionId, {})
        name = "Element"
        index = 0
        ext = ""
        while name+ext in self.optionsEnv.get(optionId, {}):
            index += 1
            ext = str(index)
        value[name+ext] = "0"
        self.optionsEnv[optionId] = value
        self.updateEnvironmentOptions()
        self.widgetsEnvironmentOptions[optionId]["listbox"].select_set(tk.END)
        self.clickListBox(optionId)

    def clickListBoxRemove(self, optionId):
        widget = self.widgetsEnvironmentOptions[optionId]["listbox"]
        if not self.widgetsEnvironmentOptions[optionId]["listbox"].curselection():
            return

        self.optionsEnv[optionId].pop(widget.get(widget.curselection()[0]))
        self.widgetsEnvironmentOptions[optionId]["entry"].delete(0, tk.END)
        widget.delete(widget.curselection()[0])

    def clickListBoxRename(self, optionId):
        widget = self.widgetsEnvironmentOptions[optionId]["listbox"]
        if not self.widgetsEnvironmentOptions[optionId]["listbox"].curselection():
            return
        
        name = widget.get(widget.curselection()[0])
        dialog = RenameDialog(self.window, "Rename", name)
        nameNew = dialog.value
        self.optionsEnv[optionId][nameNew] = self.optionsEnv[optionId].pop(name)
        self.updateEnvironmentOptions()

    def clickImageBrowse(self, optionId):
        options = {"parent": self.window, "title": "Open file", "filetypes": [("Image files", ("*.jpg", "*.png", "*.hdr")), ("All", "*.*")]}
        path = askopenfilename(**options)
        if path:
            self.optionsEnv[optionId] = path
            self.clickImageReload(optionId)

    def clickImageReload(self, optionId):
        img = getTkinterImage(self.optionsEnv[optionId], reload=True)
        if img:
            self.updateEnvironmentOptions()

    def clickFolderBrowse(self, optionId):
        options = {"parent": self.window, "title": "Open directory"}
        path = askdirectory(**options)
        if path:
            self.optionsEnv[optionId] = path
        self.updateEnvironmentOptions()

    def clickFileBrowse(self, optionId):
        filetypes = self.environmentTypes[self.optionsEnv["type"]][optionId].get("filetypes", [])
        filetypes.append(["All", "*.*"])
        options = {"parent": self.window, "title": "Open file", "filetypes": filetypes}
        path = askopenfilename(**options)
        if path:
            self.optionsEnv[optionId] = path
        self.updateEnvironmentOptions()


class EditorEnvObjects:
    def __init__(self, root, options, envId, objects, template, name="Environment Object Editor", onclose=None):
        self._init_styles()

        frameWidth = 280
        numFrames = len(template["options"])
        winWidth = (frameWidth + 10) * numFrames + 10
        self.envId = envId

        self.window = tk.Toplevel(root)
        self.window.configure(self.styleWindow)
        self.window.resizable(False, False)
        self.window.geometry(str(winWidth) + "x600")
        self.window.title(name)
        self.name = name

        self.preview = None
        if options["environments"][self.envId]["type"] in ["360image", "360imagelabel", "360imagelabeljson", "360imagecolor"]:
            self.preview = tk.Toplevel(self.window)
            w, h = 1000, 500
            self.preview.configure(self.styleWindow)
            self.preview.resizable(False, False)
            self.preview.title("Preview: "+name)
            self.preview.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))

            self.previewImage = getTkinterImage(options["environments"][self.envId]["image"], [w, h])
            if self.previewImage:
                w, h = self.previewImage.width(), self.previewImage.height()
                self.preview.geometry(str(w) + "x" + str(h))

                self.previewCanvas = tk.Canvas(self.preview)
                self.previewCanvas.configure(self.styleCanvas)
                self.previewCanvas.place(x=0, y=0, width=w, height=h)
            else:
                ErrorDialog(self.preview, "Image Error", "Image is not available. Maybe\nyou moved or deleted it or\nthe format is not supported!")
                self.preview.destroy()
                self.preview = None

        self.frameTitle = tk.Frame(self.window)
        self.frameTitle.configure(self.styleFrame)
        self.frameTitle.place(x=10, y=10, width=winWidth-20, height=50)

        self.labelTitle = tk.Label(self.frameTitle, text=name)
        self.labelTitle.configure(self.styleLabelHeading)
        self.labelTitle.place(x=0, y=0, width=winWidth-20, height=50)

        self.options = options
        self.objects = objects
        self.widgetsObjects = {}
        self.template = template

        self.framesOptions = {}
        posX = 10
        for optionId in self.template["options"]:
            if not optionId in self.objects:
                self.objects[optionId] = {}
            container = ScrollFrame(self.window)
            container.configure(self.styleFrame)
            container.strength = 0.6
            container.place(x=posX, y=70, width=frameWidth, height=520)

            frame = container.frame
            frame.configure(self.styleFrame)

            label = tk.Label(frame, text=self.template["options"][optionId])
            label.configure(self.styleLabelBig)
            label.place(x=10, y=10)

            buttons = buttonsCreate(frame, ["+", "-", "✎"], lambda operation, optionId=optionId: self.clickObjectOperation(operation, optionId))
            widgetsSetStyle(buttons.values(), self.styleButtonStd)
            widgetsSetHoverFunctions(buttons.values(), self.hoverButtonStd)
            widgetsPlace(buttons.values(), frameWidth - 3 * (24 + 6) - 4, 10, 24, 24, 6)

            listbox = tk.Listbox(frame)
            listbox.configure(self.styleListbox)
            listbox.place(x=10, y=40, width=frameWidth-20, height=140)
            listbox.bind("<<ListboxSelect>>", lambda _, optionId=optionId: self.clickListboxSelect(optionId))

            self.framesOptions[optionId] = {"container": container, "frame": frame, "label": label, "listbox": listbox}

            posX += frameWidth + 10

        self.window.update()
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))
        self.updateObjects()
        self.updateWidgets()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#121212"
        }

        self.styleFrame = {
            "background": "#202020"
        }

        self.styleLabelHeading = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 20]
        }

        self.styleLabelBig = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 15]
        }

        self.styleLabel = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 12]
        }

        self.styleLabelSmall = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleEntryDriver = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#501818",
            "highlightcolor": "#902020",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryFile = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "highlightbackground": "#404018",
            "highlightcolor": "#707020",
            "highlightthickness": 1,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryInteger = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#182050",
            "highlightcolor": "#203890",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryFloat = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#185060",
            "highlightcolor": "#208090",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleListbox = {
            "background": "#303030",
            "foreground": "#808080",
            "selectbackground": "#505050",
            "selectforeground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#909090",
            "selectborderwidth": 0,
            "relief": "flat",
            "exportselection": False,
            "font": ["Helvetica", 12]
        }

        self.styleButtonStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 17]
        }
        self.hoverButtonStd = hoverCreateFunctions("#303030", "#424242")

        self.styleButtonSmall = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }

        self.styleButtonBig = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 20]
        }

        self.styleButtonMenuStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleMenuStd = {
            "background": "#202020",
            "foreground": "#808080",
            "selectcolor": "#808080",
            "borderwidth": 0
        }

        self.styleCanvas = {
            "background": "#121212",
        }

        self.styleListBoxStd = {
            "background": "#303030",
            "foreground": "#808080",
            "selectbackground": "#505050",
            "selectforeground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#909090",
            "selectborderwidth": 0,
            "relief": "flat",
            "exportselection": False,
            "font": ["Helvetica", 12]
        }

    def run(self):
        self.window.grab_set()
        self.window.focus_force()
        self.window.mainloop()

    def onclose(self, function=None):
        self.updateData()
        if self.preview:
            self.preview.destroy()
            self.preview.quit()
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()
        if function:
            function(self.name)

    def updateWidgets(self):
        for objectTypeId in self.widgetsObjects:  # objectTypeId in ["lights", "cameras", ...]
            objectType = self.widgetsObjects[objectTypeId]
            for optionId in objectType:  # optionId in ["position", "materialPreset", ...]
                option = objectType[optionId]
                for widgetId in option:  # widgetId in ["label", "entry", ...] -> delete all widgets for all options in all object Types
                    option[widgetId].place_forget()
                    option[widgetId].destroy()

        self.widgetsObjects = {}

        for objectType in self.template["options"]:
            listbox = self.framesOptions[objectType]["listbox"]
            if not listbox.curselection():
                continue

            posY = 200
            container = self.framesOptions[objectType]["frame"]
            curObject = self.objects[objectType][listbox.get(listbox.curselection()[0])]
            curObjectType = curObject["type"]
            types = dataStandardGetObjectTypes(objectType)
            widgets = {}

            label = tk.Label(container, text="Type")
            label.configure(self.styleLabelBig)
            label.place(x=10, y=posY)
            posY += 30

            listmenu = SelectionMenuRadio(container)
            listmenu.set_styles(self.styleButtonMenuStd, self.styleMenuStd)
            listmenu.place(x=10, y=posY, width=200, height=25)
            for typeId in types:
                listmenu.add_option(types[typeId]["name"], self.clickListMenuSelect)
            text = types[self.objects[objectType][listbox.get(listbox.curselection()[0])]["type"]]["name"]
            listmenu.variable.set(text)
            listmenu.configure(text=text)
            posY += 35

            widgets["name"] = {"label": label, "listmenu": listmenu}

            for optionId in types[curObjectType]:
                option = types[curObjectType][optionId]
                if (optionId == "name") or (optionId == "display"):
                    continue
                elif option["type"] == "checkmenu":
                    text = "<Select>"
                    options = []
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    if isinstance(option["options"], str):
                        if option["options"][:3] == "rel":
                            path = option["options"][4:].split(":")
                            options = self.options
                            for part in path[:-1]:
                                options = options.get(part, {})

                            if path[-1][:2] == "id":
                                options = options.keys()
                            elif path[-1][:6] == "option":
                                name = path[-1][7:]
                                _options = []
                                for obj in options:
                                    _options.append(obj[name])
                                options = _options

                    elif isinstance(option["options"], list):
                        options = option["options"]

                    menubutton = SelectionMenuCheck(container, text=text)
                    menubutton.configure(self.styleButtonMenuStd)
                    menubutton.menu.configure(self.styleMenuStd)
                    menubutton.add_options(options, self.updateData)
                    for value in curObject.get(optionId, {}):
                        menubutton.values[value].set(True)
                    menubutton.place(x=10, y=posY, width=200)
                    posY += 35

                    widgets[optionId] = {"menubutton": menubutton, "label": label}

                elif option["type"] == "listmenu":
                    text = "<No Elements>"
                    options = []
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    if isinstance(option["options"], str):
                        if option["options"][:3] == "rel":
                            path = option["options"][4:].split(":")
                            options = self.options
                            for part in path[:-1]:
                                options = options.get(part, {})

                            if path[-1][:2] == "id":
                                options = options.keys()
                            elif path[-1][:6] == "option":
                                name = path[-1][7:]
                                _options = []
                                for obj in options:
                                    _options.append(obj[name])
                                options = _options

                    elif isinstance(option["options"], list):
                        options = option["options"]

                    if options:
                        text = options[0]
                    text = curObject.get(optionId, text)
                    menubutton = SelectionMenuRadio(container, text=text)
                    menubutton.configure(self.styleButtonMenuStd)
                    menubutton.menu.configure(self.styleMenuStd)
                    menubutton.add_options(options, self.clickMenuButtonSelect)
                    menubutton.variable.set(text)
                    menubutton.place(x=10, y=posY, width=200)
                    posY += 35

                    widgets[optionId] = {"menubutton": menubutton, "label": label}

                elif option["type"] == "driver":
                    text = curObject.get(optionId, types[curObjectType][optionId]["default"])
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    entry = tk.Entry(container)
                    entry.configure(self.styleEntryDriver)
                    entry.bind("<Return>", self.updateData)
                    entry.bind("<Tab>", self.updateData)
                    entry.place(x=10, y=posY, width=200, height=20)
                    entry.insert(0, text)
                    buttonChange = tk.Button(container, text="⚙", command=lambda objectType=objectType, optionId=optionId: self.clickDriverChange(objectType, optionId))
                    buttonChange.configure(self.styleButtonSmall)
                    buttonChange.place(x=215, y=posY, width=20, height=20)
                    buttonOk = tk.Button(container, text="Ok", command=self.updateData)
                    buttonOk.configure(self.styleButtonSmall)
                    buttonOk.place(x=240, y=posY, height=20)
                    widgetsSetHoverFunctions([buttonChange, buttonOk], self.hoverButtonStd)
                    posY += 30

                    widgets[optionId] = {"entry": entry, "label": label, "buttonChange": buttonChange, "buttonOk": buttonOk}

                elif option["type"] == "integer":
                    text = curObject.get(optionId, types[curObjectType][optionId]["default"])
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    entry = IntEntry(container)
                    entry.configure(self.styleEntryInteger)
                    entry.bind("<Return>", self.updateData)
                    entry.bind("<Tab>", self.updateData)
                    entry.place(x=10, y=posY, width=200, height=20)
                    entry.insert(0, text)
                    posY += 30

                    widgets[optionId] = {"entry": entry, "label": label}

                elif option["type"] == "float":
                    text = curObject.get(optionId, types[curObjectType][optionId]["default"])
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    entry = FloatEntry(container)
                    entry.configure(self.styleEntryFloat)
                    entry.bind("<Return>", self.updateData)
                    entry.bind("<Tab>", self.updateData)
                    entry.place(x=10, y=posY, width=200, height=20)
                    entry.insert(0, text)
                    posY += 30

                    widgets[optionId] = {"entry": entry, "label": label}

                elif option["type"][:7] == "listbox":
                    custom = {}
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    if option["type"][8:] == "driver":
                        buttonAdd = tk.Button(container, text="+", command=lambda objectType=objectType, optionId=optionId: self.clickListboxAdd(objectType, optionId))
                        buttonAdd.configure(self.styleButtonBig)
                        buttonAdd.place(x=185, y=posY, width=25, height=25)
                        buttonDel = tk.Button(container, text="-", command=lambda objectType=objectType, optionId=optionId: self.clickListboxRemove(objectType, optionId))
                        buttonDel.configure(self.styleButtonBig)
                        buttonDel.place(x=215, y=posY, width=25, height=25)
                        buttonEdit = tk.Button(container, text="✎", command=lambda objectType=objectType, optionId=optionId: self.clickListboxRename(objectType, optionId))
                        buttonEdit.configure(self.styleButtonBig)
                        buttonEdit.place(x=245, y=posY, width=25, height=25)
                        widgetsSetHoverFunctions([buttonAdd, buttonDel, buttonEdit], self.hoverButtonStd)
                        custom = {"buttonAdd": buttonAdd, "buttonDel": buttonDel, "buttonEdit": buttonEdit, **custom}
                    posY += 30

                    listbox = tk.Listbox(container)
                    listbox.configure(self.styleListBoxStd)
                    listbox.bind("<<ListboxSelect>>", lambda _, objectType=objectType, optionId=optionId: self.clickListboxSelect(objectType, optionId))
                    listbox.place(x=10, y=posY, width=260, height=150)
                    posY += 160

                    # wenn type[8:x] listbox -> extra fenster ...

                    if option["type"][8:] == "driver":
                        labelExpression = tk.Label(container, text="Expression:")
                        labelExpression.configure(self.styleLabel)
                        labelExpression.place(x=10, y=posY, height=20)
                        entryExpression = tk.Entry(container)
                        entryExpression.configure(self.styleEntryDriver)
                        entryExpression.bind("<Return>", self.updateData)
                        entryExpression.place(x=100, y=posY, height=20, width=115)
                        buttonChange = tk.Button(container, text="⚙", command=lambda objectType=objectType, optionId=optionId: self.clickDriverChange(objectType, optionId))
                        buttonChange.configure(self.styleButtonSmall)
                        buttonChange.place(x=220, y=posY, width=20, height=20)
                        buttonOk = tk.Button(container, text="Ok", command=self.updateData)
                        buttonOk.configure(self.styleButtonSmall)
                        buttonOk.place(x=245, y=posY, width=25, height=20)
                        widgetsSetHoverFunctions([buttonOk, buttonChange], self.hoverButtonStd)

                        for name in curObject.get(optionId, {}):
                            listbox.insert(tk.END, name)

                        posY += 35
                        custom = {"labelExpression": labelExpression, "entry": entryExpression, "buttonChange": buttonChange, "buttonOk": buttonOk, **custom}

                    widgets[optionId] = {"label": label, "listbox": listbox, **custom}

                elif option["type"][:5] == "array":
                    contents = curObject.get(optionId, option["num"] * [types[curObjectType][optionId]["default"]])
                    label = tk.Label(container, text=option["name"])
                    label.configure(self.styleLabelBig)
                    label.place(x=10, y=posY)
                    posY += 30

                    names = option.get("names")
                    labels = {}

                    entries = {}
                    for i in range(option["num"]):
                        if option["type"][6:] == "float":
                            entry = FloatEntry(container)
                            entry.configure(self.styleEntryFloat)
                            entry.bind("<Return>", self.updateData)
                            entry.bind("<Tab>", self.updateData)
                            if names:
                                entry.place(x=30, y=posY, width=210, height=20)
                                labelName = tk.Label(container, text=names[i])
                                labelName.configure(self.styleLabelSmall)
                                labelName.place(x=10, y=posY, height=20)
                                labels["label" + str(i)] = labelName
                            else:
                                entry.place(x=10, y=posY, width=230, height=20)
                            entry.insert(0, contents[i])
                            posY += 30
                            entries["entry" + str(i)] = entry

                        elif option["type"][6:] == "driver":
                            entry = tk.Entry(container)
                            entry.configure(self.styleEntryDriver)
                            entry.bind("<Return>", self.updateData)
                            entry.bind("<Tab>", self.updateData)
                            if names:
                                entry.place(x=30, y=posY, width=180, height=20)
                                labelName = tk.Label(container, text=names[i])
                                labelName.configure(self.styleLabelSmall)
                                labelName.place(x=10, y=posY, height=20)
                                labels["label" + str(i)] = labelName
                            else:
                                entry.place(x=10, y=posY, width=200, height=20)
                            entry.insert(0, contents[i])
                            buttonChange = tk.Button(container, text="⚙", command=lambda objectType=objectType, optionId=optionId, i=i: self.clickDriverChange(objectType, optionId, i))
                            buttonChange.configure(self.styleButtonSmall)
                            buttonChange.place(x=215, y=posY, width=20, height=20)
                            buttonOk = tk.Button(container, text="Ok", command=self.updateData)
                            buttonOk.configure(self.styleButtonSmall)
                            buttonOk.place(x=240, y=posY, height=20)
                            widgetsSetHoverFunctions([buttonChange, buttonOk], self.hoverButtonStd)
                            posY += 30
                            entries["entry" + str(i)] = entry
                            entries["buttonChange" + str(i)] = buttonChange
                            entries["buttonOk" + str(i)] = buttonOk

                    widgets[optionId] = {"label": label, **labels, **entries}

            self.framesOptions[objectType]["container"].height(posY)
            self.widgetsObjects[objectType] = widgets

        self.updateData()

    def updateData(self, _=None):
        for objectType in self.template["options"]:
            listbox = self.framesOptions[objectType]["listbox"]
            if not listbox.curselection():
                continue

            curObjectId = listbox.get(listbox.curselection()[0])
            curObject = self.objects[objectType][curObjectId]
            curObjectType = curObject["type"]

            types = dataStandardGetObjectTypes(objectType)

            for optionId in self.widgetsObjects[objectType]:
                option = types[curObjectType][optionId]
                widgets = self.widgetsObjects[objectType][optionId]
                value = curObject.get(optionId, "")
                if optionId == "name":
                    name = widgets["listmenu"].variable.get()
                    optionId = "type"  # save value of name in "type" key of object and not in "name" key
                    for value in types:  # convert "Default Camera" back to "standard" (name -> optionValue)
                        if types[value]["name"] == name:
                            break

                elif option["type"] == "checkmenu":
                    value = []
                    for name in widgets["menubutton"].values:
                        if widgets["menubutton"].values[name].get():
                            value.append(name)

                elif option["type"] == "listmenu":
                    value = widgets["menubutton"].variable.get()

                elif option["type"] == "driver":
                    value = widgets["entry"].get()
                    if not value: value = option["default"]

                elif option["type"] == "integer":
                    value = widgets["entry"].get()

                elif option["type"] == "float":
                    value = widgets["entry"].get()

                elif option["type"][:7] == "listbox":
                    value = curObject.get(optionId, {})
                    listboxObj = widgets["listbox"]
                    if listboxObj.curselection():
                        value[listboxObj.get(listboxObj.curselection()[0])] = widgets["entry"].get()

                elif option["type"][:5] == "array":
                    value = []
                    for i in range(option["num"]):
                        if option["type"][6:] == "float":
                            value.append(self.widgetsObjects[objectType][optionId]["entry" + str(i)].get())
                        elif option["type"][6:] == "driver":
                            v = self.widgetsObjects[objectType][optionId]["entry" + str(i)].get()
                            if not v: v = option["default"]
                            value.append(v)

                curObject[optionId] = value

        self.redrawObjects()

    def updateObjects(self):
        for optionId in self.framesOptions:
            option = self.framesOptions[optionId]["listbox"]
            index = 0
            if option.curselection():
                index = option.curselection()[0]
            option.delete(0, tk.END)
            for objectId in self.objects[optionId]:
                option.insert(tk.END, objectId)

            option.select_set(index)

    def redrawObjects(self):
        if not self.preview:
            return

        self.previewCanvas.delete("all")
        w, h = self.previewImage.width(), self.previewImage.height()
        self.previewCanvas.create_image(w / 2, h / 2, image=self.previewImage)

        for optionId in self.framesOptions:
            listbox = self.framesOptions[optionId]["listbox"]
            if not listbox.curselection():
                continue

            obj = self.objects[optionId][listbox.get(listbox.curselection()[0])]
            objTypes = dataStandardGetObjectTypes(optionId)
            objType = objTypes[obj["type"]]
            display = objType.get("display", "")
            if not display:
                continue
            elif display == "rectangle":
                pos = getEvalFromObj(obj, optionId, objType, "position", 3)
                rot = getEvalFromObj(obj, optionId, objType, "rotation", 3)
                dim = getFromObj(obj, optionId, objType, "dimensions", 2)
                drawRect3D(self.previewCanvas, pos, dim, rot, "red")
            elif display == "vector3d":
                pos = getEvalFromObj(obj, optionId, objType, "position", 3)
                rot = getEvalFromObj(obj, optionId, objType, "rotation", 3)
                dim = getEvalFromObj(obj, optionId, objType, "dimensions", 2)
                # size = evalDriver(obj.get("size", objType["size"]["default"]))
                drawVector3D(self.previewCanvas, pos, dim, rot, "blue")
            elif display == "vector3d+dir":
                pos = getEvalFromObj(obj, optionId, objType, "position", 3)
                rot = getEvalFromObj(obj, optionId, objType, "rotation", 3)
                dim = getFromObj(obj, optionId, objType, "dimensions", 2)
                drawVector3D(self.previewCanvas, pos, dim, rot, "blue")
                rot[0] -= 1.5708
                drawLine3D(self.previewCanvas, pos, 2, rot, "red")
            elif display == "circle":
                pos = getEvalFromObj(obj, optionId, objType, "position", 3)
                size = getEvalFromObj(obj, optionId, objType, "size")
                drawCircle3D(self.previewCanvas, pos, size, "yellow")
            elif display == "circle+dir":
                pos = getEvalFromObj(obj, optionId, objType, "position", 3)
                rot = getEvalFromObj(obj, optionId, objType, "rotation", 3)
                size = getEvalFromObj(obj, optionId, objType, "size")
                drawCircle3D(self.previewCanvas, pos, size, "yellow")
                rot[0] -= 1.5708
                drawLine3D(self.previewCanvas, pos, 10, rot, "red")

    def clickObjectOperation(self, operation, optionId):
        widget = self.framesOptions[optionId]["listbox"]
        if operation == "+":
            name = "Object"
            index = 0
            ext = ""
            while (name+ext) in self.objects[optionId]:
                index += 1
                ext = " " + str(index)
            self.objects[optionId][name+ext] = dataStandardGetObject(optionId)
            self.updateObjects()
            widget.select_clear(0, tk.END)
            widget.select_set(widget.get(0, tk.END).index(name+ext))
            self.clickListboxSelect(optionId)

        elif operation == "-":
            if not widget.curselection():
                return

            index = widget.curselection()[0]
            name = widget.get(index)
            self.objects[optionId].pop(name)
            self.updateObjects()
            self.clickListboxSelect(optionId)

        elif operation == "✎":
            if not widget.curselection():
                return

            name = widget.get(widget.curselection()[0])
            dialog = RenameDialog(self.window, "Rename", name)
            nameNew = dialog.value
            self.objects[optionId][nameNew] = self.objects[optionId].pop(name)
            self.updateObjects()
            widget.select_clear(0, tk.END)
            widget.select_set(widget.get(0, tk.END).index(nameNew))
            self.clickListboxSelect(optionId)

    def clickListboxSelect(self, objectType=None, optionId=None):
        if objectType and optionId:
            listbox = self.widgetsObjects[objectType][optionId]["listbox"]
            if not listbox.curselection():
                return

            listboxObj = self.framesOptions[objectType]["listbox"]
            curObject = self.objects[objectType][listboxObj.get(listboxObj.curselection()[0])]

            value = curObject[optionId].get(listbox.get(listbox.curselection()[0]), "0")
            self.widgetsObjects[objectType][optionId]["entry"].delete(0, tk.END)
            self.widgetsObjects[objectType][optionId]["entry"].insert(0, value)
        else:
            self.updateWidgets()

    def clickListboxAdd(self, objectType, optionId):
        listboxObj = self.framesOptions[objectType]["listbox"]
        if not listboxObj.curselection():
            return

        listboxObj = self.framesOptions[objectType]["listbox"]
        curObject = self.objects[objectType][listboxObj.get(listboxObj.curselection()[0])]

        name = "Element"
        ext = 0
        while name in curObject.get(optionId, {}):
            ext += 1
            name = "Element " + str(ext)

        value = dataStandardGetObjectTypes(objectType)[curObject["type"]][optionId]["default"]
        self.widgetsObjects[objectType][optionId]["entry"].delete(0, tk.END)
        self.widgetsObjects[objectType][optionId]["entry"].insert(0, value)
        values = curObject.get(optionId, {})
        values[name] = value
        curObject[optionId] = values

        self.updateWidgets()
        self.widgetsObjects[objectType][optionId]["listbox"].select_set(tk.END)

    def clickListboxRename(self, objectType, optionId):
        listbox = self.widgetsObjects[objectType][optionId]["listbox"]
        if not listbox.curselection():
            return

        listboxObj = self.framesOptions[objectType]["listbox"]
        curObject = self.objects[objectType][listboxObj.get(listboxObj.curselection()[0])]

        i = listbox.curselection()[0]
        name = listbox.get(i)
        title = "Rename: " + name
        dialog = RenameDialog(self.window, title, name)
        curObject[optionId][dialog.value] = curObject[optionId].pop(name)
        self.updateWidgets()
        self.widgetsObjects[objectType][optionId]["listbox"].select_set(i)

    def clickListboxRemove(self, objectType, optionId):
        listbox = self.widgetsObjects[objectType][optionId]["listbox"]
        if not listbox.curselection():
            return

        listboxObj = self.framesOptions[objectType]["listbox"]
        curObject = self.objects[objectType][listboxObj.get(listboxObj.curselection()[0])]

        i = listbox.curselection()[0]
        name = listbox.get(i)
        listbox.delete(i)
        curObject[optionId].pop(name)
        listbox.select_set(i)

    def clickListMenuSelect(self, _optionId):
        self.updateData()
        self.updateWidgets()

    def clickMenuButtonSelect(self, _optionId):
        self.updateData()
        self.updateWidgets()

    def clickDriverChange(self, objectType, optionId, index=-1):
        listbox = self.framesOptions[objectType]["listbox"]
        if not listbox.curselection():
            return

        curObject = self.objects[objectType][listbox.get(listbox.curselection()[0])]
        template = dataStandardGetObjectTypes(objectType)[curObject["type"]][optionId]
        name = "Edit Driver: " + template["name"]
        if index != -1:
            widget = self.widgetsObjects[objectType][optionId]["entry" + str(index)]
        else:
            widget = self.widgetsObjects[objectType][optionId]["entry"]
        expression = widget.get()

        varsGlobal = self.options["options"]["environments"]["variables"].keys()

        editor = EditorDriver(self.window, name, varsGlobal, expression, lambda name, text, objectType=objectType, optionId=optionId, index=index: self.returnDriverChange(objectType, optionId, text, index))
        editor.run()

    def returnDriverChange(self, objectType, optionId, text, index=-1):
        if index != -1:
            widget = self.widgetsObjects[objectType][optionId]["entry"+str(index)]
        else:
            widget = self.widgetsObjects[objectType][optionId]["entry"]
        widget.delete(0, tk.END)
        widget.insert(0, text)
        self.updateData()


class EditorObject:
    def __init__(self, root, objId, options, onclose=None):
        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("400x800")
        self.window.configure(self.styleWindow)

        self.objId = objId
        self.options = options
        self.optionsObj = options["objects"][objId]

        self.frameObjectTitle = tk.Frame(self.window)
        self.frameObjectTitle.configure(self.styleFrameOptions)
        self.frameObjectTitle.place(x=10, y=10, width=380, height=50)

        self.labelObjectTitle = tk.Label(self.frameObjectTitle, text=objId)
        self.labelObjectTitle.configure(self.styleLabelHeading)
        self.labelObjectTitle.place(x=10, y=10, width=360, height=30)

        self.frameObjectColorHelp = tk.Frame(self.window)
        self.frameObjectColorHelp.configure(self.styleFrameOptions)
        self.frameObjectColorHelp.place(x=10, y=70, width=380, height=85)

        self.labelObjectColorHelp = tk.Label(self.frameObjectColorHelp, text="Color Codes:")
        self.labelObjectColorHelp.configure(self.styleLabelSmall)
        self.labelObjectColorHelp.place(x=10, y=10)

        colorCodes = colorCodesCreate(self.frameObjectColorHelp, {" - Filepath": "#707020", " - Driver expression": "#902020", " - Integer": "#203890"})
        widgetsSetStyle(colorCodes.keys(), self.styleLabelMicro)
        widgetsPlace(colorCodes.values(), 10, 35, 10, 10, 5, "VERTICAL")
        widgetsPlace(colorCodes.keys(), 20, 35, None, 10, 5, "VERTICAL")

        self.frameObjectOptionsContainer = ScrollFrame(self.window)
        self.frameObjectOptionsContainer.strength = 0.6
        self.frameObjectOptionsContainer.configure(self.styleFrameOptions)
        self.frameObjectOptionsContainer.place(x=10, y=165, width=380, height=625)

        self.frameObjectOptions = self.frameObjectOptionsContainer.frame
        self.frameObjectOptions.configure(self.styleFrameOptions)

        self.objectTypes = dataStandardGetObjectTypes()
        self.objectNames = dataStandardGetObjectNames()

        self.labelObjectType = tk.Label(self.frameObjectOptions, text="Object Type")
        self.labelObjectType.configure(self.styleLabelStd)
        self.labelObjectType.place(x=10, y=10, height=30)

        self.menuObjectType = SelectionMenuRadio(self.frameObjectOptions)
        self.menuObjectType.configure(self.styleButtonMenuStd)
        self.menuObjectType.menu.configure(self.styleMenuStd)
        self.menuObjectType.add_options(self.objectNames.keys(), self.clickObjectType)
        self.menuObjectType.place(x=10, y=40, width=200)

        self.widgetsObjectOptions = {}

        self.window.update()
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))
        self.setTitle()
        self.updateAll()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#121212"
        }

        self.styleFrameOptions = {
            "background": "#202020"
        }

        self.styleLabelStd = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 15]
        }

        self.styleLabelSmall = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 12]
        }

        self.styleLabelMicro = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 8]
        }

        self.styleLabelHeading = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 20]
        }

        self.styleButtonMenuStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleButtonMenuHeading = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 15]
        }

        self.styleMenuStd = {
            "background": "#202020",
            "foreground": "#808080",
            "selectcolor": "#808080",
            "borderwidth": 0
        }

        self.styleEntryStd = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryFile = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "highlightbackground": "#404018",
            "highlightcolor": "#707020",
            "highlightthickness": 1,
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryInteger = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#182050",
            "highlightcolor": "#203890",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleEntryDriver = {
            "background": "#181818",
            "foreground": "#808080",
            "highlightbackground": "#501818",
            "highlightcolor": "#902020",
            "highlightthickness": 1,
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

        self.styleButtonStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 12]
        }
        self.hoverButtonStd = hoverCreateFunctions("#303030", "#424242")

        self.styleButtonBig = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 20]
        }

        self.styleButtonSmall = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#202020",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }

        self.styleLabelImg = {
            "background": "#181818",
        }

        self.styleListBoxStd = {
            "background": "#303030",
            "foreground": "#808080",
            "selectbackground": "#505050",
            "selectforeground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#909090",
            "selectborderwidth": 0,
            "relief": "flat",
            "exportselection": False,
            "font": ["Helvetica", 12]
        }

    def onclose(self, function=None):
        self.updateData()
        self.window.destroy()
        self.window.quit()
        if function:
            function(self.objId)

    def run(self):
        self.window.focus_force()
        self.window.mainloop()

    def setTitle(self):
        title = "Untitled"
        if self.objId:
            title = self.objId

        title += " - MEE"
        self.window.title(title)

    def updateAll(self):
        self.updateObjectType()

    def updateObjectType(self):
        text = self.objectTypes[self.optionsObj["type"]]["name"]
        self.menuObjectType.variable.set(text)
        self.menuObjectType.configure(text=text)
        self.updateObjectOptions()

    def updateObjectOptions(self):
        for option in self.widgetsObjectOptions:
            for widget in self.widgetsObjectOptions[option]:
                self.widgetsObjectOptions[option][widget].place_forget()
                self.widgetsObjectOptions[option][widget].destroy()

        self.widgetsObjectOptions = {}

        posY = 90
        objType = self.objectTypes[self.optionsObj["type"]]

        for optionId in objType:
            option = objType[optionId]
            if optionId == "name":
                continue

            elif option["type"] == "listmenu":
                text = self.optionsObj.get(optionId, option["options"][0])
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                menubutton = SelectionMenuRadio(self.frameObjectOptions, text=text)
                menubutton.configure(self.styleButtonMenuStd)
                menubutton.menu.configure(self.styleMenuStd)
                menubutton.add_options(option["options"])
                menubutton.variable.set(text)
                menubutton.place(x=10, y=posY, width=200)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"menubutton": menubutton, "label": label}

            elif option["type"] == "checkmenu":
                text = "<Select>"
                options = []
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                if isinstance(option["options"], str):
                    if option["options"][:3] == "rel":
                        path = option["options"][4:].split(":")
                        options = self.options
                        for part in path[:-1]:
                            options = options.get(part, {})

                        if path[-1][:2] == "id":
                            options = options.keys()
                        elif path[-1][:6] == "option":
                            name = path[-1][7:]
                            _options = []
                            for obj in options:
                                _options.append(obj[name])
                            options = _options

                elif isinstance(option["options"], list):
                    options = option["options"]

                menubutton = SelectionMenuCheck(self.frameObjectOptions, text=text)
                menubutton.configure(self.styleButtonMenuStd)
                menubutton.menu.configure(self.styleMenuStd)
                menubutton.add_options(options, self.updateData)
                for value in self.optionsObj.get(optionId, {}):
                    menubutton.values[value].set(True)
                menubutton.place(x=10, y=posY, width=200)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"menubutton": menubutton, "label": label}

            elif option["type"] == "directory":
                path = self.optionsObj.get(optionId, "")

                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameObjectOptions)
                entry.configure(self.styleEntryFile)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, path)
                entry.configure(state="readonly")

                buttonOpen = tk.Button(self.frameObjectOptions, text="➟", command=lambda optionId=optionId: self.clickFolderBrowse(optionId))
                buttonOpen.configure(self.styleButtonStd)
                buttonOpen.place(x=215, y=posY, width=20, height=20)
                widgetsSetHoverFunctions([buttonOpen], self.hoverButtonStd)
                posY += 30

                self.widgetsObjectOptions[optionId] = {"entry": entry, "buttonOpen": buttonOpen, "label": label}

            elif option["type"] == "file":
                path = self.optionsObj.get(optionId, "")

                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameObjectOptions)
                entry.configure(self.styleEntryFile)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, path)
                entry.configure(state="readonly")

                buttonOpen = tk.Button(self.frameObjectOptions, text="➟", command=lambda optionId=optionId: self.clickFileBrowse(optionId))
                buttonOpen.configure(self.styleButtonStd)
                buttonOpen.place(x=215, y=posY, width=20, height=20)
                widgetsSetHoverFunctions([buttonOpen], self.hoverButtonStd)
                posY += 30

                self.widgetsObjectOptions[optionId] = {"entry": entry, "buttonOpen": buttonOpen, "label": label}

            elif option["type"] == "driver":
                text = self.optionsObj.get(optionId, option["default"])
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameObjectOptions)
                entry.configure(self.styleEntryDriver)
                entry.bind("<Return>", self.updateData)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, text)
                buttonChange = tk.Button(self.frameObjectOptions, text="⚙", command=lambda optionId=optionId: self.clickDriverChange(optionId))
                buttonChange.configure(self.styleButtonSmall)
                buttonChange.place(x=215, y=posY, width=20, height=20)
                buttonOk = tk.Button(self.frameObjectOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                buttonOk.place(x=240, y=posY, height=20)
                widgetsSetHoverFunctions([buttonChange, buttonOk], self.hoverButtonStd)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"entry": entry, "label": label, "buttonChange": buttonChange, "buttonOk": buttonOk}

            elif option["type"] == "string":
                text = self.optionsObj.get(optionId, "")
                print(text)
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = tk.Entry(self.frameObjectOptions)
                entry.configure(self.styleEntryStd)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.insert(0, text)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"entry": entry, "label": label}

            elif option["type"] == "integer":
                text = self.optionsObj.get(optionId, option["default"])
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = IntEntry(self.frameObjectOptions)
                entry.configure(self.styleEntryInteger)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.variable.set(text)
                buttonOk = tk.Button(self.frameObjectOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                widgetsSetHoverFunctions([buttonOk], self.hoverButtonStd)
                buttonOk.place(x=215, y=posY, height=20)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"entry": entry, "label": label, "buttonOk": buttonOk}

            elif option["type"] == "real":
                text = self.optionsObj.get(optionId, option["default"])
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                posY += 30

                entry = FloatEntry(self.frameObjectOptions)
                entry.configure(self.styleEntryStd)
                entry.place(x=10, y=posY, width=200, height=20)
                entry.variable.set(text)
                buttonOk = tk.Button(self.frameObjectOptions, text="Ok", command=self.updateData)
                buttonOk.configure(self.styleButtonSmall)
                widgetsSetHoverFunctions([buttonOk], self.hoverButtonStd)
                buttonOk.place(x=215, y=posY, height=20)
                posY += 35

                self.widgetsObjectOptions[optionId] = {"entry": entry, "label": label, "buttonOk": buttonOk}

            elif option["type"][:7] == "listbox":
                custom = {}
                label = tk.Label(self.frameObjectOptions, text=option["name"])
                label.configure(self.styleLabelStd)
                label.place(x=10, y=posY)
                if option["type"][8:] == "driver":
                    buttonAdd = tk.Button(self.frameObjectOptions, text="+", command=lambda optionId=optionId: self.clickListBoxAdd(optionId))
                    buttonAdd.configure(self.styleButtonBig)
                    buttonAdd.place(x=285, y=posY, width=25, height=25)
                    buttonDel = tk.Button(self.frameObjectOptions, text="-", command=lambda optionId=optionId: self.clickListBoxRemove(optionId))
                    buttonDel.configure(self.styleButtonBig)
                    buttonDel.place(x=315, y=posY, width=25, height=25)
                    buttonEdit = tk.Button(self.frameObjectOptions, text="✎", command=lambda optionId=optionId: self.clickListBoxRename(optionId))
                    buttonEdit.configure(self.styleButtonBig)
                    buttonEdit.place(x=345, y=posY, width=25, height=25)
                    widgetsSetHoverFunctions([buttonAdd, buttonDel, buttonEdit], self.hoverButtonStd)
                    custom = {"buttonAdd": buttonAdd, "buttonDel": buttonDel, "buttonEdit": buttonEdit, **custom}
                posY += 30

                listbox = tk.Listbox(self.frameObjectOptions)
                listbox.configure(self.styleListBoxStd)
                listbox.bind("<<ListboxSelect>>", lambda _, optionId=optionId: self.clickListBox(optionId))
                listbox.place(x=10, y=posY, width=360, height=150)
                posY += 160

                # wenn type[8:x] listbox -> extra fenster ...
                if option["type"][8:] == "driver":
                    labelExpression = tk.Label(self.frameObjectOptions, text="Expression:")
                    labelExpression.configure(self.styleLabelSmall)
                    labelExpression.place(x=10, y=posY, height=20)
                    entryExpression = tk.Entry(self.frameObjectOptions)
                    entryExpression.configure(self.styleEntryDriver)
                    entryExpression.bind("<Return>", self.updateData)
                    entryExpression.place(x=100, y=posY, height=20, width=215)
                    buttonChange = tk.Button(self.frameObjectOptions, text="⚙",
                                             command=lambda optionId=optionId: self.clickDriverChange(optionId))
                    buttonChange.configure(self.styleButtonSmall)
                    buttonChange.place(x=320, y=posY, width=20, height=20)
                    buttonOk = tk.Button(self.frameObjectOptions, text="Ok", command=self.updateData)
                    buttonOk.configure(self.styleButtonSmall)
                    buttonOk.place(x=345, y=posY, width=25, height=20)
                    widgetsSetHoverFunctions([buttonOk, buttonChange], self.hoverButtonStd)
                    for name in self.optionsObj.get(optionId, {}):
                        listbox.insert(tk.END, name)
                    posY += 35
                    custom = {"labelExpression": labelExpression, "entry": entryExpression, "buttonChange": buttonChange, "buttonOk": buttonOk, **custom}

                self.widgetsObjectOptions[optionId] = {"label": label, "listbox": listbox, **custom}

        self.frameObjectOptionsContainer.height(posY + 5)
        self.updateData()

    def updateData(self, _=None):
        objType = self.objectTypes[self.optionsObj["type"]]
        for optionId in self.widgetsObjectOptions:
            option = objType[optionId]
            widgets = self.widgetsObjectOptions[optionId]
            value = None
            if option["type"] == "directory":
                value = widgets["entry"].get()

            elif option["type"] == "listmenu":
                value = widgets["menubutton"].variable.get()

            elif option["type"] == "driver":
                value = widgets["entry"].get()

            elif option["type"] == "string":
                value = widgets["entry"].get()

            elif option["type"] == "integer":
                value = widgets["entry"].get()

            elif option["type"] == "real":
                value = widgets["entry"].get()

            elif option["type"] == "directory":
                value = widgets["entry"].get()

            elif option["type"] == "file":
                value = widgets["entry"].get()

            elif option["type"] == "checkmenu":
                value = []
                for name in widgets["menubutton"].values:
                    if widgets["menubutton"].values[name].get():
                        value.append(name)

            elif option["type"][:7] == "listbox":
                if not widgets["listbox"].curselection():
                    continue

                if option["type"][8:] == "driver":
                    value = self.optionsObj.get(optionId, {})
                    value[widgets["listbox"].get(widgets["listbox"].curselection()[0])] = widgets["entry"].get()
            self.optionsObj[optionId] = value

    def clickObjectType(self, title):
        self.updateData()
        self.optionsObj["type"] = self.objectNames[title]
        self.updateObjectType()

    def clickDriverChange(self, optionId):
        name = "Edit Driver: " + self.objectTypes[self.optionsObj["type"]][optionId]["name"]
        varsGlobal = self.options["options"]["objects"]["variables"].keys()
        varsEnv = self.optionsObj["variables"].keys()
        variables = list(varsEnv) + list(varsGlobal)
        expression = self.widgetsObjectOptions[optionId]["entry"].get()
        editor = EditorDriver(self.window, name, variables, expression, self.exitDriverChange)
        editor.run()

    def exitDriverChange(self, name, value):
        optionId = ""
        options = self.objectTypes[self.optionsObj["type"]]
        for optionId in options:
            if optionId == "name":
                continue
            if name[13:] == options[optionId]["name"]:
                break
        self.widgetsObjectOptions[optionId]["entry"].delete(0, tk.END)
        self.widgetsObjectOptions[optionId]["entry"].insert(0, value)
        self.updateData()

    def clickListBox(self, optionId):
        widget = self.widgetsObjectOptions[optionId]["listbox"]
        if not widget.curselection():
            return

        name = widget.get(widget.curselection()[0])
        if self.objectTypes[self.optionsObj["type"]][optionId]["type"][8:] == "driver":
            value = self.optionsObj[optionId][name]
            self.widgetsObjectOptions[optionId]["entry"].delete(0, tk.END)
            self.widgetsObjectOptions[optionId]["entry"].insert(0, value)

    def clickListBoxAdd(self, optionId):
        value = self.optionsObj.get(optionId, {})
        name = "Element"
        index = 0
        ext = ""
        while name + ext in self.optionsObj.get(optionId, {}):
            index += 1
            ext = str(index)
        value[name + ext] = "0"
        self.optionsObj[optionId] = value
        self.updateObjectOptions()
        self.widgetsObjectOptions[optionId]["listbox"].select_set(tk.END)
        self.clickListBox(optionId)

    def clickListBoxRemove(self, optionId):
        widget = self.widgetsObjectOptions[optionId]["listbox"]
        if not self.widgetsObjectOptions[optionId]["listbox"].curselection():
            return

        widget.delete(widget.curselection()[0])
        self.widgetsObjectOptions[optionId]["entry"].delete(0, tk.END)
        self.optionsObj[optionId].pop(widget.get(widget.curselection()[0]))

    def clickListBoxRename(self, optionId):
        widget = self.widgetsObjectOptions[optionId]["listbox"]
        if not self.widgetsObjectOptions[optionId]["listbox"].curselection():
            return

        name = widget.get(widget.curselection()[0])
        dialog = RenameDialog(self.window, "Rename", name)
        nameNew = dialog.value
        self.optionsObj[optionId][nameNew] = self.optionsObj[optionId].pop(name)
        self.updateObjectOptions()

    def clickFolderBrowse(self, optionId):
        options = {"parent": self.window, "title": "Open directory"}
        path = askdirectory(**options)
        if path:
            self.optionsObj[optionId] = path
        self.updateObjectOptions()

    def clickFileBrowse(self, optionId):
        filetypes = self.objectTypes[self.optionsObj["type"]][optionId].get("filetypes", [])
        filetypes.append(["All", "*.*"])
        options = {"parent": self.window, "title": "Open file", "filetypes": filetypes}
        path = askopenfilename(**options)
        if path:
            self.optionsObj[optionId] = path
        self.updateObjectOptions()


class EditorDriver:
    def __init__(self, root=None, name="", variables=None, expression="", onclose=None):
        self._init_styles()

        if root:
            self.window = tk.Toplevel(root)
        else:
            self.window = tk.Tk()

        self.name = name
        self.variables = ["label", "frame", "self"]
        if variables:
            self.variables += variables

        self.window.title(name)
        self.window.geometry("350x180")
        self.window.resizable(False, False)
        self.window.configure(self.styleWindow)

        self.frameDriver = tk.Frame(self.window)
        self.frameDriver.configure(self.styleFrameOptions)
        self.frameDriver.place(x=10, y=10, width=330, height=160)

        self.labelExpression = tk.Label(self.frameDriver, text="Expression:")
        self.labelExpression.configure(self.styleLabelStd)
        self.labelExpression.place(x=10, y=10)

        self.entryExpression = tk.Entry(self.frameDriver)
        self.entryExpression.configure(self.styleEntryStd)
        self.entryExpression.place(x=10, y=40, width=310, height=25)
        self.entryExpression.insert(0, expression)

        self.buttonAddVariable = SelectionMenu(self.frameDriver, text="Add global variable")
        self.buttonAddVariable.add_options(self.variables, self.clickAddVariable)
        self.buttonAddVariable.set_styles(self.styleButtonMenuStd, self.styleMenuStd)
        self.buttonAddVariable.place(x=10, y=80, width=200, height=30)

        self.functions = {"Random (0-1)": "random(self, frame)", "Absolute": "abs(x)", "Minimum": "min(a, b)", "Maximum": "max(a, b)"}

        self.buttonAddFunction = SelectionMenu(self.frameDriver, text="Add function")
        self.buttonAddFunction.add_options(self.functions.keys(), self.clickAddFunction)
        self.buttonAddFunction.set_styles(self.styleButtonMenuStd, self.styleMenuStd)
        self.buttonAddFunction.place(x=10, y=120, width=200, height=30)

        self.window.update()
        if root:
            self.window.grab_set()
        self.window.focus_force()
        self.window.title(name)
        self.window.protocol("WM_DELETE_WINDOW", lambda: self.onclose(onclose))

    def onclose(self, function=None):
        text = self.entryExpression.get()
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()
        if function:
            function(self.name, text)

    def run(self):
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#121212"
        }

        self.styleFrameOptions = {
            "background": "#202020"
        }

        self.styleLabelStd = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 15]
        }

        self.styleEntryStd = {
            "background": "#181818",
            "foreground": "#808080",
            "readonlybackground": "#181818",
            "disabledforeground": "#606060",
            "insertbackground": "#909090",
            "highlightbackground": "#606060",
            "highlightcolor": "#808080",
            "highlightthickness": 1,
            "relief": "flat",
            "font": ["Helvetica", 12]
        }

        self.styleButtonMenuStd = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#424242",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "relief": "flat",
            "font": ["Helvetica", 12]
        }

        self.styleMenuStd = {
            "background": "#202020",
            "foreground": "#808080",
            "selectcolor": "#808080",
            "borderwidth": 0
        }

    def clickAddVariable(self, name):
        cursor = self.entryExpression.index(tk.INSERT)
        self.entryExpression.insert(cursor, name)

    def clickAddFunction(self, name):
        cursor = self.entryExpression.index(tk.INSERT)
        self.entryExpression.insert(cursor, self.functions[name])


class WarningDialog:
    def __init__(self, root, title, text, answers=None, default=""):
        if not answers:
            answers = ["Ok"]

        self.value = default

        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("280x100")
        self.window.resizable(False, False)
        self.window.title(title)
        self.window.configure(self.styleWindow)
        self.window.bind("<Key>", self.pressKey)

        question = tk.Label(self.window, text="?")
        question.configure(self.styleQuestionMark)
        question.place(x=10, y=10, width=50, height=50)

        label = tk.Label(self.window, text=text)
        label.configure(self.styleMessage)
        label.place(x=70, y=10, width=200, height=50)

        buttons = buttonsCreate(self.window, answers, self.returnChange)
        widgetsPlace(buttons.values(), 280-(len(answers) * (70+10)), 70, 70, 20, 10)
        widgetsSetStyle(buttons.values(), self.styleButton)
        widgetsSetHoverFunctions(buttons.values(), self.hoverButton)

        self.window.update()
        self.window.bell()
        self.window.grab_set()
        self.window.focus_force()
        if default:
            buttons[default].focus_set()
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#202020"
        }

        self.styleQuestionMark = {
            "background": "#202020",
            "foreground": "#D0B030",
            "font": ["Helvectica", 45]
        }

        self.styleMessage = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleButton = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#121212",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }
        self.hoverButton = hoverCreateFunctions("#303030", "#404040")

    def pressKey(self, event):
        if event.char == chr(27):
            self.returnChange(self.value)

    def returnChange(self, value):
        self.value = value
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()


class ErrorDialog:
    def __init__(self, root, title, text, answers=None, default=""):
        if not answers:
            answers = ["Ok"]

        self.value = default

        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("280x100")
        self.window.resizable(False, False)
        self.window.title(title)
        self.window.configure(self.styleWindow)
        self.window.bind("<Key>", self.pressKey)

        question = tk.Label(self.window, text="!")
        question.configure(self.styleExclamationMark)
        question.place(x=10, y=10, width=50, height=50)

        label = tk.Label(self.window, text=text)
        label.configure(self.styleMessage)
        label.place(x=70, y=10, width=200, height=50)

        buttons = buttonsCreate(self.window, answers, self.returnChange)
        widgetsPlace(buttons.values(), 280-(len(answers) * (70+10)), 70, 70, 20, 10)
        widgetsSetStyle(buttons.values(), self.styleButton)
        widgetsSetHoverFunctions(buttons.values(), self.hoverButton)

        self.window.update()
        self.window.bell()
        self.window.grab_set()
        self.window.focus_force()
        if default:
            buttons[default].focus_set()
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#202020"
        }

        self.styleExclamationMark = {
            "background": "#202020",
            "foreground": "#D84040",
            "font": ["Helvectica", 45]
        }

        self.styleMessage = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleButton = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#121212",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }
        self.hoverButton = hoverCreateFunctions("#303030", "#404040")

    def pressKey(self, event):
        if event.char == chr(27):
            self.returnChange(self.value)

    def returnChange(self, value):
        self.value = value
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()


class ErrorShowDialog:
    def __init__(self, root, title, texts, answers=None, default=""):
        if not answers:
            answers = ["Ok"]

        self.value = default

        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("450x200")
        self.window.resizable(False, False)
        self.window.title(title)
        self.window.configure(self.styleWindow)
        self.window.bind("<Key>", self.pressKey)

        question = tk.Label(self.window, text="!")
        question.configure(self.styleExclamationMark)
        question.place(x=10, y=10, width=50, height=50)

        textfield = ScrolledText(self.window)
        textfield.configure(self.styleScrolledText)
        textfield.place(x=70, y=10, width=370, height=150)

        for text in texts:
            textfield.insert(tk.END, text)

        buttons = buttonsCreate(self.window, answers, self.returnChange)
        widgetsPlace(buttons.values(), 280-(len(answers) * (70+10)), 170, 70, 20, 10)
        widgetsSetStyle(buttons.values(), self.styleButton)
        widgetsSetHoverFunctions(buttons.values(), self.hoverButton)

        self.window.update()
        self.window.bell()
        self.window.grab_set()
        self.window.focus_force()
        if default:
            buttons[default].focus_set()
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#202020"
        }

        self.styleExclamationMark = {
            "background": "#202020",
            "foreground": "#D84040",
            "font": ["Helvectica", 45]
        }

        self.styleMessage = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleButton = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#121212",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }
        self.hoverButton = hoverCreateFunctions("#303030", "#404040")

        self.styleScrolledText = {
            "background": "#121212",
            "foreground": "#B0B0B0",
            "relief": "flat",
            "selectbackground": "#505050",
            "insertbackground": "#909090"
        }

    def pressKey(self, event):
        if event.char == chr(27):
            self.returnChange(self.value)

    def returnChange(self, value):
        self.value = value
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()


class RenameDialog:
    def __init__(self, root, title, name):
        self.value = name

        self._init_styles()

        self.window = tk.Toplevel(root)
        self.window.geometry("170x70")
        self.window.resizable(False, False)
        self.window.title(title)
        self.window.configure(self.styleWindow)
        self.window.bind("<Key>", self.pressKey)

        label = tk.Label(self.window, text="Rename:")
        label.configure(self.styleMessage)
        label.place(x=10, y=10, height=20)

        self.entry = tk.Entry(self.window)
        self.entry.configure(self.styleEntry)
        self.entry.place(x=70, y=10, width=90, height=20)
        self.entry.insert(0, name)
        self.entry.select_range(0, tk.END)

        buttons = buttonsCreate(self.window, ["Ok", "Cancel"], self.returnChange)
        widgetsPlace(buttons.values(), 170-(2 * (70+10)), 40, 70, 20, 10)
        widgetsSetStyle(buttons.values(), self.styleButton)
        widgetsSetHoverFunctions(buttons.values(), self.hoverButton)

        self.window.update()
        self.window.bell()
        self.window.grab_set()
        self.window.focus_force()
        self.entry.focus_set()
        self.window.mainloop()

    def _init_styles(self):
        self.styleWindow = {
            "background": "#202020"
        }

        self.styleMessage = {
            "background": "#202020",
            "foreground": "#808080",
            "font": ["Helvetica", 10]
        }

        self.styleButton = {
            "background": "#303030",
            "foreground": "#808080",
            "activebackground": "#121212",
            "activeforeground": "#909090",
            "borderwidth": 0,
            "font": ["Helvetica", 10]
        }
        self.hoverButton = hoverCreateFunctions("#303030", "#404040")

        self.styleEntry = {
            "background": "#181818",
            "foreground": "#808080",
            "insertbackground": "#909090",
            "relief": "flat",
            "font": ["Helvetica", 10]
        }

    def pressKey(self, event):
        if event.char == chr(27):
            self.entry.delete(0, tk.END)
            self.entry.insert(0, self.value)
            self.returnChange()
        if event.char == chr(13):
            self.returnChange()

    def returnChange(self, _=None):
        self.value = self.entry.get()
        self.window.grab_release()
        self.window.destroy()
        self.window.quit()


class SelectionMenu(tk.Menubutton):
    def __init__(self, root, **config):
        super().__init__(root, **config)
        self.menu = tk.Menu(self, tearoff=0)
        self["menu"] = self.menu

    def set_styles(self, styleButton=None, styleMenu=None):
        if styleButton:
            self.configure(styleButton)
        if styleMenu:
            self.menu.configure(styleMenu)

    def add_options(self, options, command):
        for option in options:
            self.menu.add_command(label=option, command=lambda key=option: command(key))

    def add_option(self, option, command):
        self.menu.add_command(label=option, command=lambda key=option: command(key))

    def delete_all(self):
        self.menu.delete(0, tk.END)


class SelectionMenuCheck(tk.Menubutton):
    def __init__(self, root, **config):
        super().__init__(root, **config)
        self.menu = tk.Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.values = {}

    def set_styles(self, styleButton=None, styleMenu=None):
        if styleButton:
            self.configure(styleButton)
        if styleMenu:
            self.menu.configure(styleMenu)

    def add_options(self, options, command=None):
        for option in options:
            var = tk.BooleanVar(self)
            if command:
                self.menu.add_checkbutton(label=option, variable=var, command=lambda key=option: command(key))
            else:
                self.menu.add_checkbutton(label=option, variable=var)
            self.values[option] = var

    def add_option(self, option, command=None):
        var = tk.BooleanVar(self)
        if command:
            self.menu.add_checkbutton(label=option, variable=var, command=lambda key=option: command(key))
        else:
            self.menu.add_checkbutton(label=option, variable=var)
        self.values[option] = var

    def delete_all(self):
        self.values = {}
        self.menu.delete(0, tk.END)

    def get_values(self):
        ret = []
        for key in self.values:
            if self.values[key].get():
                ret.append(key)
        return ret


class SelectionMenuRadio(tk.Menubutton):
    def __init__(self, root, **config):
        super().__init__(root, **config)
        self.menu = tk.Menu(self, tearoff=0)
        self["menu"] = self.menu
        self.variable = tk.StringVar(self)

    def set_styles(self, styleButton=None, styleMenu=None):
        if styleButton:
            self.configure(styleButton)
        if styleMenu:
            self.menu.configure(styleMenu)

    def add_options(self, options, command=None, default=-1):
        for option in options:
            if command:
                self.menu.add_radiobutton(label=option, value=option, variable=self.variable, command=lambda key=option: command(key))
            else:
                self.menu.add_radiobutton(label=option, value=option, variable=self.variable)

        if default != -1:
            self.variable.set(options[default])

    def add_option(self, option, command=None, default=False):
        if command:
            self.menu.add_radiobutton(label=option, value=option, variable=self.variable, command=lambda key=option: command(key))
        else:
            self.menu.add_radiobutton(label=option, value=option, variable=self.variable)

        if default:
            self.variable.set(option)

    def delete_all(self):
        self.variable.set("")
        self.menu.delete(0, tk.END)

    def set_value(self, value):
        self.variable.set(value)

    def get_values(self):
        return self.variable.get()


class ScrollFrame(tk.Frame):
    def __init__(self, root):
        super().__init__(root)
        self.frame = tk.Frame(self)

        self.bind_all("<MouseWheel>", self._mousewheel, True)

        self.heightInner = 0
        self.heightOuter = 0
        self.maxY = 0
        self.posY = 0
        self.strength = 1.5

    def _mousewheel(self, event):
        widget = event.widget
        while hasattr(widget, "master"):
            if widget == self:
                self.posY = round(max(min(self.posY + self.strength*event.delta, 0), self.maxY))
                self.frame.place_configure(y=self.posY)
                break
            else:
                widget = widget.master

    def configure(self, cnf=None, **kwargs):
        super().configure(cnf, **kwargs)
        self.frame.configure(cnf, **kwargs)

    def place(self, cnf=None, **kw):
        super().place(cnf, **kw)
        self.frame.place(x=0, y=self.posY, width=kw["width"], height=kw["height"])
        self.heightInner = kw["height"]
        self.heightOuter = kw["height"]

    def height(self, height):
        self.frame.place_configure(height=height)
        self.heightInner = height
        self.maxY = min(0, self.heightOuter - self.heightInner)


class Tooltip(tk.Frame):
    def __init__(self, root, text, **kw):
        super().__init__(root, **kw)
        self.label = tk.Label(self, text=text)
        self.label.place(x=5, y=5)


class IntEntry(tk.Entry):
    def __init__(self, root, **kw):
        super().__init__(root, **kw)
        self.variable = tk.StringVar(self)
        self.variable.trace("w", self.checkVar)
        self.configure(textvariable=self.variable)

    def checkVar(self, *_):
        var = self.variable.get()
        if var == "":
            return

        try:
            int(var)
        except:
            self.variable.set(var[:-1])

    def get(self):
        if not self.variable.get():
            self.variable.set("0")
        return int(self.variable.get())


class FloatEntry(tk.Entry):
    def __init__(self, root, **kw):
        super().__init__(root, **kw)
        self.variable = tk.StringVar(self)
        self.variable.trace("w", self.checkVar)
        self.configure(textvariable=self.variable)

    def checkVar(self, *_):
        var = self.variable.get()
        if var == "":
            return

        if var[-1] == ",":
            self.variable.set(var[:-1] + ".")

        if var == ".":
            return

        try:
            float(var)
        except:
            self.variable.set(var[:-1])

    def get(self):
        if not self.variable.get():
            self.variable.set("0")
        return float(self.variable.get())


if __name__ == "__main__":
    p = Program()
    p.run()
