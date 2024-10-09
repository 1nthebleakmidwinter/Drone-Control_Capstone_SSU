import time
import tkinter as tk
from tkinter import messagebox
from tkinter import Event
from PIL import Image, ImageTk
import os
import ray
from rayengine import Engine
import rayengine as kp
from random import randint
from math import sin, cos, radians
import datetime

class Application(tk.Tk) :

    def __init__(self) :
        super().__init__()

        self._target = None
        self._reserved_site = None
        self._tolerance_range = [48000, 52000]
        self._duplicate_check = 0
        self._sub_engines = None
        self._engine_types = ['drone', 'frame', 'fire detection']

        self._mode = 'idling'
        self._ctrl_types = ['idling', 'direct', 'auto', 'tracking']

        self._appLogo = tk.PhotoImage(file = 'C:/DCS/applogo.png')

        self.appBg = Image.open('C:/DCS/appbg.png')
        self.listBg = Image.open('C:/DCS/statelist.png')
        self.listBgSize = self.listBg.size
        self.listBg = self.listBg.resize((int(self.listBgSize[0]/3), int(self.listBgSize[1]/2.7)))
        self.appBg.paste(self.listBg, (660, 20))
        self._appBg = ImageTk.PhotoImage(self.appBg)

        self._count = 0
        self._ssid = 'RMTT-3B3E92'
        self._connectionCode = False
        self._padCode = False
        self._trigger = True
        self._trg1 = True
        self._trg2 = True
        self._tracking = False
        self._info = None
        self._autoSpeed = 30
        self.wm_iconphoto(False, self._appLogo)
        self.title('Drone Control Station')
        self.geometry('1600x600')
        self.resizable(width = tk.FALSE, height = tk.FALSE)

        self._appBgLabel = tk.Label(self, image = self._appBg)
        self._stateLabel = tk.Label(self, relief = 'ridge', borderwidth = 5, text = 'Current Drone State', font = 'default 15', bg = '#d2d2d2', width = 20, height = 1)
        self._modeLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Current Mode', font = 'default 15', bg = '#d2d2d2', width = 11, height = 1)
        self._batteryLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Remaining Battery', font = 'default 15', bg = '#d2d2d2', width = 14, height = 1)
        self._tofLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Distance of the front', font = 'default 15', bg = '#d2d2d2', width = 17, height = 1)
        self._heightLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Current Height', font = 'default 15', bg = '#d2d2d2', width = 11, height = 1)
        self._currentSiteLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Last Site', font = 'default 15', bg = '#d2d2d2', width = 11, height = 1)
        self._reservedSiteLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Reserved Site', font = 'default 15', bg = '#d2d2d2', width = 12, height = 1)
        self._targetLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Target', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._fireLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Fire detected', font = 'default 15', bg = '#d2d2d2', width = 14, height = 1)
        self._currentMode = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._currentBattery = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._currentTof = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._currentHeight = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._currentSite = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._reservedSite = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 15', bg = '#d2d2d2', width = 8, height = 1)
        self._currentTarget = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'None', font = 'default 12', bg = '#d2d2d2', width = 12, height = 1)
        self._fireDetected = tk.Label(self, relief = 'solid', borderwidth = 2, font = 'default 15', bg = '#00ff00', width = 8, height = 1)
        self._modeListLabel2 = tk.Label(self, relief = 'ridge', borderwidth = 5, font = 'default 15', bg = '#d2d2d2', width = 12, height = 13)
        self._modeListLabel = tk.Label(self, relief = 'ridge', borderwidth = 5, text = 'Mode List', font = 'default 15', bg = '#d2d2d2', width = 10, height = 1)
        self._autolistLabel = tk.Label(self, bg = '#1f1f1f', width = 18, height = 8)
        self._spdsetLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Auto mode speed setting', font = 'default 16', fg = 'white', bg = '#2d2d2d', width = 20, height = 1)
        self._spdLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = '25 cm/s', font = 'default 16', fg = 'white', bg = '#2d2d2d', width = 7, height = 1)
        self._rsvLabel2 = tk.Label(self, relief = 'ridge', borderwidth = 5, font = 'default 15', bg = '#d2d2d2', width = 40, height = 2)
        self._rsvLabel = tk.Label(self, relief = 'ridge', borderwidth = 5, text = 'Reservation', font = 'default 15', bg = '#d2d2d2', width = 11, height = 1)
        self._rsvSiteLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Next site', font = 'default 15', bg = '#d2d2d2', width = 7, height = 1)
        self._rsvTargetLabel = tk.Label(self, relief = 'solid', borderwidth = 2, text = 'Target', font = 'default 15', bg = '#d2d2d2', width = 15, height = 1)

        self._scroll = tk.Scrollbar(self, orient='vertical')
        self._log = tk.Listbox(self, yscrollcommand = self._scroll.set, width = 90, height = 16)
        self._scroll.config(command=self._log.yview)

        self._rsvSiteEnt = tk.Entry(self, font = 'default 15', width = 2)
        self._rsvTargetEnt = tk.Entry(self, font = 'default 15', width = 13)

        self._rsvSiteEnt.bind("<Return>", self.set_site)
        self._rsvTargetEnt.bind("<Return>", self.set_target)

        self._scale = 2.5
        self._map = tk.Canvas(self, width = 200 * self._scale, height = 200 * self._scale, bg = '#aaaaaa')
        self._pad1x = 150 * self._scale
        self._pad1y = 150 * self._scale
        self._pad2x = 150 * self._scale
        self._pad2y = 50 * self._scale
        self._pad3x = 50 * self._scale
        self._pad3y = 50 * self._scale
        self._pad4x = 50 * self._scale
        self._pad4y = 150 * self._scale
        self._padx0 = 0.0
        self._pady0 = 0.0
        self._drx = -100
        self._dry = -100
        self._ex_dst = None

        self._connButton = tk.Button(self, overrelief = 'solid', text = 'Connect Drone', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.connect, width = 20, height = 1)
        self._disconnButton = tk.Button(self, overrelief = 'solid', text = 'Disconnect Drone', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.disconnect, width = 20, height = 1, state = 'disabled')
        self._takeoffButton = tk.Button(self, overrelief = 'solid', text = 'Take Off', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.central_takeoff, width = 10, height = 1, state = 'disabled')
        self._landButton = tk.Button(self, overrelief = 'solid', text = 'Land', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.central_land, width = 10, height = 1, state = 'disabled')
        self._stopButton = tk.Button(self, overrelief = 'solid', text = 'Stop', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.central_stop, width = 10, height = 1, state = 'disabled')
        self._padButton = tk.Button(self, overrelief = 'solid', text = 'Control Pad', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.controlPad, width = 15, height = 1, state = 'disabled')
        self._idlingButton = tk.Button(self, overrelief = 'solid', text = 'Idling', font = 'default 12', fg = 'white', bg = '#888888', command = self.idling_selector, width = 12, height = 1, state = 'disabled')
        self._directButton = tk.Button(self, overrelief = 'solid', text = 'Direct', font = 'default 12', fg = 'white', bg = '#888888', command = self.direct_selector, width = 12, height = 1, state = 'disabled')
        self._autoButton = tk.Button(self, overrelief = 'solid', text = 'Auto', font = 'default 12', fg = 'white', bg = '#888888', command = self.auto_selector, width = 12, height = 1, state = 'disabled')
        self._trOnButton = tk.Button(self, overrelief = 'solid', text = 'Tracking On', font = 'default 10', fg = 'white', bg = '#888888', command = self.tracking_on, width = 11, height = 1, state = 'disabled')
        self._trOffButton = tk.Button(self, overrelief = 'solid', text = 'Tracking Off', font = 'default 10', fg = 'white', bg = '#888888', command = self.tracking_off, width = 11, height = 1, state = 'disabled')
        self._sensingButton = tk.Button(self, overrelief = 'solid', text = 'Sensing again', font = 'default 10', fg = 'white', bg = '#888888', command = self.re_sensing, width = 11, height = 1, state = 'disabled')
        self._camOnButton = tk.Button(self, overrelief = 'solid', text = 'Camera On', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.camera_on, width = 12, height = 1, state = 'disabled')
        self._camOffButton = tk.Button(self, overrelief = 'solid', text = 'Camera Off', font = 'default 15', fg = 'white', bg = '#2d2d2d', command = self.camera_off, width = 12, height = 1, state = 'disabled')
        self._spdUpButton = tk.Button(self, overrelief = 'solid', text = '▲', font = 'default 10', fg = 'white', bg = '#2d2d2d', command = self.autoUp, width = 1, height = 1, state = 'disabled')
        self._spdDownpButton = tk.Button(self, overrelief = 'solid', text = '▼', font = 'default 10', fg = 'white', bg = '#2d2d2d', command = self.autoDown, width = 1, height = 1, state = 'disabled')
        self._trackingButton = tk.Button(self, overrelief = 'solid', text = 'Tracking', font = 'default 12', fg = 'white', bg = '#888888', command = self.tracking_selector, width = 12, height = 1, state = 'disabled')

        self._appBgLabel.place(x = -10, y = 0)
        self._stateLabel.place(x = 702, y = 8)
        self._modeLabel.place(x = 670, y = 50)
        self._batteryLabel.place(x = 670, y = 92)
        self._tofLabel.place(x = 670, y = 134)
        self._heightLabel.place(x = 670, y = 176)
        self._currentSiteLabel.place(x = 670, y = 218)
        self._reservedSiteLabel.place(x = 670, y = 260)
        self._targetLabel.place(x = 670, y = 302)
        self._fireLabel.place(x = 670, y = 344)
        self._currentMode.place(x = 880, y = 50)
        self._currentBattery.place(x = 880, y = 92)
        self._currentTof.place(x = 880, y = 134)
        self._currentHeight.place(x = 880, y = 176)
        self._currentSite.place(x = 880, y = 218)
        self._reservedSite.place(x = 880, y = 260)
        self._currentTarget.place(x = 860, y = 305)
        self._fireDetected.place(x = 880, y = 344)
        self._modeListLabel.place(x = 510, y = 8)
        self._modeListLabel2.place(x = 500, y = 22)
        self._autolistLabel.place(x = 506, y = 125)
        self._spdsetLabel.place(x = 10, y = 170)
        self._spdLabel.place(x = 250, y = 170)
        self._rsvLabel.place(x = 10, y = 231)
        self._rsvLabel2.place(x = 40, y = 241)
        self._rsvSiteLabel.place(x = 173, y = 231)
        self._rsvTargetLabel.place(x = 290, y = 231)

        self._rsvSiteEnt.place(x = 202, y = 259)
        self._rsvTargetEnt.place(x = 302, y = 259)

        self._map.place(x = 1040, y = 50)
        self._map.create_line(0, 100 * self._scale, 200 * self._scale, 100 * self._scale, fill = '#eeeeee')
        self._map.create_line(100 * self._scale, 0, 100 * self._scale, 200 * self._scale, fill = '#eeeeee')
        self._map.create_rectangle(self._pad1x - 25, self._pad1y - 25, self._pad1x + 25, self._pad1y + 25, fill = '#0a0a0a')
        self._map.create_text(self._pad1x, self._pad1y, text = '1', font = 'default 18', fill = '#eeeeee')
        self._map.create_rectangle(self._pad2x - 25, self._pad2y - 25, self._pad2x + 25, self._pad2y + 25, fill = '#0a0a0a')
        self._map.create_text(self._pad2x, self._pad2y, text = '2', font = 'default 18', fill = '#eeeeee')
        self._map.create_rectangle(self._pad3x - 25, self._pad3y - 25, self._pad3x + 25, self._pad3y + 25, fill = '#0a0a0a')
        self._map.create_text(self._pad3x, self._pad3y, text = '3', font = 'default 18', fill = '#eeeeee')
        self._map.create_rectangle(self._pad4x - 25, self._pad4y - 25, self._pad4x + 25, self._pad4y + 25, fill = '#0a0a0a')
        self._map.create_text(self._pad4x, self._pad4y, text = '4', font = 'default 18', fill = '#eeeeee')

        self._dr = self._map.create_oval(0, 0, 0, 0, fill = 'blue')
        self._dr_range_left = self._map.create_line(0, 0, 0, 0)
        self._dr_range_right = self._map.create_line(0, 0, 0, 0)

        self._ob0 = self._map.create_oval(0, 0, 0, 0, fill = 'green')
        self._ob1 = self._map.create_oval(0, 0, 0, 0, fill = 'green')
        self._ob2 = self._map.create_oval(0, 0, 0, 0, fill = 'green')
        self._ob3 = self._map.create_oval(0, 0, 0, 0, fill = 'green')
        self._ob4 = self._map.create_oval(0, 0, 0, 0, fill = 'green')
        self._ob_list = [self._ob0, self._ob1, self._ob2, self._ob3, self._ob4]

        self._obn0 = self._map.create_text(0, 0)
        self._obn1 = self._map.create_text(0, 0)
        self._obn2 = self._map.create_text(0, 0)
        self._obn3 = self._map.create_text(0, 0)
        self._obn4 = self._map.create_text(0, 0)
        self._obn_list = [self._obn0, self._obn1, self._obn2, self._obn3, self._obn4]

        self._connButton.place(x = 10, y = 10)
        self._disconnButton.place(x = 250, y = 10)
        self._takeoffButton.place(x = 10, y = 60)
        self._landButton.place(x = 140, y = 60)
        self._stopButton.place(x = 270, y = 60)
        self._padButton.place(x = 10, y = 110)
        self._idlingButton.place(x = 511, y = 50)
        self._directButton.place(x = 511, y = 90)
        self._autoButton.place(x = 511, y = 130)
        self._trOnButton.place(x = 522, y = 165)
        self._trOffButton.place(x = 522, y = 195)
        self._sensingButton.place(x = 522, y = 225)
        self._camOnButton.place(x = 200, y = 110)
        self._camOffButton.place(x = 350, y = 110)
        self._spdUpButton.place(x = 340, y = 162)
        self._spdDownpButton.place(x = 340, y = 182)
        self._trackingButton.place(x = 511, y = 257)
        
        self._log.place(x = 10, y = 316)

        self.append_log('Welcome to Drone Control System Application !')

    def append_log(self, msg) :
        now = str(datetime.datetime.now())[0:-7]
        self._log.insert(tk.END, "[{}] {}".format(now, msg))
        self._log.update()
        self._log.see(tk.END)

    def os_wlan_connect(self) :
        os.system(f'''cmd /c "netsh wlan connect name={self._ssid}"''')

    def connection_check(self) :
        try :
            self.append_log('Trying to connect to our drone... (%d/5)' %(self._count + 1))

            result = os.popen("netsh wlan show interfaces").read()
            result = result.replace(' ', '').split('\n')
            if result[8] == 'SSID:RMTT-3B3E92' :
                self.append_log('Connected SUCCESSFULLY.')

                messagebox.showinfo('Notice', 'Connection Success.')

                self._connButton['state'] = tk.DISABLED

                self._connectionCode = True
                self._count = 0
                self.after(3000, self.connect)
                return None
            elif self._count > 3 :
                raise Exception('Time out.')
            
        except :
            self.append_log('Time out.')

            self._count = 0
            messagebox.showerror('Notice', 'Runtime Error.')

        else :
            self._count += 1
            self.os_wlan_connect()
            self.after(3000, self.connection_check)

    def connect(self) :
        if self._connectionCode == False :
            self.connection_check()
        else :
            self.append_log('A booting process starts.')

            self._count = 1000
            self._sub_engines = [Engine.remote(type) for type in self._engine_types]
            self.engine_booting()

    def disconnect(self) :
        self._connectionCode = False
        self._mode = self._ctrl_types[0]

        _ = ray.get(self._sub_engines[0].drone_off.remote())
        ray.shutdown()

        os.system("netsh wlan disconnect")
        self._currentBattery['text'] = 'None'
        self._currentTof['text'] = 'None'
        self._currentHeight['text'] = 'None'
        self._currentMode['text'] = 'None'

        self._disconnButton['state'] = tk.DISABLED
        self._takeoffButton['state'] = tk.DISABLED
        self._landButton['state'] = tk.DISABLED
        self._stopButton['state'] = tk.DISABLED
        self._padButton['state'] = tk.DISABLED
        self._idlingButton['state'] = tk.DISABLED
        self._directButton['state'] = tk.DISABLED
        self._autoButton['state'] = tk.DISABLED
        self._trOnButton['state'] = tk.DISABLED
        self._trOffButton['state'] = tk.DISABLED
        self._sensingButton['state'] = tk.DISABLED
        self._camOnButton['state'] = tk.DISABLED
        self._camOffButton['state'] = tk.DISABLED

        self._connButton['state'] = tk.NORMAL

        self.append_log('Disconnected.')

    def engine_booting(self) :
        if self._count > 1 :
            self.append_log('Now %.1fpercent progressed for booting.' %((1000 - self._count)*100/1000))

            power = ray.get([engine.main_operation.remote() for engine in self._sub_engines])
            self._count -= 1
            self._log.delete(tk.END)
            self.after(1, self.engine_booting)
        
        elif self._count == 1 :
            self.append_log('The system operation starts.')

            power = ray.get([engine.main_operation.remote() for engine in self._sub_engines])
            self._count -= 1
            self.power_storage(power)
            self.after(1, self.engine_booting)

        else :
            self.append_log('Initial mode of drone : Idling')
            self.append_log('Initial cam window : Nonvisualized')

            _ = ray.get([engine.set_engine.remote() for engine in self._sub_engines])
           
            self._disconnButton['state'] = tk.NORMAL
            self._takeoffButton['state'] = tk.NORMAL
            self._stopButton['state'] = tk.NORMAL
            self._padButton['state'] = tk.NORMAL
            self._directButton['state'] = tk.NORMAL
            self._autoButton['state'] = tk.NORMAL
            self._sensingButton['state'] = tk.NORMAL
            self._trackingButton['state'] = tk.NORMAL

            self._camOnButton['state'] = tk.NORMAL
            self._spdUpButton['state'] = tk.NORMAL
            self._spdDownpButton['state'] = tk.NORMAL

            self._currentMode['text'] = self._ctrl_types[0]

            self.after(1, self.engine_operation)

    def engine_operation(self) :
        if self._connectionCode :
            t0 = time.time()

            sharing_frame = ray.put(self._held_frame)
            command = ray.put(self.central_control())

            power = ray.get([engine.main_operation.remote(command, sharing_frame) for engine in self._sub_engines])
            self.power_storage(power)

            self._currentBattery['text'] = self._held_bat
            self._currentHeight['text'] = self._held_height
            self._currentTof['text'] = self._held_tof
            self._currentSite['text'] = self._held_mid
            if self._fireCode :
                self._fireDetected['bg'] = '#ff0000'
            else :
                self._fireDetected['bg'] = '#00ff00'

            delta_t = time.time() - t0
            print(delta_t)

            self.positioning(delta_t)
            self.sub_positioning()

            self.after(1, self.engine_operation)
        else :
            pass

    def power_storage(self, power) :
        self._held_mid = power[0][0][0]
        self._held_x = power[0][0][1]
        self._held_y = power[0][0][2]

        self._held_yaw = power[0][1][0]
        self._held_bat = power[0][1][1]
        self._held_height = power[0][1][2]
        self._held_tof = power[0][1][3]
        self._held_frame = power[0][1][4]

        self._takeoffCode = power[0][2][0]
        self._held_vx = power[0][2][1]
        self._held_vy = power[0][2][2]

        self._held_dic = power[1][0]
        self._eyes_dic = power[1][1]
        self._squares_dic = power[1][2]

        if power[1][3] :
            self._frame_height = power[1][3][0]
            self._frame_width = power[1][3][1]

        self._fireCode = power[2]

    def central_takeoff(self) :
        command = 'take off'
        _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
        self._landButton['state'] = tk.NORMAL
        self._takeoffButton['state'] = tk.DISABLED

        self.append_log('Central_control - takeoff command for drone')

    def central_land(self) :
        command = 'land'
        _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
        self._landButton['state'] = tk.DISABLED
        self._takeoffButton['state'] = tk.NORMAL
        self.idling_selector()

        self.append_log('Central_control - land command for drone')


    def central_stop(self) :
        command = 'stop'
        _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        self.append_log('Central_control - stop command for drone')

    def idling_selector(self) :
        command = 'stop'
        _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        self._mode = self._ctrl_types[0]
        self._currentMode['text'] = self._ctrl_types[0]
        self._idlingButton['state'] = tk.DISABLED
        self._directButton['state'] = tk.NORMAL
        self._autoButton['state'] = tk.NORMAL
        self._trOnButton['state'] = tk.DISABLED
        self._trOffButton['state'] = tk.DISABLED
        self._trackingButton['state'] = tk.NORMAL
        self._tracking = False
        self._trigger = True

        self.append_log('Mode switching - from %s to idling' %self._mode)

    def direct_selector(self) :
        command = 'stop'
        _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
        self._mode = self._ctrl_types[1]
        self._currentMode['text'] = self._ctrl_types[1]
        self._idlingButton['state'] = tk.NORMAL
        self._directButton['state'] = tk.DISABLED
        self._autoButton['state'] = tk.NORMAL
        self._trOnButton['state'] = tk.DISABLED
        self._trOffButton['state'] = tk.DISABLED
        self._trackingButton['state'] = tk.NORMAL
        self._tracking = False
        self._trigger = True

        self.append_log('Mode switching - from %s to direct' %self._mode)

    def auto_selector(self) :
        self._mode = self._ctrl_types[2]
        self._currentMode['text'] = self._ctrl_types[2]
        self._trigger = True

        self._idlingButton['state'] = tk.NORMAL
        self._directButton['state'] = tk.NORMAL
        self._autoButton['state'] = tk.DISABLED
        self._trOnButton['state'] = tk.NORMAL
        self._trackingButton['state'] = tk.NORMAL

        self.append_log('Mode switching - from %s to auto' %self._mode)

    def tracking_selector(self) :
        self._mode = self._ctrl_types[3]
        self._currentMode['text'] = self._ctrl_types[3]

        self._idlingButton['state'] = tk.NORMAL
        self._directButton['state'] = tk.NORMAL
        self._autoButton['state'] = tk.NORMAL
        self._trOnButton['state'] = tk.DISABLED
        self._trOffButton['state'] = tk.DISABLED
        self._trackingButton['state'] = tk.DISABLED
        self._trigger = True

        self.append_log('Mode switching - from %s to face tracking' %self._mode)
        
    def tracking_on(self) :
        self._tracking = True

        self._trOnButton['state'] = tk.DISABLED
        self._trOffButton['state'] = tk.NORMAL

        self.append_log('Getting function to search target with reconnaissance.')

    def tracking_off(self) :
        self._tracking = False
        self._trigger = True

        self._trOnButton['state'] = tk.NORMAL
        self._trOffButton['state'] = tk.DISABLED

        self.append_log('Searching function OFF.')

    def set_site(self, event) :
        self._reserved_site = self._rsvSiteEnt.get()
        self._reservedSite['text'] = self._reserved_site

        self.append_log('Your command for the next site "%s" is reserved.' %self._reserved_site)

    def set_target(self, event) :
        self._target = self._rsvTargetEnt.get()
        self._currentTarget['text'] = self._target

        self.append_log('Your command for the target to search "%s" is reserved.' %self._target)

    def get_faceinfo(self, target) :
        left_from_c = self._held_dic[target][0] - self._eyes_dic[tuple(self._held_dic[target])][0][0]
        right_from_c = self._eyes_dic[tuple(self._held_dic[target])][1][0] - self._held_dic[target][0]
        square = self._squares_dic[tuple(self._held_dic[target])]
        union = left_from_c + right_from_c
        left_ratio = left_from_c/union
        right_ratio = right_from_c/union

        error_x = (self._frame_width - self._held_dic[target][0])/self._frame_width
        error_y = (self._frame_height - self._held_dic[target][1])/self._frame_height

        return [square, left_ratio, right_ratio, error_x, error_y]

    def controlPad(self) :
        if self._padCode : 
            kp.pygame.quit()
            self._padCode = False

            self.append_log('The control pad is nonvisualized.')

        else :
            kp.init()
            self._padCode = True
    
            self.append_log('The control pad in use only for direct mode is visualized.')

    def positioning(self, delta_t = 0) :
        self._map.delete(self._dr)
        self._map.delete(self._dr_range_left)
        self._map.delete(self._dr_range_right)
        x = self._held_x
        y = self._held_y
        r = 20

        if int(x) == -100 and int(y) == -100 :
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')

            self._padx0 = x
            self._pady0 = y
            return

        if self._held_mid == 1.0 and (x != self._padx0 or y != self._pady0) :
            self._drx = int(self._pad1x + x * self._scale)
            self._dry = int(self._pad1y - y * self._scale)
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')

        elif self._held_mid == 2.0 and (x != self._padx0 or y != self._pady0) :
            self._drx = int(self._pad2x + x * self._scale)
            self._dry = int(self._pad2y - y * self._scale)
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')

        elif self._held_mid == 3.0 and (x != self._padx0 or y != self._pady0) :
            self._drx = int(self._pad3x + x * self._scale)
            self._dry = int(self._pad3y - y * self._scale)
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')
        
        elif self._held_mid == 4.0 and (x != self._padx0 or y != self._pady0) :
            self._drx = int(self._pad4x + x * self._scale)
            self._dry = int(self._pad4y - y * self._scale)
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')

        else :
            self._drx += int(-18*self._held_vy*delta_t*self._scale)
            self._dry += int(18*self._held_vx*delta_t*self._scale)
            self._dr = self._map.create_oval(self._drx - r, self._dry - r, self._drx + r, self._dry + r, fill = 'blue')
        
        if self._fireCode :
            self._dr_range_left = self._map.create_line(self._drx, self._dry, self._drx + int((60000**(1/2))*sin(radians(self._held_yaw - 27.5))), self._dry - int((60000**(1/2))*cos(radians(self._held_yaw - 27.5))), width = 5, fill = '#ff0000')
            self._dr_range_right = self._map.create_line(self._drx, self._dry, self._drx + int((60000**(1/2))*sin(radians(self._held_yaw + 27.5))), self._dry - int((60000**(1/2))*cos(radians(self._held_yaw + 27.5))), width = 5, fill = '#ff0000')
            if self._trg1 :
                self.append_log("Fire is detected at the direction of the front of our drone !! :")
                self.append_log("The location of detected fire : %d o'clock from (%d, %d) at the site '%d'" %(self.determine_CLKD(self._held_yaw), self._drx, self._dry, self.whereIs(self._drx, self._dry)))
                self._trg1 = False
                self.after(2000, self.trg1_rising)

        else :
            self._dr_range_left = self._map.create_line(self._drx, self._dry, self._drx + int((60000**(1/2))*sin(radians(self._held_yaw - 27.5))), self._dry - int((60000**(1/2))*cos(radians(self._held_yaw - 27.5))), width = 5, fill = '#00ff00')
            self._dr_range_right = self._map.create_line(self._drx, self._dry, self._drx + int((60000**(1/2))*sin(radians(self._held_yaw + 27.5))), self._dry - int((60000**(1/2))*cos(radians(self._held_yaw + 27.5))), width = 5, fill = '#00ff00')
        
        self._padx0 = x
        self._pady0 = y

    def sub_positioning(self) :
        rp = 24 * 17
        r = 20
        for n in range(len(self._ob_list)) :
            self._map.delete(self._ob_list[n])
        for n in range(len(self._obn_list)) :
            self._map.delete(self._obn_list[n])

        self._ob_list = []
        self._obn_list = []

        if self._held_dic :
            try :
                for name in list(self._held_dic.keys()) :
                    square = self._squares_dic[tuple(self._held_dic[name])]
                    cp = square**(1/2)
                    ratio = rp/cp
                    d = 35 * ratio * self._scale

                    x = self._held_dic[name][0]
                    error_x = ((self._frame_width/2) - x)/(self._frame_width/2)
                    d2 = d * error_x * (16.25/31)

                    x = int(self._drx + d * sin(radians(self._held_yaw)) + d2 * cos(radians(self._held_yaw)))
                    y = int(self._dry - d * cos(radians(self._held_yaw)) + d2 * sin(radians(self._held_yaw)))
                    self._ob_list.append(self._map.create_oval(x - r, y - r, x + r, y + r, fill = 'green'))
                    self._obn_list.append(self._map.create_text(x + r, y + r, text = name))

                    if self._trg2 :
                        self.append_log("%s is detected. Location : (%d, %d) at the site '%d'" %(name, x, y, self.whereIs(x, y)))
                        self._trg2 = False
                        self.after(3000, self.trg2_rising)
            except :
                pass

    def central_control(self) :
        if self._mode == self._ctrl_types[0] :
            return

        elif self._mode == self._ctrl_types[1] :
            if self._padCode :
                lr, fb, ud, yv = 0, 0, 0, 0
                speed = 40
                if kp.getKey("LEFT"):
                    lr = -speed
                elif kp.getKey("RIGHT"):
                    lr = speed
                if kp.getKey("UP"):
                    fb = speed
                elif kp.getKey("DOWN"):
                    fb = -speed
                if kp.getKey("w"):
                    ud = speed
                elif kp.getKey("s"):
                    ud = -speed
                if kp.getKey("a"):
                    yv = -speed
                elif kp.getKey("d"):
                    yv = speed
                if kp.getKey("q"):
                    self._landButton['state'] = tk.DISABLED
                    self._takeoffButton['state'] = tk.NORMAL
                    return 'land'
                elif kp.getKey("e"):
                    self._landButton['state'] = tk.NORMAL
                    self._takeoffButton['state'] = tk.DISABLED
                    return 'take off'
                return [lr, fb, ud, yv]
            return
        
        elif self._mode == self._ctrl_types[2] :
            if self._tracking :
                try :
                    self._info = self.get_faceinfo(self._target)

                except :
                    self._info = None

                else :
                    self.central_stop()
                    self.tracking_selector()
                    self._trigger = True
                    self._tracking = False

            if self._takeoffCode :
                pass
            else :
                self._landButton['state'] = tk.NORMAL
                self._takeoffButton['state'] = tk.DISABLED
                return 'take off'

            if self._trigger :
                self.after(2000, self.sub_control)
                self._trigger = False
                return
            return
        
        elif self._mode == self._ctrl_types[3] :
            try :
                self._info = self.get_faceinfo(self._target)
            
            except :
                self._info = None
                return [0, 0, 0, 0]
            
            else :
                lr, fb, ud, yv = 0, 0, 0, 0
                if self._info[0] > self._tolerance_range[1] :
                    fb = -26
                elif self._info[0] < self._tolerance_range[0] :
                    fb = 26

                if self._info[3] < 0.4 :
                    lr = -26
                elif self._info[3] > 0.6 :
                    lr = 26

                if self._info[4] < 0.5 :
                    ud = -26
                elif self._info[4] > 0.7 :
                    ud = 26

                if self._info[0] > 38000 and self._info[1] < 0.2 :
                    lr = -30
                    yv = 45
                elif self._info[0] > 38000 and self._info[2] < 0.2 :
                    lr = 30
                    yv = -45

                if self._duplicate_check == self._info[0] :
                    return [0, 0, 0, 0]
                
                self._duplicate_check = self._info[0]

                return [lr, fb, ud, yv]

    def sub_control(self) :
        if self._mode != self._ctrl_types[2] :
            self._ex_dst = None
            return

        candidate = [1, 2, 3, 4]

        if self._held_mid == 1.0 :
            if self._held_yaw > -10 and self._held_yaw < 10 :
                if self._held_tof > 1000 :
                    command = '1to2'
                else :
                    command = '1to2x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > -55 and self._held_yaw < -35 :
                if self._held_tof > 1000 :
                    command = '1to3'
                else :
                    command = '1to3x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > -100 and self._held_yaw < -80 :
                if self._held_tof > 1000 :
                    command = '1to4'
                else :
                    command = '1to4x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return
            
            else :
                pass

        elif self._held_mid == 2.0 :
            if self._held_yaw > 170 or self._held_yaw < -170 :
                if self._held_tof > 1000 :
                    command = '2to1'
                else :
                    command = '2to1x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > -100 and self._held_yaw < -80 :
                if self._held_tof > 1000 :
                    command = '2to3'
                else :
                    command = '2to3x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > -145 and self._held_yaw < -125 :
                if self._held_tof > 1000 :
                    command = '2to4'
                else :
                    command = '2to4x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return
                
            else :
                pass
            
        elif self._held_mid == 3.0 :
            if self._held_yaw > 125 and self._held_yaw < 145 :
                if self._held_tof > 1000 :
                    command = '3to1'
                else :
                    command = '3to1x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > 80 and self._held_yaw < 100 :
                if self._held_tof > 1000 :
                    command = '3to2'
                else :
                    command = '3to2x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > 170 or self._held_yaw < -170 :
                if self._held_tof > 1000 :
                    command = '3to4'
                else :
                    command = '3to4x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return
            
            else :
                pass
        
        elif self._held_mid == 4.0 :
            if self._held_yaw > 80 and self._held_yaw < 100 :
                if self._held_tof > 1000 :
                    command = '4to1'
                else :
                    command = '4to1x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > 35 and self._held_yaw < 55 :
                if self._held_tof > 1000 :
                    command = '4to2'
                else :
                    command = '4to2x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return

            elif self._held_yaw > -10 and self._held_yaw < 10 :
                if self._held_tof > 1000 :
                    command = '4to3'
                else :
                    command = '4to3x'
                _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))
                self._ex_dst = int(self._held_mid)
                self._trigger = True
                return
                
            else :
                pass
        
        if self._ex_dst :
            candidate.remove(int(self._held_mid))
            try :
                candidate.remove(self._ex_dst)
            except :
                pass
            sel = candidate[randint(0, 1)]

        else :
            candidate.remove(int(self._held_mid))
            sel = candidate[randint(0, 2)]

        if self._reserved_site :
            if self._reserved_site == '1' :
                if int(self._reserved_site) == int(self._held_mid) :
                    pass
                else :
                    sel = 1
            elif self._reserved_site == '2' :
                if int(self._reserved_site) == int(self._held_mid) :
                    pass
                else :
                    sel = 2
            elif self._reserved_site == '3' :
                if int(self._reserved_site) == int(self._held_mid) :
                    pass
                else :
                    sel = 3
            elif self._reserved_site == '4' :
                if int(self._reserved_site) == int(self._held_mid) :
                    pass
                else :
                    sel = 4

        if self._held_mid == 1.0 :
            if sel == 2 :
                dTheta = int(0 - self._held_yaw)
            elif sel == 3 :
                dTheta = int(-45 - self._held_yaw)
            elif sel == 4 :
                dTheta = int(-90 - self._held_yaw)
            command = 'rotate' + str(dTheta)
            _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        elif self._held_mid == 2.0 :
            if sel == 1 :
                dTheta = int(180 - self._held_yaw)
            elif sel == 3 :
                dTheta = int(-90 - self._held_yaw)
            elif sel == 4 :
                dTheta = int(-135 - self._held_yaw)
            command = 'rotate' + str(dTheta)
            _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        elif self._held_mid == 3.0 :
            if sel == 1 :
                dTheta = int(135 - self._held_yaw)
            elif sel == 2 :
                dTheta = int(90 - self._held_yaw)
            elif sel == 4 :
                dTheta = int(-180 - self._held_yaw)
            command = 'rotate' + str(dTheta)
            _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        elif self._held_mid == 4.0 :
            if sel == 1 :
                dTheta = int(90 - self._held_yaw)
            elif sel == 2 :
                dTheta = int(45 - self._held_yaw)
            elif sel == 3 :
                dTheta = int(0 - self._held_yaw)
            command = 'rotate' + str(dTheta)
            _ = ray.get(self._sub_engines[0].main_operation.remote(command, None))

        self._trigger = True
    
    def re_sensing(self) :
        _ = ray.get(self._sub_engines[1].re_sensing.remote())

    def camera_on(self) :
        self._camOnButton['state'] = tk.DISABLED
        self._camOffButton['state'] = tk.NORMAL
        _ = ray.get(self._sub_engines[1].camera_on.remote())

    def camera_off(self) :
        self._camOnButton['state'] = tk.NORMAL
        self._camOffButton['state'] = tk.DISABLED
        _ = ray.get(self._sub_engines[1].camera_off.remote())

    def autoUp(self) :
        if self._autoSpeed == 60 :
            return
        self._autoSpeed += 1
        self._spdLabel['text'] = str(self._autoSpeed) + ' cm/s'
        _ = ray.get(self._sub_engines[0].autoUp.remote())

    def autoDown(self) :
        if self._autoSpeed == 10 :
            return
        self._autoSpeed -= 1
        self._spdLabel['text'] = str(self._autoSpeed) + ' cm/s'
        _ = ray.get(self._sub_engines[0].autoDown.remote())

    def whereIs(self, x, y) :
        if x < 250 and y < 250 :
            return 3
        elif x > 250 and y < 250 :
            return 2
        elif x < 250 and y > 250 :
            return 4
        elif x > 250 and y > 250 :
            return 1
        else :
            return
        
    def determine_CLKD(self, yaw) :
        if -165 < yaw <= -135 :
            return 7
        elif -135 < yaw <= -105 :
            return 8
        elif -105 < yaw <= -75 :
            return 9
        elif -75 < yaw <= -45 :
            return 10
        elif -45 < yaw <= -15 :
            return 11
        elif -15 < yaw <= 15 :
            return 12
        elif 15 < yaw <= 45 :
            return 1
        elif 45 < yaw <= 75 :
            return 2
        elif 75 < yaw <= 105 :
            return 3
        elif 105 < yaw <= 135 :
            return 4
        elif 135 < yaw <= 165 :
            return 5
        elif yaw > 165 or yaw < -165 :
            return 6
        
    def trg1_rising(self) :
        self._trg1 = True
    
    def trg2_rising(self) :
        self._trg2 = True