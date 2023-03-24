from tkinter import *
from tkinter import filedialog
from tkinter import messagebox
from tkinter import ttk
from threading import *
import json
import csv
import os
import getpass
import sys
import time
import datetime
import pandas as pd
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException, TwilioException
from json.decoder import JSONDecodeError
from requests.exceptions import ConnectionError
from pandas.errors import EmptyDataError

#------- Variables -------#
x = datetime.datetime.now()
file_name = f'{x.strftime("%d")}-{x.strftime("%m")}-{x.year} {x.strftime("%H")}.{x.strftime("%M")}.{x.strftime("%S")}'
count = 0
running = True
error = False
font_style = 'Cambria'
highlight_background_color = '#bababa'
highlight_color = '#9ecaed'
button_bg_color = '#102021'
button_fg_color = 'white'

user_pc_name = getpass.getuser()
twilio_database = f'C:\\Users\\{user_pc_name}\\Documents\\Twilio\\Database\\config.json'
path = f'C:\\Users\\{user_pc_name}\\Documents\\Twilio\\Output'

root = Tk()
root.title('Twilio SMS Script')

#------- Application Measurements -------#
app_width = 400
app_height = 600

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

x = (screen_width / 2) - (app_width / 2)
y = ((screen_height / 2) - (app_height / 2)) * 0.65

root.geometry(f'{app_width}x{app_height}+{int(x)}+{int(y)}')
root.resizable(0, 0)
try:
	root.iconbitmap('.ico\\sms.ico')
except:
	root.iconbitmap('sms.ico')
# except Exception as e:
# 	print(e)

#------- Initial Variable Declaration -------#
var = IntVar()
checkvar = IntVar()
setvar = IntVar()
hour = StringVar()
minute = StringVar()
second = StringVar()

#------- Limit Check Function -------#
def limitSizeHour(*args):
	value = hour.get()
	if len(value) > 2:
		hour.set(value[:2])
	elif value == '':
		return True
	elif not value.isdigit():
		hour.set(value[:-1])
		info_msg('Warning', 'Value must be number!')
	elif int(value) > 24:
		hour.set(value[:-2])
		info_msg('Warning', 'Timer can not be set more than 1 day!')

def limitSizeMinute(*args):
	value = minute.get()
	if len(value) > 2:
		minute.set(value[:2])
	elif value == '':
		return True
	elif not value.isdigit():
		minute.set(value[:-1])
		info_msg('Warning', 'Value must be positive number!')
	elif int(value) > 59:
		minute.set(value[:-2])
		info_msg('Warning', 'Put value between 0-59!')

def limitSizeSecond(*args):
	value = second.get()
	if len(value) > 2:
		second.set(value[:2])
	elif value == '':
		return True
	elif not value.isdigit():
		second.set(value[:-1])
		info_msg('Warning', 'Value must be positive number!')
	elif int(value) > 59:
		second.set(value[:-2])
		info_msg('Warning', 'Put value between 0-59!')

#------- Clock Default Value -------#
hour.set("00")
minute.set("00")
second.set("00")

hour.trace('w', limitSizeHour)
minute.trace('w', limitSizeMinute)
second.trace('w', limitSizeSecond)

hours_title = Label(root, text='Hours', font=(font_style, 11, "normal"))
mins_title = Label(root, text='Minutes', font=(font_style, 11, "normal"))
sec_title = Label(root, text='Seconds', font=(font_style, 11, "normal"))

