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
	layout = [

			[sg.Input('', key = '-INPUT-', enable_events = True, text_color = bg_color, background_color =bg_color),
			 sg.Button('Connect Boxes', key='-CONNECT-'),sg.Button('Erase Last', key='-ERASE-'), sg.Button('Erase All', key='-ERASE-ALL-')],
			[sg.Graph((1000, 600), (0,0), (100,100), key = '-GRAPH-', enable_events=True)]
	]

	window = sg.Window('', layout).finalize()
	change_input_cursor_color(window['-INPUT-'], bg_color)

	clicked_areas = []
	text_objects = []
	lines = [] 
	while True:
		event, values = window.read()
		canvas = window['-GRAPH-']
		if event == sg.WIN_CLOSED:
			break

		elif event.startswith('-ERASE-'):
			canvas = window['-GRAPH-']
			if '-ALL-' in event: #the user wishes to clear all canvas elements
				canvas.erase()
				clicked_areas.clear()
				text_objects.clear() 
			else:
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
					

		elif event == '-GRAPH-':
			click_location = values[event]
			text_obj = get_text_objects_at_location(click_location,canvas, text_objects)
			if text_obj:
				selected_color = "white" if text_obj.is_selected() else "orange" #changes the text color given its cur selected state
				text_obj.change_text_box_color(canvas, selected_color)
				text_obj.change_selected() #toggle the texts selected state
				
			else:
				clicked_areas.append(click_location)
				window['-INPUT-'].set_focus()
				window['-INPUT-'].update("")

		elif event == '-INPUT-':
			text = values[event]
			last_clicked_area = clicked_areas[-1]
			text_obj = get_text_objects_at_location(last_clicked_area,canvas, text_objects)
			if text_obj:
				text_obj.put_text(text, canvas)
			else:
				text_obj = Text(last_clicked_area, text)
				text_obj.put_text(text, canvas)
				text_objects.append(text_obj)
			print(text_obj)

		elif event == '-CONNECT-':
			selected_text_boxes = get_selected_text_objects(canvas, text_objects)
			if len(selected_text_boxes) != 2: #Only two boxes should be connected at a time 
				sg.popup("Not enough or too many boxes have been selected for connecting.")
			else:
				line = connect_selected_text_boxes(canvas, selected_text_boxes)
				lines.append(line)
			
	window.close()

if __name__ == '__main__':
	main()