import PySimpleGUI as sg
# CONSTANTS:
VERT_EXPANSION_HEIGHT = 3 #for expanding textboxes horizontally, this constant may need to be adjusted when you adjust canvas size
RETURN_CHARACTER = '\\'

class Text:
	def __init__(self, location, text, font='default 13'):
		self.location = location #the location of the click
		self.text = text 
		self.id = None #the figure id of the text written on canvas
		self.bounding_box = None #will be a tuple of top left and bottom right coordinates (which are tuples themselves)
		self.text_box_id = None
		self.font = font
		self.selected = False
		self.ids = None

	def update_text(self, text):
		self.text = text

	def delete_text(self, canvas):
		for text_id in self.ids:
			canvas.delete_figure(text_id)

	def delete_text_box(self, canvas):
		canvas.delete_figure(self.text_box_id)

	def draw_text_box(self, canvas, fill_color = "white"):
		top_left, bott_right = self.bounding_box[0], self.bounding_box[1]
		self.text_box_id = canvas.draw_rectangle(top_left, bott_right, fill_color, line_color = "green")
		self.bring_text_to_front(canvas) 

	def change_text_box_color(self, canvas, new_fill_color):
		self.delete_text_box(canvas)
		self.draw_text_box(canvas, fill_color = new_fill_color)

	def expand_text_box_vertically(self, delta_y):
		bott_right = self.bounding_box[1]
		bott_right = (bott_right[0], bott_right[1] - delta_y) # -(delta_y) since the origin is in bottom left of canvas
		self.bounding_box = (self.bounding_box[0], bott_right)

	def get_max_line_len_idx(self, lines):
		line_lens = list(map(lambda line: len(line), lines))
		max_len = max(line_lens)
		return line_lens.index(max_len)

	def bring_text_to_front(self, canvas):
		for text_id in self.ids:
			canvas.bring_figure_to_front(text_id)

	def put_text(self, text, canvas):
		if self.text != text:
			self.update_text(text)

		if self.ids is not None:
			self.delete_text(canvas)

		delta_y = 0
		self.ids = []
		lines = self.text.split(RETURN_CHARACTER)
		for line in lines: 
			text_id = canvas.draw_text(text = line, location = (self.location[0], self.location[1] - delta_y),\
				 font = self.font, text_location = sg.TEXT_LOCATION_LEFT)
			self.ids.append(text_id)
			delta_y += VERT_EXPANSION_HEIGHT #increases the y value of the location to draw next line onto 

		# calculates the x_delta which will be appended onto the bounding box so it fits all the text lines
		extra_padding = 2
		longest_text_line_x = canvas.get_bounding_box(self.ids[self.get_max_line_len_idx(lines)])[1][0]
		first_text_line_x = canvas.get_bounding_box(self.ids[0])[1][0]
		delta_x = longest_text_line_x - first_text_line_x + extra_padding

		self.bounding_box = canvas.get_bounding_box(self.ids[0]) 
		self.bounding_box = (self.bounding_box[0], (self.bounding_box[1][0] + delta_x, self.bounding_box[1][1]) ) 

		if RETURN_CHARACTER in self.text:
			self.expand_text_box_vertically(self.text.count(RETURN_CHARACTER)*VERT_EXPANSION_HEIGHT)#expands based on the number of 'backslashes' which are our return chars

		if self.text_box_id is not None:
			self.delete_text_box(canvas)

		self.draw_text_box(canvas)


	def is_selected(self):
		return self.selected

	def change_selected(self):
		self.selected = not self.selected

	def get_location(self):
		return self.location #may need this method to connect selected boxes with a line

	def __str__(self):
		return "textbox with text {self.text}".format(self=self)


def get_text_objects_at_location(location, canvas, text_objects):
	figures_at_loc = canvas.get_figures_at_location(location)
	for text_object in text_objects:
		if text_object.text_box_id in figures_at_loc:
			return text_object
	return None

def get_selected_text_objects(canvas, text_objects):
	selected_objects = list(filter(lambda obj: obj.is_selected(), text_objects))
	return selected_objects

def deselect_connected_boxes(canvas, text_box1, text_box2):
	text_box1.change_text_box_color(canvas, 'white')
	text_box2.change_text_box_color(canvas, 'white')
	text_box1.change_selected()
	text_box2.change_selected()

def connect_selected_text_boxes(canvas, text_objects):
	box1, box2 = text_objects[0], text_objects[1]
	box1_loc, box2_loc = box1.get_location(), box2.get_location()
	line_id = canvas.draw_line(box1_loc, box2_loc, color = 'black')
	deselect_connected_boxes(canvas, box1, box2)
	canvas.send_figure_to_back(line_id)
	return line_id # we will want to have this so that we can delete the lines later...thanks for making me think of this @Mike. 

def change_input_cursor_color(widget, color):
	widget.Widget.config(insertbackground=color)