hourEntry= Entry(root, width=3, font=(font_style, 18, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1, justify='center', textvariable=hour)
minuteEntry= Entry(root, width=3, font=(font_style, 18, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1, justify='center', textvariable=minute)
secondEntry= Entry(root, width=3, font=(font_style, 18, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1, justify='center', textvariable=second)

#------- Datebase Directory Create -------#
if os.path.exists(f'C:\\Users\\{user_pc_name}\\Documents\\Twilio'):
	if os.path.exists(f'C:\\Users\\{user_pc_name}\\Documents\\Twilio\\Database'):
		pass
	else:
		os.mkdir(f'C:\\Users\\{user_pc_name}\\Documents\\Twilio\\Database')
else:
	os.mkdir(f'C:\\Users\\{user_pc_name}\\Documents\\Twilio')
	os.mkdir(f'C:\\Users\\{user_pc_name}\\Documents\\Twilio\\Database')

#------- Output Folder Create -------#
if os.path.exists(path):
	pass
else:
	os.mkdir(path)

#------- Button Hover Effect -------#
def on_enter(e):
	e.widget['background'] = '#4CA3DD'
	e.widget['cursor'] = 'hand2'

def on_leave(e):
	e.widget['background'] = button_bg_color

#------- Create CSV File -------#
header = ['Numbers']
failed_file = open(f'{path}\\failed {file_name}.csv', 'w', encoding='UTF8', newline='')
writer = csv.writer(failed_file)
writer.writerow(header)
failed_file.close()

#------- Country Code -------#
Label(root, text='Country Code or Number', font=(font_style, 11, "normal")).grid(row=0, column=0, pady=(20, 0), padx=(40, 0))
country_code = Entry(root, width=20, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)
country_code.grid(row=1, column=0, pady=(0, 10), padx=(40, 0))

#------- Text Message & Character Counter -------#
character_counter = Label(root, text='Text Message', font=(font_style, 11, "normal"))
character_counter.grid(row=2, column=0, padx=(40, 0))
text_message = Text(root, width=40, height=10, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)
text_message.grid(row=3, column=0, pady=(0, 20), padx=(40, 0))

#------- Frames -------#
frame1 = LabelFrame(root, borderwidth=0)
frame1.place(x=110, y=360)

frame2 = LabelFrame(root, borderwidth=0)
frame2.config(highlightbackground='black')
frame2.place(x=10, y=360)

#------- Short Functions -------#
def info_msg(label, msg_text):
	messagebox.showinfo(label, msg_text)

def clear_frame():
	for widgets in frame1.winfo_children():
		widgets.grid_forget()
	for widgets in frame2.winfo_children():
		widgets.destroy()

def output_Folder_location():
	root_path = os.path.realpath(path)
	os.startfile(root_path)

def on_closing():
	if os.path.exists(f'{path}\\failed {file_name}.csv'):
		try:
			failed_file.close()
			if os.stat(f'{path}\\failed {file_name}.csv').st_size <= 9:
				os.remove(f'{path}\\failed {file_name}.csv')
		except UnboundLocalError:
			pass
	root.destroy()

def btn_count():
	global count
	count = count + 1
	if count > 1:
		clear_frame()

def threading():
	thread_solve = Thread(target=clicked_menu)
	thread_solve.start()

def single_sms_threading():
	thread_solve = Thread(target=single_sms)
	thread_solve.start()

def schedule_thread():
	thread_solve = Thread(target=schedule_progress)
	thread_solve.start()

cot = 1
def stop_timer():
	global cot
	cot = 0
	hourEntry.config(state=NORMAL)
	minuteEntry.config(state=NORMAL)
	secondEntry.config(state=NORMAL)
	country_code.config(state=NORMAL)
	text_message.config(state=NORMAL)
	selection_btn.config(text='Restart Timer', command=restart_timer)

def restart_timer():
	global cot
	cot = 1
	schedule_thread()

def schedule_progress():
	try:
		get_the_message = text_message.get("1.0", "end")
		get_country_code = country_code.get()
		if int(hour.get()) < 0 or int(minute.get()) < 0 or int(second.get()) < 0:
			info_msg("Warning", "Time can not be negative!")
		elif len(get_country_code) > 3:
			info_msg("Warning", "Invalid Country Code")
		elif len(get_country_code) == 0 or len(get_the_message) == 1:
			info_msg('Warning', 'Empty number or text message!')
		else:
			temp = int(hour.get())*3600 + int(minute.get())*60 + int(second.get())
			while temp >-1:
				if cot == 0:
					break
				select_menu.grid_forget()
				set_timer_btn.grid_forget()
				contact_list.grid_forget()

				selection_btn.config(text='Stop Schedule', command=stop_timer)
				selection_btn.grid(row=2, column=0, pady=(10, 0))
				settings_button.config(state=DISABLED)
				button.config(state=DISABLED)
				single_sms_send.config(state=DISABLED)
				hourEntry.config(state='readonly')
				minuteEntry.config(state='readonly')
				secondEntry.config(state='readonly')
				country_code.config(state='readonly')
				text_message.config(state=DISABLED)

				mins,secs = divmod(temp,60)
				hours=0
				if mins >60:
					hours, mins = divmod(mins, 60)
				hour.set("{0:02d}".format(hours))
				minute.set("{0:02d}".format(mins))
				second.set("{0:02d}".format(secs))
				root.update()
				time.sleep(1)
				if (temp == 0):
					hours_title.place_forget()
					hourEntry.place_forget()
					mins_title.place_forget()
					minuteEntry.place_forget()
					sec_title.place_forget()
					secondEntry.place_forget()
					threading()
				temp -= 1
	except ValueError:
		info_msg('Warning', 'Invalid Timer Setting!')
	except RuntimeError:
		print('Exit')

def set_timer():
	if setvar.get() == 1:
		hourEntry.place(x=120,y=525)
		minuteEntry.place(x=180,y=525)
		secondEntry.place(x=240,y=525)
		hours_title.place(x=119, y=560)
		mins_title.place(x=174, y=560)
		sec_title.place(x=234, y=560)
		selection_btn.config(text='Schedule SMS', command=schedule_thread)

	elif setvar.get() == 0:
		hours_title.place_forget()
		hourEntry.place_forget()
		mins_title.place_forget()
		minuteEntry.place_forget()
		sec_title.place_forget()
		secondEntry.place_forget()
		selection_btn.config(text='Send Message', command=threading)

def update(event):
	length = len(text_message.get("1.0", 'end-1c'))
	if length <= 160:
		character_counter.config(text= f"Text Message ({str(length)}/1)")
	elif length > 160 and length <= 320:
		new_length = length - 160
		character_counter.config(text= f"Text Message ({str(new_length)}/2)")
	elif length > 320 and length <= 480:
		new_length = length - 320
		character_counter.config(text= f"Text Message ({str(new_length)}/3)")
	elif length > 480 and length <= 640:
		new_length = length - 480
		character_counter.config(text= f"Text Message ({str(new_length)}/4)")
	elif length > 640 and length <= 800:
		new_length = length - 640
		character_counter.config(text= f"Text Message ({str(new_length)}/5)")
	elif length > 800 and length <= 918:
		new_length = length - 800
		character_counter.config(text= f"Text Message ({str(new_length)}/6)")
	elif length > 918:
		character_counter.config(text= "Text Message (Limit Exceed)")

def stop():
	global running
	running = False

def sms_progress_status(text):
	progress = Text(frame2, width=46, height=10, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1, padx=5)
	progress.insert(END, text + '\n')
	progress.config(state=DISABLED)
	progress.grid(row=0, column=0, pady=10)
	progress.see("end")

def progress_stop():
	country_code.config(state=NORMAL)
	text_message.config(state=NORMAL)
	progress_stop_btn.place(x=120, y=550)
	progress_stop_btn.bind("<Enter>", on_enter)
	progress_stop_btn.bind("<Leave>", on_leave)

def restart():
	python = sys.executable
	os.execl(python, python, * sys.argv)

def success_status_log(success_status_text):
	success_status = open(f'{path}\\status.log', "a", encoding='UTF8', newline='')
	success_status.write(success_status_text)
	success_status.close()

	success_status = open(f'{path}\\status.log', "r")
	sms_progress_status(success_status.read())

def failed_status_log(failed_status_text):
	failed_status = open(f'{path}\\status.log', "a", encoding='UTF8', newline='')
	failed_status.write(failed_status_text)
	failed_status.close()

	failed_status = open(f'{path}\\status.log', "r")
	sms_progress_status(failed_status.read())

#------- Database Connection -------#
def config():
	top = Toplevel()
	top.title("Configuration File")

	config_app_width = 375
	config_app_height = 400

	config_screen_width = root.winfo_screenwidth()
	config_screen_height = root.winfo_screenheight()

	config_x = (config_screen_width / 2) - (config_app_width / 2)
	config_y = (config_screen_height / 2) - (config_app_height / 2)

	top.geometry(f'{config_app_width}x{config_app_height}+{int(config_x)}+{int(config_y)}')
	top.grid_columnconfigure(0, minsize=0)
	top.resizable(0, 0)
	top.grab_release()
	try:
		top.iconbitmap('.ico\\sms.ico')
	except Exception as e:
		print(e)

	settings_button['state'] = 'disable'
	def top_destroy():
		top.destroy()
		settings_button['state'] = 'normal'

	top.protocol("WM_DELETE_WINDOW", top_destroy)

	#------- Loading Configuration -------#
	def loading_configuration():
		with open(twilio_database) as config_file:
			data = json.load(config_file)
			sid_data = data['account_sid']
			token_data = data['auth_token']
			sender_data = data['sender']
			alpha_data = data['alphanumeric']
			checkbox_data = data['checkbox']

		#------- Display Data -------#
		global account_sid_config
		global auth_token_config
		global sender_config
		global alpha_config
		global checkbox
		Label(top, text='Account SID', font=(font_style, 11, "normal")).grid(row=0, column=1, pady=(20, 0), padx=(40, 0))
		v1 = StringVar(top, value=sid_data)
		account_sid_config = Entry(top, textvariable=v1, width=35, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)
		account_sid_config.grid(row=1, column=1, pady=(0, 10), padx=(40, 0))

		Label(top, text='Auth Token', font=(font_style, 11, "normal")).grid(row=2, column=1, pady=(20, 0), padx=(40, 0))
		v2 = StringVar(top, value=token_data)
		auth_token_config = Entry(top, textvariable=v2, width=35, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)
		auth_token_config.grid(row=3, column=1, pady=(0, 10), padx=(40, 0))

		sender_label = Label(top, text='Sender Number', font=(font_style, 11, "normal"))
		v3 = StringVar(top, value=sender_data)
		sender_config = Entry(top, textvariable=v3, width=35, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)

		alpha_label = Label(top, text='Alphanumeric Code', font=(font_style, 11, "normal"))
		v3 = StringVar(top, value=alpha_data)
		alpha_config = Entry(top, textvariable=v3, width=35, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1)

		if checkbox_data == 1:
			alpha_label.grid(row=4, column=1, pady=(20, 0), padx=(40, 0))
			alpha_config.grid(row=5, column=1, padx=(40, 0))
		elif checkbox_data == 0:
			sender_label.grid(row=4, column=1, pady=(20, 0), padx=(40, 0))
			sender_config.grid(row=5, column=1, padx=(40, 0))

		def alpha_num():
			if checkvar.get() == 1:
				sender_label.grid_forget()
				sender_config.grid_forget()
				alpha_label.grid(row=4, column=1, pady=(20, 0), padx=(40, 0))
				alpha_config.grid(row=5, column=1, padx=(40, 0))
			elif checkvar.get() == 0:
				alpha_label.grid_forget()
				alpha_config.grid_forget()
				sender_label.grid(row=4, column=1, pady=(20, 0), padx=(40, 0))
				sender_config.grid(row=5, column=1, padx=(40, 0))

		checkbox = ttk.Checkbutton(top, text = "Use Alphanumeric Code", takefocus=False, variable = checkvar, command=alpha_num)
		if checkbox_data == 1:
			checkbox.state(['selected'])
		elif checkbox_data == 0:
			checkbox.state(['active'])
		checkbox.place(x=38, y=215)

	#------- Saving The Configuration -------#
	def saving_configuration():
		if len(account_sid_config.get()) == 0 or len(auth_token_config.get()) == 0 or len(sender_config.get()) == 0:
			info_msg("Warning", "Fill out all the boxes with correct information!")
		else:
			if len(account_sid_config.get()) < 34 or len(auth_token_config.get()) < 32:
				info_msg("Warning", "Invalid configuration!")
			else:
				global sid_config_get
				global token_config_get
				global sender_config_get
				global alpha_config_get
				global checkbox_config_get
				sid_config_get = account_sid_config.get()
				token_config_get = auth_token_config.get()
				sender_config_get = sender_config.get()
				alpha_config_get = alpha_config.get()
				checkbox_config_get = checkvar.get()

				data = {
					"account_sid": sid_config_get,
					"auth_token": token_config_get,
					"sender": sender_config_get,
					"alphanumeric": alpha_config_get,
					"checkbox": checkbox_config_get
				}
				with open(twilio_database, 'w') as f:
					json.dump(data, f, indent=4)

				response = info_msg("Info", "Successfully Saved!")
				if response == None:
					top.destroy()
					settings_button['state'] = 'normal'

	if os.path.exists(twilio_database):
		try:
			loading_configuration()
		except JSONDecodeError:

			#------- Creating Database File -------#
			os.remove(twilio_database)
			confirmation = info_msg('Reset Database', 'Somehow database has messed up. The application has reset the database. Please fill up with credentials. Thank you!!')
			if confirmation == None:
				open(twilio_database, 'x')
				data = {
					"account_sid": '',
					"auth_token": '',
					"sender": '',
					"alphanumeric": '',
					"checkbox": 0
				}
				with open(twilio_database, 'w') as f:
					json.dump(data, f, indent=4)

				loading_configuration()
	else:

		#------- Creating Database File -------#
		open(twilio_database, 'x')
		data = {
			"account_sid": '',
			"auth_token": '',
			"sender": '',
			"alphanumeric": '',
			"checkbox": 0
		}
		with open(twilio_database, 'w') as f:
			json.dump(data, f, indent=4)

		loading_configuration()

	#------- Saving The Configuration -------#
	def save():
		saving_configuration()

	save_button = Button(top, text='Save', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 12, "normal"),  pady=5, padx=121, borderwidth=0, command=save)
	save_button.place(x=40, y=250)

	save_button.bind("<Enter>", on_enter)
	save_button.bind("<Leave>", on_leave)

#------- Twilio Database Connection -------#
def twilio_connection():
	def existance_check():
		try:
			with open(twilio_database) as config_file:
				data = json.load(config_file)
				sid_data = data['account_sid']
				token_data = data['auth_token']
				sender_data = data['sender']
				alpha_data = data['alphanumeric']
				checkbox_data = data['checkbox']
			global account_sid
			global auth_token
			global sender
			global alpha
			global client
			global check
			account_sid = sid_data
			auth_token = token_data
			sender = sender_data
			alpha = alpha_data
			check = checkbox_data
			client = Client(account_sid, auth_token)
		except TwilioException:
			if len(account_sid) == 0 or len(auth_token) == 0 or len(sender) == 0:
				info_msg("Warning", "Twilio is not configured!")
			elif len(account_sid) < 34 or len(auth_token) < 32:
				info_msg("Warning", "Invalid configuration!")
			global error
			error = True
	if os.path.exists(twilio_database):
		try:
			existance_check()
		except JSONDecodeError:

			#------- Creating Database File -------#
			os.remove(twilio_database)
			confirmation = info_msg('Reset Database', 'Somehow database has messed up. The application has reset the database. Please fill up with credentials. Thank you!!')
			if confirmation == None:
				open(twilio_database, 'x')
				data = {
					"account_sid": '',
					"auth_token": '',
					"sender": '',
					"alphanumeric": '',
					"checkbox": 0
				}
				with open(twilio_database, 'w') as f:
					json.dump(data, f, indent=4)

				existance_check()
	else:

		#------- Creating Database File -------#
		open(twilio_database, 'x')
		data = {
			"account_sid": '',
			"auth_token": '',
			"sender": '',
			"alphanumeric": '',
			"checkbox": 0
		}
		with open(twilio_database, 'w') as f:
			json.dump(data, f, indent=4)

		existance_check()

#------- Application Main Interface -------#
def openDialogBox():
	global running
	running = True
	btn_count()
	root.filename = filedialog.askopenfilename(title='Choose CSV File', filetypes=(("CSV file", "*.csv"), ("All files", "*.*")))

	try:
		data = pd.read_csv(root.filename)
		data_dict = data.to_dict('list')
		options = []
		for row in data.columns:
			options.append(row)

		global clicked_menu
		def clicked_menu():
			settings_button.config(state=DISABLED)
			button.config(state=DISABLED)
			single_sms_send.config(state=DISABLED)
			set_timer_btn.grid_forget()
			select_menu.grid_forget()
			selection_btn.grid_forget()
			contact_list.grid_forget()
			twilio_connection()
			if error:
				pass
			else:
				global total_send_success
				global total_send_failed
				global send_success
				global send_failed
				total_send_success = 0
				total_send_failed = 0
				send_success = 0
				send_failed = 0
				numbers = data_dict[select_menu.get()]

				try:
					#------- Convert Float Number to Integer Number -------#
					int_numbers = [int(x) for x in numbers]

					#------- Get All Numbers -------#
					global get_the_message
					get_the_message = text_message.get("1.0", "end")
					get_country_code = country_code.get()
					if len(get_country_code) > 3 or str(get_country_code).startswith('+') ==  False:
						info_msg("Warning", "Invalid Country Code")
					elif len(get_country_code) == 0 or len(get_the_message) == 1:
						info_msg('Warning', 'Empty number or text message!')
					else:
						global running
						failed_file = open(f'{path}\\failed {file_name}.csv', 'a+', encoding='UTF8', newline='')
						for i in int_numbers:
							if running:
								try:
									country_code.config(state='readonly')
									text_message.config(state=DISABLED)
									global full_phone_number
									full_phone_number = str(get_country_code) + str(i)
									if checkvar.get() == 1:
										client.messages.create(body=get_the_message, from_=alpha, to=full_phone_number)
									else:
										client.messages.create(body=get_the_message, from_=sender, to=full_phone_number)

									send_success = send_success + 1
									total_send_success = send_success
									success_status_log(f'{full_phone_number} - Successfully Send {send_success} contact(s)\n')
								except TwilioRestException as e:
									if '20003' in str(e):
										country_code.config(state=NORMAL)
										text_message.config(state=NORMAL)
										info_msg('Error', 'May be your Twilio Account is currently suspended due to a lack of funds!')
										running = False
									elif 'Authenticate' in str(e):
										country_code.config(state=NORMAL)
										text_message.config(state=NORMAL)
										info_msg('Error', 'Twilio Authentication Error!')
										running = False
									else:
										send_failed = send_failed + 1
										total_send_failed = send_failed

										data = [i]
										writer = csv.writer(failed_file)
										writer.writerow(data)

										failed_status_log(f'{full_phone_number} - Failed to send {send_failed} contact(s)\n')
								except ConnectionError:
									country_code.config(state=NORMAL)
									text_message.config(state=NORMAL)
									info_msg('Error', 'You are not connected to the internet!')
									running = False
								except:
									country_code.config(state=NORMAL)
									text_message.config(state=NORMAL)
									info_msg('Error', 'Application is facing some issues. Contact with the developer!')
									running = False

								progress_stop()
							if running == False:
								progress_stop_btn.place_forget()
						progress_stop_btn.place_forget()

						if total_send_success > 0 or total_send_failed > 0:
							failed_status_log('====================================\n')
							failed_status_log(f'Successfully send {total_send_success} contact(s). Failed to send {total_send_failed} contact(s)')
							info_msg("Sent Message Status", f'Successfully send {total_send_success} contact(s). Failed to send {total_send_failed} contact(s)')
							restart_btn.place(x=60, y=550)
							restart_btn.bind("<Enter>", on_enter)
							restart_btn.bind("<Leave>", on_leave)

							output_btn.place(x=240, y=550)
							output_btn.bind("<Enter>", on_enter)
							output_btn.bind("<Leave>", on_leave)
						else:
							restart_btn.place(x=120, y=550)
							restart_btn.bind("<Enter>", on_enter)
							restart_btn.bind("<Leave>", on_leave)

						if os.path.exists(f'{path}\\status.log'):
							os.remove(f'{path}\\status.log')
						if os.path.exists(f'{path}\\failed {file_name}.csv'):
							try:
								failed_file.close()
								if os.stat(f'{path}\\failed {file_name}.csv').st_size <= 9:
									os.remove(f'{path}\\failed {file_name}.csv')
							except UnboundLocalError:
								pass

				except ValueError:
					info_msg('Error', 'Please select phone number column!')

		#------- List Menu -------#
		global select_menu
		select_menu = ttk.Combobox(frame1, state="readonly", value=options, width=19, font=(font_style, 11, "normal"))
		select_menu.current(0)
		select_menu.grid(row=0, column=0, pady=10)

		selection_btn.grid(row=2, column=0)
		selection_btn.bind("<Enter>", on_enter)
		selection_btn.bind("<Leave>", on_leave)

		#------- Display CSV File Info -------#
		def show_contact_list():
			csv_list = Toplevel()
			csv_list.title("File Information")

			csv_app_width = 375
			csv_app_height = 375

			csv_screen_width = root.winfo_screenwidth()
			csv_screen_height = root.winfo_screenheight()

			csv_x = (csv_screen_width / 2) - (csv_app_width / 2)
			csv_y = (csv_screen_height / 2) - (csv_app_height / 2)

			csv_list.geometry(f'{csv_app_width}x{csv_app_height}+{int(csv_x)}+{int(csv_y)}')
			csv_list.resizable(0, 0)

			csv_frame = LabelFrame(csv_list, borderwidth=0)
			csv_frame.grid_columnconfigure(1, minsize=-10)
			csv_frame.place(x=0, y=0)
			try:
				csv_list.iconbitmap('.ico\\sms.ico')
			except Exception as e:
				print(e)

			data = pd.read_csv(root.filename)
			data_dict = data.to_dict('list')
			options = []
			for row in data.columns:
				options.append(row)
			numbers = data_dict[select_menu.get()]
			mega_lists = []
			for mega_list in numbers:
				mega_lists.append(str(mega_list))
			line_mega_lists = '\n'.join(mega_lists)

			lists = Text(csv_frame, width=42, height=20, font=(font_style, 11, "normal"), borderwidth=0, highlightbackground=highlight_background_color, highlightcolor= highlight_color, highlightthickness=1, padx=5)
			lists.insert(1.0, str(select_menu.get()) + '\n')
			lists.insert(END, line_mega_lists)
			lists.config(state=DISABLED)
			lists.grid(row=0, column=0, pady=10, padx=10, sticky='ew')

			scroll = ttk.Scrollbar(csv_frame, orient='vertical', command=lists.yview)
			scroll.grid(row=0, column=2, sticky='ns', pady=10)
			lists['yscrollcommand'] = scroll.set

		#------- Show Contact List Button -------#
		global contact_list
		contact_list = Button(frame1, text='See Contact Lists', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, padx=15, pady=5, font=(font_style, 12, "normal"), borderwidth=0, command=show_contact_list)
		contact_list.grid(row=3, column=0, pady=10)
		contact_list.bind("<Enter>", on_enter)
		contact_list.bind("<Leave>", on_leave)

		set_timer_btn.grid(row=4, column=0)

	except FileNotFoundError:
		pass
	except EmptyDataError:
		info_msg('Error', 'Empty file!')

#------- Single SMS System -------#
def single_sms():
	twilio_connection()
	if error:
		pass
	else:
		try:
			get_the_message = text_message.get("1.0", "end")
			get_number = country_code.get()
			if len(get_number) == 14 or len(get_number) == 12:
				if checkvar.get() == 1:
					client.messages.create(body=get_the_message, from_=alpha, to=get_number)
				else:
					client.messages.create(body=get_the_message, from_=sender, to=get_number)
				info_msg('Success', f'Successfully send to {get_number} number')
			elif len(get_number) == 0 or len(get_the_message) == 0:
				info_msg('Warning', 'Empty number or text message!')
			else:
				info_msg('Warning', 'Invalid Number')
		except TwilioRestException as e:
			if 'Authenticate' in str(e):
				info_msg('Error', 'Twilio Authentication Error!')
			else:
				info_msg('Error', f'Sending failed to {get_number} number')
		except ConnectionError:
			info_msg('Error', 'You are not connected to the internet!')
		except:
			info_msg('Error', 'Application is facing some issues. Contact with the developer!')

single_sms_send = Button(root, text='Send Single Message', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 11, "normal"), pady=5, padx=22, command=single_sms_threading, borderwidth=0)
single_sms_send.place(x=110, y=280)

button = Button(root, text='Open CSV File', bg=button_bg_color, fg=button_fg_color, font=(font_style, 11, "normal"), padx=5, pady=5, activebackground=button_bg_color, activeforeground=button_fg_color, command=openDialogBox, borderwidth=0)
button.place(x=110, y=325)

settings_button = Button(root, text='Settings', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 11, "normal"), padx=5, pady=5, command=config, borderwidth=0)
settings_button.place(x=220, y=325)

