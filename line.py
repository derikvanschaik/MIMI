import PySimpleGUI as sg 
class Line:
    def __init__(self, canvas, loc1, loc2) -> None:
        self.canvas = canvas 
        self.id = None # Pysimplegui line id
        self.color = 'black' # default color 
        self.width = 1 # default width
        self.loc1 = loc1
        self.loc2 = loc2
    
    def draw_line(self):
        self.id = self.canvas.draw_line(self.loc1, self.loc2, width = self.width, color=self.color)
        self.canvas.send_figure_to_back(self.id) # lines are always sent to back 
    
    def delete_line(self):
        self.canvas.delete_figure(self.id) 
        self.id = None # remove reference to this figure 
    
    def change_width(self, new_width):
        self.width = new_width 
        self.delete_line()
        self.draw_line(self.loc1, self.loc2, width = self.width, color = self.color)
    
    def change_color(self, new_color):
        self.color = new_color 
        self.delete_line()
        self.draw_line(self.loc1, self.loc2, width = self.width, color = self.color)
    
    def move_line(self, loc1_new, loc2_new):
        # update the new locations to where the line is being moved to 
        # in this context really only one location changes
        if self.id != None: 
            self.loc1 = loc1_new
            self.loc2 = loc2_new
            self.delete_line() 
            self.draw_line()
    
    def is_line_drawn(self):
        return self.id != None 
    
    def __str__(self):
        return f"this line currently has line id: {self.id}" 

    