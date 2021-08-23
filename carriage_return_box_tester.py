from tkinter.constants import S
import PySimpleGUI as sg
from text import Text
from line import Line 
# GLOBAL CONSTANTS 
RETURN_CHAR = "\\"

# Returns Text object if there is a text box at given location, none otherwise. 
def get_text_box_at_location(click_location, text_boxes):
    x_click, y_click = click_location
    for text in text_boxes:
        top_left, bott_right= text.get_bounding_coordinates()
        x_left, top_y = top_left 
        x_right, bott_y = bott_right
        # the user clicked on an already present textbox 
        if x_click in range(x_left, x_right +1) and y_click in range(bott_y, top_y+1):
            return text 
    return None # no textbox at given location 

def handle_canvas_click(click_location, text_boxes, user_input):
    text_at_click_location = get_text_box_at_location(click_location, text_boxes)
    # fill user input with text present in textbox so they can append new text. 
    if text_at_click_location:
        text_at_click_location.toggle_selected()
        is_selected = text_at_click_location.get_selected() # get the selected property 
        if is_selected:
            text_at_click_location.draw_selected_box() 
            user_input.update(text_at_click_location.get_lines()) 
        else:
            text_at_click_location.delete_selected_box() 
    else:
        user_input.update("") # we want to clear user input so user can start typing
    # finally we want to set the focus onto the input element 
    user_input.set_focus()

def delete_text_box(textbox):
    textbox.delete_bounding_box()
    textbox.delete_lines()

def draw_text_box(textbox, user_text):
    # sometimes we may not want to use this function to draw new text
    # when we already have text and just want to draw 
    # same text at say a given new location when dragging
    # for which we would simply set None as user_text param.   
    if user_text:
        textbox.put_lines(user_text) 
    textbox.write_lines()
    textbox.draw_bounding_box()

def delete_text_boxes(textboxes):
    for textbox in textboxes:
        delete_text_box(textbox)

def move_text_box(textbox, new_location):
    delete_text_box(textbox)
    textbox.change_location(new_location)   
    draw_text_box(textbox, None) # draw textbox at new location 

def get_selected_text_boxes(textboxes):
    return [textbox for textbox in textboxes if textbox.get_selected() ] 

# helper method for deleting selected text boxes 
def delete_lines(selected_textboxes, texts_to_lines):
    for textbox in selected_textboxes:
        if textbox in texts_to_lines: # not all textboxes are connected 
            for line in texts_to_lines[textbox]:
                line.delete_line() #delete line from canvas 
 
# event handler for 'delete' event
def delete_selected_text_boxes(texts, texts_to_others, texts_to_lines):
    # delete the boxes from canvases 
    selected_textboxes = get_selected_text_boxes(texts)
    drag_textboxes = [texts_to_others[textbox] for textbox in selected_textboxes]  
    delete_text_boxes(selected_textboxes)
    delete_text_boxes(drag_textboxes)
    delete_lines(selected_textboxes, texts_to_lines)
    #remove all references 
    for textbox in selected_textboxes:
        # remove all references 
        texts.remove(textbox) 
        del texts_to_others[textbox]
        if textbox in texts_to_lines: 
            del texts_to_lines[textbox] 

        

def connect_selected_text_boxes(selected_textboxes, texts_to_lines, canvas, canvas_drag):
    loc1, loc2 = (textbox.get_location() for textbox in selected_textboxes)
    line_main = Line(canvas, loc1, loc2)
    line_drag = Line(canvas_drag, loc1, loc2) 
    line_main.draw_line()
    line_drag.draw_line() 
    for textbox in selected_textboxes:
        if textbox not in texts_to_lines:
            texts_to_lines[textbox] = []  

        texts_to_lines[textbox] += [line_main, line_drag]  # extending array of lines to text to lines dict 
        textbox.delete_selected_box() # delete the selected box 
        textbox.toggle_selected() # now false

def switch_tabs(drag_button, drag_tab, no_drag_tab):
    drag_button_text = drag_button.get_text() 
    if drag_button_text == "Drag mode: OFF":
        drag_tab.update(visible=True)
        drag_tab.select() 
        no_drag_tab.update(visible=False)
        drag_button.update(text = f"Drag mode: ON")
    else:
        drag_tab.update(visible=False)
        no_drag_tab.select() 
        no_drag_tab.update(visible=True) 
        drag_button.update(text = f"Drag mode: OFF")

def enable_and_disable_buttons_and_inputs(drag_button_text, user_input, selected_texts, delete_button, connect_button):
    user_input.update( disabled = (drag_button_text == "Drag mode: ON") ) # want to disable user input if in drag mode
    delete_button.update( disabled = not(len(selected_texts) > 0) )
    connect_button.update( disabled = not(len(selected_texts) == 2 ) ) 