def main():
	sg.theme('Material1')
	bg_color = sg.theme_background_color()
	# Building the layout of the window 
	layout = [
			[sg.Input('', key = '-INPUT-', enable_events = True, text_color = 'black', background_color ='white'),
			 sg.Button('Connect Boxes', key='-CONNECT-'),\
			sg.Button('Erase Last', key='-ERASE-'), sg.Button('Erase All', key='-ERASE-ALL-'),\
			sg.Button('Drag Mode Off', key='-DRAG-MODE-')],
	]
	# We need a canvas with drag submits for dragging and moving the textboxes 
	canvas_drag = sg.Graph(
		(1000, 600), (0,0), (100,100),
		background_color="white", 
		 key = '-GRAPH-2', enable_events=True, drag_submits=True,
		)
	# We also need a canvas without drag submits so that the user can click toggle the selected 
	# property of the text boxes -- the drag submits will interfere with this behaviour 
	# so we need to alternate between the two canvases behind the scenes 
	canvas_no_drag = sg.Graph(
		(1000, 600), (0,0), (100,100),
		background_color="white", key = '-GRAPH-1', enable_events=True
		)
	list_of_tabs = [[
		sg.Tab('tab 1',[[canvas_no_drag]] ), 
		sg.Tab('tab 2', [[canvas_drag]], visible=False) # Only one of these tabs will ever be visible at a time 
		]]
	tabs = sg.TabGroup(list_of_tabs)

	layout .append(
		[tabs]
	)
	window = sg.Window('', layout).finalize()
	# change_input_cursor_color(window['-INPUT-'], bg_color)

	clicked_areas = []
	text_objects = []
	lines = []
	drag_mode = False# global variable to enable dragging widgets
	cur_canvas = '-GRAPH-1' # global variable to track which tab we are currently on 

	while True:
		event, values = window.read()
		canvas = window[cur_canvas]
		if event == sg.WIN_CLOSED:
			break

		elif event == '-DRAG-MODE-':
			drag_mode = not drag_mode # toggle the drag_mode 
			button_text = f"Drag Mode {'On' if drag_mode else 'Off'}"
			window[event].update(text = button_text)
			if drag_mode:
				cur_canvas = '-GRAPH-2'
				window['tab 1'].update(visible=False)
				window['tab 2'].update(visible = True)
				window['tab 2'].select() 
			else:
				cur_canvas = '-GRAPH-1'
				window['tab 2'].update(visible=False)
				window['tab 1'].update(visible = True)
				window['tab 1'].select() 				

		elif event.startswith('-ERASE-'):
			
			if '-ALL-' in event: #the user wishes to clear all canvas elements
				canvas.erase()
				clicked_areas.clear()
				text_objects.clear() 
			else: # user wishes to delete only the last text object drawn 
				if text_objects: 
					last_text_box = text_objects.pop()
					location = last_text_box.get_location()
					last_text_box.delete_text(canvas)
					last_text_box.delete_text_box(canvas)
					# this deletes the line attached to the text box we just deleted 
					for fig in canvas.get_figures_at_location(location):
						if fig in lines:
							line = lines.pop(lines.index(fig))
							canvas.delete_figure(line)
					

		elif event.startswith('-GRAPH-'):
			print("**********GRAPH************")
			print(values)
			print(clicked_areas)
			click_location = values[cur_canvas] 
			text_obj = get_text_objects_at_location(click_location,canvas, text_objects)
			if text_obj:
				if cur_canvas == '-GRAPH-2': # the canvas with drag submits -- we are in drag mode 
					text_obj.selected = True
					x_click, y_click = click_location
					threshold = 10 
					x_cur, y_cur = text_obj.get_location() 
					# for dragging 
					if (abs(x_click-x_cur) <= threshold and abs(y_click-y_cur) <= threshold):
						print("Here in move location")
						text_obj.location = (x_click, y_click) #change the location of box 
						text_obj.put_text(text_obj.text, canvas) # update the textbox
						# we need to set the selected property back to false in case the user decides
						# to leave the box at the new location 
						text_obj.selected = False
						# need to draw the lines that were connected to the text box again 
						# this deletes the line attached to the text box we just deleted 
						previous_location = (x_cur, y_cur) 
						for fig in canvas.get_figures_at_location(previous_location):
							if fig in lines:
								line = lines.pop(lines.index(fig))
								canvas.delete_figure(line)
								
				elif cur_canvas == "-GRAPH-1": # user is toggling a text object selected property while not in drag mode 
					text_obj.change_selected() # toggle the text boxes selection property 
					text_obj.change_text_box_color(canvas, "orange" if text_obj.selected else "white")


			else: # no text objects currently at area clicked -- user is creating a text object
				# so we need to grab the users input
				clicked_areas.append(click_location)
				window['-INPUT-'].update("") # clear the input (may be old text input from previous text boxes )
				window['-INPUT-'].set_focus() # set the focus to input element which grabs user input
	
		# Event that is triggered when user is typing and creating a text object 
		elif event == '-INPUT-':
			other_canvas = '-GRAPH-1' if cur_canvas == "-GRAPH-2" else "-GRAPH-2"
			text = values[event]
			last_clicked_area = clicked_areas[-1]
			text_obj = get_text_objects_at_location(last_clicked_area,canvas, text_objects)
			
			if text_obj:
				if last_clicked_area != text_obj.location: # this is a bug that occurs sometimes -- can't tell you why 
					text_obj.location = last_clicked_area # need to correct this 
				text_obj.put_text(text, canvas)
					
			else:
				text_obj = Text(last_clicked_area, text)
				text_obj.put_text(text, canvas)
				text_objects.append(text_obj)
				print("Did you last click: ", last_clicked_area)
			print(text_obj)

		elif event == '-CONNECT-':
			selected_text_boxes = get_selected_text_objects(canvas, text_objects)
			if len(selected_text_boxes) != 2: #Only two boxes should be connected at a time 
				sg.popup(
					f"num of selected text boxes = {len(selected_text_boxes)}"
					)
				for selected_box in selected_text_boxes:
					print(selected_box)
			else:
				line = connect_selected_text_boxes(canvas, selected_text_boxes)
				lines.append(line)
			
	window.close()

if __name__ == '__main__':
	main()