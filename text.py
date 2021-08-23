import PySimpleGUI as sg 
class Text:
    def __init__(self, location, canvas):
        self.canvas = canvas 
        self.location = location 
        self.lines = [] # list of text that the text box contains, each element is a seperate line. 
        self.line_height = 0
        self.max_line_width = 0  
        self.line_ids = [] # ids of pysimple gui drawn lines 
        self.bounding_box_id = None # id of pysimple gui bounding boxes
        # field for determining if cur text box is selected 
        self.selected = False 
        # styling fields 
        self.font_name = "Default"
        self.font_size = 15 
        # return character 
        self.return_character = "\\" # back tab is return chars 
        # visual aid for indicating whether box is selected or not
        self.selected_box_id_color = "RoyalBlue" 
        self.selected_box_id = None 
        # colors of figures 
        self.background_color = "white"
        self.line_color = "black"
        self.text_color = "black"
    
    def get_location(self):
        return self.location
    
    def change_location(self, new_location): 
        self.location = new_location 
    
    def get_lines(self): # returns the current text inside of textbox 
        return "\\".join(self.lines)  # escape char joins the lines 

    def put_lines(self, text):
        self.lines = text.split(self.return_character)
    
    def update_line_height(self, text):
        drawn_text = self.canvas.draw_text(
            text, self.location, font=f"{self.font_name} {self.font_size}"
            )
        (_, top_y), (_, bott_y) = self.canvas.get_bounding_box(drawn_text)
        self.canvas.delete_figure(drawn_text) 
        self.line_height = top_y - bott_y

    def update_max_line_width(self, line_id):
        (left_x, _), (right_x, _) = self.canvas.get_bounding_box(line_id)
        cur_line_width = right_x-left_x
        self.max_line_width = max(self.max_line_width, cur_line_width) 

    def write_lines(self):
        self.update_line_height(self.lines[0])
        for line_num, line in enumerate(self.lines):
            x, y = self.location 
            y = y - line_num*self.line_height # y is updated to be on next line 
            # write text onto canvas 
            line_drawn = self.canvas.draw_text(
                            line, (x, y), font = f"{self.font_name} {self.font_size}", 
                            text_location = sg.TEXT_LOCATION_LEFT, color = self.text_color, 
                            )
            self.update_max_line_width(line_drawn) 
            self.line_ids.append(line_drawn)

    def get_bounding_coordinates(self):
        # we want to get location of top and bottom of bounding box 
        (x_left, top_y), (_, _) = self.canvas.get_bounding_box(self.line_ids[0])
        (_, _), (_, bott_y) = self.canvas.get_bounding_box(self.line_ids[-1])
        top_left = (x_left, top_y)
        bott_right = (x_left + self.max_line_width, bott_y) 
        return top_left, bott_right 

    def draw_bounding_box(self):
        # we want to get location of top and bottom of bounding box 
        top_left, bott_right = self.get_bounding_coordinates() 
        self.bounding_box_id = self.canvas.draw_rectangle(
            top_left, bott_right, fill_color = self.background_color, line_color = self.line_color 
            )
        # since we have now drawn over the text we need to redraw the text....
        self.write_lines()  
        # we will also want to draw the selected bounding box in case we are redrawing...
        if self.selected_box_id:
            self.delete_selected_box() # delete old one 
        if self.selected:
            self.draw_selected_box()  # draw new one if selected 
    
    def draw_selected_box(self):
        top_left, bott_right = self.get_bounding_coordinates()
        top_left_x, top_left_y = top_left
        bott_right_x, bott_right_y = bott_right
        pad = 5 
        top_left_x -= pad 
        top_left_y += pad 
        bott_right_x += pad 
        bott_right_y -= pad 
        self.selected_box_id = self.canvas.draw_rectangle( (top_left_x, top_left_y), (bott_right_x, bott_right_y), 
                                                            line_color = self.selected_box_id_color
                                                        )
    def delete_selected_box(self):
        self.canvas.delete_figure(self.selected_box_id)
        self.selected_box_id = None 

    def delete_lines(self):
        for line_id in self.line_ids:
            self.canvas.delete_figure(line_id) 
        self.line_ids = [] # reset 

    def delete_bounding_box(self):
        # deletes and resets bounding box to None 
        self.canvas.delete_figure(self.bounding_box_id)
        self.bounding_box_id = None
        # may need to delete selected box as well 
        if self.selected_box_id:
            self.delete_selected_box()
    
    def get_font_size(self):
        return self.font_size

    def change_font_size(self, new_font_size):
        self.font_size = new_font_size 
    
    def change_font_name(self, new_font_name):
        self.font_name = new_font_name
    
    def change_background_color(self, new_color):
        self.background_color = new_color 
    
    def change_line_color(self, new_color):
        self.line_color = new_color 
    
    def change_text_color(self, new_color):
        self.text_color = new_color 

    def get_selected(self):
        return self.selected 
    
    def toggle_selected(self):
        self.selected = not self.selected
    
    def __str__(self):
        return "-".join(self.lines)
        