def main():
    #layout widgets 
    canvas = sg.Graph(
        (700, 600), (0,0), (500, 500), key='-CANVAS-',
        background_color='white', enable_events=True, 
        )
    canvas_drag = sg.Graph(
        (700, 600), (0,0), (500, 500), key='-CANVAS-DRAG-',
        background_color='white', enable_events=True,drag_submits=True,
        )
    no_drag_tab = sg.Tab('Dragging Off', [[canvas]])
    drag_tab = sg.Tab('Dragging On', [[canvas_drag]], visible = False ) 
    tabs = sg.TabGroup([[no_drag_tab, drag_tab]])
    connect_button = sg.Button("Delete")
    delete_button = sg.Button("connect selected boxes")
    drag_mode_button = sg.Button("Drag mode: OFF", key="-TOGGLE-DRAG-MODE-")
    user_input = sg.Input('', key="-INPUT-", enable_events=True) 
    layout = [[user_input,drag_mode_button, connect_button, delete_button], [tabs]]
    window = sg.Window('carriage return tester', layout).finalize() 
    user_input.bind('<Return>', '-RETURN-CHARACTER-') # make an event for the return character
    # global event variables 
    location = None
    texts = [] # list of text box figures drawn onto the main canvas (the non-draggable canvas)
    texts_to_others = {} # for each textbox we have a corresponding text box figure drawn onto the other canvas -this maps the two.
    texts_to_lines = {} # maps text objects to a list of line objects which are 'connected' to these textboxes. 

    while True: 
        event , values = window.read()
        # print(texts_to_lines, texts_to_others, texts)  
        if event == sg.WIN_CLOSED:
            break
        if event == '-RETURN-CHARACTER-':
            # append return character to current text 
            window['-INPUT-'].update( 
                values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
            )
        if event == "-CANVAS-":
            location = values[event] # location of click
            handle_canvas_click(location, texts, user_input)
        
        if event.startswith("-CANVAS-DRAG-"):
            x_click, y_click = values['-CANVAS-DRAG-'] #drag location 
            hot_spot_threshold = 10 # the error we give for a hotspot drag  
            for main_textbox, drag_textbox in texts_to_others.items():
                x, y = drag_textbox.get_location() 
                if abs(x-x_click) <= hot_spot_threshold and abs(y-y_click) <= hot_spot_threshold:
                    new_location = (x_click, y_click)
                    # move both textboxes on both canvases 
                    move_text_box(main_textbox, new_location)
                    move_text_box(drag_textbox, new_location)  

                    if main_textbox in texts_to_lines: 
                        for line in texts_to_lines[main_textbox]:
                            x_1, y_1 = line.loc1 
                            if abs(x_1-x_click) <= hot_spot_threshold and abs(y_1-y_click) <= hot_spot_threshold:
                                line.move_line((x_click, y_click), line.loc2 )
                            else:
                                line.move_line(line.loc1, (x_click, y_click) )
                    

                    

        if event.startswith("-INPUT-"):
            # we only want to execute this code when NOT in drag mode 
            if drag_mode_button.get_text() == "Drag mode: OFF": 

                if event == "-INPUT--RETURN-CHARACTER-":
                    window['-INPUT-'].update( 
                            values['-INPUT-'] + RETURN_CHAR # text box splits based on return char 
                                )
                try:
                    user_text = values['-INPUT-']
                    text_at_click_location = get_text_box_at_location(location, texts)
                    if text_at_click_location is None: # no text at current location, user is trying to create a new textbox here. 
                        # create new text onto both canvases 
                        text_at_click_location = Text(location, canvas)
                        text_on_drag_canvas = Text(location, canvas_drag)
                        # key value pairing for easy and efficient tracking when dragging event occurs.
                        texts_to_others[text_at_click_location] = text_on_drag_canvas
                        texts.append(text_at_click_location) # append it to list for tracking 
                    else:
                        text_at_click_location.put_lines(user_text)
                        delete_text_box(text_at_click_location) 
                        delete_text_box(texts_to_others[text_at_click_location])  
                        # this is required for a subtle reason -- when rewriting into text boxes 
                        # and the textbox happens to be a multiple line textbox: if you backspace to a previous line 
                        # the older location of a click may sometimes no longer be valid and cause a bug where 
                        # rewriting the same text into a new textbox somewhere near. This is the solution to this bug: 
                        location = text_at_click_location.get_location()

                    draw_text_box(text_at_click_location, user_text)
                    draw_text_box(texts_to_others[text_at_click_location], user_text)  

                except Exception as e:
                    sg.popup(f"This action returned the following error: \n\t'{e}'.\nYou probably forgot to click where you want to type!")
        
        if event == "Delete":
            delete_selected_text_boxes(texts, texts_to_others, texts_to_lines)

        if event == "connect selected boxes":
            selected_textboxes = get_selected_text_boxes(texts)
            connect_selected_text_boxes(selected_textboxes, texts_to_lines, canvas, canvas_drag) 
        
        if event == "-TOGGLE-DRAG-MODE-":
            switch_tabs(drag_mode_button, drag_tab, no_drag_tab)
        
        # want to disable and enable buttons based on certain conditions
        # so that the user can't fire certain events based on these conditions 
        enable_and_disable_buttons_and_inputs( 
            drag_mode_button.get_text(), 
            user_input, get_selected_text_boxes(texts), 
            connect_button, delete_button
        )

           


    window.close()

if __name__=="__main__":
    main() 