#------- Text Message Bind -------#
text_message.bind('<KeyPress>', update)
text_message.bind('<KeyRelease>', update)

#------- Button Bind -------#
single_sms_send.bind("<Enter>", on_enter)
single_sms_send.bind("<Leave>", on_leave)

button.bind("<Enter>", on_enter)
button.bind("<Leave>", on_leave)

settings_button.bind("<Enter>", on_enter)
settings_button.bind("<Leave>", on_leave)

#------- Submit Button -------#
selection_btn = Button(frame1, text='Send Message', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, padx=41, pady=5, font=(font_style, 11, "normal"), borderwidth=0, command=threading)

#------- Progress Stop Button -------#
progress_stop_btn = Button(root, text='Stop Sending Message', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 11, "normal"), borderwidth=0, pady=5, padx=5, command=stop)

#------- Restart Button -------#
restart_btn = Button(root, text='Restart The Application', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 11, "normal"), borderwidth=0, pady=5, padx=5, command=restart)

#------- Output Folder Path -------#
output_btn = Button(root, text='Output Folder', bg=button_bg_color, fg=button_fg_color, activebackground=button_bg_color, activeforeground=button_fg_color, font=(font_style, 11, "normal"), borderwidth=0, pady=5, padx=5, command=output_Folder_location)

#------- Set Timer Button -------#
set_timer_btn = ttk.Checkbutton(frame1, text = "Set Timer", takefocus=False, variable = setvar, command=set_timer)

root.protocol("WM_DELETE_WINDOW", on_closing)
root.mainloop()